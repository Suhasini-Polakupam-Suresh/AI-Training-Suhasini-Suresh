"""HTTP API implementation for customer CRUD."""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from customer_api.store import CustomerStore


def _extract_customer_id(path):
    parts = [part for part in path.split("/") if part]
    if len(parts) == 2 and parts[0] == "customers" and parts[1].isdigit():
        return int(parts[1])
    return None


def _validate_payload(payload, partial=False):
    required_fields = ("name", "email", "city")
    if not isinstance(payload, dict):
        return False, "Payload must be a JSON object"

    if not partial:
        missing = [field for field in required_fields if field not in payload]
        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"

    for field in required_fields:
        if field in payload:
            value = payload[field]
            if not isinstance(value, str) or not value.strip():
                return False, f"Field '{field}' must be a non-empty string"

    return True, None


class CustomerAPI:
    """Business operations for customer endpoints."""

    def __init__(self, store=None):
        self.store = store or CustomerStore()

    def list_customers(self):
        return 200, self.store.list_all()

    def get_customer(self, customer_id):
        customer = self.store.get(customer_id)
        if not customer:
            return 404, {"error": "Customer not found"}
        return 200, customer

    def create_customer(self, payload):
        ok, err = _validate_payload(payload, partial=False)
        if not ok:
            return 400, {"error": err}
        return 201, self.store.create(payload)

    def update_customer(self, customer_id, payload):
        ok, err = _validate_payload(payload, partial=True)
        if not ok:
            return 400, {"error": err}
        updated = self.store.update(customer_id, payload)
        if not updated:
            return 404, {"error": "Customer not found"}
        return 200, updated

    def delete_customer(self, customer_id):
        deleted = self.store.delete(customer_id)
        if not deleted:
            return 404, {"error": "Customer not found"}
        return 204, None


class CustomerRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler exposing customer CRUD routes."""

    api = None

    def _api(self):
        return self.__class__.api

    def _send_json(self, status, payload):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if payload is not None:
            self.wfile.write(json.dumps(payload).encode("utf-8"))

    def _read_json_payload(self):
        content_length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return None

    def do_GET(self):
        if self.path == "/customers":
            status, payload = self._api().list_customers()
            return self._send_json(status, payload)

        customer_id = _extract_customer_id(self.path)
        if customer_id is not None:
            status, payload = self._api().get_customer(customer_id)
            return self._send_json(status, payload)

        self._send_json(404, {"error": "Route not found"})

    def do_POST(self):
        if self.path != "/customers":
            return self._send_json(404, {"error": "Route not found"})

        payload = self._read_json_payload()
        if payload is None:
            return self._send_json(400, {"error": "Invalid JSON payload"})

        status, response = self._api().create_customer(payload)
        self._send_json(status, response)

    def do_PUT(self):
        customer_id = _extract_customer_id(self.path)
        if customer_id is None:
            return self._send_json(404, {"error": "Route not found"})

        payload = self._read_json_payload()
        if payload is None:
            return self._send_json(400, {"error": "Invalid JSON payload"})

        status, response = self._api().update_customer(customer_id, payload)
        self._send_json(status, response)

    def do_DELETE(self):
        customer_id = _extract_customer_id(self.path)
        if customer_id is None:
            return self._send_json(404, {"error": "Route not found"})

        status, response = self._api().delete_customer(customer_id)
        self._send_json(status, response)


def run_server(host="127.0.0.1", port=8000, api=None):
    configured_api = api or CustomerAPI()

    class _ConfiguredHandler(CustomerRequestHandler):
        api = configured_api

    server = HTTPServer((host, port), _ConfiguredHandler)
    print(f"Server running on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
