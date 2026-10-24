from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_page import TIMEOUT, BasePage
from pages.components.header import Header


class InventoryPage(BasePage):
    CONTAINER = (By.CSS_SELECTOR, '[data-test="inventory-container"]')
    TITLE = (By.CSS_SELECTOR, '[data-test="title"]')
    ITEM_NAMES = (By.CSS_SELECTOR, '[data-test="inventory-item-name"]')

    def __init__(self, driver: WebDriver, timeout: float = TIMEOUT) -> None:
        super().__init__(driver, timeout)
        # The URL changes before React renders the list, so the page is "loaded" when this shows.
        self._visible(self.CONTAINER)
        self.header = Header(driver)

    def title(self) -> str:
        return self.driver.find_element(*self.TITLE).text

    def item_names(self) -> list[str]:
        return self._texts(self.ITEM_NAMES)
