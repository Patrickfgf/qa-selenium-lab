from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

TIMEOUT = 10


class InventoryPage:
    CONTAINER = (By.CSS_SELECTOR, '[data-test="inventory-container"]')
    TITLE = (By.CSS_SELECTOR, '[data-test="title"]')
    ITEM_NAMES = (By.CSS_SELECTOR, '[data-test="inventory-item-name"]')

    def __init__(self, driver: WebDriver, timeout: float = TIMEOUT) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)
        # The URL changes before React renders the list, so the page is "loaded" when this shows.
        self.wait.until(EC.visibility_of_element_located(self.CONTAINER))

    def title(self) -> str:
        return self.driver.find_element(*self.TITLE).text

    def item_names(self) -> list[str]:
        return [item.text for item in self.driver.find_elements(*self.ITEM_NAMES)]
