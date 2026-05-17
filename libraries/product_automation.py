import time
import re
import logging

class ProductAutomation:
    """Class for automating product addition in Gapli."""

    def __init__(self, page, client=None, username=None, password=None):
        self.page = page
        self.client = client
        self.username = username
        self.password = password
        self.logger = logging.getLogger(__name__)

    def retry_action(self, action_func, retries=3, delay=2):
        """Helper to retry UI actions."""
        for i in range(retries):
            try:
                if action_func():
                    return True
            except Exception as e:
                self.logger.warning(f"Attempt {i+1} failed: {e}")
            
            # Check for logout or session loss after each failure
            if "login" in self.page.url or not self.page.locator("aside").is_visible():
                self.logger.warning("Session lost or UI missing during action. Waiting for recovery...")
                self.wait_for_ui_ready()
                # After recovery, we should ideally retry the action again, potentially resetting retries
                return self.retry_action(action_func, retries, delay)

            if i < retries - 1:
                time.sleep(delay)
        return False

    def wait_for_ui_ready(self):
        """Waits indefinitely until the UI is ready (logged in and on marketplace)."""
        self.logger.info("Entering wait loop for UI recovery. Please log in and navigate to the Marketplace.")
        error_count = 0
        while True:
            try:
                # 1. Check if we can auto-login if error is visible or we are on login page
                login_error = self.page.locator("div.text-red-300:has-text('Wystąpił błąd podczas logowania')")
                if login_error.is_visible() or "login" in self.page.url:
                    error_count += 1
                    if error_count >= 2: # On persistent error, restart browser
                        self.logger.warning("Persistent login error detected. Waiting 20 seconds and RESTARTING CHROME...")
                        time.sleep(20)
                        # We don't have direct access to the restart logic here, but we can trigger a reload
                        # or rely on the fact that if we are in this loop, something is fundamentally wrong.
                        # For a real browser restart, we would need to raise an exception that main() catches.
                        raise Exception("RESTART_REQUIRED")
                    
                    if self.client and self.username and self.password:
                        self.logger.info("Login error detected or on login page. Attempting automatic login...")
                        if self.client.login(self.username, self.password):
                            self.logger.info("Automatic login successful. Navigating to marketplace...")
                            self.navigate_to_marketplace()
                            error_count = 0
                            time.sleep(2)
                        else:
                            self.logger.warning("Automatic login failed. Will retry in 10 seconds.")
                            time.sleep(5)
                    else:
                        self.logger.warning("Robot is on LOGIN page or error visible, but no credentials available for auto-login.")
                else:
                    error_count = 0 # Reset if no error visible
                
                # 2. Check for critical element: Wholesaler selector button
                # This button is only visible on the marketplace/products page when logged in.
                wholesaler_selector = self.page.locator("label:has-text('Hurtownia')").locator("xpath=..")
                wholesaler_btn = wholesaler_selector.locator("button").first
                
                if wholesaler_btn.is_visible():
                    self.logger.info("UI recovered: Wholesaler selector is visible. Resuming...")
                    time.sleep(2) # Brief pause to let everything settle
                    return True
                
                # 3. If sidebar is visible but not on marketplace
                if self.page.locator("aside").is_visible():
                    self.logger.info("Logged in, but not on Marketplace page. Attempting auto-navigation...")
                    if self.navigate_to_marketplace():
                        time.sleep(2)
                    else:
                        self.logger.info("Please navigate manually to 'Produkty' -> 'Wszystkie dostępne produkty'.")

            except Exception as e:
                self.logger.warning(f"Error in recovery wait loop: {e}")
            
            time.sleep(5)

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

    def set_basic_filters(self, min_price, max_price, min_stock, store_name=None):
        """Sets basic filters: wholesale price (min/max), stock level and Allegro account."""
        self.logger.info(f"Setting filters: price={min_price}-{max_price}, min stock={min_stock}, store={store_name}")
        try:
            price_container = self.page.locator("label:has-text('Cena hurtowa (PLN)')").locator("xpath=..")
            
            price_min_input = price_container.locator("input[placeholder='Od']").first
            price_min_input.fill(str(min_price))
            
            price_max_input = price_container.locator("input[placeholder='Do']").first
            price_max_input.fill(str(max_price))
            
            stock_input = self.page.locator("label:has-text('Ilość w magazynie')").locator("xpath=..").locator("input[placeholder='Od']").first
            stock_input.fill(str(min_stock))

            hide_blocked_label = self.page.locator("label").filter(has_text="Ukrywa produkty zablokowane do wysyłki na Allegro").first
            if hide_blocked_label.is_visible():
                # Check if it is already active (active state has bg-blue-50 class)
                if hide_blocked_label.locator("div.bg-blue-50").count() == 0:
                    hide_blocked_label.click(force=True)
                    self.logger.info("Activated 'Hide blocked products' filter.")
                    time.sleep(0.5)
                else:
                    self.logger.info("'Hide blocked products' filter is already active.")

            # Select Platform / Source: Allegro
            platform_trigger = self.page.locator("button").filter(has_text="Platforma / Źródło")
            if platform_trigger.first.is_visible():
                platform_trigger.first.click(force=True)
                time.sleep(1)
                allegro_option = self.page.locator("button[data-value='allegro']")
                if allegro_option.count() == 0:
                    allegro_option = self.page.locator("button").filter(has_text="Allegro")
                
                if allegro_option.first.is_visible():
                    allegro_option.first.click(force=True)
                    self.logger.info("Selected 'Allegro' as Platform / Source.")
                    time.sleep(1.5)

            # Select Allegro Account based on store_name
            if store_name:
                account_trigger = self.page.locator("button").filter(has_text="Wybierz konto Allegro")
                if account_trigger.first.is_visible():
                    account_trigger.first.click(force=True)
                    time.sleep(1)
                    
                    # Look for the account button that contains the store name
                    account_option = self.page.locator("button").filter(
                        has_text=re.compile(rf"{re.escape(store_name)}.*\| PROD \|", re.I)
                    )
                    if account_option.count() == 0:
                        account_option = self.page.locator("button").filter(has_text=store_name)
                    
                    if account_option.first.is_visible():
                        account_option.first.click(force=True)
                        self.logger.info(f"Selected Allegro account: {store_name}")
                        time.sleep(1)

            # Select how to handle already sent products: Hide
            sent_handle_trigger = self.page.locator("button").filter(has_text="Jak obsłużyć produkty już wysłane na wybrane konto?")
            if sent_handle_trigger.first.is_visible():
                sent_handle_trigger.first.click(force=True)
                time.sleep(1)
                hide_option = self.page.locator("button[data-value='hide']")
                if hide_option.count() == 0:
                    hide_option = self.page.locator("button").filter(has_text="Ukryj produkty już wysłane")
                
                if hide_option.first.is_visible():
                    hide_option.first.click(force=True)
                    self.logger.info("Selected 'Hide' for already sent products.")
                    time.sleep(1)

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

    def ensure_session_active(self):
        """Checks if the session is active and waits if not."""
        if "login" in self.page.url or not self.page.locator("aside").is_visible():
            self.logger.warning("Session lost or UI missing. Waiting for recovery...")
            self.wait_for_ui_ready()
            return True
        return False

    def select_wholesaler(self, wholesaler):
        """Selects a wholesaler from the filter dropdown."""
        self.ensure_session_active()
        self.logger.info(f"Attempting to select wholesaler: {wholesaler}")
        
        # Scroll to top to ensure the wholesaler selector is reachable
        self.page.evaluate("window.scrollTo(0, 0)")
        time.sleep(0.5)

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
        self.ensure_session_active()
        self.logger.info(f"Processing page {page_num}")
        
        pagination_inputs = self.page.locator("input[title*='Wpisz numer strony']").filter(visible=True)
        if pagination_inputs.count() > 0:
            actual_val = pagination_inputs.first.get_attribute("value")
            if actual_val != str(page_num):
                pagination_inputs.first.fill(str(page_num))
                self.page.keyboard.press("Enter")
                time.sleep(4)
                self.page.wait_for_load_state("networkidle")

        # Use label for visibility check and clicking
        select_all_label = self.page.locator("label").filter(has_text="Zaznacz wszystkie na tej stronie").first
        
        if not select_all_label.is_visible():
            self.logger.info("Select All label not visible, trying PageDown...")
            self.page.keyboard.press("PageDown")
            time.sleep(2)

        if not select_all_label.is_visible():
            self.logger.info("Still not visible, waiting for products to load...")
            time.sleep(4)
        
        if not select_all_label.is_visible():
            self.logger.info(f"No products found on page {page_num} (Select All label missing)")
            return False
        
        # Click the label to toggle the hidden checkbox
        try:
            # Check if internal input is already checked
            checkbox_input = select_all_label.locator("input[type='checkbox']")
            is_checked = False
            if checkbox_input.count() > 0:
                is_checked = checkbox_input.is_checked()
            
            if not is_checked:
                select_all_label.click(force=True)
                self.logger.info("Clicked 'Select All' label.")
                time.sleep(1)
            else:
                self.logger.info("'Select All' already checked.")
        except Exception as e:
            self.logger.warning(f"Error interacting with 'Select All' label: {e}. Trying text fallback.")
            self.page.get_by_text("Zaznacz wszystkie na tej stronie").first.click(force=True)

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

        self.logger.info(f"Successfully processed page {page_num}")
        self.page.wait_for_load_state("networkidle")
        time.sleep(2)
        return True

    def _select_marketplace_and_account(self, store_name):
        """Internal helper to select Allegro and the specific account."""
        self.logger.info(f"Modal opened. Selecting marketplace and account for: {store_name}")
        
        # 1. Check/Select Marketplace
        # Find the marketplace trigger button. It usually contains the text of the selected platform.
        marketplace_label = self.page.locator("h3").filter(has_text=re.compile("Wybierz miejsce wysyłki produktów", re.I))
        if marketplace_label.count() > 0:
            # The button is likely in the next div or relative to this label
            container = marketplace_label.locator("xpath=./ancestor::div[1]/following-sibling::div").first
            trigger = container.locator("button").first
            
            if trigger.is_visible():
                current_text = trigger.inner_text()
                if "Allegro" in current_text:
                    self.logger.info("Marketplace 'Allegro' already selected.")
                else:
                    self.logger.info(f"Selecting Allegro. Current: {current_text}")
                    trigger.click(force=True)
                    time.sleep(1.5)
                    allegro_opt = self.page.locator('button').filter(
                        has_text=re.compile("marketplace Allegro", re.I))
                    if allegro_opt.count() > 0:
                        allegro_opt.first.click(force=True)
                        time.sleep(1.5)

        # 2. Check/Select Allegro Account
        account_label = self.page.locator("h3").filter(has_text=re.compile("Wybierz konto Allegro", re.I))
        if account_label.count() > 0:
            container = account_label.locator("xpath=./ancestor::div[1]/following-sibling::div").first
            acc_dropdown = container.locator("button").first
            
            if acc_dropdown.is_visible():
                current_acc = acc_dropdown.inner_text()
                # Check if the store name is already in the selected text
                if store_name.lower() in current_acc.lower():
                    self.logger.info(f"Account for {store_name} already selected: {current_acc}")
                else:
                    self.logger.info(f"Selecting account for {store_name}. Current: {current_acc}")
                    acc_dropdown.click(force=True)
                    time.sleep(1.5)
                    
                    # Select the specific account
                    acc_opt = self.page.locator("button").filter(
                        has_text=re.compile(rf"{re.escape(store_name)}.*\| PROD \|", re.I))
                    
                    if acc_opt.count() == 0:
                        acc_opt = self.page.locator("button").filter(
                            has_text=re.compile(rf"{re.escape(store_name)}", re.I))

                    if acc_opt.count() > 0:
                        acc_opt.first.click(force=True)
                        time.sleep(1.5)
                    else:
                        self.logger.warning(f"Could not find account option for: {store_name}")

        # 3. Fill pricing (if visible in this stage)
        # Note: Sometimes pricing fields are in the modal, sometimes in the main filter area.
        price_label = self.page.locator("label:has-text('Cena minimalna')")
        if price_label.is_visible():
            # In some versions of the UI, we might need to fill these here
            pass

        # 4. Final Submission - Click the "Wyślij na Allegro" button
        # This button is usually at the bottom of the modal and contains the count of products.
        submit_btn = self.page.locator("button").filter(has_text=re.compile("Wyślij na Allegro", re.I))
        if submit_btn.count() > 0:
            for i in range(submit_btn.count()):
                btn = submit_btn.nth(i)
                if btn.is_visible() and btn.is_enabled():
                    self.logger.info("Clicking final 'Wyślij na Allegro' button.")
                    btn.click(force=True)
                    time.sleep(3) # Wait for modal to process
                    return True
        
        self.logger.warning("Could not find or click final submission button.")
        return False

    def set_zoom(self, zoom_percent):
        """Sets the page zoom level using CSS."""
        self.logger.info(f"Setting page zoom to {zoom_percent}%")
        self.page.evaluate(f"document.body.style.zoom = '{zoom_percent}%'")
