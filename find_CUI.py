# find_CUI.py
import json
import os
import time
import random
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Setează cheia ta OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
CACHE_FILE = "CUI_cache.json"

# Încarcă cache
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        cache = json.load(f)
else:
    cache = {}

def save_cache():
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=4, ensure_ascii=False)

def get_company_info_from_domain(domain: str, max_retries=3):
    """
    Returnează info firmă după domeniu cu throttling și retry dacă rate-limit
    """
    if domain in cache:
        return cache[domain]

    prompt = f"""
Ești expert în firme din România.
Cine deține site-ul {domain}? Răspunde STRICT cu JSON:
{{"nume": "...", "identificator": "...", "tip": "firma" sau "persoana fizica" sau "necunoscut"}}
"""

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-5-search-api",
                messages=[
                    {"role": "system", "content": "Ești expert în identificarea firmelor din România."},
                    {"role": "user", "content": prompt}
                ],
            )
            content = response.choices[0].message.content.strip()
            try:
                result = json.loads(content)
            except:
                result = {"nume": None, "identificator": None, "tip": "necunoscut"}

            cache[domain] = result
            save_cache()

            # Delay aleatoriu pentru throttling
            time.sleep(random.uniform(1.0, 2.0))
            return result

        except RateLimitError:
            wait_time = (attempt + 1) * 2
            print(f"[RateLimit] Retry in {wait_time}s for domain {domain}")
            time.sleep(wait_time)
        except Exception as e:
            print(f"Eroare la domeniu {domain}: {e}")
            break

    # fallback după retry-uri
    result = {"nume": None, "identificator": None, "tip": "necunoscut"}
    cache[domain] = result
    save_cache()
    return result


# Paralelizare moderată pentru mai multe domenii
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_companies_parallel(domains):
    results = [None] * len(domains)
    with ThreadPoolExecutor(max_workers=2) as executor:  # max 2 simultan pentru GPT-5
        future_to_idx = {executor.submit(get_company_info_from_domain, domain): i for i, domain in enumerate(domains)}
        for future in as_completed(future_to_idx):
            i = future_to_idx[future]
            try:
                results[i] = future.result()
            except Exception:
                results[i] = {"nume": None, "identificator": None, "tip": "necunoscut"}
    return results
