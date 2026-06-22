# -*- coding: utf-8 -*-
"""
Скрипт для создания 5 мест через POST запросы.
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.google_maps_client import GoogleMapsApiClient


def create_5_places() -> None:
    """Создание 5 мест и сохранение place_id в файл"""
    
    api = GoogleMapsApiClient()
    filename = "place_ids.txt"
    
    print("\n" + "="*70)
    print(" СОЗДАНИЕ 5 МЕСТ ДЛЯ ТЕСТА DELETE")
    print("="*70)
    
    locations = [
        (-38.383494, 33.427362, "Frontline house", "29, side layout, cohen 09"),
        (-38.383495, 33.427363, "Backline house", "30, side layout, cohen 10"),
        (-38.383496, 33.427364, "Centerline house", "31, side layout, cohen 11"),
        (-38.383497, 33.427365, "Mainline house", "32, side layout, cohen 12"),
        (-38.383498, 33.427366, "Newline house", "33, side layout, cohen 13"),
    ]
    
    place_ids = []
    
    for i, (lat, lng, name, address) in enumerate(locations, 1):
        print(f"\n--- Создание места #{i} ---")
        place_id = api.create_place(lat, lng, name, address)
        place_ids.append(place_id)
        time.sleep(0.5)
    
    # Сохраняем в файл
    with open(filename, "w", encoding="utf-8") as f:
        for pid in place_ids:
            f.write(pid + "\n")
    
    print(f"\n✅ СОЗДАНО 5 МЕСТ!")
    print(f"   place_id сохранены в файл: {filename}")
    for i, pid in enumerate(place_ids, 1):
        print(f"   {i}. {pid}")


if __name__ == "__main__":
    create_5_places()