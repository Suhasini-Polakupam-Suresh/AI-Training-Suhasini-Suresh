# AI-Training-Suhasini-Suresh

## Customer CRUD API (Mock Data)

This repository contains a simple CRUD API for customer details using in-project mock data.

### Project Structure

- `customer_api/store.py`: In-memory customer data store
- `customer_api/api.py`: CRUD business logic and HTTP request handlers
- `tests/test_store.py`: Unit tests for store operations
- `tests/test_api.py`: Unit tests for API behaviors and validation

### Run the API

```bash
python -m customer_api.api
```

Server starts at `http://127.0.0.1:8000`.

### API Endpoints

- `GET /customers` - List all customers
- `GET /customers/{id}` - Get customer by ID
- `POST /customers` - Create customer
- `PUT /customers/{id}` - Update customer
- `DELETE /customers/{id}` - Delete customer

### Sample Request Body

```json
{
  "name": "Charlie",
  "email": "charlie@example.com",
  "city": "Chicago"
}
```

### Run Unit Tests

```bash
python -m unittest discover -s tests -v
```
