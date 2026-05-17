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
        
        # Clear the field first - using fill("") is most reliable
        element.fill("")
        time.sleep(random.uniform(0.1, 0.3))
        
        for char in text:
            self.page.keyboard.type(char, delay=random.uniform(50, 150))
        time.sleep(random.uniform(0.2, 0.5))

    def move_and_click_like_human(self, selector):
        """Moves mouse in a curve and clicks an element."""
        element = self.page.locator(selector)
        box = element.bounding_box()
        if not box:
            self.logger.error(f"ERROR: Element {selector} not found for clicking.")
            return

        target_x = box['x'] + box['width'] / 2 + random.uniform(-5, 5)
        target_y = box['y'] + box['height'] / 2 + random.uniform(-5, 5)

        # Start from current or (0,0)
        start_x, start_y = 0, 0 
        
        cp1_x = start_x + (target_x - start_x) * random.uniform(0.1, 0.4)
        cp1_y = start_y + (target_y - start_y) * random.uniform(0.7, 0.9)
        
        cp2_x = start_x + (target_x - start_x) * random.uniform(0.6, 0.9)
        cp2_y = start_y + (target_y - start_y) * random.uniform(0.1, 0.3)

        steps = random.randint(15, 30)
        for i in range(steps + 1):
            t = i / steps
            curr_x = self._bezier_curve(start_x, cp1_x, cp2_x, target_x, t)
            curr_y = self._bezier_curve(start_y, cp1_y, cp2_y, target_y, t)
            self.page.mouse.move(curr_x, curr_y)
            time.sleep(random.uniform(0.005, 0.02))

        self.page.mouse.down()
        time.sleep(random.uniform(0.05, 0.15))
        self.page.mouse.up()
        self.logger.info(f"Clicked element: {selector}")

    def _bezier_curve(self, p0, p1, p2, p3, t):
        """Calculates point on a Bezier curve."""
        return (
            (1-t)**3 * p0 + 
            3*(1-t)**2 * t * p1 + 
            3*(1-t) * t**2 * p2 + 
            t**3 * p3
        )
