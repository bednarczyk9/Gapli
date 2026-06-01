import requests
import pandas as pd
import os
import logging
import time
import re
import json
import random
from datetime import datetime
from playwright.sync_api import sync_playwright
from libraries.chrome_manager import ChromeManager

# Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
CHROME_DEBUG_PORT = 9222 
TARGET_COUNT = 500

# CapSolver API Key
CAPSOLVER_API_KEY = os.environ.get("CAPSOLVER_API_KEY")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
]

def is_blocked(page):
    """Sprawdza czy strona jest zablokowana przez Captcha lub inne zabezpieczenia."""
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

def solve_recaptcha_enterprise(page):
    """Zaawansowane rozwiązywanie reCAPTCHA przez CapSolver wewnątrz iframe."""
    if not CAPSOLVER_API_KEY:
        logger.warning("Brak klucza CapSolver! Rozwiąż Captcha ręcznie.")
        return False

    try:
        logger.info("Szukam iframe z Captcha...")
        captcha_frame = None
        for frame in page.frames:
            if "allegrocaptcha.com" in frame.url:
                captcha_frame = frame
                break
        
        target = captcha_frame if captcha_frame else page
        logger.info(f"Target do rozwiązania: {'IFRAME' if captcha_frame else 'MAIN PAGE'}")

        # Detekcja sitekey
        try:
            content = target.content()
            site_key_match = re.search(r'data-sitekey=["\']([^"\']+)["\']', content)
            if not site_key_match:
                site_key_match = re.search(r'sitekey[:\s]+["\']([^"\']+)["\']', content)
            site_key = site_key_match.group(1) if site_key_match else "6LeVb4QUAAAAAP16EQ4T0TImCD13PIPqEePFvGLx"
        except:
            site_key = "6LeVb4QUAAAAAP16EQ4T0TImCD13PIPqEePFvGLx"
            
        page_url = target.url
        
        payload = {
            "clientKey": CAPSOLVER_API_KEY,
            "task": {
                "type": "ReCaptchaV2EnterpriseTaskProxyLess",
                "websiteURL": page_url,
                "websiteKey": site_key,
                "isInvisible": False
            }
        }
        
        resp = requests.post("https://api.capsolver.com/createTask", json=payload).json()
        task_id = resp.get("taskId")
        if not task_id: return False
            
        logger.info(f"Zadanie CapSolver ID: {task_id}. Czekam na token...")
        
        while True:
            result = requests.post("https://api.capsolver.com/getTaskResult", json={"clientKey": CAPSOLVER_API_KEY, "taskId": task_id}).json()
            if result.get("status") == "ready":
                token = result.get("solution", {}).get("gRecaptchaResponse")
                logger.info("Token otrzymany! Wstrzykuję...")
                
                target.evaluate(f"""
                    (token) => {{
                        const setToken = (id) => {{
                            const el = document.getElementById(id) || document.getElementsByName(id)[0];
                            if (el) {{
                                el.innerHTML = token;
                                el.value = token;
                                return true;
                            }}
                            return false;
                        }};
                        setToken("g-recaptcha-response");
                        setToken("h-captcha-response");
                        document.querySelectorAll('textarea[id*="captcha"], textarea[name*="captcha"]').forEach(el => {{
                            el.innerHTML = token; el.value = token;
                        }});

                        if (window.___grecaptcha_cfg) {{
                            const clients = window.___grecaptcha_cfg.clients;
                            for (let i in clients) {{
                                const client = clients[i];
                                for (let j in client) {{
                                    if (client[j] && client[j].callback) {{
                                        if (typeof client[j].callback === 'function') {{
                                            client[j].callback(token);
                                        }} else if (typeof client[j].callback === 'string') {{
                                            window[client[j].callback](token);
                                        }}
                                    }}
                                }}
                            }}
                        }}
                        
                        setTimeout(() => {{
                            const btns = [...document.querySelectorAll('button, input[type="submit"], div[role="button"]')];
                            const btn = btns.find(b => /potwierdź|sprawdź|ok|submit|verify|wyślij|kontynuuj/i.test(b.innerText || b.value)) || 
                                        document.querySelector('button[type="submit"], .btn-captcha-submit');
                            if (btn) btn.click();
                        }}, 500);
                    }}
                """, token)
                
                # Czekaj na zniknięcie blokady
                for i in range(15):
                    time.sleep(2)
                    if not is_blocked(page):
                        logger.info("Blokada zniknęła!")
                        return True
                    if i == 7: # W połowie czekania spróbujmy kliknąć jeszcze raz
                        target.evaluate('const b = [...document.querySelectorAll("button")].find(x => /potwierdź|sprawdź|ok/i.test(x.innerText)); if(b) b.click();')
                
                logger.warning("Blokada nadal widoczna po 30s. Odświeżam stronę...")
                page.reload()
                time.sleep(5)
                return not is_blocked(page)

            elif result.get("status") == "failed":
                return False
            time.sleep(3)
            
    except Exception as e:
        logger.error(f"Błąd CapSolver: {e}")
        return False

