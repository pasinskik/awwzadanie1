import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

URL = "https://www.tiobe.com/tiobe-index/"

def scrape_tiobe_index():
    # Pobranie zawartości strony
    response = requests.get(URL)
    response.raise_for_status()  # Sprawdzenie, czy strona zwróciła kod 200 OK

    # Parsowanie HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # Znalezienie tabeli
    table = soup.find("table", class_="table table-striped table-top20")
    if not table:
        raise ValueError("Nie znaleziono tabeli z rankingiem!")

    # Znalezienie wszystkich wierszy w tabeli (pomijamy nagłówki)
    rows = table.find_all("tr")[1:]

    data = []

    # Upewnij się, że jest wystarczająco kolumn, by odczytać wszystkie potrzebne dane.
    for row in rows:
        columns = row.find_all("td")
        if len(columns) >= 7:
            rank = columns[0].text.strip()
            language = columns[4].text.strip()
            rating = columns[5].text.strip()
            change = columns[6].text.strip()

            data.append({
                "rank": rank,
                "language": language,
                "rating": rating,
                "change": change
            })

    return data

def generate_markdown(data, filename):
    """Generuje plik Markdown zawierający tabelę z danymi."""
    md_lines = []
    md_lines.append("# Ranking języków programowania - TIOBE Index")
    md_lines.append("")
    md_lines.append("| Rank | Language | Rating | Change |")
    md_lines.append("|------|----------|--------|--------|")
    
    for item in data:
        md_lines.append(f"| {item['rank']} | {item['language']} | {item['rating']} | {item['change']} |")
    
    md_content = "\n".join(md_lines)
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(md_content)

if __name__ == "__main__":
    languages = scrape_tiobe_index()

    # Zapis do pliku JSON
    with open("data/scraped_data.json", "w", encoding="utf-8") as f:
        json.dump(languages, f, indent=4, ensure_ascii=False)

    # Zapis do pliku CSV
    df = pd.DataFrame(languages)
    df.to_csv("data/scraped_data.csv", index=False, encoding="utf-8")
    
    # Generowanie pliku Markdown
    generate_markdown(languages, "data/scraped_data.md")

    print("Dane zapisane w formatach JSON, CSV i Markdown!")
