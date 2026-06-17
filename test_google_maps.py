# ============================================================================
# ИМПОРТ НЕОБХОДИМЫХ БИБЛИОТЕК
# ============================================================================

import requests
import json
import os
import time

# ============================================================================
# ПРИМЕЧАНИЕ: Dict, List, Any НЕ ИМПОРТИРУЮТСЯ из typing
# Используются встроенные типы: dict, list
# ============================================================================



# ============================================================================
# КЛАСС ДЛЯ РАБОТЫ С API (ПРИНЦИП SOLID)
# ============================================================================

class GoogleMapsApiClient:
    """
    Клиент для работы с Google Maps API.
    Каждый метод выполняет только одну задачу.
    """

    def __init__(self) -> None:
        self.base_url: str = "https://rahulshettyacademy.com"
        self.api_key: str = "qaclick123"
        self.timeout: int = 30

    # ------------------------------------------------------------------------
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # ------------------------------------------------------------------------

    def _get_post_url(self) -> str:
        """URL для POST /maps/api/place/add/json"""
        return f"{self.base_url}/maps/api/place/add/json?key={self.api_key}"

    def _get_get_url(self, place_id: str) -> str:
        """URL для GET /maps/api/place/get/json"""
        return f"{self.base_url}/maps/api/place/get/json?key={self.api_key}&place_id={place_id}"

    def _send_post(self, url: str, body: dict) -> requests.Response:
        headers = {"Content-Type": "application/json"}
        return requests.post(url, json=body, headers=headers, timeout=self.timeout)

    def _send_get(self, url: str) -> requests.Response:
        return requests.get(url, timeout=self.timeout)

    # ------------------------------------------------------------------------
    # БИЗНЕС-МЕТОДЫ С ИСПОЛЬЗОВАНИЕМ assert
    # ------------------------------------------------------------------------

    def create_place(self, lat: float, lng: float, name: str, address: str) -> str:
        """
        Создать новое место через POST запрос.
        Возвращает place_id.
        При ошибке – выбрасывает AssertionError.
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
        url = self._get_post_url()
        print(f"\n📡 POST запрос на создание места '{name}'")
        print(f"   URL: {url}")
        response = self._send_post(url, body)
        print(f"   Статус-код: {response.status_code}")

        assert response.status_code == 200, \
            f"Ожидался статус 200, получен {response.status_code}"

        resp_json: dict = response.json()
        assert resp_json.get("status") == "OK", \
            f"Статус ответа не 'OK': {resp_json}"

        place_id: str = resp_json.get("place_id")
        assert place_id is not None, "В ответе отсутствует поле place_id"

        print(f"   ✅ Место создано! place_id: {place_id}")
        return place_id

    def get_place_details(self, place_id: str) -> dict:
        """
        Получить данные о месте через GET запрос.
        Возвращает словарь с данными места.
        Если место не найдено – выбрасывает AssertionError.
        """
        url = self._get_get_url(place_id)
        print(f"\n📡 GET запрос для place_id: {place_id}")
        print(f"   URL: {url}")
        response = self._send_get(url)
        print(f"   Статус-код: {response.status_code}")

        assert response.status_code == 200, \
            f"GET вернул статус {response.status_code}"

        data: dict = response.json()
        assert "msg" not in data, \
            f"Место не существует: {data.get('msg')}"

        print(f"   ✅ Место найдено, адрес: {data.get('address')}")
        return data



# ============================================================================
# КЛАСС ДЛЯ ТЕСТА (SOLID: отвечает за последовательность шагов)
# ============================================================================

class TestGoogleMapsPostGetFile:
    """
    Тест: POST 5 мест → сохранить place_id в файл → прочитать из файла → GET проверить
    """

    def __init__(self) -> None:
        self.api = GoogleMapsApiClient()
        self.filename: str = "place_ids.txt"

    def save_place_ids(self, ids: list) -> None:
        """
        Сохранить список place_id в текстовый файл.

        Args:
            ids: список place_id
        """
        with open(self.filename, "w", encoding="utf-8") as f:
            for pid in ids:
                f.write(pid + "\n")
        print(f"\n💾 Сохранено {len(ids)} place_id в файл '{self.filename}'")

    def read_place_ids(self) -> list:
        """
        Прочитать place_id из текстового файла.

        Returns:
            Список place_id

        Raises:
            AssertionError: если файл не найден
        """
        assert os.path.exists(self.filename), \
            f"Файл {self.filename} не найден! Сначала создайте места."
        with open(self.filename, "r", encoding="utf-8") as f:
            ids: list = [line.strip() for line in f if line.strip()]
        print(f"\n📖 Прочитано {len(ids)} place_id из файла '{self.filename}'")
        return ids

    def run_test(self) -> None:
        """Запуск полного теста: POST → файл → GET."""
        print("\n" + "="*70)
        print(" ТЕСТ: POST (5 мест) → файл → GET (проверка из файла)")
        print("="*70)

        # --------------------------------------------------------------------
        # ШАГ 1: Отправить 5 POST запросов (разные координаты)
        # --------------------------------------------------------------------
        print("\n[ШАГ 1] Создание 5 мест через POST")

        # Список кортежей: (широта, долгота, имя, адрес)
        locations: list = [
            (-38.383494, 33.427362, "Frontline house", "29, side layout, cohen 09"),
            (-38.383495, 33.427363, "Backline house",   "30, side layout, cohen 10"),
            (-38.383496, 33.427364, "Centerline house", "31, side layout, cohen 11"),
            (-38.383497, 33.427365, "Mainline house",   "32, side layout, cohen 12"),
            (-38.383498, 33.427366, "Newline house",    "33, side layout, cohen 13"),
        ]

        place_ids: list = []
        for i, (lat, lng, name, addr) in enumerate(locations, 1):
            print(f"\n--- Создание места #{i} ---")
            pid = self.api.create_place(lat, lng, name, addr)
            place_ids.append(pid)
            time.sleep(1)

        # --------------------------------------------------------------------
        # ШАГ 2: Сохранить все place_id в текстовый файл
        # --------------------------------------------------------------------
        print("\n[ШАГ 2] Сохранение place_id в файл")
        self.save_place_ids(place_ids)

        # --------------------------------------------------------------------
        # ШАГ 3: Прочитать place_id из файла и проверить через GET
        # --------------------------------------------------------------------
        print("\n[ШАГ 3] Чтение place_id из файла и проверка через GET")
        read_ids: list = self.read_place_ids()

        assert len(read_ids) == len(place_ids), \
            f"Количество прочитанных id ({len(read_ids)}) не совпадает с сохранёнными ({len(place_ids)})"

        for pid in read_ids:
            self.api.get_place_details(pid)
            time.sleep(0.5)

        # --------------------------------------------------------------------
        # ИТОГ
        # --------------------------------------------------------------------
        print("\n" + "="*70)
        print("✅ ТЕСТ ПРОЙДЕН УСПЕШНО!")
        print("="*70)
        print("   - 5 мест созданы через POST")
        print("   - place_id сохранены в файл")
        print("   - GET запрос из файла подтвердил существование всех мест")



# ============================================================================
# ТОЧКА ВХОДА: СОЗДАНИЕ ЭКЗЕМПЛЯРА КЛАССА И ЗАПУСК ТЕСТА
# ============================================================================

if __name__ == "__main__":
    test = TestGoogleMapsPostGetFile()
    test.run_test()
