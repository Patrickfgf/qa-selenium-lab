import pytest

from pages.login_page import LoginPage
from tests.a11y.axe import wcag_violations

BACKPACK = "Sauce Labs Backpack"

pytestmark = pytest.mark.a11y


def test_login_page_has_no_wcag_violations(driver, base_url, axe_source):
    LoginPage.open(driver, base_url)

    assert wcag_violations(driver, axe_source) == []


# Each step returns the next page object, and its constructor waits for the page to render, so
# axe never runs on a half-drawn page. The backpack goes in the cart so the next pages have content.
@pytest.mark.parametrize(
    "go_to",
    [
        pytest.param(lambda inventory: inventory, id="inventory"),
        pytest.param(
            lambda inventory: inventory.add_to_cart(BACKPACK).header.open_cart(), id="cart"
        ),
        pytest.param(
            lambda inventory: inventory.add_to_cart(BACKPACK).header.open_cart().checkout(),
            id="checkout-info",
        ),
    ],
)
def test_logged_in_page_has_no_wcag_violations(driver, inventory_page, axe_source, go_to):
    go_to(inventory_page)

    assert wcag_violations(driver, axe_source) == []
