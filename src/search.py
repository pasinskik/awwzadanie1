import json
import time
import os
import requests

SCRAPED_FILE = "data/scraped_data.json"      # Dane zescrapowane ze strony TIOBE
SEARCH_FILE = "data/languages_info2.json"      # Plik, w którym zapiszemy wzbogacone dane

def load_existing_data():
    """Wczytuje już zapisane dane, by nie pobierać ich ponownie."""
    if os.path.exists(SEARCH_FILE):
        with open(SEARCH_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def get_wikipedia_info(query):
    """
    Pobiera informacje z Wikipedii dla podanego zapytania.
    Zwraca słownik z kluczami: summary, image_url oraz wiki_url.
    """
    base_url = "https://en.wikipedia.org/w/api.php"
    
    # 1. Szukamy artykułu odpowiadającego zapytaniu
    params_search = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query,
    }
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(base_url, params=params_search, headers=headers)
    data = response.json()
    search_results = data.get("query", {}).get("search", [])
    if not search_results:
        return None
    
    page_title = search_results[0]["title"]
    
    # 2. Pobieramy streszczenie i obrazek z artykułu
    params_page = {
        "action": "query",
        "format": "json",
        "prop": "extracts|pageimages",
        "exintro": True,
        "titles": page_title,
        "pithumbsize": 500,
    }
    response = requests.get(base_url, params=params_page, headers=headers)
    data = response.json()
    pages = data.get("query", {}).get("pages", {})
    if not pages:
        return None
    
    page = next(iter(pages.values()))
    summary = page.get("extract", "Brak opisu")
    image_url = page.get("thumbnail", {}).get("source", "")
    wiki_url = f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
    
    return {"summary": summary, "image_url": image_url, "wiki_url": wiki_url}

def fetch_extra_info():
    """
    Dla każdego języka z pliku scraped_data.json pobiera dodatkowe informacje
    z Wikipedii i zapisuje wyniki do languages_info.json.
    """
    existing_data = load_existing_data()
    
    with open(SCRAPED_FILE, "r", encoding="utf-8") as f:
        languages = json.load(f)
    
    results = {}
    
    # Przetwarzamy ograniczenie do pierwszych 10 języków, żeby nie obciążać API
    for lang in languages:
        lang_name = lang["language"]
        
        if lang_name in existing_data:
            print(f"Pominięto: {lang_name} (dane już zapisane)")
            results[lang_name] = existing_data[lang_name]
            continue
        
        print(f"Pobieranie informacji o {lang_name} z Wikipedii...")
        query = f"{lang_name} programming language"
        info = get_wikipedia_info(query)
        if info is None:
            info = {"summary": "Brak dodatkowych informacji.", "image_url": "", "wiki_url": ""}
        
        # Dodajemy również dane z pierwotnego scrapowania
        info["rank"] = lang["rank"]
        info["rating"] = lang["rating"]
        info["change"] = lang["change"]
        
        results[lang_name] = info
        
        # Pauza, żeby nie przeciążyć API Wikipedii
        time.sleep(5)
    
    with open(SEARCH_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    
    print("Dodatkowe informacje zapisane!")

if __name__ == "__main__":
    fetch_extra_info()