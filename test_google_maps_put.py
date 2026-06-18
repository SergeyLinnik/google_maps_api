# ============================================================================
# ИМПОРТ НЕОБХОДИМЫХ БИБЛИОТЕК
# ============================================================================

import requests
import json
import os
import time



# ============================================================================
# КЛАСС ДЛЯ РАБОТЫ С API (ПРИНЦИП SOLID - ЕДИНСТВЕННАЯ ОТВЕТСТВЕННОСТЬ)
# ============================================================================

class GoogleMapsApiClient:
    """
    Клиент для работы с Google Maps API.
    Каждый метод выполняет только одну задачу (SOLID).
    """

    def __init__(self) -> None:
        """Инициализация базовых параметров API"""
        self.base_url: str = "https://rahulshettyacademy.com"
        self.api_key: str = "qaclick123"
        self.timeout: int = 30

    # ------------------------------------------------------------------------
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ (ФОРМИРОВАНИЕ URL)
    # ------------------------------------------------------------------------

    def _get_post_url(self) -> str:
        """URL для POST /maps/api/place/add/json"""
        return f"{self.base_url}/maps/api/place/add/json?key={self.api_key}"

    def _get_get_url(self, place_id: str) -> str:
        """URL для GET /maps/api/place/get/json"""
        return f"{self.base_url}/maps/api/place/get/json?key={self.api_key}&place_id={place_id}"

    def _get_put_url(self) -> str:
        """URL для PUT /maps/api/place/update/json"""
        return f"{self.base_url}/maps/api/place/update/json?key={self.api_key}"

    # ------------------------------------------------------------------------
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ (ОТПРАВКА ЗАПРОСОВ)
    # ------------------------------------------------------------------------

    def _send_post(self, url: str, body: dict[str, any]) -> requests.Response:
        """Отправка POST запроса"""
        headers: dict[str, str] = {"Content-Type": "application/json"}
        return requests.post(url, json=body, headers=headers, timeout=self.timeout)

    def _send_get(self, url: str) -> requests.Response:
        """Отправка GET запроса"""
        return requests.get(url, timeout=self.timeout)

    def _send_put(self, url: str, body: dict[str, any]) -> requests.Response:
        """Отправка PUT запроса"""
        headers: dict[str, str] = {"Content-Type": "application/json"}
        return requests.put(url, json=body, headers=headers, timeout=self.timeout)

    # ------------------------------------------------------------------------
    # МЕТОД POST: СОЗДАНИЕ МЕСТА
    # ------------------------------------------------------------------------

    def create_place(self, lat: float, lng: float, name: str, address: str) -> str:
        """
        Создать новое место через POST запрос.
        Возвращает place_id.
        При ошибке – выбрасывает AssertionError.
        """
        body: dict[str, any] = {
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
        print(f"\n📡 POST запрос на создание места '{name}'")
        print(f"   URL: {url}")

        response: requests.Response = self._send_post(url, body)
        print(f"   Статус-код: {response.status_code}")

        # Проверка через assert (без if/else)
        assert response.status_code == 200, \
            f"Ожидался статус 200, получен {response.status_code}"

        resp_json: dict[str, any] = response.json()
        assert resp_json.get("status") == "OK", \
            f"Статус ответа не 'OK': {resp_json}"

        place_id: str = resp_json.get("place_id")
        assert place_id is not None, "В ответе отсутствует поле place_id"

        print(f"   ✅ Место создано! place_id: {place_id}")
        return place_id

    # ------------------------------------------------------------------------
    # МЕТОД GET: ПОЛУЧЕНИЕ ДАННЫХ О МЕСТЕ
    # ------------------------------------------------------------------------

    def get_place_details(self, place_id: str) -> dict[str, any]:
        """
        Получить данные о месте через GET запрос.
        Возвращает словарь с данными места.
        Если место не найдено – выбрасывает AssertionError.
        """
        url: str = self._get_get_url(place_id)
        print(f"\n📡 GET запрос для place_id: {place_id}")
        print(f"   URL: {url}")

        response: requests.Response = self._send_get(url)
        print(f"   Статус-код: {response.status_code}")

        assert response.status_code == 200, \
            f"GET вернул статус {response.status_code}"

        data: dict[str, any] = response.json()
        assert "msg" not in data, \
            f"Место не существует: {data.get('msg')}"

        print(f"   ✅ Место найдено, адрес: {data.get('address')}")
        return data

    # ------------------------------------------------------------------------
    # МЕТОД PUT: ОБНОВЛЕНИЕ АДРЕСА МЕСТА
    # ------------------------------------------------------------------------

    def update_place(self, place_id: str, new_address: str) -> dict[str, any]:
        """
        PUT запрос: обновление адреса существующего места.
        Возвращает ответ API.
        При ошибке – выбрасывает AssertionError.
        """
        url: str = self._get_put_url()
        body: dict[str, any] = {
            "place_id": place_id,
            "address": new_address,
            "key": self.api_key
        }

        print(f"\n📡 PUT запрос на обновление адреса")
        print(f"   URL: {url}")
        print(f"   Body: {json.dumps(body, indent=2)}")

        response: requests.Response = self._send_put(url, body)
        print(f"   Статус-код: {response.status_code}")

        assert response.status_code == 200, \
            f"PUT запрос вернул статус {response.status_code}"

        resp_json: dict[str, any] = response.json()
        assert "msg" in resp_json, \
            f"Ответ PUT не содержит 'msg': {resp_json}"
        assert "updated" in resp_json["msg"].lower(), \
            f"PUT не выполнен: {resp_json.get('msg')}"

        print(f"   ✅ PUT запрос выполнен успешно!")
        print(f"   Сообщение: {resp_json.get('msg')}")
        return resp_json

    def verify_address_updated(self, place_id: str, expected_address: str) -> bool:
        """
        Проверка через GET, что адрес был обновлён.
        Возвращает True если адрес совпадает, False если нет.
        """
        details: dict[str, any] = self.get_place_details(place_id)
        actual_address: str = details.get("address", "")

        print(f"\n   🔍 Проверка обновления адреса:")
        print(f"   Ожидаемый адрес: {expected_address}")
        print(f"   Фактический адрес: {actual_address}")

        return actual_address == expected_address



# ============================================================================
# КЛАСС ДЛЯ ТЕСТА (SOLID - ОТВЕЧАЕТ ЗА ПОСЛЕДОВАТЕЛЬНОСТЬ ШАГОВ)
# ============================================================================

class TestGoogleMapsPut:
    """
    Тест для PUT метода Google Maps API.
    Шаги:
    1. Создать место через POST
    2. Обновить адрес через PUT
    3. Проверить через GET, что адрес обновлён
    """

    def __init__(self) -> None:
        """Инициализация API клиента"""
        self.api: GoogleMapsApiClient = GoogleMapsApiClient()
        self.filename: str = "place_ids.txt"

    def save_place_id(self, place_id: str) -> None:
        """Сохранить place_id в файл"""
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write(place_id + "\n")
        print(f"\n💾 Сохранен place_id в файл '{self.filename}'")

    def read_place_id(self) -> str:
        """Прочитать place_id из файла"""
        assert os.path.exists(self.filename), \
            f"Файл {self.filename} не найден! Сначала создайте место."

        with open(self.filename, "r", encoding="utf-8") as f:
            place_id: str = f.readline().strip()

        assert place_id, "Файл пуст или не содержит place_id"
        print(f"\n📖 Прочитан place_id из файла: {place_id}")
        return place_id

    def run_test(self) -> None:
        """
        Запуск теста PUT метода.
        Шаги:
        1. Создать место через POST
        2. Обновить адрес через PUT
        3. Проверить через GET, что адрес обновлён
        """
        print("\n" + "="*70)
        print(" ТЕСТ: PUT МЕТОД (ОБНОВЛЕНИЕ АДРЕСА)")
        print("="*70)

        # --------------------------------------------------------------------
        # ШАГ 1: Создать место через POST
        # --------------------------------------------------------------------
        print("\n[ШАГ 1] Создание места через POST")

        lat: float = -38.383494
        lng: float = 33.427362
        name: str = "Frontline house"
        address: str = "29, side layout, cohen 09"

        place_id: str = self.api.create_place(lat, lng, name, address)
        self.save_place_id(place_id)

        # --------------------------------------------------------------------
        # ШАГ 2: Обновить адрес через PUT
        # --------------------------------------------------------------------
        print("\n[ШАГ 2] Обновление адреса через PUT")

        new_address: str = "100 Lenina street, RU"

        print(f"\n   place_id: {place_id}")
        print(f"   Новый адрес: {new_address}")

        put_response: dict[str, any] = self.api.update_place(place_id, new_address)

        assert put_response is not None, "PUT запрос не вернул ответ"
        print(f"\n   ✅ PUT запрос отработал верно!")

        # --------------------------------------------------------------------
        # ШАГ 3: Проверить через GET, что адрес обновлён
        # --------------------------------------------------------------------
        print("\n[ШАГ 3] Проверка через GET, что адрес обновлён")

        is_updated: bool = self.api.verify_address_updated(place_id, new_address)
        assert is_updated, f"Адрес не обновился! Ожидался: {new_address}"

        # --------------------------------------------------------------------
        # ИТОГ ТЕСТА
        # --------------------------------------------------------------------
        print("\n" + "="*70)
        print(" РЕЗУЛЬТАТЫ ТЕСТА")
        print("="*70)

        print(f"\n📊 СТАТИСТИКА:")
        print(f"   ✅ Место создано (POST): {place_id}")
        print(f"   ✅ Адрес обновлен (PUT): {new_address}")
        print(f"   ✅ Обновление подтверждено (GET)")

        print("\n" + "="*70)
        print("✅ ТЕСТ PUT ПРОЙДЕН УСПЕШНО!")
        print("="*70)



# ============================================================================
# ТОЧКА ВХОДА: СОЗДАНИЕ ЭКЗЕМПЛЯРА КЛАССА И ЗАПУСК ТЕСТА
# ============================================================================

if __name__ == "__main__":
    # Создание экземпляра класса
    test: TestGoogleMapsPut = TestGoogleMapsPut()

    # Вызов метода теста
    test.run_test()