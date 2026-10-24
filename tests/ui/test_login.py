from pages.login_page import LoginPage
from tests.data.users import LOCKED_OUT_USER, PASSWORD, STANDARD_USER


def test_standard_user_logs_in_and_sees_products(driver, base_url):
    inventory = LoginPage.open(driver, base_url).login_as(STANDARD_USER, PASSWORD)

    assert driver.current_url == f"{base_url}/inventory.html"
    assert inventory.title() == "Products"
    assert inventory.item_names()


def test_locked_out_user_sees_error_and_stays_on_login(driver, base_url):
    login = LoginPage.open(driver, base_url).login_expecting_error(LOCKED_OUT_USER, PASSWORD)

    assert login.error_message() == "Epic sadface: Sorry, this user has been locked out."
    assert driver.current_url == f"{base_url}/"
