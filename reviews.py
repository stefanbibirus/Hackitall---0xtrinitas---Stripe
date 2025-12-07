
#main.py

# main.py
from find_link import get_product_links
from find_CUI import get_companies_parallel
from anaf_api import get_cui, get_financial_info
from reviews import get_reviews_score
import requests
from bs4 import BeautifulSoup
import json

def extract_product_image(link):
    try:
        r = requests.get(link, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")
        img = soup.find("img")
        if img and img.get("src"):
            return img["src"]
    except:
        pass
    return None

def main():
    produs = input("Introduceți produsul: ").strip()
    
    # 1️⃣ Obține 6 linkuri + domenii
    links, domains, city, country = get_product_links(produs)

    # 2️⃣ Obține info firme per domeniu (paralel + throttling)
    companies_info = get_companies_parallel(domains)
    nume_firme = [info.get("nume") or "" for info in companies_info]

    # 3️⃣ Obține CUI-uri
    cui_list = get_cui(nume_firme)

    # 4️⃣ Obține info financiare
    financial_data = get_financial_info(cui_list)

    # 5️⃣ Obține scor review pentru fiecare domeniu
    review_data = [get_reviews_score(domain) for domain in domains]

    # 6️⃣ Compilează rezultatele
    results = []
    for i in range(len(links)):
        scor_final = financial_data[i]["scor"] * 0.7 + review_data[i]["nota_medie"] * 0.3
        poza = extract_product_image(links[i]) or ""
        result = {
            "link": links[i],
            "domeniu": domains[i],
            "firma": companies_info[i],
            "cui": cui_list[i],
            "financiar": financial_data[i],
            "review": review_data[i],
            "scor_final": scor_final,
            "poza": poza
        }
        results.append(result)

    # 7️⃣ Sortează după scor final descrescător
    results = sorted(results, key=lambda x: x["scor_final"], reverse=True)

    # 8️⃣ Salvează JSON
    with open("rezultate.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print(json.dumps(results, indent=4, ensure_ascii=False))
    print("Rezultatele au fost salvate în 'rezultate.json'")

if __name__ == "__main__":
    main()