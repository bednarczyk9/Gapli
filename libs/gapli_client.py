import logging
from .human_interaction import HumanInteraction

class GapliClient:
    """Class for interacting with the Gapli platform."""

    def __init__(self, page):
        self.page = page
        self.human = HumanInteraction(page)
        self.logger = logging.getLogger(__name__)

    def login(self, username, password):
        """Logs into Gapli using human-like interaction."""
        try:
            self.logger.info(f"Current URL: {self.page.url}")
            
            # 1. Sprawdź czy już zalogowani (dashboard lub sidebar widoczny)
            if "dashboard" in self.page.url or self.page.locator("aside").is_visible():
                self.logger.info("Already on dashboard. Session active.")
                return True

            if "gapli.com/login" not in self.page.url:
                self.logger.info("Navigating to login page...")
                self.page.goto("https://gapli.com/login", wait_until="load", timeout=60000)
            
            # Wait for "Sprawdzanie sesji..." to disappear
            self.logger.info("Waiting for session check to complete...")
            try:
                self.page.wait_for_selector("text=Sprawdzanie sesji...", state="hidden", timeout=15000)
            except Exception:
                self.logger.warning("Session check screen did not disappear quickly, continuing...")

            self.page.wait_for_timeout(2000)

            # Re-check after navigation
            if "dashboard" in self.page.url or self.page.locator("aside").is_visible():
                self.logger.info("Redirected to dashboard. Session active.")
                return True

            self.logger.info("Waiting for login form...")
            try:
                # Spróbuj znaleźć po ID, a jeśli nie, to po nazwie lub placeholderze
                self.page.wait_for_selector('input[name="username"], #username, input[placeholder*="użytkownika"]', timeout=10000)
            except Exception:
                if self.page.locator("aside").is_visible():
                    return True
                self.logger.error("Login form elements not found.")
                self.page.screenshot(path="login_missing_form.png")
                return False

            self.logger.info("Entering credentials...")
            # Używamy bardziej elastycznych selektorów do wpisywania
            user_selector = 'input[name="username"], #username'
            pass_selector = 'input[name="password"], #password'
            
            self.human.type_like_human(user_selector, username)
            self.human.type_like_human(pass_selector, password)

            if self.page.locator("#remember-me").is_visible():
                self.human.move_and_click_like_human("#remember-me")

            self.logger.info("Submitting login form (attempt 1)...")
            self.human.move_and_click_like_human('button:has-text("Zaloguj się")')
            
            # Wait for navigation or potential error
            for attempt in range(2, 4): # Attempt 2 and 3 if needed
                try:
                    self.page.wait_for_url("**/dashboard**", timeout=8000)
                    self.logger.info("Login successful: URL changed to dashboard.")
                    return True
                except Exception:
                    # Sprawdź czy nadal jesteśmy na stronie logowania i czy przycisk jest dostępny
                    if "login" in self.page.url and self.page.locator('button:has-text("Zaloguj się")').is_visible():
                        self.logger.warning(f"Still on login page after attempt {attempt-1}. Retrying click (attempt {attempt})...")
                        self.page.wait_for_timeout(2000) # Chwila przerwy przed ponownym kliknięciem
                        self.human.move_and_click_like_human('button:has-text("Zaloguj się")')
                    elif self.page.locator("aside").is_visible():
                        self.logger.info("Detected dashboard elements. Login successful.")
                        return True
                    else:
                        break # Inny błąd, wyjdź z pętli

            # Final check
            if "dashboard" in self.page.url or self.page.locator("aside").is_visible():
                return True
                
            self.logger.error("Login failed after multiple click attempts.")
            self.page.screenshot(path="login_retry_failed.png")
            return False
                
        except Exception as e:
            self.logger.error(f"Critical error during login: {e}")
            return False

    def is_logged_in(self):
        """Checks if the user is currently logged in."""
        return "dashboard" in self.page.url or self.page.locator("text=Wyloguj").is_visible()

    def set_zoom(self, zoom_percent):
        """Sets the page zoom level using CSS."""
        self.logger.info(f"Setting page zoom to {zoom_percent}%")
        self.page.evaluate(f"document.body.style.zoom = '{zoom_percent}%'")
