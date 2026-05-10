import time
import re
from playwright.sync_api import sync_playwright

def test_allegro_account_selection(store_name="hit_bazar"):
    with sync_playwright() as p:
        try:
            print(f"Łączenie z Chrome (127.0.0.1:9222) dla sklepu: {store_name}...")
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()

            print("Rozpoczynam test wyboru konta Allegro...")
            
            # Szukanie kontenera "Wybierz konto Allegro"
            account_container = page.locator("div").filter(has_text=re.compile("Wybierz konto Allegro", re.I)).filter(has=page.locator("button")).last
            
            if account_container.count() > 0:
                print("Znaleziono kontener 'Wybierz konto Allegro'.")
                
                # Kliknięcie w dropdown konta
                dropdown_trigger = account_container.locator("button").first
                print(f"Klikam w dropdown konta...")
                dropdown_trigger.click(force=True)
                time.sleep(2)
                
                # Debug: Wypisz wszystkie przyciski dostępne na stronie po kliknięciu
                all_buttons = page.locator("button")
                print(f"Liczba przycisków na stronie: {all_buttons.count()}")
                for i in range(all_buttons.count()):
                    text = all_buttons.nth(i).inner_text().strip()
                    if text:
                        print(f"Button {i}: '{text}'")

                # Szukanie opcji pasującej do store_name
                # Próbujemy bardziej elastycznego dopasowania
                account_option = page.locator("button").filter(has_text=re.compile(rf"{re.escape(store_name)}", re.I))
                
                if account_option.count() > 0:
                    print(f"Znaleziono konto dla {store_name}. Klikam...")
                    account_option.first.click(force=True)
                    time.sleep(1.5)
                    print(f"✅ Sukces: Wybrano konto Allegro dla {store_name}.")
                else:
                    print(f"❌ Błąd: Nie znaleziono opcji konta dla '{store_name}' na liście.")
            else:
                print("❌ Błąd: Nie znaleziono kontenera 'Wybierz konto Allegro'.")

        except Exception as e:
            print(f"\nBŁĄD: {e}")

if __name__ == "__main__":
    # Możesz zmienić nazwę sklepu tutaj do testu
    test_allegro_account_selection("hit_bazar")
