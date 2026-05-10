import time
import re
import logging

class ProductAutomation:
    """Class for automating product addition in Gapli."""

    def __init__(self, page):
        self.page = page
        self.logger = logging.getLogger(__name__)

    def retry_action(self, action_func, retries=3, delay=2):
        """Helper to retry UI actions."""
        for i in range(retries):
            try:
                if action_func():
                    return True
            except Exception as e:
                self.logger.warning(f"Attempt {i+1} failed: {e}")
            if i < retries - 1:
                time.sleep(delay)
        return False

    def select_store(self, store_name):
        """Selects a store from the dropdown menu."""
        def _action():
            store_selector_btn = self.page.locator('button[aria-label="Wybór sklepu"]')
            if not store_selector_btn.is_visible():
                store_selector_btn = self.page.get_by_role("button", name="Wybór sklepu")
            
            store_selector_btn.click(force=True)
            time.sleep(1.5)

            store_item = self.page.locator("button").filter(
                has=self.page.locator(f"span:text-is('{store_name}')")
            )
            if store_item.count() == 0:
                store_item = self.page.locator(f"button:has-text('{store_name}')").filter(
                    has_selector="span"
                )

            if store_item.count() > 0:
                store_item.first.click(force=True)
                self.page.wait_for_load_state("networkidle")
                return True
            return False

        if not self.retry_action(_action):
            self.logger.error(f"Failed to select store: {store_name}")
            self.page.keyboard.press("Escape")
            return False
        return True

    def navigate_to_marketplace(self):
        """Navigates to the marketplace (all products) page."""
        def _action():
            self.logger.info(f"Current URL: {self.page.url}")
            if "/dashboard/products" in self.page.url or "/dashboard/marketplace" in self.page.url:
                self.set_zoom(50)
                return True
                
            # Try to find 'Produkty' link
            produkty_link = self.page.get_by_role("link", name="Produkty", exact=True)
            if not produkty_link.is_visible():
                self.logger.info("Sidebar 'Produkty' not visible, checking if sidebar is collapsed or needs 'Twoje sklepy' click.")
                twoje_sklepy_btn = self.page.get_by_role("button", name="Twoje sklepy")
                if twoje_sklepy_btn.is_visible():
                    twoje_sklepy_btn.click(force=True)
                    time.sleep(1)
            
            if produkty_link.is_visible():
                produkty_link.click(force=True)
                self.page.wait_for_load_state("load")
                time.sleep(1)

            # Look for 'Wszystkie dostępne produkty'
            all_products_btn = self.page.get_by_role("button", name="Wszystkie dostępne produkty").first
            if not all_products_btn.is_visible():
                all_products_btn = self.page.locator("button:has-text('Wszystkie dostępne produkty')").first
            
            if all_products_btn.is_visible():
                all_products_btn.click(force=True)
                self.page.wait_for_load_state("load")
                time.sleep(2)
            
            # Re-apply zoom after navigation
            if "/dashboard/products" in self.page.url or "/dashboard/marketplace" in self.page.url:
                self.set_zoom(50)
                return True
            
            self.logger.warning(f"Failed to reach marketplace. Current URL: {self.page.url}")
            return False

        result = self.retry_action(_action)
        if not result:
            self.page.screenshot(path="navigation_error_debug.png")
        return result

    def set_basic_filters(self, min_price, min_stock):
        """Sets basic filters: wholesale price and stock level."""
        self.logger.info(f"Setting filters: min price={min_price}, min stock={min_stock}")
        try:
            price_input = self.page.locator("label:has-text('Cena hurtowa (PLN)')").locator("xpath=..").locator("input[placeholder='Od']").first
            price_input.fill(str(min_price))
            
            stock_input = self.page.locator("label:has-text('Ilość w magazynie')").locator("xpath=..").locator("input[placeholder='Od']").first
            stock_input.fill(str(min_stock))

            hide_blocked = self.page.get_by_text("Ukrywa produkty zablokowane do wysyłki na Allegro")
            if hide_blocked.first.is_visible():
                hide_blocked.first.click(force=True)
                self.logger.info("Checked 'Hide blocked products'.")

            # Set 1000 items per page
            per_page_select = self.page.locator("select").filter(
                has=self.page.locator("option[value='1000']")).first
            if per_page_select.is_visible():
                current_per_page = per_page_select.evaluate("node => node.value")
                if current_per_page != "1000":
                    per_page_select.select_option("1000")
                    self.logger.info("Set 1000 items per page.")
                    self.page.wait_for_load_state("networkidle")
                    time.sleep(2)
        except Exception as e:
            self.logger.error(f"Error setting basic filters: {e}")

    def select_wholesaler(self, wholesaler):
        """Selects a wholesaler from the filter dropdown."""
        self.logger.info(f"Attempting to select wholesaler: {wholesaler}")
        def _action():
            wholesaler_selector = self.page.locator("label:has-text('Hurtownia')").locator("xpath=..")
            wholesaler_btn = wholesaler_selector.locator("button").first
            if not wholesaler_btn.is_visible():
                self.logger.warning("Wholesaler selection button not visible.")
                return False
            
            wholesaler_btn.click(force=True)
            time.sleep(1)
            
            search_input = self.page.locator("input[placeholder='Szukaj opcji...']")
            if search_input.is_visible():
                search_input.fill(wholesaler)
                time.sleep(1.5)
                option_btn = self.page.locator("div.overflow-y-auto button").filter(
                    has_text=re.compile(f"^{re.escape(wholesaler)}", re.I))
                
                if option_btn.count() > 0:
                    self.logger.info(f"Found wholesaler option: {wholesaler}. Clicking...")
                    option_btn.first.click(force=True)
                    return True
                else:
                    self.logger.warning(f"Wholesaler {wholesaler} not found in list. Pressing Enter as fallback.")
                    self.page.keyboard.press("Enter")
                    return True
            return False

        if self.retry_action(_action):
            self.page.wait_for_load_state("networkidle")
            time.sleep(3)
            return True
        return False

    def get_max_pages(self):
        """Attempts to determine the total number of pages."""
        max_pages = 1
        try:
            stats_text = self.page.locator(r"text=/Pokazuje \d+-\d+ z \d+/").filter(
                visible=True).first.inner_text()
            match = re.search(r'z (\d+)', stats_text)
            if match:
                total_prods = int(match.group(1))
                max_pages = (total_prods + 999) // 1000
        except:
            pass

        pagination_inputs = self.page.locator("input[title*='Wpisz numer strony']").filter(visible=True)
        if pagination_inputs.count() > 0:
            title_text = pagination_inputs.first.get_attribute("title") or ""
            match = re.search(r'\(1-\{(\d+)\}\)', title_text) or re.search(r'\(1-(\d+)\)', title_text)
            if match:
                max_pages = int(match.group(1))
        
        return max_pages

    def process_page(self, page_num, store_name, min_price, max_price):
        """Processes a single page of products: selects and sends to marketplace."""
        self.logger.info(f"Processing page {page_num}")
        
        pagination_inputs = self.page.locator("input[title*='Wpisz numer strony']").filter(visible=True)
        if pagination_inputs.count() > 0:
            actual_val = pagination_inputs.first.get_attribute("value")
            if actual_val != str(page_num):
                pagination_inputs.first.fill(str(page_num))
                self.page.keyboard.press("Enter")
                time.sleep(4)
                self.page.wait_for_load_state("networkidle")

        select_all = self.page.get_by_role("checkbox", name="Zaznacz wszystkie na tej stronie")
        if not select_all.is_visible():
            time.sleep(3)
            if not select_all.is_visible():
                self.logger.info(f"No products on page {page_num}")
                return False
        
        select_all.check(force=True)
        time.sleep(0.5)
                        
        send_btn = self.page.get_by_role("button", name="Wyślij zaznaczone produkty")
        if not (send_btn.is_visible() and send_btn.is_enabled()):
            self.logger.error("Send button not found or disabled.")
            return False

        send_btn.click(force=True)
        time.sleep(1.5)
        
        if not self.retry_action(lambda: self._select_marketplace_and_account(store_name)):
            self.logger.error("Failed to select marketplace/account.")
            return False

        # Fill final form
        if self.page.locator("label:has-text('Cena minimalna')").is_visible():
            self.page.locator("label:has-text('Cena minimalna')").locator("xpath=..").locator("input").fill(str(min_price))
            
            max_price_label = self.page.locator("label:has-text('Cena maksymalna (PLN)')")
            if max_price_label.is_visible():
                max_price_label.locator("xpath=..").locator("input").fill(str(max_price))
            
            submit_btn = self.page.get_by_role("button", name=re.compile("Wyślij na Allegro", re.I))
            if not submit_btn.is_visible():
                submit_btn = self.page.locator('button').filter(has_text=re.compile("Wyślij na Allegro", re.I))
            
            if submit_btn.is_visible():
                submit_btn.click(force=True)
                self.logger.info(f"Successfully submitted page {page_num}")
                time.sleep(5) 
                self.page.wait_for_load_state("networkidle")
                return True
            else:
                self.logger.error("Final submit button not found.")
                return False
        
        return False

    def _select_marketplace_and_account(self, store_name):
        """Internal helper to select Allegro and the specific account."""
        container = self.page.locator("div").filter(
            has_text=re.compile("Wybierz miejsce wysyłki produktów", re.I)).filter(
            has=self.page.locator("button")).last
        if container.count() == 0:
            return False
        
        trigger = container.locator("button").filter(
            has_text=re.compile("Wyślij produkty na", re.I)).first
        if not trigger.is_visible():
            trigger = container.locator("button").first
        
        trigger.click(force=True)
        time.sleep(1)
        
        allegro_opt = self.page.locator('button').filter(
            has_text=re.compile("marketplace Allegro", re.I))
        if allegro_opt.count() > 0:
            allegro_opt.first.click(force=True)
            time.sleep(1)
        else:
            return False

        acc_container = self.page.locator("div").filter(
            has_text=re.compile("Wybierz konto Allegro", re.I)).filter(
            has=self.page.locator("button")).last
        if acc_container.count() > 0:
            acc_dropdown = acc_container.locator("button").first
            acc_dropdown.click(force=True)
            time.sleep(1)
            
            acc_opt = self.page.locator("button").filter(
                has_text=re.compile(rf"{re.escape(store_name)}.*\| PROD \|", re.I))
            if acc_opt.count() == 0:
                acc_opt = self.page.locator("button[data-value]").filter(
                    has_text=re.compile(rf"{re.escape(store_name)}", re.I))

            if acc_opt.count() > 0:
                acc_opt.first.click(force=True)
                return True
        return False

    def set_zoom(self, zoom_percent):
        """Sets the page zoom level using CSS."""
        self.logger.info(f"Setting page zoom to {zoom_percent}%")
        self.page.evaluate(f"document.body.style.zoom = '{zoom_percent}%'")
