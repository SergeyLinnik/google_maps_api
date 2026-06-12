# ============================================================================
# ИМПОРТ БИБЛИОТЕК
# ============================================================================

import requests
import json
import os
import time
from typing import Dict, Any, Optional, List



# ============================================================================
# КЛАСС ДЛЯ ТЕСТИРОВАНИЯ GOOGLE MAPS API
# ============================================================================

class TestGoogleMapsApi:
    """
    Класс для тестирования Google Maps API
    Каждый метод отвечает за одну задачу (принцип SOLID)
    """
    
    def __init__(self) -> None:
        """Инициализация базового URL и параметров API"""
        self.base_url: str = "https://rahulshettyacademy.com"
        self.api_key: str = "qaclick123"
        self.file_name: str = "place_ids.txt"
        self.timeout: int = 30
    
    def get_full_url_for_post(self) -> str:
        """Формирование URL для POST запроса (создание места)"""
        return f"{self.base_url}/maps/api/place/add/json?key={self.api_key}"
    
    def get_full_url_for_get(self, place_id: str) -> str:
        """
        Формирование URL для GET запроса (получение места)
        
        Args:
            place_id: Идентификатор места
        """
        return f"{self.base_url}/maps/api/place/get/json?key={self.api_key}&place_id={place_id}"
    
    def send_post_request(self, url: str, body: Dict[str, Any]) -> requests.Response:
        """Отправка POST запроса"""
        headers = {"Content-Type": "application/json"}
        return requests.post(url, json=body, headers=headers, timeout=self.timeout)
    
    def send_get_request(self, url: str) -> requests.Response:
        """Отправка GET запроса"""
        return requests.get(url, timeout=self.timeout)
    
    def create_place_body(self, lat: float, lng: float, name: str, address: str) -> Dict[str, Any]:
        """Создание тела запроса для создания места"""
        return {
            "location": {
                "lat": lat,
                "lng": lng
            },
            "accuracy": 50,
            "name": name,
            "phone_number": "(+91) 983 893 3937",
            "address": address,
            "types": ["shoe park", "shop"],
            "website": "http://google.com",
            "language": "French-IN"
        }
    
    def create_place(self, place_data: Dict[str, Any]) -> Optional[str]:
        """
        Отправка POST запроса для создания места
        
        Returns:
            place_id или None при ошибке
        """
        full_url: str = self.get_full_url_for_post()
        
        print(f"\n📡 Отправка POST запроса...")
        print(f"   URL: {full_url}")
        
        response = self.send_post_request(full_url, place_data)
        
        print(f"   Статус-код: {response.status_code}")
        
        if response.status_code == 200:
            response_json: Dict[str, Any] = response.json()
            
            if response_json.get("status") == "OK":
                place_id: str = response_json.get("place_id")
                print(f"   ✅ Место создано! place_id: {place_id}")
                return place_id
            else:
                print(f"   ❌ Ошибка: {response_json}")
                return None
        else:
            print(f"   ❌ Ошибка: статус-код {response.status_code}")
            return None
    
    def save_place_ids_to_file(self, place_ids: List[str]) -> None:
        """Сохранение place_id в текстовый файл"""
        with open(self.file_name, "w", encoding="utf-8") as file:
            for place_id in place_ids:
                file.write(place_id + "\n")
        
        print(f"\n💾 Сохранено {len(place_ids)} place_id в файл: {self.file_name}")
    
    def read_place_ids_from_file(self) -> List[str]:
        """Чтение place_id из текстового файла"""
        if not os.path.exists(self.file_name):
            print(f"\n❌ Файл {self.file_name} не найден!")
            return []
        
        with open(self.file_name, "r", encoding="utf-8") as file:
            place_ids = [line.strip() for line in file if line.strip()]
        
        print(f"\n📖 Прочитано {len(place_ids)} place_id из файла: {self.file_name}")
        return place_ids
    
    def get_place_details(self, place_id: str) -> Optional[Dict[str, Any]]:
        """
        Отправка GET запроса для получения данных о месте
        
        Args:
            place_id: Идентификатор места
        """
        full_url: str = self.get_full_url_for_get(place_id)
        
        print(f"\n📡 Отправка GET запроса...")
        print(f"   URL: {full_url}")
        
        try:
            response = self.send_get_request(full_url)
            print(f"   Статус-код: {response.status_code}")
            
            if response.status_code == 200:
                response_json: Dict[str, Any] = response.json()
                
                if "msg" not in response_json:
                    print(f"   ✅ Место найдено!")
                    print(f"   📍 Название: {response_json.get('name')}")
                    print(f"   📍 Адрес: {response_json.get('address')}")
                    return response_json
                else:
                    print(f"   ❌ Место не найдено: {response_json.get('msg')}")
                    return None
            else:
                print(f"   ❌ Ошибка: статус-код {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Таймаут подключения. Сервер не отвечает.")
            return None
        except requests.exceptions.ConnectionError:
            print(f"   🔌 Ошибка подключения. Проверьте интернет.")
            return None
    
    def verify_place_exists(self, place_id: str) -> bool:
        """Проверка существования места по place_id"""
        place_data = self.get_place_details(place_id)
        return place_data is not None
    
    def test_post_and_get_with_file(self) -> None:
        """
        ТЕСТ: POST (создание 5 мест) -> файл -> GET (проверка из файла)
        """
        
        print("\n" + "="*70)
        print(" ТЕСТ: GOOGLE MAPS API (POST + GET + ФАЙЛ)")
        print("="*70)
        
        # --------------------------------------------------------------------
        # ШАГ 1: Отправить метод POST (создать 5 мест)
        # --------------------------------------------------------------------
        print("\n[ШАГ 1] Отправка POST запросов для создания 5 мест...")
        
        place_ids: List[str] = []
        
        # Координаты для 5 разных мест
        locations: List[tuple] = [
            (-38.383494, 33.427362, "Frontline house", "29, side layout, cohen 09"),
            (-38.383495, 33.427363, "Backline house", "30, side layout, cohen 10"),
            (-38.383496, 33.427364, "Centerline house", "31, side layout, cohen 11"),
            (-38.383497, 33.427365, "Mainline house", "32, side layout, cohen 12"),
            (-38.383498, 33.427366, "Newline house", "33, side layout, cohen 13")
        ]
        
        for i, (lat, lng, name, address) in enumerate(locations, 1):
            print(f"\n   --- Создание места #{i} ---")
            place_body = self.create_place_body(lat, lng, name, address)
            place_id = self.create_place(place_body)
            
            if place_id:
                place_ids.append(place_id)
            else:
                print(f"   ⚠️ Не удалось создать место #{i}")
            
            # Небольшая задержка между запросами
            time.sleep(1)
        
        print(f"\n   ✅ Создано мест: {len(place_ids)} из 5")
        
        if len(place_ids) == 0:
            print("\n❌ ТЕСТ НЕ ПРОЙДЕН: Не удалось создать ни одного места")
            return
        
        # --------------------------------------------------------------------
        # ШАГ 2: Создать текстовый файл для хранения place_id
        # --------------------------------------------------------------------
        print("\n[ШАГ 2] Создание текстового файла для хранения place_id...")
        self.save_place_ids_to_file(place_ids)
        
        # --------------------------------------------------------------------
        # ШАГ 3: Отправить метод GET для чтения place_id из файла
        # --------------------------------------------------------------------
        print("\n[ШАГ 3] Чтение place_id из файла и проверка существования...")
        
        read_place_ids: List[str] = self.read_place_ids_from_file()
        
        if len(read_place_ids) == 0:
            print("\n❌ ТЕСТ НЕ ПРОЙДЕН: Файл пуст или не найден")
            return
        
        print("\n   Проверка существования мест...")
        
        verified_count: int = 0
        failed_count: int = 0
        
        for place_id in read_place_ids:
            print(f"\n   --- Проверка place_id: {place_id[:20]}... ---")
            if self.verify_place_exists(place_id):
                verified_count += 1
            else:
                failed_count += 1
            time.sleep(0.5)
        
        # --------------------------------------------------------------------
        # РЕЗУЛЬТАТЫ ТЕСТА
        # --------------------------------------------------------------------
        print("\n" + "="*70)
        print(" РЕЗУЛЬТАТЫ ТЕСТА")
        print("="*70)
        
        print(f"\n📊 Статистика:")
        print(f"   Создано мест: {len(place_ids)}")
        print(f"   Сохранено в файл: {len(read_place_ids)}")
        print(f"   ✅ Подтверждено существование: {verified_count}")
        print(f"   ❌ Не найдено: {failed_count}")
        
        if verified_count == len(read_place_ids) and verified_count > 0:
            print("\n✅ ТЕСТ ПРОЙДЕН УСПЕШНО!")
            print("   Все place_id из файла существуют")
        else:
            print("\n⚠️ ТЕСТ ПРОЙДЕН ЧАСТИЧНО")


if __name__ == "__main__":
    test_runner = TestGoogleMapsApi()
    test_runner.test_post_and_get_with_file()