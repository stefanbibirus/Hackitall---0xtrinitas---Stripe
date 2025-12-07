# 0xtrinitas - HackItAll - Stripe

### Colaboratori:
- Bibirus Stefan : 
- Cocut Ioana-Maria:
- Oprea Maria-Ariadna: 


# HuntZ 

O platformă e-commerce inteligentă care folosește AI pentru a găsi cele mai bune produse din magazinele online românești.

##  Descriere

**HuntZ** este o aplicație web inovatoare care combină puterea inteligenței artificiale cu analiza datelor financiare pentru a ajuta utilizatorii să găsească produse de la vânzători de încredere. Platforma caută automat în magazinele online din România, verifică informațiile despre companii prin API-ul ANAF și oferă un scor de încredere pentru fiecare vânzător.

##  Funcționalități

### Căutare Inteligentă cu AI
- Utilizează **OpenAI GPT-4** pentru a căuta produse în magazinele online românești
- Prioritizează magazine locale și artizanale
- Returnează 6 rezultate relevante cu imagini, prețuri și descrieri

### Verificare Companii (ANAF)
- Extrage automat **CUI-ul** companiilor din listafirme.ro
- Obține date financiare oficiale: cifra de afaceri, număr angajați
- Calculează un **scor de încredere** bazat pe sănătatea financiară

### Sistem de Review-uri
- Agregă recenzii de la surse externe
- Combină scorul financiar (70%) cu review-urile (30%)
- Sortează rezultatele după scorul final

### Coș de Cumpărături
- Adaugă/elimină produse
- Modifică cantități în timp real
- Persistență între sesiuni

### Plăți Securizate
- Integrare completă cu **Stripe Checkout**
- Suport pentru carduri de credit/debit
- Confirmare instant și istoric comenzi

### Autentificare
- Înregistrare și autentificare utilizatori
- Istoric comenzi personalizat
- Sesiuni securizate

## Stack Tehnologic

| Componentă | Tehnologie |
|------------|------------|
| **Backend** | Django 4.2+ (Python) |
| **Frontend** | HTML5, CSS3, JavaScript |
| **AI Search** | OpenAI GPT-4 API |
| **Plăți** | Stripe API |
| **Date Companii** | ANAF API |
| **Bază de Date** | SQLite |
| **Web Scraping** | BeautifulSoup4, Requests |