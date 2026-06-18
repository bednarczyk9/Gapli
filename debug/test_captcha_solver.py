import sys
import logging
import time
import os
import requests
import re
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CHROME_DEBUG_PORT = 9222
CAPSOLVER_API_KEY = os.environ.get("CAPSOLVER_API_KEY")

def solve_with_capsolver(websiteKey, websiteURL):
    if not CAPSOLVER_API_KEY:
        logger.error("Brak klucza CAPSOLVER_API_KEY!")
        return None

    logger.info("Zlecam zadanie do CapSolver...")
    url = "https://api.capsolver.com/createTask"
    payload = {
        "clientKey": CAPSOLVER_API_KEY,
        "task": {
            "type": "ReCaptchaV2TaskProxyLess",
            "websiteURL": websiteURL,
            "websiteKey": websiteKey,
            "isInvisible": False
        }
    }
    
    resp = requests.post(url, json=payload).json()
    task_id = resp.get("taskId")
    if not task_id:
        logger.error(f"Błąd tworzenia zadania: {resp}")
        return None

    logger.info(f"Zadanie ID: {task_id}. Oczekuję na rozwiązanie...")
    
    while True:
        res = requests.post("https://api.capsolver.com/getTaskResult", json={
            "clientKey": CAPSOLVER_API_KEY,
            "taskId": task_id
        }).json()
        
        status = res.get("status")
        if status == "ready":
            logger.info("Otrzymano token z CapSolver!")
            return res.get("solution", {}).get("gRecaptchaResponse")
        elif status == "failed":
            logger.error("CapSolver nie rozwiązał zadania.")
            return None
            
        time.sleep(3)

def main():
    logger.info("Łączenie z aktywną przeglądarką (Playwright na porcie 9222)...")
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{CHROME_DEBUG_PORT}")
            context = browser.contexts[0]
            
            target_page = None
            for page in context.pages:
                content = page.content().lower()
                indicators = ["nietypowy ruch", "pokaż, że jesteś człowiekiem", "potwierdź, że jesteś człowiekiem", "udowodnij, że nie jesteś robotem"]
                if any(x in content for x in indicators) or "allegrocaptcha" in content or "datadome" in content or page.locator("iframe[title*='reCAPTCHA']").is_visible():
                    target_page = page
                    break
            
            if not target_page:
                logger.error("Nie znaleziono strony z blokadą!")
                return

            logger.info(f"Aktywna strona: {target_page.url}")
            target_page.bring_to_front()
            
            # Wzór z Twojego skryptu: 1. Szukamy ramki z checkboxem
            logger.info("Szukam pierwszej ramki z checkboxem (aby w niego kliknąć)...")
            captcha_frame = None
            for frame in target_page.frames:
                if "allegrocaptcha" in frame.url or "recaptcha/api2/anchor" in frame.url:
                    captcha_frame = frame
                    break
            
            if not captcha_frame:
                if len(target_page.frames) > 1:
                    captcha_frame = target_page.frames[1]
                else:
                    logger.error("Brak ramek.")
                    return

            # Krok 1: Wyciągamy sitekey (z kodu strony lub z URL ramki)
            site_key = None
            try:
                # Szukamy sitekey w zmiennych globalnych lub kodzie
                match = re.search(r'data-sitekey=["\']([^"\']+)["\']', target_page.content())
                if match: site_key = match.group(1)
                
                # Jeśli nie, szukamy w parametrach (k=...) URL ramki
                if not site_key:
                    match = re.search(r'([?&]k=)([^&]+)', captcha_frame.url)
                    if match: site_key = match.group(2)
            except: pass

            if not site_key:
                site_key = "6LeVb4QUAAAAAP16EQ4T0TImCD13PIPqEePFvGLx" # Domyślny Allegro
            
            logger.info(f"SiteKey: {site_key}")

            # Krok 2: Klikamy checkbox "I'm not a robot" (jak w Twoim skrypcie)
            logger.info("Klikam checkbox (jeśli istnieje)...")
            try:
                # Playwright pozwala kliknąć w element wewnątrz iframe
                checkbox = captcha_frame.locator(".recaptcha-checkbox-border").first
                if checkbox.is_visible(timeout=2000):
                    checkbox.click()
                    logger.info("Kliknięto checkbox.")
                    time.sleep(2)
            except:
                logger.warning("Nie udało się kliknąć checkboxa w pierwszej ramce.")

            # Krok 3: Sprawdzamy czy pojawiła się druga ramka (z obrazkami / bframe)
            logger.info("Sprawdzam czy Captcha wymaga rozwiązania (obrazki)...")
            needs_solve = False
            for frame in target_page.frames:
                if "recaptcha/api2/bframe" in frame.url:
                    needs_solve = True
                    break
            
            # W Allegro często od razu jesteśmy zablokowani (brak checkboxa), więc rozwiązujemy z góry
            if needs_solve or is_blocked_still(target_page):
                logger.info("Rozwiązuję Captcha przez API...")
                token = solve_with_capsolver(site_key, target_page.url)
                
                if token:
                    # Krok 4: Wstrzykiwanie rozwiązania (zamiast klikać w obrazki)
                    logger.info("Wstrzykuję odpowiedź do ukrytych pól...")
                    target_page.evaluate(f"""
                        (token) => {{
                            const els = document.querySelectorAll('[name="g-recaptcha-response"], [name="h-captcha-response"], #g-recaptcha-response');
                            els.forEach(el => {{ el.innerHTML = token; el.value = token; }});
                        }}
                    """, token)
                    
                    # W starszych skryptach po wstrzyknięciu klikało się przycisk "Submit" z głównego formularza
                    logger.info("Szukam przycisku wyślij/Submit...")
                    try:
                        btn = target_page.locator("button[type='submit'], input[type='submit'], .btn-captcha-submit").first
                        if btn.is_visible(timeout=1000):
                            btn.click()
                            logger.info("Kliknięto przycisk zatwierdzający.")
                        else:
                            # Próba wywołania callbacku jak w CapSolver
                            target_page.evaluate(f"""
                                (token) => {{
                                    if (window.___grecaptcha_cfg && window.___grecaptcha_cfg.clients) {{
                                        const clients = window.___grecaptcha_cfg.clients;
                                        for (let i in clients) {{
                                            for (let j in clients[i]) {{
                                                if (clients[i][j] && clients[i][j].callback) {{
                                                    if (typeof clients[i][j].callback === 'function') {{
                                                        clients[i][j].callback(token);
                                                    }} else if (typeof clients[i][j].callback === 'string') {{
                                                        window[clients[i][j].callback](token);
                                                    }}
                                                }}
                                            }}
                                        }}
                                    }}
                                }}
                            """, token)
                            logger.info("Wywołano wewnętrzne callbacki Captcha.")
                    except: pass
            
            time.sleep(3)
            logger.info("Zakończono testowy skrypt. Sprawdź okno przeglądarki.")

        except Exception as e:
            logger.error(f"Główny błąd: {e}")

def is_blocked_still(page):
    content = page.content().lower()
    return "nietypowy ruch" in content or "pokaż, że jesteś człowiekiem" in content

if __name__ == "__main__":
    main()
