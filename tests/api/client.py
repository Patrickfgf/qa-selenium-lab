from typing import Any

import requests

# Seconds per HTTP call: a server that hangs fails the test instead of hanging the CI job.
TIMEOUT = 10


class ServeRestClient:
    """Thin wrapper over requests: base URL, timeout and the Authorization header.

    It returns the raw Response on purpose, so each test asserts on status, headers and body.
    """

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.session = requests.Session()

    def get(self, path: str) -> requests.Response:
        return self.session.get(f"{self.base_url}{path}", timeout=TIMEOUT)

    def post(self, path: str, json: dict[str, Any], token: str | None = None) -> requests.Response:
        # ServeRest expects the token exactly as /login returns it ("Bearer <jwt>").
        headers = {"Authorization": token} if token else {}
        return self.session.post(
            f"{self.base_url}{path}", json=json, headers=headers, timeout=TIMEOUT
        )

    def delete(self, path: str, token: str | None = None) -> requests.Response:
        headers = {"Authorization": token} if token else {}
        return self.session.delete(f"{self.base_url}{path}", headers=headers, timeout=TIMEOUT)
