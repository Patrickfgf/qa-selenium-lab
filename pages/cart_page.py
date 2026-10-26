from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_page import BasePage
from pages.checkout_info_page import CheckoutInfoPage


class CartPage(BasePage):
    CART_LIST = (By.CSS_SELECTOR, '[data-test="cart-list"]')
    ITEM_NAMES = (By.CSS_SELECTOR, '[data-test="inventory-item-name"]')
    CHECKOUT_BUTTON = (By.CSS_SELECTOR, '[data-test="checkout"]')

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)
        self._visible(self.CART_LIST)

    def item_names(self) -> list[str]:
        return self._texts(self.ITEM_NAMES)

    def checkout(self) -> CheckoutInfoPage:
        self._click(self.CHECKOUT_BUTTON)
        return CheckoutInfoPage(self.driver)
