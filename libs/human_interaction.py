import time
import random
import logging

class HumanInteraction:
    """Helper class for human-like browser interactions."""

    def __init__(self, page):
        self.page = page
        self.logger = logging.getLogger(__name__)

    def type_like_human(self, selector, text):
        """Types text with random delays between characters, clearing the field first."""
        element = self.page.locator(selector)
        element.wait_for(state="visible", timeout=10000)
        element.click()
        
        # Clear the field first
        element.fill("")
        time.sleep(random.uniform(0.1, 0.3))
        
        for char in text:
            self.page.keyboard.type(char, delay=random.uniform(50, 150))
        time.sleep(random.uniform(0.2, 0.5))

    def move_and_click_like_human(self, selector_or_locator):
        """Standard click with a small delay."""
        if isinstance(selector_or_locator, str):
            element = self.page.locator(selector_or_locator).first
        else:
            element = selector_or_locator
            
        try:
            element.wait_for(state="visible", timeout=5000)
            element.click()
            time.sleep(random.uniform(0.5, 1.0))
        except Exception as e:
            self.logger.error(f"Error clicking element: {e}")

    def random_move(self):
        """Simulate a mouse move (dummy for compatibility)."""
        time.sleep(random.uniform(0.1, 0.3))

    def scroll_like_human(self):
        """Perform simple scroll."""
        try:
            self.page.mouse.wheel(0, random.randint(300, 600))
            time.sleep(random.uniform(0.5, 1.0))
        except: pass

    def jitter_mouse(self):
        """Dummy for compatibility."""
        pass
