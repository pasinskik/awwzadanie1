import os
import json

# Ścieżki do plików z danymi
SCRAPED_FILE = "data/scraped_data.json"
INFO_FILE = "data/languages_info.json"

# Katalog, w którym zostanie wygenerowana witryna
SITE_DIR = "site"
LANG_DIR = os.path.join(SITE_DIR, "languages")

def clean_filename(name):
    """
    Usuwa lub zastępuje znaki, które mogą być problematyczne w nazwach plików.
    """
    forbidden = ["/", "\\", ":", "*", "?", "\"", "<", ">", "|", " "]
    for char in forbidden:
        name = name.replace(char, "")
    return name

def generate_ranking_md(scraped_data):
    """Generuje plik ranking.md zawierający tabelę z danymi i linkami do podstron."""
    ranking_lines = []
    ranking_lines.append("# Ranking języków programowania - TIOBE Index\n")
    ranking_lines.append("| Rank | Language | Rating | Change |")
    ranking_lines.append("|------|----------|--------|--------|")
    
    for item in scraped_data:
        language = item["language"]
        rank = item["rank"]
        rating = item["rating"]
        change = item["change"]
        # Przygotowujemy link do podstrony - upewniamy się, że nazwa pliku jest poprawna
        filename = clean_filename(language)
        link = f"[{language}](languages/{filename}.md)"
        ranking_lines.append(f"| {rank} | {link} | {rating} | {change} |")
    
    ranking_content = "\n".join(ranking_lines)
    with open(os.path.join(SITE_DIR, "ranking.md"), "w", encoding="utf-8") as f:
        f.write(ranking_content)

def generate_language_md(language_item, additional_info):
    """Generuje plik Markdown dla pojedynczego języka."""
    language = language_item["language"]
    rank = language_item["rank"]
    rating = language_item["rating"]
    change = language_item["change"]
    
    # Pobieramy dodatkowe informacje – jeśli nie ma, stosujemy domyślne wartości
    summary = additional_info.get("summary", "Brak opisu.")
    image_url = additional_info.get("image_url", "")
    wiki_url = additional_info.get("wiki_url", "")
    
    lines = []
    lines.append("---")
    lines.append("layout: default")
    lines.append(f"title: \"{language}\"")
    lines.append("---")
    lines.append(f"# {language}\n")
    if image_url:
        lines.append(f"![{language} Logo]({image_url})\n")
    lines.append(f"**Ranking:** {rank}  ")
    lines.append(f"**Rating:** {rating}  ")
    lines.append(f"**Change:** {change}\n")
    lines.append("## Description\n")
    lines.append(summary + "\n")
    if wiki_url:
        lines.append(f"More information: [Wikipedia]({wiki_url})\n")
    else:
        lines.append("No additional information.\n")
    
    return "\n".join(lines)

def generate_index_md():
    """Generuje stronę główną witryny index.md."""
    index_content = (
        "# Programming languages ranking - TIOBE Index\n\n"
        "This is a website about programming languages based on data scraped from TIOBE Index and Wikipedia.\n\n"
        "Content:\n"
        "- [Languages ranking](ranking.md)\n"
        "- Subsites with additional info about each language.\n"
    )
    with open(os.path.join(SITE_DIR, "index.md"), "w", encoding="utf-8") as f:
        f.write(index_content)

def generate_site():
    # Utwórz katalogi, jeśli nie istnieją
    os.makedirs(SITE_DIR, exist_ok=True)
    os.makedirs(LANG_DIR, exist_ok=True)

    # Wczytaj dane zescrapowane
    with open(SCRAPED_FILE, "r", encoding="utf-8") as f:
        scraped_data = json.load(f)
    
    # Wczytaj dodatkowe informacje z Wikipedii (jeśli istnieją)
    if os.path.exists(INFO_FILE):
        with open(INFO_FILE, "r", encoding="utf-8") as f:
            languages_info = json.load(f)
    else:
        languages_info = {}
    
    # Generuj ranking.md
    generate_ranking_md(scraped_data)
    
    # Generuj pliki dla poszczególnych języków
    for item in scraped_data:
        language = item["language"]
        info = languages_info.get(language, {})
        md_content = generate_language_md(item, info)
        filename = clean_filename(language) + ".md"
        filepath = os.path.join(LANG_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md_content)
    
    # Generuj stronę główną index.md
    generate_index_md()
    print("Witryna została wygenerowana w folderze 'site/'.")

if __name__ == "__main__":
    generate_site()
