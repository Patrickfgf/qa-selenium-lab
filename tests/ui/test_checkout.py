import pytest

from tests.data.checkout import CUSTOMER

PRODUCTS = ["Sauce Labs Backpack", "Sauce Labs Bike Light"]
# Every product except the backpack: their prices add up to 99.95.
FIVE_PRODUCTS = [
    "Sauce Labs Bike Light",
    "Sauce Labs Bolt T-Shirt",
    "Sauce Labs Fleece Jacket",
    "Sauce Labs Onesie",
    "Test.allTheThings() T-Shirt (Red)",
]


@pytest.fixture
def checkout_info_page(inventory_page):
    inventory_page.add_to_cart("Sauce Labs Backpack")
    return inventory_page.header.open_cart().checkout()


@pytest.mark.smoke
def test_standard_user_buys_two_products(inventory_page):
    for product in PRODUCTS:
        inventory_page.add_to_cart(product)
    assert inventory_page.header.cart_count() == len(PRODUCTS)

    cart = inventory_page.header.open_cart()
    assert sorted(cart.item_names()) == sorted(PRODUCTS)

    overview = cart.checkout().continue_with(*CUSTOMER)
    # Oracle built from what the page shows: the item total adds up the listed prices and the
    # total adds the tax. The tax rate is not published anywhere, so the test does not assume one.
    assert overview.subtotal() == sum(overview.item_prices())
    assert overview.total() == overview.subtotal() + overview.tax()

    assert overview.finish().header_text() == "Thank you for your order!"


# Equivalence partitions per field: empty, whitespace only, filled. The form checks first name,
# then last name, then postal code, so each row leaves the next required field empty. The
# all-filled partition is the purchase test above.
@pytest.mark.parametrize(
    ("first_name", "last_name", "postal_code", "expected_error"),
    [
        pytest.param("", "", "", "Error: First Name is required", id="TC-CHK-01-all-empty"),
        pytest.param("Ana", "", "", "Error: Last Name is required", id="TC-CHK-02-no-last-name"),
        pytest.param(
            "Ana", "Lima", "", "Error: Postal Code is required", id="TC-CHK-03-no-postal-code"
        ),
        pytest.param(
            "   ",
            "   ",
            "   ",
            "Error: First Name is required",
            id="TC-CHK-04-whitespace-only",
            marks=pytest.mark.xfail(
                strict=True,
                raises=AssertionError,
                reason="BUG-001: whitespace-only fields are accepted, so no error ever shows",
            ),
        ),
    ],
)
def test_checkout_info_requires_each_field(
    checkout_info_page, first_name, last_name, postal_code, expected_error
):
    info = checkout_info_page.continue_expecting_error(first_name, last_name, postal_code)

    assert info.error_message() == expected_error


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-002: item total shows a float artifact ($99.94999999999999 instead of $99.95)",
)
def test_item_total_adds_up_five_products(inventory_page):
    for product in FIVE_PRODUCTS:
        inventory_page.add_to_cart(product)

    overview = inventory_page.header.open_cart().checkout().continue_with(*CUSTOMER)

    assert overview.subtotal() == sum(overview.item_prices())
