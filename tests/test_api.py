import unittest

from customer_api.api import CustomerAPI, _extract_customer_id
from customer_api.store import CustomerStore


class TestCustomerAPI(unittest.TestCase):
    def setUp(self):
        store = CustomerStore(
            [{"id": 1, "name": "A", "email": "a@example.com", "city": "X"}]
        )
        self.api = CustomerAPI(store=store)

    def test_extract_customer_id(self):
        self.assertEqual(1, _extract_customer_id("/customers/1"))
        self.assertIsNone(_extract_customer_id("/customers"))
        self.assertIsNone(_extract_customer_id("/customers/abc"))
        self.assertIsNone(_extract_customer_id("/customers/0"))
        self.assertEqual(1, _extract_customer_id("/customers/1/"))
        self.assertIsNone(_extract_customer_id("/customers/1/extra"))
        self.assertIsNone(_extract_customer_id("/customers/-1"))

    def test_list_customers(self):
        status, payload = self.api.list_customers()
        self.assertEqual(200, status)
        self.assertEqual(1, len(payload))

    def test_get_missing_customer(self):
        status, payload = self.api.get_customer(999)
        self.assertEqual(404, status)
        self.assertEqual("Customer not found", payload["error"])

    def test_create_customer_validation_failure(self):
        status, payload = self.api.create_customer({"name": "New"})
        self.assertEqual(400, status)
        self.assertIn("Missing required fields", payload["error"])

    def test_create_customer_success(self):
        status, payload = self.api.create_customer(
            {"name": "New", "email": "new@example.com", "city": "N"}
        )
        self.assertEqual(201, status)
        self.assertEqual(2, payload["id"])

    def test_update_customer_success(self):
        status, payload = self.api.update_customer(1, {"city": "Updated"})
        self.assertEqual(200, status)
        self.assertEqual("Updated", payload["city"])

    def test_update_customer_invalid_payload(self):
        status, payload = self.api.update_customer(1, {"city": ""})
        self.assertEqual(400, status)
        self.assertIn("non-empty string", payload["error"])

    def test_update_missing_customer(self):
        status, payload = self.api.update_customer(999, {"city": "Nowhere"})
        self.assertEqual(404, status)
        self.assertEqual("Customer not found", payload["error"])

    def test_delete_customer(self):
        status, payload = self.api.delete_customer(1)
        self.assertEqual(204, status)
        self.assertIsNone(payload)
        status_after_delete, _ = self.api.get_customer(1)
        self.assertEqual(404, status_after_delete)

    def test_delete_missing_customer(self):
        status, payload = self.api.delete_customer(999)
        self.assertEqual(404, status)
        self.assertEqual("Customer not found", payload["error"])


if __name__ == "__main__":
    unittest.main()
