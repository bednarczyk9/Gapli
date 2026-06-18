import os
import time
import logging
from datetime import datetime
import openpyxl
from playwright.sync_api import sync_playwright

# Importy z lokalnego projektu
from libraries.chrome_manager import ChromeManager
from libraries.gapli_client import GapliClient

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_browser_export():
    """
    Uruchamia przeglądarkę, loguje się do Gapli i wykonuje skrypt JS do pobrania hurtowni.
    """
    username = os.getenv("GAPLI_USER")
    password = os.getenv("GAPLI_PASS")

    if not username or not password:
        logger.error("Błąd: Zmienne środowiskowe GAPLI_USER lub GAPLI_PASS nie są ustawione.")
        return

    chrome = ChromeManager()
    if not chrome.start_chrome():
        logger.error("Nie udało się uruchomić Chrome.")
        return

    with sync_playwright() as p:
        try:
            logger.info("Łączenie z Chrome...")
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()

            client = GapliClient(page)
            
            # 1. Logowanie (jeśli potrzebne)
            logger.info("Logowanie do Gapli...")
            if not client.login(username, password):
                logger.error("Logowanie nie powiodło się.")
                return

            # 2. Nawigacja do Marketplace (tam gdzie jest lista hurtowni)
            logger.info("Nawigacja do sekcji produktów...")
            page.goto("https://gapli.com/dashboard/products", wait_until="networkidle")
            time.sleep(3)

            # 3. Otwarcie listy hurtowni (aby elementy pojawiły się w DOM)
            logger.info("Otwieranie listy hurtowni...")
            # Szukamy przycisku filtra hurtowni
            wholesaler_btn = page.locator("label:has-text('Hurtownia')").locator("xpath=..").locator("button").first
            if not wholesaler_btn.is_visible():
                 wholesaler_btn = page.get_by_role("button", name="Hurtownia").first
            
            wholesaler_btn.click()
            time.sleep(2) # Czekamy na rozwinięcie listy

            # 4. Wykonanie skryptu JavaScript dostarczonego przez użytkownika
            # Zmieniamy go lekko, aby zamiast pobierania pliku w przeglądarce, zwrócił dane do Pythona
            js_script = """
            () => {
                const buttons = document.querySelectorAll('.select-list-scrollbar button[data-value]');
                const results = [];
                
                buttons.forEach(button => {
                    const id = button.getAttribute('data-value');
                    const span = button.querySelector('span');
                    if (!span) return;

                    const text = span.innerText.trim();
                    const regex = /^(.*?)\s*\((\d+)\s+na\s+stanie\)(?:\s*([^\s\w]+)\s*(\d+))?$/;
                    const match = text.match(regex);

                    if (match) {
                        results.append({
                            id: id,
                            name: match[1].trim(),
                            stock: match[2],
                            icon: match[3] || '',
                            indicator: match[4] || ''
                        });
                    } else {
                        results.push({
                            id: id,
                            name: text,
                            stock: '',
                            icon: '',
                            indicator: ''
                        });
                    }
                });
                return results;
            }
            """
            
            # Poprawka: results.push zamiast results.append w JS
            js_script_fixed = js_script.replace("results.append", "results.push")
            
            logger.info("Pobieranie danych z interfejsu...")
            data = page.evaluate(js_script_fixed)

            if not data:
                logger.warning("Nie znaleziono danych hurtowni na stronie. Upewnij się, że lista jest widoczna.")
                return

            # 5. Zapis do XLSX (zamiast CSV, zgodnie z pierwotnym wymogiem)
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Hurtownie"
            
            headers = ['ID z systemu', 'Nazwa', 'Ilosc na stanie', 'Znacznik', 'Wskaznik']
            ws.append(headers)
            
            for item in data:
                ws.append([
                    item['id'],
                    item['name'],
                    item['stock'],
                    item['icon'],
                    item['indicator']
                ])

            # Formatowanie
            for cell in ws[1]:
                cell.font = openpyxl.styles.Font(bold=True)

            filename = f"export/wholesalers_ui_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            wb.save(filename)
            
            logger.info(f"Sukces! Wyeksportowano {len(data)} hurtowni do: {filename}")
            print(f"\n✅ Sukces! Pomyślnie pobrano dane z interfejsu i zapisano w: {filename}")

        except Exception as e:
            logger.error(f"Wystąpił błąd podczas eksportu: {e}")
        finally:
            logger.info("Zamykanie przeglądarki...")
            # Nie zamykamy całego Chrome, tylko połączenie CDP (zgodnie z konwencją projektu)
            browser.close()

if __name__ == "__main__":
    run_browser_export()
