from decimal import Decimal
from typing import Self

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import Select

from pages.base_page import TIMEOUT, BasePage, Locator
from pages.components.header import Header
from pages.prices import to_decimal


class InventoryPage(BasePage):
    CONTAINER = (By.CSS_SELECTOR, '[data-test="inventory-container"]')
    TITLE = (By.CSS_SELECTOR, '[data-test="title"]')
    ITEM_NAMES = (By.CSS_SELECTOR, '[data-test="inventory-item-name"]')
    ITEM_PRICES = (By.CSS_SELECTOR, '[data-test="inventory-item-price"]')
    SORT_SELECT = (By.CSS_SELECTOR, '[data-test="product-sort-container"]')
    ACTIVE_SORT = (By.CSS_SELECTOR, '[data-test="active-option"]')

    def __init__(self, driver: WebDriver, timeout: float = TIMEOUT) -> None:
        super().__init__(driver, timeout)
        # The URL changes before React renders the list, so the page is "loaded" when this shows.
        self._visible(self.CONTAINER)
        self.header = Header(driver)

    def title(self) -> str:
        return self.driver.find_element(*self.TITLE).text

    def item_names(self) -> list[str]:
        return self._texts(self.ITEM_NAMES)

    def item_prices(self) -> list[Decimal]:
        return [to_decimal(text) for text in self._texts(self.ITEM_PRICES)]

    def sort_by(self, option_text: str) -> Self:
        Select(self._visible(self.SORT_SELECT)).select_by_visible_text(option_text)
        return self

    def active_sort(self) -> str:
        return self.driver.find_element(*self.ACTIVE_SORT).text

    def add_to_cart(self, product_name: str) -> Self:
        self.click_add_to_cart(product_name)
        # The button turning into "Remove" is the app's confirmation; reading the cart badge
        # right after the click could race the re-render.
        self._visible(self._item_button(product_name, "Remove"))
        return self

    def click_add_to_cart(self, product_name: str) -> Self:
        """Click "Add to cart" without waiting for the app to confirm it (see is_in_cart)."""
        self._click(self._item_button(product_name, "Add to cart"))
        return self

    def is_in_cart(self, product_name: str) -> bool:
        """Whether the product's button turns into "Remove", the app's confirmation, in time."""
        try:
            self._visible(self._item_button(product_name, "Remove"))
        except TimeoutException:
            return False
        return True

    @staticmethod
    def _item_button(product_name: str, label: str) -> Locator:
        # XPath because CSS cannot match text: find the card by product name, then its button.
        card = (
            '//*[@data-test="inventory-item"]'
            f'[.//*[@data-test="inventory-item-name"][normalize-space()="{product_name}"]]'
        )
        return (By.XPATH, f'{card}//button[normalize-space()="{label}"]')
