import pytest

from pages.login_page import LoginPage
from tests.data.users import LOCKED_OUT_USER, PASSWORD, PERFORMANCE_GLITCH_USER, STANDARD_USER

NO_MATCH = "Epic sadface: Username and password do not match any user in this service"


@pytest.mark.smoke
def test_standard_user_logs_in_and_sees_products(driver, base_url):
    inventory = LoginPage.open(driver, base_url).login_as(STANDARD_USER, PASSWORD)

    assert driver.current_url == f"{base_url}/inventory.html"
    assert inventory.title() == "Products"
    assert inventory.item_names()


# Decision table: username (valid / locked / unknown / empty) x password (right / wrong / empty).
# TC-LOGIN-01, the only accepted combination, is the test above. Rows left out are in TEST_PLAN.md.
@pytest.mark.parametrize(
    ("username", "password", "expected_error"),
    [
        pytest.param(
            LOCKED_OUT_USER,
            PASSWORD,
            "Epic sadface: Sorry, this user has been locked out.",
            id="TC-LOGIN-02-locked-out",
        ),
        pytest.param(STANDARD_USER, "wrong_password", NO_MATCH, id="TC-LOGIN-03-wrong-password"),
        pytest.param("unknown_user", PASSWORD, NO_MATCH, id="TC-LOGIN-04-unknown-user"),
        pytest.param(
            STANDARD_USER, "", "Epic sadface: Password is required", id="TC-LOGIN-05-empty-password"
        ),
        pytest.param(
            "", PASSWORD, "Epic sadface: Username is required", id="TC-LOGIN-06-empty-username"
        ),
        # Both empty: the username rule is checked first, so only its message shows.
        pytest.param("", "", "Epic sadface: Username is required", id="TC-LOGIN-07-both-empty"),
    ],
)
def test_login_is_rejected_and_stays_on_login(driver, base_url, username, password, expected_error):
    login = LoginPage.open(driver, base_url).login_expecting_error(username, password)

    assert login.error_message() == expected_error
    assert driver.current_url == f"{base_url}/"


def test_log_out_ends_the_session(driver, base_url, inventory_page):
    login = inventory_page.header.log_out()

    assert driver.current_url == f"{base_url}/"
    driver.get(f"{base_url}/inventory.html")
    assert (
        login.error_message()
        == "Epic sadface: You can only access '/inventory.html' when you are logged in."
    )


# This user's login takes about five seconds (seen while exploring the site). Only this flow gets
# a longer wait; raising the global timeout would slow down every failing test in the suite.
SLOW_USER_TIMEOUT = 20


def test_performance_glitch_user_gets_in_with_a_longer_wait(driver, base_url):
    inventory = LoginPage.open(driver, base_url).login_as(
        PERFORMANCE_GLITCH_USER, PASSWORD, timeout=SLOW_USER_TIMEOUT
    )

    assert inventory.title() == "Products"
