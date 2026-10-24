from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_page import BasePage


class CheckoutCompletePage(BasePage):
    CONTAINER = (By.CSS_SELECTOR, '[data-test="checkout-complete-container"]')
    HEADER = (By.CSS_SELECTOR, '[data-test="complete-header"]')

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)
        self._visible(self.CONTAINER)

    def header_text(self) -> str:
        return self.driver.find_element(*self.HEADER).text
