from typing import Self

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_page import BasePage
from pages.checkout_overview_page import CheckoutOverviewPage


class CheckoutInfoPage(BasePage):
    """Checkout step one: buyer's name and postal code."""

    FIRST_NAME = (By.CSS_SELECTOR, '[data-test="firstName"]')
    LAST_NAME = (By.CSS_SELECTOR, '[data-test="lastName"]')
    POSTAL_CODE = (By.CSS_SELECTOR, '[data-test="postalCode"]')
    CONTINUE_BUTTON = (By.CSS_SELECTOR, '[data-test="continue"]')
    ERROR = (By.CSS_SELECTOR, '[data-test="error"]')

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)
        self._visible(self.FIRST_NAME)

    def continue_with(
        self, first_name: str, last_name: str, postal_code: str
    ) -> CheckoutOverviewPage:
        self._submit(first_name, last_name, postal_code)
        return CheckoutOverviewPage(self.driver)

    def continue_expecting_error(self, first_name: str, last_name: str, postal_code: str) -> Self:
        self._submit(first_name, last_name, postal_code)
        return self

    def error_message(self) -> str | None:
        """Text of the error banner, or None if no error shows up within the timeout."""
        try:
            return self._visible(self.ERROR).text
        except TimeoutException:
            return None

    def _submit(self, first_name: str, last_name: str, postal_code: str) -> None:
        self.driver.find_element(*self.FIRST_NAME).send_keys(first_name)
        self.driver.find_element(*self.LAST_NAME).send_keys(last_name)
        self.driver.find_element(*self.POSTAL_CODE).send_keys(postal_code)
        self._click(self.CONTINUE_BUTTON)
