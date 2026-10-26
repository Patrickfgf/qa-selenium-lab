import os

import pytest

from tests.a11y.axe import AXE_SCRIPT


@pytest.fixture(scope="session")
def axe_source() -> str:
    if not AXE_SCRIPT.exists():
        message = f"axe-core is not installed at {AXE_SCRIPT}; install it with: npm ci"
        # Same rule as the API tests: a skip on CI would be lost coverage that nobody notices.
        if os.getenv("CI"):
            pytest.fail(message)
        pytest.skip(message)
    return AXE_SCRIPT.read_text(encoding="utf-8")
