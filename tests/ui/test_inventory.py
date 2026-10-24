import pytest

from pages.inventory_page import InventoryPage


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
