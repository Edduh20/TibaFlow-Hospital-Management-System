import os

def clean_text(text: str) -> str:
    key_facts_index = text.lower().find("key facts")
    if key_facts_index != -1:
        text = text[key_facts_index:]

    footer_markers = ["Related\n", "Regions\nAfrica", "Policies\nCybersecurity", "© 2026 WHO", "References\n", "\n(1) ","\n1An "]
    for marker in footer_markers:
        marker_index = text.lower().find(marker.lower())
        if marker_index != -1:
            text = text[:marker_index]
            break

    lines = text.split("\n")
    cleaned = []

    # noise patterns to skip
    noise_patterns = [
        "Global", "Regions", "WHO Regional", "Africa", "Americas",
        "South-East Asia", "Europe", "Eastern Mediterranean", "Western Pacific",
        "Home", "Health Topics", "All topics", "Resources", "Fact sheets",
        "Facts in pictures", "Multimedia", "Podcasts", "Publications",
        "Countries", "Newsroom", "Emergencies", "Data", "About WHO",
        "Cybersecurity", "Ethics", "Information disclosure", "Permissions",
        "Preventing sexual exploitation", "Terms of use", "Careers",
        "Frequently asked questions", "Library", "Procurement",
        "Contact us", "© 2026 WHO", "Privacy policy", "Home/",
        "Newsroom/", "Fact sheets/", "Detail/", "A\nB\nC",
        "Ask AI", "Chat AI", "logo", "managemanage", "useruser",
        "fullfull", "closeclose", "Skip to main content"
    ]

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if any(noise.lower() == line.lower() for noise in noise_patterns):
            continue
        if len(line) <= 2:
            continue
        cleaned.append(line)

    return "\n".join(cleaned)

def run_cleaning():
    files = os.listdir("data/raw/who_fact_sheets/")
    os.makedirs("data/processed/knowledge_base", exist_ok=True)
    for filename in files:
        if filename.endswith(".txt"):
            raw_path = f"data/raw/who_fact_sheets/{filename}"

            with open(raw_path, "r", encoding="utf-8") as f:
                text = f.read()

            cleaned = clean_text(text)

            processed_path = f"data/processed/knowledge_base/{filename}"
            with open(processed_path, "w", encoding="utf-8") as f:
                f.write(cleaned)

            print(f"Cleaned: {filename}")

if __name__ == "__main__":
    run_cleaning()