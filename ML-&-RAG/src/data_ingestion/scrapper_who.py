from bs4 import BeautifulSoup
import requests
import time
import os

index_url = "https://www.who.int/news-room/fact-sheets/"
def get_all_diseases():
    response = requests.get(index_url)
    soup = BeautifulSoup(response.content, "html.parser")

    links = []
    items = soup.find_all("li", class_="alphabetical-nav--list-item")
    for item in items:
        a_tags = item.find_all("a")
        for a_tag in a_tags:
            full_url = "https://www.who.int" + a_tag["href"]
            disease_name = a_tag.text.strip()
            links.append((disease_name, full_url))
    return links

def scrape_who_fact_sheet(disease_name: str, url: str):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    content_parts = []
    for tag in soup.find_all(["h1", "h2", "h3", "p", "li"]):
        text = tag.get_text(strip=True)
        if text:
            content_parts.append(text)
    text = "\n".join(content_parts)
    if not text:
        print(f"Could not find content for {disease_name}")
        return
    os.makedirs("data/raw/who_fact_sheets", exist_ok=True)
    safe_name = disease_name.replace("/", "-").replace("\\", "-")
    with open(f"data/raw/who_fact_sheets/{safe_name}.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Saved: {disease_name}")

def run_scrapper():
    diseases = get_all_diseases()
    for disease_name, url in diseases:
        scrape_who_fact_sheet(disease_name, url)
        time.sleep(2)

if __name__ == "__main__":
    run_scrapper()

