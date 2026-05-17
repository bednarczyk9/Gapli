import sys
from playwright.sync_api import sync_playwright

def vote_once(current: int, total: int):
    """
    Uruchamia przeglądarkę, oddaje jeden głos i zamyka przeglądarkę.
    """
    with sync_playwright() as p:
        try:
            # Uruchamiamy przeglądarkę
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            url = "https://sugester.fakturownia.pl/158004200-obsluga-zwrotow-korekt-paragonow"
            print(f"[{current}/{total}] Wchodzę na stronę...")
            page.goto(url)
            
            # Selektor oparty na tekście
            selector = 'span:has-text("Zagłosuj")'
            
            # Czekamy na element
            page.wait_for_selector(selector, timeout=10000)
            
            # Klikamy
            page.click(selector)
            print(f"[{current}/{total}] Kliknięcie zakończone sukcesem.")
            
            # Krótka pauza na zapisanie zmian
            page.wait_for_timeout(2000)
            
            browser.close()
        except Exception as e:
            print(f"[{current}/{total}] Błąd: {e}")

def vote(x: int):
    """
    Wykonuje x iteracji głosowania, restartując przeglądarkę za każdym razem.
    """
    for i in range(x):
        vote_once(i + 1, x)
        print(f"--- Zakończono sesję {i + 1}. Restartowanie przeglądarki... ---")

if __name__ == "__main__":
        
        vote(10)
