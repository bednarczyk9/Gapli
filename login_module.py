import os
import time
import random
import math
from playwright.sync_api import sync_playwright

def human_type(page, selector, text):
    """
    Wpisuje tekst symulując uderzenia w klawisze przez człowieka z losowymi opóźnieniami.
    """
    element = page.locator(selector)
    element.click() # Najpierw kliknij, aby ustawić focus
    for char in text:
        page.keyboard.type(char, delay=random.uniform(50, 150))
    time.sleep(random.uniform(0.2, 0.5))

def bezier_curve(p0, p1, p2, p3, t):
    """Oblicza punkt na krzywej Beziera."""
    return (
        (1-t)**3 * p0 + 
        3*(1-t)**2 * t * p1 + 
        3*(1-t) * t**2 * p2 + 
        t**3 * p3
    )

def human_move_and_click(page, selector):
    """
    Przesuwa mysz po krzywej i klika w element, aby uniknąć wykrycia przez proste ruchy.
    """
    element = page.locator(selector)
    box = element.bounding_box()
    if not box:
        print(f"BŁĄD: Nie znaleziono elementu {selector}")
        return

    # Docelowy punkt (środek elementu z małym losowym offsetem)
    target_x = box['x'] + box['width'] / 2 + random.uniform(-5, 5)
    target_y = box['y'] + box['height'] / 2 + random.uniform(-5, 5)

    # Obecna pozycja myszy (lub startowa)
    start_x, start_y = 0, 0 # Playwright nie ma 'get_mouse_pos', więc zaczynamy od góry/lewej lub poprzedniego miejsca
    
    # Punkty kontrolne dla krzywej Beziera (losowe)
    cp1_x = start_x + (target_x - start_x) * random.uniform(0.1, 0.4)
    cp1_y = start_y + (target_y - start_y) * random.uniform(0.7, 0.9)
    
    cp2_x = start_x + (target_x - start_x) * random.uniform(0.6, 0.9)
    cp2_y = start_y + (target_y - start_y) * random.uniform(0.1, 0.3)

    # Ruch po krzywej
    steps = random.randint(15, 30)
    for i in range(steps + 1):
        t = i / steps
        curr_x = bezier_curve(start_x, cp1_x, cp2_x, target_x, t)
        curr_y = bezier_curve(start_y, cp1_y, cp2_y, target_y, t)
        page.mouse.move(curr_x, curr_y)
        time.sleep(random.uniform(0.005, 0.02))

    # Kliknięcie
    page.mouse.down()
    time.sleep(random.uniform(0.05, 0.15))
    page.mouse.up()
    print(f"Kliknięto element: {selector}")

def login_to_gapli_human(page, username, password):
    """
    Zaludnione logowanie: symulacja ruchów myszy i uderzeń klawiszy.
    """
    try:
        if "gapli.com/login" not in page.url:
            page.goto("https://gapli.com/login")
            page.wait_for_load_state("networkidle")

        # Sprawdzenie czy już zalogowani
        if "dashboard" in page.url or page.locator("text=Wyloguj").is_visible():
            print("Użytkownik już zalogowany.")
            return True

        # 1. Wpisanie username
        print("Wpisywanie loginu (human-like)...")
        human_type(page, "#username", username)
        
        # 2. Wpisanie hasła
        print("Wpisywanie hasła (human-like)...")
        human_type(page, "#password", password)

        # 3. Checkbox "Zapamiętaj mnie" (jeśli potrzebny, symulujemy kliknięcie)
        if page.locator("#remember-me").is_visible():
            print("Klikanie checkboxa 'Zapamiętaj mnie' (human-like)...")
            human_move_and_click(page, "#remember-me")

        # 4. Przycisk logowania
        print("Klikanie przycisku logowania (human-like)...")
        human_move_and_click(page, 'button:has-text("Zaloguj się")')
        
        page.wait_for_load_state("networkidle")
        
        if "login" not in page.url or page.locator("text=Wyloguj").is_visible():
            print("Zalogowano pomyślnie jako człowiek!")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Błąd podczas 'ludzkiego' logowania: {e}")
        return False

if __name__ == "__main__":
    # Test lokalny (wymaga uruchomionego Chrome z CDP)
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()
            
            user = os.getenv("GAPLI_USER")
            pw = os.getenv("GAPLI_PASS")
            
            login_to_gapli_human(page, user, pw)
        except Exception as e:
            print(f"Błąd testu: {e}")