class CaptchaDetectedException(Exception):
    pass

def find_cheapest_on_allegro(page, ean):
    if not ean or len(str(ean)) < 8: return None
    
    try:
        # Dodajemy losowe opóźnienie i ruchy
        time.sleep(random.uniform(2.0, 4.0))
        
        # Metoda 1: Bezpośrednie wejście (szybsze)
        search_url = f"https://allegro.pl/listing?string={ean}&sort=p&order=p"
        page.goto(search_url, wait_until="load", timeout=45000)
        time.sleep(1.5)

        if is_blocked(page):
            logger.error(f"WYKRYTO BLOKADĘ CAPTCHA! Zatrzymuję skrypt główny do testów.")
            raise CaptchaDetectedException("Captcha wykryta na direct URL")

        # Obsługa komunikatu o braku dokładnych wyników (Allegro proponuje "podobne")
        page_text = page.content().lower()
        if "teraz nie mamy dokładnie tego" in page_text or "znaleźliśmy podobne oferty" in page_text or "nie znaleźliśmy ofert dla" in page_text:
            return None # Brak dokładnego odpowiednika

        # Obsługa wieku
        try:
            age1 = page.get_by_role("button", name="Potwierdź wiek", exact=False).first
            if age1.is_visible(timeout=1000):
                age1.click()
                time.sleep(1)
                age2 = page.get_by_role("button", name="TAK, MAM 18 LAT", exact=False).first
                if age2.is_visible(timeout=1000): age2.click()
        except: pass

        # Pobieranie ofert, POMIJAJĄC te zawierające napis "Sponsorowane" lub "Produkty promowane"
        offers = page.locator("article").all()
        for offer in offers:
            try:
                # Sprawdzenie czy oferta jest promowana/sponsorowana
                offer_text = offer.inner_text().lower()
                if "sponsorowane" in offer_text or "promowane" in offer_text:
                    continue # Pomijamy reklamy, idziemy do kolejnej oferty
                    
                price_el = offer.locator("span[class*='price']").first
                if not price_el.is_visible():
                    price_el = offer.locator("span:has-text(' zł')").filter(has_not=page.locator("del")).first
                
                if price_el.is_visible():
                    text = price_el.inner_text().replace(" ", "").replace(",", ".").replace("zł", "").strip()
                    match = re.search(r"(\d+\.\d{2})", text)
                    if not match: match = re.search(r"(\d+)", text)
                    if match:
                        price = float(match.group(1))
                        if price > 1: return price # Zwracamy PIERWSZĄ niesponsorowaną ofertę (czyli najtańszą, bo sort=p)
            except: continue
        return None
    except CaptchaDetectedException as e:
        raise e
    except: return None

