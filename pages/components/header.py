from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

TIMEOUT = 10


class Header:
    """Top bar shared by every page after login: cart badge, cart link and side menu."""

    CART_BADGE = (By.CSS_SELECTOR, '[data-test="shopping-cart-badge"]')
    # data-test="open-menu" sits on the icon inside the button, and Chrome rejects that click
    # ("element click intercepted"); the button's own id is stable, so it is the target.
    MENU_BUTTON = (By.ID, "react-burger-menu-btn")
    LOGOUT_LINK = (By.CSS_SELECTOR, '[data-test="logout-sidebar-link"]')

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, TIMEOUT)

    def cart_count(self) -> int:
        badges = self.driver.find_elements(*self.CART_BADGE)
        # The badge is removed from the DOM when the cart is empty.
        return int(badges[0].text) if badges else 0

    def log_out(self):
        # Imported here: LoginPage leads to InventoryPage, which has a Header (circular import).
        from pages.login_page import LoginPage

        self.wait.until(EC.element_to_be_clickable(self.MENU_BUTTON)).click()
        self.wait.until(EC.element_to_be_clickable(self.LOGOUT_LINK)).click()
        return LoginPage(self.driver)
