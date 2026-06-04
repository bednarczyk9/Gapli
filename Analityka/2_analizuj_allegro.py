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
from modem.modem_fast import reset_modem_ip, get_public_ip

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CHROME_DEBUG_PORT = 9222
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OPR/110.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 OPR/108.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 OPR/107.0.0.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
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
                    # Usuwamy wszystkie białe znaki (w tym twarde spacje /xa0 występujące przy tysiącach)
                    raw_text = price_el.inner_text()
                    text = re.sub(r'\s+', '', raw_text).replace(",", ".").replace("zł", "").replace("pln", "").strip()
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
    try:
        # Wymuszamy wczytanie EAN jako string, żeby uniknąć problemów z formatowaniem
        df = pd.read_excel(input_file, engine='openpyxl', dtype={'global_unique_id': str, 'ean': str})
    except Exception as e:
        logger.error(f"Błąd podczas wczytywania pliku Excel: {e}")
        return

    # Walidacja danych - jeśli kluczowe kolumny są puste, przerywamy, żeby nie nadpisać dobrego pliku zepsutymi danymi
    if df.empty:
        logger.error("Wczytany plik jest pusty.")
        return
        
    ean_col = 'global_unique_id' if 'global_unique_id' in df.columns else ([c for c in df.columns if 'ean' in c.lower()][0] if any('ean' in c.lower() for c in df.columns) else None)
    
    if not ean_col or df[ean_col].dropna().empty:
        logger.error(f"BŁĄD KRYTYCZNY: Kolumna EAN ({ean_col}) jest pusta lub jej brakuje! Przerywam, aby chronić dane.")
        return

    # Upewniamy się, że potrzebne kolumny istnieją i mogą przyjmować tekst
    for col in ['Najtańszy Allegro', 'Różnica', 'Status']:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].astype('object')

    # Szukamy, ile zostało nam do zrobienia (gdzie Status jest pusty, NaN lub "nan")
    to_process = df[df['Status'].isna() | (df['Status'] == "") | (df['Status'] == "nan")].index.tolist()
    total = len(df)
    left = len(to_process)
    
    if left == 0:
        logger.info("Wszystkie pozycje w tym pliku zostały już przeanalizowane.")
        return

    logger.info(f"Wykryto zapisany progres. Do przeanalizowania pozostało {left} z {total} produktów.")

    # Funkcja do bezpiecznego zapisywania (atomic save)
    def safe_save(p_df, p_path):
        temp_path = p_path + ".tmp"
        try:
            p_df.to_excel(temp_path, index=False, engine='openpyxl')
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 1000: # Prosta weryfikacja czy plik nie jest podejrzanie mały
                os.replace(temp_path, p_path)
                return True
            else:
                logger.error("Błąd zapisu: Plik tymczasowy jest pusty lub zbyt mały.")
                return False
        except Exception as se:
            logger.error(f"Błąd podczas bezpiecznego zapisywania: {se}")
            return False

    manager = ChromeManager(port=CHROME_DEBUG_PORT)
    if not manager.start_chrome(): 
        logger.error("Nie udało się uruchomić przeglądarki Chrome.")
        return

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{CHROME_DEBUG_PORT}")
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        
        # Funkcja do ustawiania UA (fizyczny Chrome może ignorować, ale nagłówki pójdą)
        def set_random_ua(p_page):
            new_ua = random.choice(USER_AGENTS)
            logger.info(f"Ustawiam User-Agent: {new_ua}")
            try:
                p_page.set_extra_http_headers({"User-Agent": new_ua})
            except: pass
            return new_ua

        ua = set_random_ua(page)
        
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.evaluate("document.body.style.zoom='0.6'")

        session_count = 0
        reset_count = 0
        # Zmieniamy IP co ok. 100 produktów (od 80 do 120)
        next_ip_reset = random.randint(80, 120)
        
        try:
            for idx in to_process:
                row = df.iloc[idx]
                
                ean = str(row[ean_col])
                my_price = row.get('Cena Brutto', 0)
                sku = row.get('sku', 'N/A')
                
                logger.info(f"[{total - left + session_count + 1}/{total}] SKU: {sku} | EAN: {ean}")
                
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
                session_count += 1
                reset_count += 1
                
                # Zapisywanie pliku co 10 przeanalizowanych produktów
                if session_count % 10 == 0:
                    safe_save(df, input_file)
                    logger.info(f"Zapisano punkt kontrolny (zrobiono {session_count} sztuk w tej sesji).")

                # Sprawdzenie czy czas na reset IP
                if reset_count >= next_ip_reset:
                    logger.info(f"Osiągnięto limit {reset_count} produktów. Rozpoczynam procedurę resetu IP...")
                    safe_save(df, input_file) # Zapisujemy przed resetem
                    
                    success = False
                    try:
                        success = reset_modem_ip()
                    except Exception as re:
                        logger.error(f"Błąd podczas resetu modemu: {re}")
                    
                    if success:
                        logger.info("IP zostało pomyślnie zmienione. Czekam na powrót połączenia (max 5 minut, sprawdzenie co 2s)...")
                        
                        start_wait = time.time()
                        internet_back = False
                        while time.time() - start_wait < 300: # 5 minut
                            if get_public_ip():
                                internet_back = True
                                break
                            time.sleep(2)
                        
                        if internet_back:
                            logger.info(f"Połączenie wznowione po {round(time.time() - start_wait, 1)}s. Kontynuuję...")
                            time.sleep(1) # Krótka sekunda na stabilizację
                            set_random_ua(page)
                        else:
                            logger.error("Brak internetu po 5 minutach od resetu IP. Zatrzymuję skrypt.")
                            return
                    else:
                        logger.warning("Nie udało się zresetować IP. Próbuję kontynuować mimo to...")
                    
                    reset_count = 0
                    next_ip_reset = random.randint(80, 120)
                    logger.info(f"Następny reset za ok. {next_ip_reset} produktów.")

        except KeyboardInterrupt:
            logger.warning("Skrypt przerwany przez użytkownika (Ctrl+C). Progres zostanie zapisany!")
        except Exception as e:
            logger.error(f"Wystąpił nieoczekiwany błąd, przerywam: {e}")
        finally:
            # TEN BLOK WYKONA SIĘ ZAWSZE - ZAPISUJEMY PROGRES
            safe_save(df, input_file)
            logger.info(f"Zapisano aktualny stan do pliku: {input_file}")
            
            # Jeśli udało się dobrnąć do końca, generujemy ładne raporty końcowe
            if len(df[df['Status'].isna() | (df['Status'] == "")]) == 0:
                logger.info("ANALIZA W 100% ZAKOŃCZONA!")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                
                full_report = f"Analityka/raport_pelny_{timestamp}.xlsx"
                safe_save(df, full_report)
                
                okazje_report = f"Analityka/raport_OKAZJE_{timestamp}.xlsx"
                df_okazje = df[df['Status'].isin(["OK - JESTEŚ TAŃSZY/RÓWNY", "BRAK KONKURENCJI"])]
                safe_save(df_okazje, okazje_report)
                
                logger.info(f"Wygenerowano raporty końcowe:\n1. {full_report}\n2. {okazje_report}")


if __name__ == "__main__":
    main()
