import os
import re
import shutil
from collections.abc import Iterator
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

from pages.inventory_page import InventoryPage
from tests.data.users import STANDARD_USER

BASE_URL = os.getenv("BASE_URL", "https://www.saucedemo.com")
ARTIFACTS_DIR = Path("screenshots")

phase_report_key = pytest.StashKey[dict[str, pytest.TestReport]]()


def pytest_sessionstart(session: pytest.Session) -> None:
    # Evidence left by an earlier run would be mistaken for a failure of this one.
    shutil.rmtree(ARTIFACTS_DIR, ignore_errors=True)


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]):
    # Keep each phase's report on the test item so fixtures can read the outcome in teardown.
    report = yield
    item.stash.setdefault(phase_report_key, {})[report.when] = report
    return report


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL


@pytest.fixture
def driver(request: pytest.FixtureRequest) -> Iterator[WebDriver]:
    # A fresh browser per test: no cookie, cart or localStorage leaks from one test to the next.
    options = webdriver.ChromeOptions()
    if os.getenv("HEADLESS", "1") != "0":
        options.add_argument("--headless=new")
    # Fixed size so the layout (and any screenshot) is the same locally and on CI.
    options.add_argument("--window-size=1920,1080")
    # The demo password is on public breach lists; without this Chrome opens a
    # "change your password" dialog on top of the page after login.
    options.add_experimental_option(
        "prefs",
        {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.password_manager_leak_detection": False,
        },
    )
    drv = webdriver.Chrome(options=options)  # Selenium Manager resolves chromedriver
    yield drv
    try:
        if _failed(request.node):
            _save_failure_artifacts(drv, request.node.nodeid)
    finally:
        drv.quit()


@pytest.fixture
def inventory_page(driver: WebDriver, base_url: str) -> InventoryPage:
    # Back door instead of the login form: the site keeps the session in this cookie, so tests
    # that are not about login start already logged in. Login itself is covered in test_login.py.
    driver.get(base_url)  # a cookie can only be set for the domain that is open
    driver.add_cookie({"name": "session-username", "value": STANDARD_USER})
    driver.get(f"{base_url}/inventory.html")
    return InventoryPage(driver)


def _failed(item: pytest.Item) -> bool:
    reports = item.stash.get(phase_report_key, {})
    # Setup can fail after the browser is up (e.g. a fixture that logs in), so check both phases.
    # An xfail is a known bug failing as expected: its screenshot is the bug's evidence.
    return any(
        rep.failed or hasattr(rep, "wasxfail")
        for when, rep in reports.items()
        if when in ("setup", "call")
    )


def _save_failure_artifacts(drv: WebDriver, nodeid: str) -> None:
    ARTIFACTS_DIR.mkdir(exist_ok=True)
    name = re.sub(r"[^\w.-]+", "_", nodeid)
    drv.save_screenshot(str(ARTIFACTS_DIR / f"{name}.png"))
    # The DOM separates "locator broke" from "page came back different"; a screenshot can't.
    (ARTIFACTS_DIR / f"{name}.html").write_text(drv.page_source, encoding="utf-8")
