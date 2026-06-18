import os
import time
import pandas as pd
import logging
import re
from datetime import datetime
from playwright.sync_api import sync_playwright
from libraries.chrome_manager import ChromeManager

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ustawienia portu Chrome
CHROME_DEBUG_PORT = 9222 
DEBUG_SCREENSHOT_DIR = r"c:\Users\bedna\Desktop\1"

def find_cheapest_on_allegro(page, ean, sku):
    """Wyszukuje EAN na Allegro i zwraca najniższą cenę."""
    if not ean or ean == "BRAK" or len(str(ean)) < 8:
        return None

    # URL wyszukiwania z pełnym sortowaniem (sort=p oraz order=p dla Allegro Business)
    search_url = f"https://allegro.pl/listing?string={ean}&sort=p&order=p"
    
    try:
        page.goto(search_url, wait_until="load", timeout=30000)
        time.sleep(2)

        # 1. Obsługa Captcha
        if "captcha" in page.url.lower() or page.locator("#captcha").is_visible():
            logger.warning("WYKRYTO CAPTCHA! Rozwiąż ją w przeglądarce...")
            while "captcha" in page.url.lower() or page.locator("#captcha").is_visible():
                time.sleep(2)

        # 2. Obsługa kategorii dla dorosłych (Dwuetapowa)
        # Etap 1: "Potwierdź wiek"
        age_btn1 = page.get_by_role("button", name="Potwierdź wiek", exact=False).first
        if age_btn1.is_visible():
            logger.info("Klikam 'Potwierdź wiek' (etap 1)")
            age_btn1.click()
            time.sleep(1.5)

        # Etap 2: "TAK, MAM 18 LAT, IDĘ DALEJ"
        age_btn2 = page.get_by_role("button", name="TAK, MAM 18 LAT", exact=False).first
        if age_btn2.is_visible():
            logger.info("Klikam 'TAK, MAM 18 LAT' (etap 2)")
            age_btn2.click()
            time.sleep(2)

        # 3. Wymuszenie sortowania (jeśli Allegro zignorowało parametr w URL)
        # Sprawdzamy czy wybrane jest "cena: od najniższej"
        # Selektor dla dropdowna sortowania często się zmienia, ale tekst zazwyczaj zawiera "najniższej"
        sort_dropdown = page.locator("select[data-role='sort-control']").first
        if sort_dropdown.is_visible():
            current_sort = sort_dropdown.input_value()
            if current_sort != "p":
                logger.info("Ręcznie zmieniam sortowanie na 'cena: od najniższej'")
                sort_dropdown.select_option("p")
                time.sleep(2)

        # 4. Zrzut ekranu (tylko dla mnie do debugowania, nadpisuje poprzedni)
        screenshot_path = os.path.join(DEBUG_SCREENSHOT_DIR, "last_allegro_view.png")
        page.screenshot(path=screenshot_path)

        # 5. Pobieranie ceny z pierwszej oferty (article)
        # Szukamy ofert w kontenerze wyników
        offers = page.locator("article").all()
        
        for offer in offers:
            # Szukamy ceny brutto
            # Allegro używa konkretnych struktur dla ceny, np. <span>123,45 zł</span>
            # Najbardziej uniwersalny selektor ceny to taki, który ma tekst " zł" i nie jest przekreślony
            
            price_element = offer.locator("span[class*='price']").first
            if not price_element.is_visible():
                 # Szukamy po tekście " zł" ale wykluczamy stare ceny (przekreślone)
                 price_element = offer.locator("span:has-text(' zł')").filter(has_not=page.locator("del")).first

            if price_element.is_visible():
                text = price_element.inner_text()
                # Usuwamy wszystko co nie jest cyfrą, kropką lub przecinkiem
                clean_text = text.replace(" ", "").replace(",", ".").replace("zł", "").strip()
                match = re.search(r"(\d+\.\d{2})", clean_text) # 123.45
                if not match:
                    match = re.search(r"(\d+)", clean_text) # 123
                
                if match:
                    price = float(match.group(1))
                    if price > 1:
                        return {"price": price, "url": page.url}

        return None
    except Exception as e:
        logger.error(f"Błąd dla EAN {ean}: {e}")
        return None

def main():
    import glob
    files = glob.glob("gapli_potential_products_diverse.xlsx") + glob.glob("gapli_potential_products_*.xlsx")
    if not files:
        logger.error("Brak pliku!")
        return
    input_file = files[0]
    df = pd.read_excel(input_file)

    manager = ChromeManager(port=CHROME_DEBUG_PORT)
    if not manager.start_chrome():
        return

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{CHROME_DEBUG_PORT}")
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()

        price_col = 'Cena w Gapli' if 'Cena w Gapli' in df.columns else 'Cena Brutto (Gapli)'
        
        results = []
        test_limit = 20
        df_test = df.head(test_limit)
        
        logger.info(f"Start: 20 produktów. Poprawki: podwójny wiek, wymuszone sortowanie.")

        for index, row in df_test.iterrows():
            sku = row['SKU']
            ean = str(row['EAN']).strip()
            my_price = float(row[price_col])
            
            logger.info(f"[{index+1}/{test_limit}] {sku} (EAN: {ean})")
            comp = find_cheapest_on_allegro(page, ean, sku)
            
            if comp:
                diff = round(my_price - comp['price'], 2)
                results.append({
                    "SKU": sku, "EAN": ean, "Nazwa": row['Nazwa Produktu'],
                    "Moja Cena": my_price, "Najtańszy Allegro": comp['price'],
                    "Różnica": diff, "Link": comp['url']
                })
                logger.info(f"   -> OK: {comp['price']} (Różnica: {diff})")
            else:
                results.append({
                    "SKU": sku, "EAN": ean, "Nazwa": row['Nazwa Produktu'],
                    "Moja Cena": my_price, "Najtańszy Allegro": "Brak",
                    "Różnica": "", "Link": ""
                })
                logger.info(f"   -> Brak ofert.")
            
            time.sleep(1)

        output_df = pd.DataFrame(results)
        output_file = f"raport_allegro_v3_{datetime.now().strftime('%H%M%S')}.xlsx"
        output_df.to_excel(output_file, index=False)
        logger.info(f"GOTOWE: {output_file}")

if __name__ == "__main__":
    main()
