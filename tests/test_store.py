import unittest

from customer_api.store import CustomerStore


class TestCustomerStore(unittest.TestCase):
    def setUp(self):
        self.store = CustomerStore(
            [
                {"id": 1, "name": "A", "email": "a@example.com", "city": "X"},
                {"id": 2, "name": "B", "email": "b@example.com", "city": "Y"},
            ]
        )

    def test_list_all_returns_seed_data(self):
        customers = self.store.list_all()
        self.assertEqual(2, len(customers))
        self.assertEqual("A", customers[0]["name"])

    def test_create_adds_customer_with_incremented_id(self):
        created = self.store.create(
            {"name": "C", "email": "c@example.com", "city": "Z"}
        )
        self.assertEqual(3, created["id"])
        self.assertEqual("C", self.store.get(3)["name"])

    def test_update_existing_customer(self):
        updated = self.store.update(1, {"city": "Updated"})
        self.assertIsNotNone(updated)
        self.assertEqual("Updated", updated["city"])

    def test_update_missing_customer_returns_none(self):
        self.assertIsNone(self.store.update(999, {"city": "Nowhere"}))

    def test_delete_existing_customer(self):
        self.assertTrue(self.store.delete(2))
        self.assertIsNone(self.store.get(2))

    def test_delete_missing_customer_returns_false(self):
        self.assertFalse(self.store.delete(999))


if __name__ == "__main__":
    unittest.main()
