from decimal import Decimal


def to_decimal(text: str) -> Decimal:
    """Read a price as shown on the page: "$29.99" or "Item total: $39.98".

    Decimal, not float: the tests add prices up, and float sums drift. Every catalog price
    except the backpack's adds up to 99.94999999999999 as floats and to 99.95 as Decimal.
    """
    return Decimal(text.rsplit("$", 1)[1])
