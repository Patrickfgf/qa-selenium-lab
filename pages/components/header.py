from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class Header(BasePage):
    """Top bar shared by every page after login: cart badge, cart link and side menu."""

    CART_BADGE = (By.CSS_SELECTOR, '[data-test="shopping-cart-badge"]')
    CART_LINK = (By.CSS_SELECTOR, '[data-test="shopping-cart-link"]')
    # data-test="open-menu" sits on the icon inside the button, and Chrome rejects that click
    # ("element click intercepted"); the button's own id is stable, so it is the target.
    MENU_BUTTON = (By.ID, "react-burger-menu-btn")
    LOGOUT_LINK = (By.CSS_SELECTOR, '[data-test="logout-sidebar-link"]')

    def cart_count(self) -> int:
        badges = self.driver.find_elements(*self.CART_BADGE)
        # The badge is removed from the DOM when the cart is empty.
        return int(badges[0].text) if badges else 0

    def open_cart(self):
        # Imported here: CartPage has a Header itself (circular import).
        from pages.cart_page import CartPage

        self._click(self.CART_LINK)
        return CartPage(self.driver)

    def log_out(self):
        # Imported here: LoginPage leads to InventoryPage, which has a Header (circular import).
        from pages.login_page import LoginPage

        self._click(self.MENU_BUTTON)
        self._click(self.LOGOUT_LINK)
        return LoginPage(self.driver)
