# anaf_api.py
import requests
from datetime import datetime
import time

ANAF_API_URL = "https://webservicesp.anaf.ro/api/PlatitorTvaRest/v9/tva"
ANAF_BILANT_URL = "https://webservicesp.anaf.ro/bilant"
LISTAFIRME_BASE_URL = "https://listafirme.ro"

def normalize_name(name):
    """
    Curața denumirea firmei:
    - Elimina punctele
    - Elimina "SC" daca e primul cuvânt
    - Transforma în lowercase și înlocuiește spațiile cu cratime
    - Elimina caractere speciale (doar litere, cifre și cratime)
    """
    # Elimina punctele
    name = name.replace(".", "")
    
    # Împarte în cuvinte
    words = name.strip().split()
    
    # Daca primul cuvânt e 'SC', îl eliminam
    if words and words[0].lower() == "sc":
        words = words[1:]
    
    # Reunim cu cratime
    name = "-".join(words).lower()
    
    return name

def get_cui(nume_vector):
    """
    Primește un vector de denumiri de firme și returneaza vector de ID-uri numeric.
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
            
            # Pauza mica ca sa nu lovești site-ul prea tare
            time.sleep(0.5)
        except requests.exceptions.RequestException as e:
            print(f"Eroare la firma {nume_firma}: {e}")
            ids.append(None)
    
    return ids

def get_companies_info(cui_vector):
    """
    Interrogheaza ANAF pentru un vector de CUI-uri și returneaza datele în matrice.
    
    Args:
        cui_vector: Lista de CUI-uri
    
    Returns:
        Lista de liste cu [cui, localitate, judet]
    """
    date_companii = []
    
    data = datetime.now().strftime("%Y-%m-%d")
    headers = {"Content-Type": "application/json"}
    
    # Proceseaza câte 100 de CUI-uri odata (limita ANAF)
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
        
        # Respecta limita de 1 request/secunda
        if i + 100 < len(cui_vector):
            time.sleep(1)
    
    return date_companii


def get_financial_info(cui_vector):
    """
    Interrogheaza ANAF pentru cifra de afaceri și numarul de angajați din ultimul an fiscal.
    
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
        
        # Verifica daca exista date
        if response.status_code == 200:
            result = response.json()
            
            if result.get("i"):
                # Creeaza un dicționar pentru acces rapid la indicatori
                indicatori_map = {item["indicator"]: item["val_indicator"] for item in result["i"]}
                
                # Încearca sa extragi valorile folosind cheile indicatorilor
                # I27: Venituri totale (Surogat CA pt. Asigurari)
                cifra_afaceri = indicatori_map.get("I13") 
                # I33: Numar mediu de salariati
                numar_angajati = indicatori_map.get("I20") 
    
        date_financiare.append([cui, cifra_afaceri, numar_angajati])
        time.sleep(1)
    
    return date_financiare