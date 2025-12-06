import requests
from bs4 import BeautifulSoup
import ssl, socket
import subprocess
import re

# --- Validare nume firmă ---
def is_valid_company_name(text):
    text = text.strip()

    if len(text) < 6: return False
    if not re.search(r"[a-zA-Z]", text): return False
    if len(text.split()) < 2: return False
    if text.lower().endswith(" sa") and "s.a" not in text.lower(): return False

    return True

# --- Extrage firma din pagină ---
def extract_company_from_page(url):
    try:
        html = requests.get(url, timeout=7).text
    except:
        return None

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)

    patterns = [
        r"[A-Z0-9 ,.'-]+ SRL",
        r"[A-Z0-9 ,.'-]+ S\.A\.",
        r"[A-Z0-9 ,.'-]+ SA",
        r"SC [A-Z0-9 ,.'-]+ SRL",
        r"SC [A-Z0-9 ,.'-]+ SA",
    ]

    for p in patterns:
        matches = re.findall(p, text, flags=re.IGNORECASE)
        for m in matches:
            if is_valid_company_name(m):
                return m

    return None

def scan_site(domain):
    pages = [
        f"https://{domain}",
        f"https://{domain}/contact",
        f"https://{domain}/termeni",
        f"https://{domain}/gdpr",
        f"https://{domain}/privacy",
        f"https://{domain}/despre",
        f"https://{domain}/about",
    ]

    for page in pages:
        result = extract_company_from_page(page)
        if result:
            return result

    return None

# --- Extrage organizația din certificatul SSL ---
def get_ssl_organization(domain):
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()

        subject = dict(x[0] for x in cert.get("subject", []))
        org = subject.get("organizationName")

        if org and is_valid_company_name(org):
            return org
    except:
        return None

# --- Main ---
def find_owner(domain):
    # 1. Caută firmă în site
    company = scan_site(domain)
    if company:
        print(company)
        return

    # 2. Caută firmă în SSL
    ssl_org = get_ssl_organization(domain)
    if ssl_org:
        print(ssl_org)
        return

    # 3. Implicit: persoană fizică
    print("persoana fizica")


# exemplu:
find_owner("site")
