"""In-memory data store for customer details."""

from copy import deepcopy
from threading import Lock


MOCK_CUSTOMERS = [
    {"id": 1, "name": "Alice Johnson", "email": "alice@example.com", "city": "Austin"},
    {"id": 2, "name": "Bob Smith", "email": "bob@example.com", "city": "Boston"},
]


class CustomerStore:
    """Simple thread-safe in-memory store for customer records."""

    def __init__(self, seed_data=None):
        records = seed_data if seed_data is not None else MOCK_CUSTOMERS
        self._lock = Lock()
        self._customers = {item["id"]: deepcopy(item) for item in records}

    def list_all(self):
        with self._lock:
            return [deepcopy(self._customers[key]) for key in sorted(self._customers)]

    def get(self, customer_id):
        with self._lock:
            customer = self._customers.get(customer_id)
            return deepcopy(customer) if customer else None

    def create(self, data):
        with self._lock:
            next_id = max(self._customers.keys(), default=0) + 1
            customer = {"id": next_id, **deepcopy(data)}
            self._customers[next_id] = customer
            return deepcopy(customer)

    def update(self, customer_id, data):
        with self._lock:
            current = self._customers.get(customer_id)
            if not current:
                return None
            current.update(deepcopy(data))
            return deepcopy(current)

    def delete(self, customer_id):
        with self._lock:
            if customer_id not in self._customers:
                return False
            del self._customers[customer_id]
            return True
