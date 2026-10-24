from decimal import Decimal

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_page import BasePage
from pages.checkout_complete_page import CheckoutCompletePage
from pages.prices import to_decimal


class CheckoutOverviewPage(BasePage):
    """Checkout step two: items, item total, tax and total before confirming."""

    SUMMARY = (By.CSS_SELECTOR, '[data-test="checkout-summary-container"]')
    ITEM_PRICES = (By.CSS_SELECTOR, '[data-test="inventory-item-price"]')
    SUBTOTAL = (By.CSS_SELECTOR, '[data-test="subtotal-label"]')
    TAX = (By.CSS_SELECTOR, '[data-test="tax-label"]')
    TOTAL = (By.CSS_SELECTOR, '[data-test="total-label"]')
    FINISH_BUTTON = (By.CSS_SELECTOR, '[data-test="finish"]')

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)
        self._visible(self.SUMMARY)

    def item_prices(self) -> list[Decimal]:
        return [to_decimal(text) for text in self._texts(self.ITEM_PRICES)]

    def subtotal(self) -> Decimal:
        return to_decimal(self.driver.find_element(*self.SUBTOTAL).text)

    def tax(self) -> Decimal:
        return to_decimal(self.driver.find_element(*self.TAX).text)

    def total(self) -> Decimal:
        return to_decimal(self.driver.find_element(*self.TOTAL).text)

    def finish(self) -> CheckoutCompletePage:
        self._click(self.FINISH_BUTTON)
        return CheckoutCompletePage(self.driver)
