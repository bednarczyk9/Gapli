import pandas as pd
import os
import logging
import time
import re
import random
import glob
from datetime import datetime
from playwright.sync_api import sync_playwright
import sys

# Dodanie ścieżki do głównego folderu, żeby import ChromeManager działał
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libraries.chrome_manager import ChromeManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CHROME_DEBUG_PORT = 9222
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
]

def is_blocked(page):
    try:
        content = page.content().lower()
        has_iframe = False
        for frame in page.frames:
            if "allegrocaptcha.com" in frame.url or "captcha-delivery.com" in frame.url:
                has_iframe = True
                break
        
        indicators = ["nietypowy ruch", "pokaż, że jesteś człowiekiem", "potwierdź, że jesteś człowiekiem", "sprawdź czy nie jesteś robotem", "udowodnij, że nie jesteś robotem"]
        return any(x in content for x in indicators) or page.locator("iframe[title*='reCAPTCHA']").is_visible() or has_iframe
    except:
        return False

def find_cheapest_on_allegro(page, ean):
    if not ean or len(str(ean)) < 8: return None
    
    try:
        time.sleep(random.uniform(2.0, 4.0))
        search_url = f"https://allegro.pl/listing?string={ean}&sort=p&order=p"
        page.goto(search_url, wait_until="load", timeout=45000)
        time.sleep(1.5)

        if is_blocked(page):
            logger.error("WYKRYTO BLOKADĘ CAPTCHA! Skrypt zostaje wstrzymany.")
            logger.info("Rozwiąż ręcznie zadanie w otwartym oknie przeglądarki Chrome.")
            start_wait = time.time()
            
            # Pętla czekająca na interwencję użytkownika
            while is_blocked(page):
                time.sleep(5)
                # Maksymalny czas czekania: np. 10 minut
                if time.time() - start_wait > 600:
                    raise Exception("Brak rozwiązania Captcha przez 10 minut. Zatrzymuję skrypt.")
            
            logger.info("Blokada zniknęła! Wznawiam analizę...")
            # Odświeżenie na wszelki wypadek
            page.goto(search_url, wait_until="load", timeout=30000)
            time.sleep(2)

        page_text = page.content().lower()
        if "teraz nie mamy dokładnie tego" in page_text or "znaleźliśmy podobne oferty" in page_text or "nie znaleźliśmy ofert dla" in page_text:
            return None 

        try:
            age1 = page.get_by_role("button", name="Potwierdź wiek", exact=False).first
            if age1.is_visible(timeout=1000):
                age1.click()
                time.sleep(1)
                age2 = page.get_by_role("button", name="TAK, MAM 18 LAT", exact=False).first
                if age2.is_visible(timeout=1000): age2.click()
        except: pass

        offers = page.locator("article").all()
        for offer in offers:
            try:
                offer_text = offer.inner_text().lower()
                if "sponsorowane" in offer_text or "promowane" in offer_text:
                    continue 
                    
                price_el = offer.locator("span[class*='price']").first
                if not price_el.is_visible():
                    price_el = offer.locator("span:has-text(' zł')").filter(has_not=page.locator("del")).first
                
                if price_el.is_visible():
                    text = price_el.inner_text().replace(" ", "").replace(",", ".").replace("zł", "").strip()
                    match = re.search(r"(\d+\.\d{2})", text)
                    if not match: match = re.search(r"(\d+)", text)
                    if match:
                        price = float(match.group(1))
                        if price > 1: return price 
            except: continue
        return None
    except Exception as e:
        logger.error(f"Wystąpił błąd podczas szukania EAN {ean}: {e}")
        raise e

def get_latest_file():
    files = glob.glob("Analityka/baza_gapli_*.xlsx")
    if not files: 
        return None
    # Zwraca najnowszy plik na podstawie czasu modyfikacji/utworzenia
    return max(files, key=os.path.getctime)

