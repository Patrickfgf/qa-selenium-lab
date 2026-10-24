import os
import re
from collections.abc import Iterator
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

BASE_URL = os.getenv("BASE_URL", "https://www.saucedemo.com")
ARTIFACTS_DIR = Path("screenshots")

phase_report_key = pytest.StashKey[dict[str, pytest.TestReport]]()


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


def _failed(item: pytest.Item) -> bool:
    reports = item.stash.get(phase_report_key, {})
    # Setup can fail after the browser is up (e.g. a fixture that logs in), so check both phases.
    return any(rep.failed for when, rep in reports.items() if when in ("setup", "call"))


def _save_failure_artifacts(drv: WebDriver, nodeid: str) -> None:
    ARTIFACTS_DIR.mkdir(exist_ok=True)
    name = re.sub(r"[^\w.-]+", "_", nodeid)
    drv.save_screenshot(str(ARTIFACTS_DIR / f"{name}.png"))
    # The DOM separates "locator broke" from "page came back different"; a screenshot can't.
    (ARTIFACTS_DIR / f"{name}.html").write_text(drv.page_source, encoding="utf-8")
