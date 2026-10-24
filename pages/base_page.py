from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

TIMEOUT = 10
# Short on purpose: it is also how long a page that shows no alert makes the caller wait.
ALERT_TIMEOUT = 2

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

    def accept_alert(self, timeout: float = ALERT_TIMEOUT) -> str | None:
        """Accept a JavaScript alert if one opens within the timeout and return its text."""
        try:
            alert = WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
        except TimeoutException:
            return None
        text = alert.text
        alert.accept()
        return text
