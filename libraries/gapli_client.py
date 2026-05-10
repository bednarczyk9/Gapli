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
            if "gapli.com/login" not in self.page.url:
                self.page.goto("https://gapli.com/login")
                self.page.wait_for_load_state("networkidle")

            if "dashboard" in self.page.url or self.page.locator("text=Wyloguj").is_visible():
                self.logger.info("User already logged in.")
                return True

            self.logger.info("Entering credentials (human-like)...")
            self.human.type_like_human("#username", username)
            self.human.type_like_human("#password", password)

            if self.page.locator("#remember-me").is_visible():
                self.logger.info("Clicking 'Remember me'...")
                self.human.move_and_click_like_human("#remember-me")

            self.logger.info("Clicking login button...")
            self.human.move_and_click_like_human('button:has-text("Zaloguj się")')
            
            self.page.wait_for_load_state("networkidle")
            
            if "login" not in self.page.url or self.page.locator("text=Wyloguj").is_visible():
                self.logger.info("Successfully logged in.")
                return True
            else:
                self.logger.error("Login failed.")
                return False
                
        except Exception as e:
            self.logger.error(f"Error during login: {e}")
            return False

    def is_logged_in(self):
        """Checks if the user is currently logged in."""
        return "dashboard" in self.page.url or self.page.locator("text=Wyloguj").is_visible()

    def set_zoom(self, zoom_percent):
        """Sets the page zoom level using CSS."""
        self.logger.info(f"Setting page zoom to {zoom_percent}%")
        self.page.evaluate(f"document.body.style.zoom = '{zoom_percent}%'")