def fetch_all_and_sort_by_profit():
    url = 'https://gapli.com/api/products-manager/products'
    headers = {'Authorization': GAPLI_TOKEN}
    all_products = []
    page = 1
    limit = 50
    
    logger.info("Pobieranie produktów z Gapli...")
    while len(all_products) < 2000: 
        params = {'limit': limit, 'page': page}
        try:
            logger.info(f"Pobieranie strony {page}...")
            resp = requests.get(url, headers=headers, params=params, timeout=45).json()
            products = resp.get('products', [])
            if not products: break
            all_products.extend(products)
            page += 1
            if len(products) < limit: break
        except: break

    if not all_products: return pd.DataFrame()
    df = pd.DataFrame(all_products)
    
    col_ean = 'global_unique_id' if 'global_unique_id' in df.columns else (df.columns[df.columns.str.contains('ean', case=False)][0] if any(df.columns.str.contains('ean', case=False)) else None)
    if not col_ean: return pd.DataFrame()

    df = df[df[col_ean].notna()]
    if 'allegro_blocked' in df.columns: df = df[df['allegro_blocked'] == False]
    if 'stock_quantity' in df.columns:
        df['stock_quantity'] = pd.to_numeric(df['stock_quantity'], errors='coerce').fillna(0)
        df = df[df['stock_quantity'] > 0]
        
    df = df.drop_duplicates(subset=[col_ean])
    price_col = 'sale_net_price' if 'sale_net_price' in df.columns else (df.columns[df.columns.str.contains('price', case=False)][0] if any(df.columns.str.contains('price', case=False)) else None)
    
    if price_col:
        df['sale_net_price'] = pd.to_numeric(df[price_col], errors='coerce').fillna(0)
        df['Cena Brutto'] = round(df['sale_net_price'] * 1.23, 2)
        df = df.sort_values(by='Cena Brutto', ascending=False)
    
    return df.head(TARGET_COUNT)

def main():
    df_candidates = fetch_all_and_sort_by_profit()
    if df_candidates.empty: return

    manager = ChromeManager(port=CHROME_DEBUG_PORT)
    if not manager.start_chrome(): return

    results = []
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{CHROME_DEBUG_PORT}")
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()
            
            # Losujemy User-Agenta dla sesji
            ua = random.choice(USER_AGENTS)
            logger.info(f"Używam User-Agent: {ua}")
            
            page.set_viewport_size({"width": 1920, "height": 1080})
            page.evaluate("document.body.style.zoom='0.6'")
            
            logger.info(f"Rozpoczynanie analizy {TARGET_COUNT} produktów...")

            for index, row in df_candidates.iterrows():
                ean_col = 'global_unique_id' if 'global_unique_id' in row else [c for c in row.index if 'ean' in c.lower()][0]
                ean = str(row[ean_col])
                my_price = row.get('Cena Brutto', 0)
                sku = row.get('sku', 'N/A')
                
                logger.info(f"[{len(results)+1}/{TARGET_COUNT}] {sku} | EAN: {ean}")
                comp_price = find_cheapest_on_allegro(page, ean)
                
                res = {
                    "SKU": sku, "EAN": ean, "Nazwa": row.get('name', 'N/A'),
                    "Moja Cena": my_price, "Najtańszy Allegro": comp_price if comp_price else "Brak",
                    "Różnica": round(my_price - comp_price, 2) if comp_price else "",
                    "Status": "OK" if comp_price and my_price <= comp_price else ("DROŻSZY" if comp_price else "BRAK KONKURENCJI")
                }
                
                results.append(res)
                logger.info(f"   -> {res['Status']} (Allegro: {comp_price})")
                
                if len(results) % 25 == 0:
                    pd.DataFrame(results).to_excel(f"backup_analiza_{len(results)}.xlsx", index=False)

            full_df = pd.DataFrame(results)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            full_df.to_excel(f"raport_pelny_{timestamp}.xlsx", index=False)
            full_df[full_df['Status'].isin(["OK", "BRAK KONKURENCJI"])].to_excel(f"raport_OKAZJE_{timestamp}.xlsx", index=False)
            logger.info("ANALIZA ZAKOŃCZONA.")
            
        except Exception as e:
            logger.error(f"Błąd krytyczny: {e}")

if __name__ == "__main__":
    main()
