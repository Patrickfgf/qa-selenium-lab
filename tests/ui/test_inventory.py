import pytest
from selenium.common.exceptions import TimeoutException

from pages.inventory_page import InventoryPage
from tests.data.users import ERROR_USER, PROBLEM_USER


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


# The special users log in during setup: a failure there is reported as an error, and can never
# be mistaken for the expected failure of the known-bug tests below.
@pytest.fixture
def error_user_inventory(open_inventory_as):
    return open_inventory_as(ERROR_USER)


@pytest.fixture
def problem_user_inventory(open_inventory_as):
    return open_inventory_as(PROBLEM_USER)


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-004: sorting as error_user opens a 'Sorting is broken!' alert and does not sort",
)
def test_error_user_sorts_products_without_an_error(error_user_inventory):
    inventory = error_user_inventory.sort_by("Name (Z to A)")

    alert_text = inventory.accept_alert()
    names = inventory.item_names()

    assert alert_text is None
    assert names == sorted(names, reverse=True)


@pytest.mark.xfail(
    strict=True,
    raises=TimeoutException,
    reason="BUG-003: as problem_user, Add to cart never works for 3 of the 6 products",
)
def test_problem_user_adds_any_product_to_cart(problem_user_inventory):
    # add_to_cart waits for the button to turn into "Remove"; with the bug it never does.
    problem_user_inventory.add_to_cart("Sauce Labs Bolt T-Shirt")

    assert problem_user_inventory.header.cart_count() == 1
