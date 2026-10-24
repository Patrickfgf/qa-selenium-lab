from tests.data.checkout import CUSTOMER

PRODUCTS = ["Sauce Labs Backpack", "Sauce Labs Bike Light"]


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
