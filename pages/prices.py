from decimal import Decimal


def to_decimal(text: str) -> Decimal:
    """Read a price as shown on the page: "$29.99" or "Item total: $39.98".

    Decimal, not float: the tests add prices up, and float sums drift. Added one by one as
    floats, every catalog price except the backpack's gives 99.94999999999999; as Decimal, 99.95.
    """
    return Decimal(text.rsplit("$", 1)[1])
