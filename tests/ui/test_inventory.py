import pytest
from selenium.common.exceptions import TimeoutException

from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from tests.data.users import ERROR_USER, PASSWORD, PROBLEM_USER


# Oracle independent of the app: Python's sorted() over what the page shows.
@pytest.mark.parametrize(
    ("option", "read_values", "descending"),
    [
        pytest.param("Name (A to Z)", InventoryPage.item_names, False, id="TC-SORT-01-name-asc"),
        pytest.param("Name (Z to A)", InventoryPage.item_names, True, id="TC-SORT-02-name-desc"),
        pytest.param(
            "Price (low to high)", InventoryPage.item_prices, False, id="TC-SORT-03-price-asc"
        ),
        pytest.param(
            "Price (high to low)", InventoryPage.item_prices, True, id="TC-SORT-04-price-desc"
        ),
    ],
)
def test_sort_orders_products(inventory_page, option, read_values, descending):
    names_before = sorted(inventory_page.item_names())

    inventory = inventory_page.sort_by(option)
    values = read_values(inventory)

    assert inventory.active_sort() == option
    assert values == sorted(values, reverse=descending)
    # Sorting must reorder the catalog, not drop or duplicate products.
    assert sorted(inventory.item_names()) == names_before


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-004: sorting as error_user opens a 'Sorting is broken!' alert and does not sort",
)
def test_error_user_sorts_without_an_error_alert(driver, base_url):
    inventory = LoginPage.open(driver, base_url).login_as(ERROR_USER, PASSWORD)

    inventory.sort_by("Name (Z to A)")

    assert inventory.accept_alert() is None


@pytest.mark.xfail(
    strict=True,
    raises=TimeoutException,
    reason="BUG-003: as problem_user, Add to cart does nothing for 4 of the 6 products",
)
def test_problem_user_adds_any_product_to_cart(driver, base_url):
    inventory = LoginPage.open(driver, base_url).login_as(PROBLEM_USER, PASSWORD)

    inventory.add_to_cart("Sauce Labs Bolt T-Shirt")

    assert inventory.header.cart_count() == 1