def main():
    input_file = get_latest_file()
    if not input_file:
        logger.error("Nie znaleziono pliku bazy w folderze Analityka! Najpierw uruchom 1_pobierz_z_gapli.py")
        return

    logger.info(f"Wczytywanie pliku bazy: {input_file}")
    df = pd.read_excel(input_file)

    # Upewniamy się, że potrzebne kolumny istnieją
    for col in ['Najtańszy Allegro', 'Różnica', 'Status']:
        if col not in df.columns:
            df[col] = ""

    # Szukamy, ile zostało nam do zrobienia (gdzie Status jest pusty lub NaN)
    to_process = df[df['Status'].isna() | (df['Status'] == "")].index.tolist()
    total = len(df)
    left = len(to_process)
    
    if left == 0:
        logger.info("Wszystkie pozycje w tym pliku zostały już przeanalizowane.")
        return

    logger.info(f"Wykryto zapisany progres. Do przeanalizowania pozostało {left} z {total} produktów.")

    manager = ChromeManager(port=CHROME_DEBUG_PORT)
    if not manager.start_chrome(): 
        logger.error("Nie udało się uruchomić przeglądarki Chrome.")
        return

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{CHROME_DEBUG_PORT}")
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        
        ua = random.choice(USER_AGENTS)
        logger.info(f"Używam User-Agent: {ua}")
        
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.evaluate("document.body.style.zoom='0.6'")

        count = 0
        try:
            for idx in to_process:
                row = df.iloc[idx]
                
                ean_col = 'global_unique_id' if 'global_unique_id' in row.index else [c for c in row.index if 'ean' in c.lower()][0]
                ean = str(row[ean_col])
                my_price = row.get('Cena Brutto', 0)
                sku = row.get('sku', 'N/A')
                
                logger.info(f"[{total - left + count + 1}/{total}] SKU: {sku} | EAN: {ean}")
                
                comp_price = find_cheapest_on_allegro(page, ean)
                
                # Zapisanie wyników do DataFrame
                df.at[idx, 'Najtańszy Allegro'] = comp_price if comp_price else "Brak"
                
                if comp_price:
                    df.at[idx, 'Różnica'] = round(my_price - comp_price, 2)
                    df.at[idx, 'Status'] = "OK - JESTEŚ TAŃSZY/RÓWNY" if my_price <= comp_price else "DROŻSZY"
                else:
                    df.at[idx, 'Różnica'] = ""
                    df.at[idx, 'Status'] = "BRAK KONKURENCJI"

                logger.info(f"   -> {df.at[idx, 'Status']} (Allegro: {comp_price})")
                count += 1
                
                # Zapisywanie pliku co 10 przeanalizowanych produktów, aby nie tracić danych w razie awarii
                if count % 10 == 0:
                    df.to_excel(input_file, index=False)
                    logger.info(f"Zapisano punkt kontrolny (zrobiono {count} sztuk).")

        except KeyboardInterrupt:
            logger.warning("Skrypt przerwany przez użytkownika (Ctrl+C). Progres zostanie zapisany!")
        except Exception as e:
            logger.error(f"Wystąpił nieoczekiwany błąd, przerywam: {e}")
        finally:
            # TEN BLOK WYKONA SIĘ ZAWSZE - ZAPISUJEMY PROGRES
            df.to_excel(input_file, index=False)
            logger.info(f"Zapisano aktualny stan do pliku: {input_file}")
            
            # Jeśli udało się dobrnąć do końca, generujemy ładne raporty końcowe
            if len(df[df['Status'].isna() | (df['Status'] == "")]) == 0:
                logger.info("ANALIZA W 100% ZAKOŃCZONA!")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                
                full_report = f"Analityka/raport_pelny_{timestamp}.xlsx"
                df.to_excel(full_report, index=False)
                
                okazje_report = f"Analityka/raport_OKAZJE_{timestamp}.xlsx"
                df_okazje = df[df['Status'].isin(["OK - JESTEŚ TAŃSZY/RÓWNY", "BRAK KONKURENCJI"])]
                df_okazje.to_excel(okazje_report, index=False)
                
                logger.info(f"Wygenerowano raporty końcowe:\n1. {full_report}\n2. {okazje_report}")

if __name__ == "__main__":
    main()
