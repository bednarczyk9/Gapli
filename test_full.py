import time
import re
from playwright.sync_api import sync_playwright

def test_full_sequence():
    current_store = "radosnydzieciak" 
    
    with sync_playwright() as p:
        try:
            print("Łączenie z Chrome (127.0.0.1:9222)...")
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()

            # 1. Wybór Marketplace
            print("KROK 1: Wybór Marketplace...")
            dropdown_selector = "button.w-full.border.rounded-lg.px-3.py-2.text-left.relative.pr-10"
            dropdown_btn = page.locator(dropdown_selector).filter(has_text="Wyślij produkty na marketplace")
            
            if dropdown_btn.count() > 0:
                print("Klikam w dropdown marketplace...")
                dropdown_btn.first.click(force=True)
                time.sleep(1.5)
                
                allegro_option = page.locator('button').filter(has_text="📦 Wyślij produkty na marketplace Allegro")
                if allegro_option.count() > 0:
                    print("Wybieram opcję Allegro...")
                    allegro_option.first.click(force=True)
                    time.sleep(2)
                else:
                    print("Nie znaleziono opcji Allegro.")
                    return
            else:
                print("Nie znaleziono dropdowna marketplace (może już wybrany?).")

            # 2. Wybór Konta Allegro
            print(f"KROK 2: Wybór konta dla: {current_store}...")
            
            # Szukamy etykiety 'Wybierz konto Allegro'
            account_label = page.locator("label").filter(has_text="Wybierz konto Allegro")
            if account_label.count() > 0:
                print("Znaleziono etykietę 'Wybierz konto Allegro'")
                account_btn = account_label.locator("xpath=..").locator("button").first
            else:
                # Alternatywa: szukamy przycisku który ma wewnątrz span z odpowiednią klasą
                print("Nie znaleziono etykiety, szukam po spanach...")
                account_btn = page.locator("button").filter(has=page.locator("span.break-words"))

            if account_btn.count() > 0:
                current_selection_span = account_btn.locator("span.break-words").first
                current_text = current_selection_span.inner_text().strip()
                current_class = current_selection_span.get_attribute("class") or ""
                
                print(f"Aktualnie w polu konta: '{current_text}'")
                
                # Sprawdzamy czy to czarny tekst (wybrany)
                is_selected = "text-gray-900" in current_class or "dark:text-white" in current_class
                
                if is_selected and current_store in current_text:
                    print(f"Sklep {current_store} jest już wybrany.")
                else:
                    print(f"Klikam w dropdown konta...")
                    account_btn.first.click(force=True)
                    time.sleep(2)
                    
                    # Szukamy opcji na liście
                    options = page.locator("div[class*='overflow-y-auto'] button")
                    # Szukamy opcji która zawiera nazwę sklepu (np. "radosnydzieciak | PROD | radosnydzieciak")
                    target_option = options.filter(has_text=re.compile(f"{current_store}", re.I))
                    
                    if target_option.count() > 0:
                        print(f"Znaleziono opcję: '{target_option.first.inner_text().strip()}', klikam...")
                        target_option.first.click(force=True)
                        print("Sukces!")
                    else:
                        print("Nie znaleziono opcji na liście.")
                        # Dump dla debugowania
                        with open("debug_account_full.html", "w", encoding="utf-8") as f:
                            f.write(page.content())
            else:
                print("Nie znaleziono przycisku wyboru konta.")

        except Exception as e:
            print(f"Błąd: {e}")

if __name__ == "__main__":
    test_full_sequence()
