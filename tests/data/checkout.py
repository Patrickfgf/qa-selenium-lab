from typing import NamedTuple


class Customer(NamedTuple):
    first_name: str
    last_name: str
    postal_code: str


CUSTOMER = Customer("Ana", "Lima", "70000-000")
