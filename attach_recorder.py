from playwright.sync_api import sync_playwright

#    1. start_chrome.py – Uruchamia bezpieczne okno Chrome z odblokowanym portem (zamyka też stare procesy).
#    2. attach_recorder.py – Podłącza nagrywarkę (Inspektora) do otwartego okna Chrome.

#   Instrukcja użycia:
#    1. Wpisz w terminalu: python start_chrome.py
#    2. Zaloguj się w Chrome.
#    3. Wpisz w terminalu: python attach_recorder.py


def attach_to_chrome():
    with sync_playwright() as p:
        try:
            # Używamy jawnie adresu IP 127.0.0.1 zamiast localhost
            print("Próbuję podłączyć się do 127.0.0.1:9222...")
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            
            if not browser.contexts:
                print("Błąd: Brak aktywnych kontekstów w przeglądarce.")
                return

            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()
            
            print(f"Sukces! Podłączono do: {page.url}")
            print("Otwieram Playwright Inspector...")
            
            page.pause()
            
        except Exception as e:
            print(f"\nBŁĄD: {e}")
            print("\nInstrukcja naprawy:")
            print("1. Zamknij całkowicie Chrome.")
            print('2. Uruchom: chrome.exe --remote-debugging-port=9222')
            print("3. Sprawdź komendą: netstat -ano | findstr :9222")

if __name__ == "__main__":
    attach_to_chrome()
