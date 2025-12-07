# anaf_api.py
import requests
from datetime import datetime
import time

ANAF_API_URL = "https://webservicesp.anaf.ro/api/PlatitorTvaRest/v9/tva"
ANAF_BILANT_URL = "https://webservicesp.anaf.ro/bilant"
LISTAFIRME_BASE_URL = "https://listafirme.ro"

def normalize_name(name):
    """
    Curăță denumirea firmei:
    - Elimină punctele
    - Elimină "SC" dacă e primul cuvânt
    - Transformă în lowercase și înlocuiește spațiile cu cratime
    - Elimină caractere speciale (doar litere, cifre și cratime)
    """
    # Elimină punctele
    name = name.replace(".", "")
    
    # Împarte în cuvinte
    words = name.strip().split()
    
    # Dacă primul cuvânt e 'SC', îl eliminăm
    if words and words[0].lower() == "sc":
        words = words[1:]
    
    # Reunim cu cratime
    name = "-".join(words).lower()
    
    return name

def get_cui(nume_vector):
    """
    Primește un vector de denumiri de firme și returnează vector de ID-uri numeric.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    ids = []
    
    for nume_firma in nume_vector:
        url_name = normalize_name(nume_firma)
        url = f"{LISTAFIRME_BASE_URL}/{url_name}"
        
        try:
            response = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
            final_url = response.url
            last_part = final_url.rstrip("/").split("-")[-1]
            
            if last_part.isdigit():
                ids.append(last_part)
            else:
                ids.append(None)
            
            # Pauză mică ca să nu lovești site-ul prea tare
            time.sleep(0.5)
        except requests.exceptions.RequestException as e:
            print(f"Eroare la firma {nume_firma}: {e}")
            ids.append(None)
    
    return ids

def get_companies_info(cui_vector):
    """
    Interroghează ANAF pentru un vector de CUI-uri și returnează datele în matrice.
    
    Args:
        cui_vector: Lista de CUI-uri
    
    Returns:
        Lista de liste cu [cui, localitate, judet]
    """
    date_companii = []
    
    data = datetime.now().strftime("%Y-%m-%d")
    headers = {"Content-Type": "application/json"}
    
    # Procesează câte 100 de CUI-uri odată (limita ANAF)
    for i in range(0, len(cui_vector), 100):
        batch = cui_vector[i:i+100]
        payload = [{"cui": cui, "data": data} for cui in batch]
        
        response = requests.post(ANAF_API_URL, json=payload, headers=headers)
        result = response.json()
        
        if result.get("found"):
            for companie in result["found"]:
                date_generale = companie.get("date_generale", {})
                cui_gasit = date_generale.get("cui", "")
                
                domiciliu = companie.get("adresa_domiciliu_fiscal", {})
                localitate = domiciliu.get("ddenumire_Localitate", "")
                judet = domiciliu.get("ddenumire_Judet", "")
                
                date_companii.append([cui_gasit, localitate, judet])
        
        # Respectă limita de 1 request/secundă
        if i + 100 < len(cui_vector):
            time.sleep(1)
    
    return date_companii


def get_financial_info(cui_vector):
    """
    Interroghează ANAF pentru cifra de afaceri și numărul de angajați din ultimul an fiscal.
    
    Args:
        cui_vector: Lista de CUI-uri
    
    Returns:
        Lista de liste cu [cui, cifra_afaceri, numar_angajati]
    """
    date_financiare = []
    
    # Ultimul an fiscal complet (anul trecut)
    an = datetime.now().year - 1
    
    for cui in cui_vector:
        params = {
            "an": an,
            "cui": cui
        }
        
        response = requests.get(ANAF_BILANT_URL, params=params)
        
        cifra_afaceri = None
        numar_angajati = None
        
        # Verifică dacă există date
        if response.status_code == 200:
            result = response.json()
            
            if result.get("i"):
                # Creează un dicționar pentru acces rapid la indicatori
                indicatori_map = {item["indicator"]: item["val_indicator"] for item in result["i"]}
                
                # Încearcă să extragi valorile folosind cheile indicatorilor
                # I27: Venituri totale (Surogat CA pt. Asigurari)
                cifra_afaceri = indicatori_map.get("I13") 
                # I33: Numar mediu de salariati
                numar_angajati = indicatori_map.get("I20") 
    
        date_financiare.append([cui, cifra_afaceri, numar_angajati])
        time.sleep(1)
    
    return date_financiare
