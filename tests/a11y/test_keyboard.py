import pytest
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver

from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from tests.data.users import PASSWORD, STANDARD_USER

pytestmark = pytest.mark.a11y

# Upper bound on Tab presses: the catalog has about two dozen focusable elements.
MAX_TAB_STOPS = 60


def press(driver: WebDriver, *keys: str) -> None:
    # ActionChains without a target element types into whatever has focus, like a real keyboard.
    ActionChains(driver).send_keys(*keys).perform()


def tab_stops(driver: WebDriver) -> list[str]:
    """Press Tab from the top of the page and name each element that gets focus, in order."""
    stops = []
    for _ in range(MAX_TAB_STOPS):
        press(driver, Keys.TAB)
        focused = driver.switch_to.active_element
        name = focused.get_attribute("data-test") or focused.get_attribute("id") or focused.tag_name
        # After the last element, Chrome moved focus to <body> on some runs and back to the first
        # element on others (seen while exploring); either way the page has been walked.
        if focused.tag_name == "body" or (stops and name == stops[0]):
            return stops
        stops.append(name)
    raise RuntimeError(f"Tab never came back around after {MAX_TAB_STOPS} presses: {stops}")


def test_login_works_with_the_keyboard_only(driver, base_url):
    LoginPage.open(driver, base_url)
    assert tab_stops(driver) == ["username", "password", "login-button"]

    LoginPage.open(driver, base_url)  # fresh page: focus starts at the top again
    press(driver, Keys.TAB, STANDARD_USER, Keys.TAB, PASSWORD, Keys.ENTER)

    assert InventoryPage(driver).title() == "Products"


def test_catalog_controls_are_reachable_with_the_keyboard(inventory_page):
    stops = tab_stops(inventory_page.driver)

    assert "react-burger-menu-btn" in stops
    assert "product-sort-container" in stops
    # One "Add to cart" button per product: every product can be bought without a mouse.
    add_buttons = [stop for stop in stops if stop.startswith("add-to-cart-")]
    assert len(add_buttons) == len(inventory_page.item_names())


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-006: the cart link never gets keyboard focus, so the cart needs a mouse",
)
def test_cart_link_is_reachable_with_the_keyboard(inventory_page):
    stops = tab_stops(inventory_page.driver)
    # A walk that missed the controls around the cart is broken, and proves nothing about BUG-006.
    # RuntimeError, not assert: an AssertionError here would be counted as the expected failure.
    if not {"react-burger-menu-btn", "product-sort-container"} <= set(stops):
        raise RuntimeError(f"the Tab walk did not cover the top of the catalog: {stops}")

    assert "shopping-cart-link" in stops
