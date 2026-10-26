from pathlib import Path
from typing import Any

from selenium.webdriver.remote.webdriver import WebDriver

# Installed from package-lock.json with `npm ci`; the path is anchored to the repo root.
AXE_SCRIPT = Path(__file__).resolve().parents[2] / "node_modules" / "axe-core" / "axe.min.js"

# WCAG 2.0, 2.1 and 2.2 at levels A and AA. axe's "best-practice" rules are left out: they are
# advice, not conformance criteria, so they are noted in TEST_PLAN.md instead of failing the build.
WCAG_A_AA = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]

# axe.run returns a promise; execute_async_script passes a callback as the last argument.
_RUN_AXE = """
const done = arguments[arguments.length - 1];
axe.run(document, {runOnly: {type: "tag", values: arguments[0]}})
  .then(results => done(results.violations.map(v => ({
    rule: v.id,
    impact: v.impact,
    help: v.help,
    elements: v.nodes.map(node => node.target.join(" ")),
  }))))
  .catch(error => done({error: String(error)}));
"""


def wcag_violations(driver: WebDriver, axe_source: str) -> list[dict[str, Any]]:
    """Run axe-core's WCAG A/AA rules on the page that is open and return the violations."""
    driver.execute_script(axe_source)
    result = driver.execute_async_script(_RUN_AXE, WCAG_A_AA)
    if isinstance(result, dict):
        # axe crashing would otherwise look like a page with nothing to report.
        raise RuntimeError(f"axe-core did not run: {result['error']}")
    return result
