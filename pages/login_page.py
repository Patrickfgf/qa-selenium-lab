from typing import Self

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_page import TIMEOUT, BasePage
from pages.inventory_page import InventoryPage


class LoginPage(BasePage):
    USERNAME = (By.CSS_SELECTOR, '[data-test="username"]')
    PASSWORD = (By.CSS_SELECTOR, '[data-test="password"]')
    LOGIN_BUTTON = (By.CSS_SELECTOR, '[data-test="login-button"]')
    ERROR = (By.CSS_SELECTOR, '[data-test="error"]')

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)
        self._visible(self.USERNAME)

    @classmethod
    def open(cls, driver: WebDriver, base_url: str) -> Self:
        driver.get(base_url)
        return cls(driver)

    def login_as(self, username: str, password: str, timeout: float = TIMEOUT) -> InventoryPage:
        self._submit(username, password)
        return InventoryPage(self.driver, timeout)

    def login_expecting_error(self, username: str, password: str) -> Self:
        self._submit(username, password)
        return self

    def error_message(self) -> str:
        return self._visible(self.ERROR).text

    def _submit(self, username: str, password: str) -> None:
        self.driver.find_element(*self.USERNAME).send_keys(username)
        self.driver.find_element(*self.PASSWORD).send_keys(password)
        self.driver.find_element(*self.LOGIN_BUTTON).click()
