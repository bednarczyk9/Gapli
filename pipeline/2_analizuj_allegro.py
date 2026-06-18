import pandas as pd
import os
import logging
import time
import re
import random
import glob
import csv
from datetime import datetime
from playwright.sync_api import sync_playwright
import sys

# Dodanie ścieżki do głównego folderu
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libraries.chrome_manager import ChromeManager
from libraries.human_interaction import HumanInteraction
from modem.modem_fast import reset_modem_ip, get_public_ip

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ACCOUNTS_CSV = os.path.join("allegro_accounts", "accounts_list.csv")
LOGIN_URL = "https://allegro.pl/logowanie?origin_url=%2F%3Fdd_referrer%3D"
LOGOUT_URL = "https://allegro.pl/wyloguj?origin_url=%2F"

def is_blocked(page):
    try:
        content = page.content().lower()
        has_iframe = False
        for frame in page.frames:
            if "allegrocaptcha.com" in frame.url or "captcha-delivery.com" in frame.url:
                has_iframe = True
                break
        
        indicators = ["nietypowy ruch", "pokaż, że jesteś człowiekiem", "potwierdź, że jesteś człowiekiem", "sprawdź czy nie jesteś robotem", "udowodnij, że nie jesteś robotem", "zostałeś zablokowany"]
        return any(x in content for x in indicators) or page.locator("iframe[title*='reCAPTCHA']").is_visible() or has_iframe
    except:
        return False

def wait_for_captcha(page):
    if is_blocked(page):
        logger.warning("WYKRYTO BLOKADĘ CAPTCHA! Rozwiąż ją ręcznie w oknie przeglądarki.")
        while is_blocked(page):
            time.sleep(5)
        logger.info("Blokada Captcha rozwiązana. Kontynuuję...")
        time.sleep(2)

def handle_cookies(page, hi):
    """Akceptuje zgody cookies jeśli się pojawią."""
    try:
        # Czekamy chwilę na pojawienie się modala
        time.sleep(2)
        
        # Selektory dla przycisków w modalu GDPR
        consent_selectors = [
            "button[data-testid='accept_home_view_action']",
            "button[data-metatestid='accept-event']",
            "button:has-text('Ok, zgadzam się')",
            "button:has-text('Zgadzam się')",
            "button:has-text('PRZEJDŹ DALEJ')",
            "button[data-role='accept-consent']"
        ]
        
        for selector in consent_selectors:
            btn = page.locator(selector).first
            if btn.is_visible(timeout=3000):
                logger.info(f"Klikam przycisk zgody: {selector}")
                hi.move_and_click_like_human(btn)
                # Czekamy aż modal zniknie
                page.wait_for_selector("#opbox-gdpr-consents-modal", state="hidden", timeout=5000)
                time.sleep(1)
                return True
    except Exception as e:
        logger.debug(f"Brak lub problem z modalem cookies: {e}")
    
    # Dodatkowy check czy coś jeszcze nie zasłania ekranu
    wait_for_captcha(page)
    return False

