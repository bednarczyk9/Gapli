import os
import time
import re
import openpyxl
from playwright.sync_api import sync_playwright

# Konfiguracja
STORES = ["hit_bazar", "radosnydzieciak", "skarbiec_ofert"]
WHOLESALERS_XLSX = "Recorded/hurtownie_allegro.xlsx"
CENA_HURTOWA_OD = "200"
ILOSC_W_MAGAZYNIE = "2"
CENA_MINIMALNA = "200"

def retry_action(action_func, retries=3, delay=2):
    """Pomocnicza funkcja do ponawiania prób w razie błędów UI."""
    for i in range(retries):
        try:
            if action_func():
                return True
        except Exception as e:
            print(f"Próba {i+1} nieudana: {e}")
        if i < retries - 1:
            time.sleep(delay)
    return False

def run_automation():
    if not os.path.exists(WHOLESALERS_XLSX):
        print(f"BŁĄD: Nie znaleziono pliku {WHOLESALERS_XLSX}")
        return
    
    wb = openpyxl.load_workbook(WHOLESALERS_XLSX)
    ws = wb.active
    wholesalers = [row[0] for row in ws.iter_rows(min_row=2, values_only=True) if row[0]]

    with sync_playwright() as p:
        try:
            print("Łączenie z Chrome (127.0.0.1:9222)...")
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()

            for store_name in STORES:
                print(f"\n=== PROCES DLA SKLEPU: {store_name} ===")
                
                # 1. Wybór sklepu na górze strony
                print(f"Otwieram menu wyboru sklepu...")
                
                def select_store():
                    # Szukamy przycisku po aria-label lub tekście
                    store_selector_btn = page.locator('button[aria-label="Wybór sklepu"]')
                    if not store_selector_btn.is_visible():
                        store_selector_btn = page.get_by_role("button", name="Wybór sklepu")
                    
                    store_selector_btn.click(force=True)
                    time.sleep(1.5)

                    store_item = page.locator("button").filter(has=page.locator(f"span:text-is('{store_name}')"))
                    if store_item.count() == 0:
                        store_item = page.locator(f"button:has-text('{store_name}')").filter(has_selector="span")

                    if store_item.count() > 0:
                        store_item.first.click(force=True)
                        page.wait_for_load_state("networkidle")
                        return True
                    return False

                if not retry_action(select_store):
                    print(f"Ostrzeżenie: Nie udało się wybrać sklepu {store_name} po kilku próbach.")
                    page.keyboard.press("Escape")

                # 2. Nawigacja Sidebar
                print("Nawigacja do produktów...")
                
                def navigate_to_products():
                    if "/dashboard/marketplace" in page.url:
                        return True
                        
                    produkty_link = page.get_by_role("link", name="Produkty", exact=True)
                    if not produkty_link.is_visible():
                        twoje_sklepy_btn = page.get_by_role("button", name="Twoje sklepy")
                        if not twoje_sklepy_btn.is_visible():
                            twoje_sklepy_btn = page.locator("button:has-text('Twoje sklepy')")
                        twoje_sklepy_btn.click(force=True)
                        time.sleep(0.5)
                    
                    produkty_link.click(force=True)
                    page.wait_for_load_state("networkidle")

                    all_products_btn = page.get_by_role("button", name="Wszystkie dostępne produkty").first
                    if not all_products_btn.is_visible():
                        all_products_btn = page.locator("button:has-text('Wszystkie dostępne produkty')").first
                    
                    all_products_btn.click(force=True)
                    page.wait_for_load_state("networkidle")
                    time.sleep(1)
                    return "/dashboard/marketplace" in page.url

                retry_action(navigate_to_products)

                # 3. Ustawienie filtrów podstawowych
                print("Ustawianie filtrów...")
                page.locator("label:has-text('Cena hurtowa (PLN)')").locator("xpath=..").locator("input[placeholder='Od']").first.fill(CENA_HURTOWA_OD)
                page.locator("label:has-text('Ilość w magazynie')").locator("xpath=..").locator("input[placeholder='Od']").first.fill(ILOSC_W_MAGAZYNIE)

                hide_blocked = page.get_by_text("Ukrywa produkty zablokowane do wysyłki na Allegro")
                if hide_blocked.first.is_visible():
                    hide_blocked.first.click(force=True)
                    print("Zaznaczono: Ukryj produkty zablokowane")

                # 4. Pętla dla każdej hurtowni
                for wholesaler in wholesalers:
                    print(f"\nPrzetwarzanie hurtowni: {wholesaler}")
                    
                    def select_wholesaler():
                        wholesaler_selector = page.locator("label:has-text('Hurtownia')").locator("xpath=..")
                        wholesaler_btn = wholesaler_selector.locator("button").first
                        if not wholesaler_btn.is_visible(): return False
                        
                        search_input = page.locator("input[placeholder='Szukaj opcji...']")
                        if not search_input.is_visible():
                            wholesaler_btn.click(force=True)
                            time.sleep(1)
                        
                        if search_input.is_visible():
                            search_input.fill(wholesaler)
                            time.sleep(1)
                            option_btn = page.locator("div.overflow-y-auto button").filter(has_text=re.compile(f"^{re.escape(wholesaler)}", re.I))
                            if option_btn.count() > 0:
                                option_btn.first.click(force=True)
                                return True
                            else:
                                page.keyboard.press("Enter")
                                return True
                        return False

                    retry_action(select_wholesaler)
                    page.wait_for_load_state("networkidle")
                    time.sleep(4)

                    # Ustawienie liczby produktów na stronę na 1000
                    per_page_select = page.locator("select").filter(has=page.locator("option[value='1000']")).first
                    if per_page_select.is_visible():
                        current_per_page = per_page_select.evaluate("node => node.value")
                        if current_per_page != "1000":
                            per_page_select.select_option("1000")
                            page.wait_for_load_state("networkidle")
                            time.sleep(2)

                    # DYNAMICZNA OBSŁUGA PAGINACJI
                    print("Rozpoczynam dynamiczne przetwarzanie stron...")
                    
                    processed_pages = 0
                    max_safety_limit = 500 # Zabezpieczenie przed pętlą nieskończoną
                    
                    while processed_pages < max_safety_limit:
                        # 1. Sprawdzenie aktualnej strony i sumy stron
                        pagination_input = page.locator("input[title*='Wpisz numer strony']").first
                        total_pages = 1
                        current_page_num = processed_pages + 1
                        
                        if pagination_input.is_visible():
                            title_text = pagination_input.get_attribute("title") or ""
                            # Próba wyciągnięcia liczby stron z formatu (1-{8}) lub (1-8)
                            match = re.search(r'\(1-\{(\d+)\}\)', title_text) or re.search(r'\(1-(\d+)\)', title_text)
                            if match:
                                total_pages = int(match.group(1))
                            
                            # Pobranie aktualnego numeru strony z wartości inputa (jeśli strona sama się przełączyła)
                            val = pagination_input.get_attribute("value")
                            if val and val.isdigit():
                                current_page_num = int(val)

                        print(f"Przetwarzanie strony {current_page_num} z {total_pages} (Łącznie przetworzono: {processed_pages})")

                        # 2. Zaznaczanie produktów na obecnej stronie
                        select_all = page.get_by_role("checkbox", name="Zaznacz wszystkie na tej stronie")
                        if not select_all.is_visible():
                            print(f"Koniec produktów dla hurtowni {wholesaler}.")
                            break
                        
                        select_all.check(force=True)
                        time.sleep(0.5)
                                        
                        # 3. Proces wysyłki
                        marketplace_selected = False
                        send_btn = page.get_by_role("button", name="Wyślij zaznaczone produkty")
                        
                        if send_btn.is_visible() and send_btn.is_enabled():
                            send_btn.click(force=True)
                            time.sleep(1.5)
                            
                            def select_marketplace_and_account():
                                nonlocal marketplace_selected
                                container = page.locator("div").filter(has_text=re.compile("Wybierz miejsce wysyłki produktów", re.I)).filter(has=page.locator("button")).last
                                if container.count() == 0: return False
                                
                                trigger = container.locator("button").filter(has_text=re.compile("Wyślij produkty na", re.I)).first
                                if not trigger.is_visible(): trigger = container.locator("button").first
                                
                                trigger.click(force=True)
                                time.sleep(1)
                                
                                allegro_opt = page.locator('button').filter(has_text=re.compile("marketplace Allegro", re.I))
                                if allegro_opt.count() > 0:
                                    allegro_opt.first.click(force=True)
                                    time.sleep(1)
                                    marketplace_selected = True
                                else:
                                    return False

                                acc_container = page.locator("div").filter(has_text=re.compile("Wybierz konto Allegro", re.I)).filter(has=page.locator("button")).last
                                if acc_container.count() > 0:
                                    acc_dropdown = acc_container.locator("button").first
                                    acc_dropdown.click(force=True)
                                    time.sleep(1)
                                    
                                    acc_opt = page.locator("button").filter(has_text=re.compile(rf"{re.escape(store_name)}.*\| PROD \|", re.I))
                                    if acc_opt.count() == 0:
                                        acc_opt = page.locator("button[data-value]").filter(has_text=re.compile(rf"{re.escape(store_name)}", re.I))

                                    if acc_opt.count() > 0:
                                        acc_opt.first.click(force=True)
                                        return True
                                return False

                            if not retry_action(select_marketplace_and_account, retries=3):
                                print(f"BŁĄD: Nie udało się wybrać marketplace/konta na stronie {current_page_num}")

                        # 4. Wypełnianie ceny i finalna wysyłka
                        if marketplace_selected or page.locator("label:has-text('Cena minimalna')").is_visible():
                            page.locator("label:has-text('Cena minimalna')").locator("xpath=..").locator("input").fill(CENA_MINIMALNA)
                            
                            submit_btn = page.get_by_role("button", name=re.compile("Wyślij na Allegro", re.I))
                            if not submit_btn.is_visible():
                                submit_btn = page.locator('button').filter(has_text=re.compile("Wyślij na Allegro", re.I))
                            
                            if submit_btn.is_visible():
                                submit_btn.click(force=True)
                                print(f"✅ Wysłano stronę {current_page_num}/{total_pages}")
                                page.wait_for_load_state("networkidle")
                                time.sleep(3) # Dłuższy czas na przeładowanie i auto-przejście
                                processed_pages += 1
                                
                                if current_page_num >= total_pages:
                                    print(f"Osiągnięto ostatnią stronę ({total_pages}).")
                                    break
                            else:
                                print("BŁĄD: Nie znaleziono przycisku finalnego wysyłki.")
                                break
                        else:
                            print("BŁĄD: Nie udało się przejść do formularza wysyłki.")
                            break

        except Exception as e:
            print(f"\nBŁĄD: {e}")

if __name__ == "__main__":
    run_automation()
