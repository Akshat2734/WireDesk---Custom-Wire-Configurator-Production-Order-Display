import os
from uuid import uuid4

import requests


class ApiError(RuntimeError):
    pass


class ApiClient:
    def __init__(self, base_url=None, timeout=10):
        self.base_url = (base_url or os.environ.get(
            "WIREDESK_API_URL", "http://localhost"
        )).rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.token = os.environ.get("WIREDESK_ACCESS_TOKEN")

    def _request(self, method, path, **kwargs):
        headers = kwargs.pop("headers", {})
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        try:
            response = self.session.request(
                method,
                f"{self.base_url}{path}",
                headers=headers,
                timeout=self.timeout,
                **kwargs,
            )
        except requests.RequestException as exc:
            raise ApiError(f"Cannot reach WireDesk server: {exc}") from exc

        if not response.ok:
            try:
                detail = response.json().get("error") or response.json().get("message")
            except (ValueError, AttributeError):
                detail = response.text
            raise ApiError(detail or f"Server returned HTTP {response.status_code}")
        return response.json() if response.content else None

    def register(self, username, email, password):
        return self._request(
            "POST", "/register",
            json={"username": username, "email": email, "password": password},
        )

    def sign_in(self, username, email, password=""):
        result = self._request(
            "POST", "/signin",
            json={"username": username, "email": email, "password": password},
        )
        self.token = result["access_token"]
        return result

    def get_orders(self, status=None):
        params = {"status": status} if status else None
        return self._request("GET", "/view_orders", params=params)

    def create_order(self, order):
        return self._request(
            "POST",
            "/create_order",
            json=order,
            headers={"X-Idempotency-Key": str(uuid4())},
        )

    def update_order_status(self, order_id, status):
        return self._request(
            "PATCH", f"/orders/{order_id}/status", json={"status": status}
        )
