import re

def extract_context():
    try:
        content = open('page_dump_modal.html', encoding='utf-8').read()
        patterns = [
            "Wybierz konto Allegro",
            "marketplace Allegro",
            "Wyślij produkty na",
            "Wybierz miejsce wysyłki produktów",
            "Cena minimalna",
            "Wyślij na Allegro"
        ]
        
        for p in patterns:
            print(f"=== Searching for: {p} ===")
            matches = list(re.finditer(re.escape(p), content))
            if not matches:
                print("No matches found.")
                continue
                
            for i, m in enumerate(matches):
                start = max(0, m.start() - 300)
                end = min(len(content), m.end() + 1000)
                print(f"Match {i+1} at index {m.start()}:")
                print(content[start:end])
                print("-" * 50)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_context()
