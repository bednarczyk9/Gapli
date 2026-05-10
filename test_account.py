import time
import re
from playwright.sync_api import sync_playwright

def test_account_selection():
    # Zmienna testowa - udajemy, że aktualnie przetwarzamy ten sklep
    current_store = "radosnydzieciak" 
    
    with sync_playwright() as p:
        try:
            print("Łączenie z Chrome (127.0.0.1:9222)...")
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()

            print(f"Szukam pola 'Wybierz konto Allegro' dla sklepu: {current_store}")
            
            # Precyzyjne szukanie pola wyboru konta Allegro
            # Szukamy etykiety, a potem przycisku obok niej lub w tym samym kontenerze
            account_label = page.locator("label:has-text('Wybierz konto Allegro')")
            if account_label.count() > 0:
                print("Znaleziono etykietę 'Wybierz konto Allegro'")
                # Przycisk powinien być w tym samym divie (parent)
                account_btn = account_label.locator("xpath=..").locator("button").first
            else:
                # Alternatywa: szukanie przycisku z konkretną klasą szarą (nie wybrany) lub czarną (wybrany)
                print("Nie znaleziono etykiety, szukam po klasach...")
                account_btn = page.locator("button").filter(has=page.locator("span[class*='break-words']")).filter(has_text=re.compile("Wybierz konto", re.I))

            if account_btn.count() > 0:
                # Sprawdzamy co jest aktualnie wybrane
                current_selection_span = account_btn.locator("span.break-words").first
                current_text = current_selection_span.inner_text().strip()
                current_class = current_selection_span.get_attribute("class")
                print(f"Aktualnie w polu: '{current_text}'")
                
                # Warunek: czy sklep jest wybrany (czarny tekst) i czy to ten właściwy
                is_selected = "text-gray-900" in current_class or "dark:text-white" in current_class
                
                if is_selected and current_store in current_text:
                    print(f"Sklep {current_store} jest już poprawnie wybrany.")
                else:
                    print(f"Klikam w dropdown konta Allegro (obecnie: {current_text})...")
                    account_btn.click(force=True)
                    time.sleep(2)
                    
                    # Szukamy opcji na liście - używamy selektora z HTML użytkownika
                    # button[data-value] wewnątrz kontenera listy
                    print(f"Szukam opcji '{current_store}' na liście...")
                    
                    # Próba znalezienia przycisku który ma w środku span z nazwą sklepu
                    options = page.locator("div[class*='overflow-y-auto'] button")
                    target_option = options.filter(has_text=re.compile(f"^{current_store}\\b", re.I))
                    
                    if target_option.count() == 0:
                         # Druga próba: cokolwiek co zawiera nazwę sklepu na liście
                         target_option = options.filter(has_text=current_store)

                    if target_option.count() > 0:
                        print(f"Znaleziono opcję: '{target_option.first.inner_text().strip()}', klikam...")
                        target_option.first.click(force=True)
                        print("Sukces!")
                    else:
                        print("Nie znaleziono opcji na liście. Zrzucam HTML do debug_account.html")
                        with open("debug_account.html", "w", encoding="utf-8") as f:
                            f.write(page.content())
            else:
                print("Nie znaleziono przycisku wyboru konta.")

        except Exception as e:
            print(f"Błąd: {e}")

if __name__ == "__main__":
    test_account_selection()
