from openai import OpenAI
from dotenv import load_dotenv
import os
import re
import time
import requests
from bs4 import BeautifulSoup
import json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})

def fetch_url(url, tries=3):
    for i in range(tries):
        try:
            r = session.get(url, timeout=20)
            if "Just a moment" in r.text or "cf-browser-verification" in r.text:
                time.sleep(1 + i)
                continue
            return r
        except:
            time.sleep(1)
    return None

def get_preview(url):
    data = {"url": url}
    try:
        r = fetch_url(url)
        if not r:
            return data
    except:
        return data
    
    soup = BeautifulSoup(r.text, "html.parser")
    
    t = soup.find("meta", property="og:title") or soup.find("title")
    if t:
        data["title"] = t.get("content") if t.name == "meta" else t.text.strip()
    
    i = soup.find("meta", property="og:image")
    if i:
        data["image"] = i.get("content")
    
    d = soup.find("meta", property="og:description")
    if d:
        data["description"] = d.get("content")
    
    p = soup.find("meta", property="product:price:amount")
    if p:
        data["price"] = p.get("content")
    
    if "price" not in data:
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                obj = json.loads(script.string)
                if isinstance(obj, dict) and "offers" in obj:
                    offer = obj["offers"]
                    if isinstance(offer, dict) and "price" in offer:
                        data["price"] = offer["price"]
            except:
                pass
    
    return data

def search_with_openai(query, city="București",filters=""):
    prompt = f"""
    Cauta produse dupa descrierea {query}.
Prioritate siteuri din apropiere de {city}.
DOAR SITEURI .ro
Extrage DOAR linkurile care apar în rezultatele de căutare.
Nu inventa nimic.

Reguli:
- incearca sa iei in vedere filtrul, dar nu e obligatoriu, filtru: {filters}
- link direct produs, nu homepage
- 1 link per domeniu
- preferă magazine românești
- evita magazin mare (emag.ro / altex.ro / decathlon.ro)
- dacă nu există 6, poti cauta de la magazine mari
- răspunde DOAR cu linkurile, câte unul pe rând
"""
    
    try:
        completion = client.chat.completions.create(
        model="gpt-4o-search-preview",
        web_search_options={
            "user_location": {
                "type": "approximate",
                "approximate": {
                    "country": "RO",
                    "city": city,
                    "region": city,
                }
            },
        },
        messages=[{
            "role": "user",
            "content": prompt,
        }],
    )

        result = completion.choices[0].message.content
        links = re.findall(r'https?://[^\s<>"]+', result)
        return [l.rstrip('.,;:)') for l in links if '.ro' in l][:6]
    except Exception as e:
        print(f"OpenAI error: {e}")
        return []

def search_products_service(query: str, filters: str = ""):
    links = search_with_openai(query)
    
    if not links:
        q = query.replace(' ', '-')
        links = [f"https://www.emag.ro/search/{q}", f"https://altex.ro/cautare/?q={q}"]
    
    products = []
    for i, link in enumerate(links[:6]):
        preview = get_preview(link)
        price = 0
        if "price" in preview:
            try:
                price = float(re.sub(r'[^\d.]', '', str(preview["price"]).replace(',', '.')))
            except:
                price = 50 + i * 20
        
        products.append({
            "name": preview.get("title", f"{query} - Produs {i+1}"),
            "description": preview.get("description", f"Produs: {query}"),
            "price": price if price > 0 else 50 + i * 20,
            "image_url": preview.get("image", f"https://picsum.photos/seed/{query}{i}/400/300"),
            "url": link,
        })
        time.sleep(0.3)
    
    return products
