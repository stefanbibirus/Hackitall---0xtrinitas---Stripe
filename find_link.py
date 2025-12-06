import openai
from urllib.parse import urlparse
import re
import requests
from dotenv import load_dotenv
import os

load_dotenv()

# Setează cheia ta OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_user_location():
    try:
        response = requests.get("https://ipinfo.io/json")
        data = response.json()
        city = data.get("city", "")
        country = data.get("country", "")
        return city, country
    except:
        return "", ""

def extract_domain(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc

def search_product(product, city, country):
    prompt = f"""
Găsește 6 linkuri valide pentru produsul '{product}' în România.
Reguli:
- Fiecare link direct către produs, nu homepage.
- Fiecare link de la un vendor diferit (un domeniu per link).
- Prioritizează magazine mici, artizanale și locale din {city}, {country}.
- Include maxim 1 magazine mari (ex: emag.ro, zara.ro).
- Fără duplicate de domeniu.
Returnează doar linkuri complete, fiecare pe un rând.
"""
    response = openai.chat.completions.create(
        model="gpt-5-search-api",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that finds online stores."},
            {"role": "user", "content": prompt}
        ],
    )

    result_text = response.choices[0].message.content
    links = re.findall(r'https?://\S+', result_text)
    return links[:6]  # limităm la 6 linkuri

def main():
    product = input("Introduceți produsul: ")
    city, country = get_user_location()
    print(f"Localizare detectată: {city}, {country}")

    links = search_product(product, city, country)
    domains = [extract_domain(link) for link in links]

    # Scriem domeniile
    with open("domains.txt", "w", encoding="utf-8") as f:
        for domain in domains:
            f.write(domain + "\n")

    # Scriem linkurile
    with open("links.txt", "w", encoding="utf-8") as f:
        for link in links:
            f.write(link + "\n")

    print("\n--- Domenii ---")
    print(domains)
    
    print("\n--- Linkuri complete ---")
    print(links)

if __name__ == "__main__":
    main()
