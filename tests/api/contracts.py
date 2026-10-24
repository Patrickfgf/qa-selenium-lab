import json
from pathlib import Path
from typing import Any

SCHEMAS_DIR = Path(__file__).parent / "schemas"


def schema(name: str) -> dict[str, Any]:
    """Load a JSON Schema from tests/api/schemas/ (written from the API's Swagger)."""
    return json.loads((SCHEMAS_DIR / f"{name}.json").read_text(encoding="utf-8"))
