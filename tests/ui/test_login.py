# Raw Selenium on purpose: the next step moves these steps into Page Objects,
# and the git history keeps the before/after.
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

PASSWORD = "secret_sauce"
TIMEOUT = 10


def test_standard_user_logs_in_and_sees_products(driver, base_url):
    wait = WebDriverWait(driver, TIMEOUT)
    driver.get(base_url)
    username = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-test="username"]'))
    )
    username.send_keys("standard_user")
    driver.find_element(By.CSS_SELECTOR, '[data-test="password"]').send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, '[data-test="login-button"]').click()

    # The URL changes before React finishes rendering, so wait on the page content, not the route.
    title = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-test="title"]')))
    assert driver.current_url == f"{base_url}/inventory.html"
    assert title.text == "Products"
    assert driver.find_elements(By.CSS_SELECTOR, '[data-test="inventory-item"]')


def test_locked_out_user_sees_error_and_stays_on_login(driver, base_url):
    wait = WebDriverWait(driver, TIMEOUT)
    driver.get(base_url)
    username = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-test="username"]'))
    )
    username.send_keys("locked_out_user")
    driver.find_element(By.CSS_SELECTOR, '[data-test="password"]').send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, '[data-test="login-button"]').click()

    error = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-test="error"]')))
    assert error.text == "Epic sadface: Sorry, this user has been locked out."
    assert driver.current_url == f"{base_url}/"
