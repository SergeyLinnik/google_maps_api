# -*- coding: utf-8 -*-
"""
Tests for Google Maps API PUT method.
"""

from __future__ import annotations

import os

from src.google_maps_client import GoogleMapsApiClient


class TestGoogleMapsPut:
    """
    Test for Google Maps API PUT method.
    Steps:
    1. Create a place via POST
    2. Update address via PUT
    3. Verify via GET that address was updated
    """

    def __init__(self) -> None:
        """Initialize API client"""
        self.api: GoogleMapsApiClient = GoogleMapsApiClient()
        self.filename: str = "place_ids.txt"

    def save_place_id(self, place_id: str) -> None:
        """Save place_id to file"""
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write(place_id + "\n")
        print(f"\n[FILE] Saved place_id to: {self.filename}")

    def read_place_id(self) -> str:
        """Read place_id from file"""
        assert os.path.exists(self.filename), \
            f"File {self.filename} not found! Please create a place first."

        with open(self.filename, "r", encoding="utf-8") as f:
            place_id: str = f.readline().strip()

        assert place_id, "File is empty or contains no place_id"
        print(f"\n[FILE] Read place_id from file: {place_id}")
        return place_id

    def run_test(self) -> None:
        """
        Run PUT method test.
        Steps:
        1. Create a place via POST
        2. Update address via PUT
        3. Verify via GET that address was updated
        """
        print("\n" + "="*70)
        print(" TEST: PUT METHOD (UPDATE ADDRESS)")
        print("="*70)

        # --------------------------------------------------------------------
        # STEP 1: Create a place via POST
        # --------------------------------------------------------------------
        print("\n[STEP 1] Creating a place via POST")

        lat: float = -38.383494
        lng: float = 33.427362
        name: str = "Frontline house"
        address: str = "29, side layout, cohen 09"

        place_id: str = self.api.create_place(lat, lng, name, address)
        self.save_place_id(place_id)

        # --------------------------------------------------------------------
        # STEP 2: Update address via PUT
        # --------------------------------------------------------------------
        print("\n[STEP 2] Updating address via PUT")

        new_address: str = "100 Lenina street, RU"

        print(f"\n   place_id: {place_id}")
        print(f"   New address: {new_address}")

        put_response: dict = self.api.update_place(place_id, new_address)

        # CHECK: PUT worked correctly
        assert put_response is not None, "PUT request did not return a response"
        print(f"\n   [OK] PUT request completed successfully!")

        # --------------------------------------------------------------------
        # STEP 3: Verify via GET that address was updated
        # --------------------------------------------------------------------
        print("\n[STEP 3] Verifying via GET that address was updated")

        is_updated: bool = self.api.verify_address_updated(place_id, new_address)
        assert is_updated, f"Address was not updated! Expected: {new_address}"

        # --------------------------------------------------------------------
        # TEST RESULTS
        # --------------------------------------------------------------------
        print("\n" + "="*70)
        print(" TEST RESULTS")
        print("="*70)

        print(f"\n[STATISTICS]:")
        print(f"   [OK] Place created (POST): {place_id}")
        print(f"   [OK] Address updated (PUT): {new_address}")
        print(f"   [OK] Update verified (GET)")

        print("\n" + "="*70)
        print("[OK] PUT TEST PASSED SUCCESSFULLY!")
        print("="*70)


if __name__ == "__main__":
    test: TestGoogleMapsPut = TestGoogleMapsPut()
    test.run_test()