# reviews.py
import requests
from bs4 import BeautifulSoup

def get_reviews_score(domain):
    """
    Extrage nota medie și numărul de review-uri din Compari (sau alt site).
    Placeholder: poți înlocui cu scraping real.
    """
    try:
        # Exemplu: scraping pagina de recenzii
        url = f"https://www.compari.ro/{domain}"
        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")
        nota_medie = float(soup.select_one(".nota-medie").text.strip())
        nr_reviewuri = int(soup.select_one(".nr-reviewuri").text.strip())
        return {"nota_medie": nota_medie, "numar_reviewuri": nr_reviewuri}
    except:
        # fallback
        return {"nota_medie": 4.0, "numar_reviewuri": 10}
