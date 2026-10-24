from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

TIMEOUT = 10

Locator = tuple[str, str]


class BasePage:
    """Explicit-wait helpers shared by page objects and page components."""

    def __init__(self, driver: WebDriver, timeout: float = TIMEOUT) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def _visible(self, locator: Locator) -> WebElement:
        return self.wait.until(EC.visibility_of_element_located(locator))

    def _click(self, locator: Locator) -> None:
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def _texts(self, locator: Locator) -> list[str]:
        return [element.text for element in self.driver.find_elements(*locator)]