def login_to_allegro(page, hi):
    """Loguje się do Allegro używając losowego konta z listy."""
    if not os.path.exists(ACCOUNTS_CSV):
        logger.warning(f"Brak pliku z kontami: {ACCOUNTS_CSV}. Kontynuuję jako niezalogowany.")
        return False

    try:
        accounts = []
        with open(ACCOUNTS_CSV, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Normalizujemy nagłówki (usuwamy białe znaki)
            reader.fieldnames = [h.strip() for h in reader.fieldnames]
            for row in reader:
                if row.get('Status', '').strip().upper() == 'SUCCESS':
                    accounts.append(row)
        
        if not accounts:
            logger.warning("Brak aktywnych kont (SUCCESS) w pliku CSV.")
            return False

        account = random.choice(accounts)
        email = account.get('Email')
        # Obsługa różnych nazw kolumn dla hasła
        password = account.get('Hasło') or account.get('Haslo_Allegro')

        if not email or not password:
            logger.error(f"Błąd danych konta: Email={email}, Hasło={'***' if password else 'BRAK'}")
            return False

        logger.info(f"Próba logowania na konto: {email}")
        page.goto(LOGIN_URL, wait_until="load", timeout=60000)
        time.sleep(2)
        wait_for_captcha(page)
        handle_cookies(page, hi)

        # Wypełnianie loginu
        hi.type_like_human("input#login", email)
        hi.move_and_click_like_human("button[type='submit']")
        time.sleep(2)
        wait_for_captcha(page)

        # Wypełnianie hasła
        hi.type_like_human("input#password", password)
        hi.move_and_click_like_human("button[type='submit']")
        time.sleep(5)
        wait_for_captcha(page)

        if "allegro.pl" in page.url and "logowanie" not in page.url:
            logger.info("Logowanie udane!")
            # Powrót na główną żeby wyczyścić prompty
            page.goto("https://allegro.pl", wait_until="load", timeout=30000)
            time.sleep(2)
            return True
        else:
            logger.error("Logowanie nieudane.")
            return False
    except Exception as e:
        logger.error(f"Błąd podczas logowania: {e}")
        return False

def find_cheapest_on_allegro(page, hi, ean):
    if not ean or len(str(ean)) < 8: return None
    
    try:
        time.sleep(random.uniform(1.0, 3.0))
        search_url = f"https://allegro.pl/listing?string={ean}&sort=p&order=p"
        page.goto(search_url, wait_until="load", timeout=45000)
        time.sleep(1.0)
        handle_cookies(page, hi)
        wait_for_captcha(page)

        page_text = page.content().lower()
        if "teraz nie mamy dokładnie tego" in page_text or "znaleźliśmy podobne oferty" in page_text or "nie znaleźliśmy ofert dla" in page_text:
            return None 

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
        return None

def main():
    input_file = glob.glob("Analityka/baza_gapli_*.xlsx")
    if not input_file:
        logger.error("Nie znaleziono pliku bazy!")
        return
    input_file = max(input_file, key=os.path.getctime)

    logger.info(f"Wczytywanie pliku bazy: {input_file}")
    df = pd.read_excel(input_file, engine='openpyxl', dtype={'ean': str, 'global_unique_id': str})

    ean_col = 'global_unique_id' if 'global_unique_id' in df.columns else 'ean'
    for col in ['Najtańszy Allegro', 'Różnica', 'Status']:
        if col not in df.columns: df[col] = ""
        df[col] = df[col].astype('object')

    to_process = df[df['Status'].isna() | (df['Status'] == "") | (df['Status'] == "nan")].index.tolist()
    total = len(df)
    
    def safe_save(p_df, p_path):
        temp_path = p_path + ".tmp"
        p_df.to_excel(temp_path, index=False, engine='openpyxl')
        os.replace(temp_path, p_path)

    session_count = 0
    reset_count = 0
    next_rotation = random.randint(80, 120)

    try:
        while to_process:
            profile_name = f"Session_{random.randint(100, 999)}"
            cm = ChromeManager(port=9222, profile_name=profile_name)
            if not cm.start_chrome(): break

            with sync_playwright() as p:
                browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:9222")
                context = browser.contexts[0]
                page = context.pages[0] if context.pages else context.new_page()
                hi = HumanInteraction(page)

                # Ustawienie zoomu na 30%
                logger.info("Ustawiam zoom przeglądarki na 30%...")
                try:
                    page.evaluate("document.body.style.zoom='0.3'")
                except: pass

                page.goto("https://allegro.pl", wait_until="load", timeout=60000)
                handle_cookies(page, hi)
                login_to_allegro(page, hi)

                while reset_count < next_rotation and to_process:
                    idx = to_process.pop(0)
                    row = df.iloc[idx]
                    ean = str(row[ean_col])
                    my_price = row.get('Cena Brutto', 0)
                    
                    logger.info(f"[{total-len(to_process)}/{total}] EAN: {ean}")
                    comp_price = find_cheapest_on_allegro(page, hi, ean)
                    
                    df.at[idx, 'Najtańszy Allegro'] = comp_price if comp_price else "Brak"
                    if comp_price:
                        df.at[idx, 'Różnica'] = round(my_price - comp_price, 2)
                        df.at[idx, 'Status'] = "OK - JESTEŚ TAŃSZY/RÓWNY" if my_price <= comp_price else "DROŻSZY"
                    else:
                        df.at[idx, 'Status'] = "BRAK KONKURENCJI"

                    reset_count += 1
                    session_count += 1
                    if session_count % 10 == 0: safe_save(df, input_file)

                # Rotacja
                logger.info("Rotacja sesji i IP...")
                page.goto(LOGOUT_URL, wait_until="load")
                cm.kill_chrome()
                reset_modem_ip()
                reset_count = 0
                next_rotation = random.randint(80, 120)

    except Exception as e:
        logger.error(f"Błąd: {e}")
    finally:
        safe_save(df, input_file)
        logger.info("Zapisano progres.")

if __name__ == "__main__":
    main()
