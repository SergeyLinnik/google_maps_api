# -*- coding: utf-8 -*-
"""
Business logic for Google Maps API.
Contains client class with all API methods (POST, GET, PUT).
"""

from __future__ import annotations

import json
import requests


class GoogleMapsApiClient:
    """
    Client for Google Maps API.
    Each method performs only one task (SOLID).
    """

    def __init__(self) -> None:
        """Initialize API base parameters"""
        self.base_url: str = "https://rahulshettyacademy.com"
        self.api_key: str = "qaclick123"
        self.timeout: int = 30

    def _get_post_url(self) -> str:
        """URL for POST /maps/api/place/add/json"""
        return f"{self.base_url}/maps/api/place/add/json?key={self.api_key}"

    def _get_get_url(self, place_id: str) -> str:
        """URL for GET /maps/api/place/get/json"""
        return f"{self.base_url}/maps/api/place/get/json?key={self.api_key}&place_id={place_id}"

    def _get_put_url(self) -> str:
        """URL for PUT /maps/api/place/update/json"""
        return f"{self.base_url}/maps/api/place/update/json?key={self.api_key}"

    def _send_post(self, url: str, body: dict) -> requests.Response:
        """Send POST request"""
        headers: dict = {"Content-Type": "application/json"}
        return requests.post(url, json=body, headers=headers, timeout=self.timeout)

    def _send_get(self, url: str) -> requests.Response:
        """Send GET request"""
        return requests.get(url, timeout=self.timeout)

    def _send_put(self, url: str, body: dict) -> requests.Response:
        """Send PUT request"""
        headers: dict = {"Content-Type": "application/json"}
        return requests.put(url, json=body, headers=headers, timeout=self.timeout)

    def create_place(self, lat: float, lng: float, name: str, address: str) -> str:
        """
        Create a new place via POST request.

        Args:
            lat: Latitude
            lng: Longitude
            name: Place name
            address: Place address

        Returns:
            place_id

        Raises:
            AssertionError: If request fails
        """
        body: dict = {
            "location": {"lat": lat, "lng": lng},
            "accuracy": 50,
            "name": name,
            "phone_number": "(+91) 983 893 3937",
            "address": address,
            "types": ["shoe park", "shop"],
            "website": "http://google.com",
            "language": "French-IN"
        }

        url: str = self._get_post_url()
        print(f"\n[POST] Creating place: {name}")
        print(f"   URL: {url}")

        response: requests.Response = self._send_post(url, body)
        print(f"   Status code: {response.status_code}")

        assert response.status_code == 200, \
            f"Expected status 200, got {response.status_code}"

        resp_json: dict = response.json()
        assert resp_json.get("status") == "OK", \
            f"Status is not 'OK': {resp_json}"

        place_id: str = resp_json.get("place_id")
        assert place_id is not None, "place_id not found in response"

        print(f"   [OK] Place created! place_id: {place_id}")
        return place_id

    def get_place_details(self, place_id: str) -> dict | None:
        """
        Get place details via GET request.

        Args:
            place_id: Place identifier

        Returns:
            Place data as dict or None if place does not exist
        """
        url: str = self._get_get_url(place_id)
        print(f"\n[GET] Getting place details for: {place_id}")
        print(f"   URL: {url}")

        response: requests.Response = self._send_get(url)
        print(f"   Status code: {response.status_code}")

        if response.status_code == 404:
            print(f"   [INFO] Place does not exist (404)")
            return None

        assert response.status_code == 200, \
            f"GET returned unexpected status {response.status_code}"

        data: dict = response.json()

        if "msg" in data:
            print(f"   [INFO] Place does not exist: {data.get('msg')}")
            return None

        print(f"   [OK] Place found, address: {data.get('address')}")
        return data

    def update_place(self, place_id: str, new_address: str) -> dict:
        """
        Update place address via PUT request.

        Args:
            place_id: Place identifier
            new_address: New address

        Returns:
            API response

        Raises:
            AssertionError: If update fails
        """
        url: str = self._get_put_url()
        body: dict = {
            "place_id": place_id,
            "address": new_address,
            "key": self.api_key
        }

        print(f"\n[PUT] Updating address")
        print(f"   URL: {url}")
        print(f"   Body: {json.dumps(body, indent=2)}")

        response: requests.Response = self._send_put(url, body)
        print(f"   Status code: {response.status_code}")

        assert response.status_code == 200, \
            f"PUT request returned status {response.status_code}"

        resp_json: dict = response.json()
        assert "msg" in resp_json, \
            f"PUT response missing 'msg': {resp_json}"
        assert "updated" in resp_json["msg"].lower(), \
            f"PUT failed: {resp_json.get('msg')}"

        print(f"   [OK] PUT request successful!")
        print(f"   Message: {resp_json.get('msg')}")
        return resp_json

    def verify_address_updated(self, place_id: str, expected_address: str) -> bool:
        """
        Verify that address was updated via GET request.

        Args:
            place_id: Place identifier
            expected_address: Expected address

        Returns:
            True if address matches, False otherwise
        """
        details: dict = self.get_place_details(place_id)
        if details is None:
            return False
        actual_address: str = details.get("address", "")

        print(f"\n   [CHECK] Address update verification:")
        print(f"   Expected address: {expected_address}")
        print(f"   Actual address: {actual_address}")

        return actual_address == expected_address