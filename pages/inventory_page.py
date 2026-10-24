from decimal import Decimal
from typing import Self

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_page import TIMEOUT, BasePage, Locator
from pages.components.header import Header
from pages.prices import to_decimal


class InventoryPage(BasePage):
    CONTAINER = (By.CSS_SELECTOR, '[data-test="inventory-container"]')
    TITLE = (By.CSS_SELECTOR, '[data-test="title"]')
    ITEM_NAMES = (By.CSS_SELECTOR, '[data-test="inventory-item-name"]')
    ITEM_PRICES = (By.CSS_SELECTOR, '[data-test="inventory-item-price"]')

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

    def add_to_cart(self, product_name: str) -> Self:
        self._click(self._item_button(product_name, "Add to cart"))
        # The button turning into "Remove" is the app's confirmation; reading the cart badge
        # right after the click could race the re-render.
        self._visible(self._item_button(product_name, "Remove"))
        return self

    @staticmethod
    def _item_button(product_name: str, label: str) -> Locator:
        # XPath because CSS cannot match text: find the card by product name, then its button.
        card = (
            '//*[@data-test="inventory-item"]'
            f'[.//*[@data-test="inventory-item-name"][normalize-space()="{product_name}"]]'
        )
        return (By.XPATH, f'{card}//button[normalize-space()="{label}"]')
