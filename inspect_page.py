import os
import time
import re
from playwright.sync_api import sync_playwright

def inspect_page():
    with sync_playwright() as p:
        try:
            print("Łączenie z Chrome (127.0.0.1:9222)...")
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()

            print(f"Obecny URL: {page.url}")
            
            # 1. Sprawdzenie menu wyboru sklepu
            print("\n--- Sprawdzanie menu wyboru sklepu ---")
            try:
                # Spróbujmy otworzyć menu jeśli nie jest otwarte
                store_selector_btn = page.get_by_role("button", name="Wybór sklepu")
                if store_selector_btn.is_visible():
                    print("Klikam w 'Wybór sklepu'...")
                    store_selector_btn.click()
                    time.sleep(2)
                
                # Zrzut przycisków w prawdopodobnym kontenerze dropdowna
                dropdown_buttons = page.locator("div.absolute button").all()
                print(f"Znaleziono {len(dropdown_buttons)} przycisków w dropdownie.")
                for i, btn in enumerate(dropdown_buttons[:10]):
                    print(f"Przycisk {i}: {btn.inner_text().strip()} | HTML: {btn.evaluate('el => el.outerHTML')[:200]}")
            except Exception as e:
                print(f"Błąd podczas sprawdzania menu sklepu: {e}")

            # 2. Sprawdzenie dropdowna 'Wyślij produkty na'
            print("\n--- Sprawdzanie dropdowna 'Wyślij produkty na' ---")
            try:
                # Spróbujmy znaleźć przycisk 'Wyślij zaznaczone produkty' żeby wywołać dropdown (tylko do inspekcji)
                send_btn = page.get_by_role("button", name="Wyślij zaznaczone produkty")
                if send_btn.is_visible():
                    print("Znaleziono przycisk 'Wyślij zaznaczone produkty'.")
                    # Tutaj nie klikamy, bo mogłoby to wysłać coś realnie, ale sprawdzimy co jest w DOM
                
                # Szukamy wszystkich przycisków które mogą być opcjami marketplace
                all_buttons = page.locator("button").all()
                for btn in all_buttons:
                    text = btn.inner_text().lower()
                    if "allegro" in text or "erli" in text or "kaufland" in text:
                        print(f"Znaleziono potencjalny przycisk: {btn.inner_text().strip()} | Data-value: {btn.get_attribute('data-value')} | HTML: {btn.evaluate('el => el.outerHTML')[:200]}")
            except Exception as e:
                print(f"Błąd podczas sprawdzania marketplace: {e}")

            # Zapisz pełny dump strony do pliku dla głębszej analizy
            with open("page_debug_dump.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            print("\nZapisano zrzut strony do page_debug_dump.html")

        except Exception as e:
            print(f"\nBŁĄD: {e}")

if __name__ == "__main__":
    inspect_page()
