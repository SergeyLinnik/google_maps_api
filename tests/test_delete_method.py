# -*- coding: utf-8 -*-
"""
Тест DELETE метода Google Maps API.
Удаляет 2-й и 4-й place_id из файла, проверяет существование,
создает новый файл с 3 существующими локациями.
"""

from __future__ import annotations

import os
import time
import sys
import requests

# Добавляем путь к корню проекта для импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.google_maps_client import GoogleMapsApiClient


class TestDeleteMethod:
    """
    Тест для DELETE метода Google Maps API.
    Шаги:
    1. Удалить 2-й и 4-й place_id из файла через DELETE
    2. Проверить все place_id через GET (существующие/несуществующие)
    3. Создать новый файл с 3 существующими локациями
    """

    def __init__(self) -> None:
        """Инициализация API клиента"""
        self.api: GoogleMapsApiClient = GoogleMapsApiClient()
        self.input_file: str = "place_ids.txt"
        self.output_file: str = "existing_place_ids.txt"

    # ------------------------------------------------------------------------
    # РАБОТА С ФАЙЛАМИ
    # ------------------------------------------------------------------------

    def read_place_ids(self) -> list[str]:
        """
        Чтение place_id из текстового файла.

        Returns:
            Список place_id

        Raises:
            AssertionError: Если файл не найден или пуст
        """
        assert os.path.exists(self.input_file), \
            f"Файл {self.input_file} не найден! Сначала запустите тест создания мест."

        with open(self.input_file, "r", encoding="utf-8") as f:
            place_ids: list[str] = [line.strip() for line in f if line.strip()]

        assert place_ids, f"Файл {self.input_file} пуст"
        print(f"\n📖 Прочитано {len(place_ids)} place_id из файла: {self.input_file}")
        return place_ids

    def save_place_ids(self, place_ids: list[str], filename: str) -> None:
        """
        Сохранение place_id в текстовый файл.

        Args:
            place_ids: Список place_id
            filename: Имя файла
        """
        with open(filename, "w", encoding="utf-8") as f:
            for pid in place_ids:
                f.write(pid + "\n")
        print(f"\n💾 Сохранено {len(place_ids)} place_id в файл: {filename}")

    # ------------------------------------------------------------------------
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # ------------------------------------------------------------------------

    def print_separator(self, title: str) -> None:
        """Вывод разделителя с заголовком"""
        print("\n" + "="*70)
        print(f" {title}")
        print("="*70)

    # ------------------------------------------------------------------------
    # МЕТОД DELETE (БЕЗ TRY-EXCEPT)
    # ------------------------------------------------------------------------

    def delete_place_by_id(self, place_id: str, index: int) -> bool:
        """
        Удаление места по place_id через DELETE метод.

        Args:
            place_id: Идентификатор места
            index: Порядковый номер для вывода

        Returns:
            True если удаление успешно или место уже удалено, False если ошибка
        """
        print(f"\n   --- Удаление #{index} place_id: {place_id[:20]}... ---")

        url: str = f"{self.api.base_url}/maps/api/place/delete/json?key={self.api.api_key}"
        body: dict = {"place_id": place_id}

        print(f"   URL: {url}")

        response = requests.delete(url, json=body, headers={"Content-Type": "application/json"}, timeout=30)
        print(f"   Статус-код: {response.status_code}")

        # Если уже удален (404) - считаем успехом
        if response.status_code == 404:
            print(f"   ℹ️ Место уже было удалено ранее (404)")
            return True

        # Проверка через assert для остальных статусов
        assert response.status_code == 200, \
            f"DELETE вернул статус {response.status_code}"

        resp_json: dict = response.json()
        assert resp_json.get("status") == "OK", \
            f"DELETE не успешен: {resp_json}"

        print(f"   ✅ Место удалено!")
        return True

    # ------------------------------------------------------------------------
    # ОСНОВНОЙ ТЕСТ
    # ------------------------------------------------------------------------

    def test_delete_and_filter(self) -> None:
        """
        Запуск теста DELETE метода.
        Шаги:
        1. Удалить 2-й и 4-й place_id из файла через DELETE
        2. Проверить все place_id через GET (существующие/несуществующие)
        3. Создать новый файл с 3 существующими локациями
        """
        self.print_separator("ТЕСТ: DELETE МЕТОД И ФИЛЬТРАЦИЯ PLACE_ID")

        # --------------------------------------------------------------------
        # ШАГ 1: Чтение place_id из файла
        # --------------------------------------------------------------------
        print("\n[ШАГ 1] Чтение place_id из файла...")

        all_place_ids: list[str] = self.read_place_ids()

        print(f"\n   Все place_id ({len(all_place_ids)}):")
        for i, pid in enumerate(all_place_ids, 1):
            print(f"   {i}. {pid}")

        assert len(all_place_ids) >= 4, \
            f"Недостаточно place_id (нужно >=4), найдено {len(all_place_ids)}"

        # --------------------------------------------------------------------
        # ШАГ 2: Удаление 2-го и 4-го place_id через DELETE
        # --------------------------------------------------------------------
        self.print_separator("[ШАГ 2] Удаление 2-го и 4-го place_id через DELETE")

        indexes_to_delete: list[int] = [1, 3]
        deleted_count: int = 0

        for idx in indexes_to_delete:
            if idx < len(all_place_ids):
                place_id = all_place_ids[idx]
                success = self.delete_place_by_id(place_id, idx + 1)

                if success:
                    deleted_count += 1
                else:
                    print(f"   ⚠️ Не удалось удалить #{idx + 1} place_id")

                time.sleep(0.5)

        print(f"\n   ✅ Удалено мест: {deleted_count} из 2")

        # --------------------------------------------------------------------
        # ШАГ 3: Проверка всех place_id через GET
        # --------------------------------------------------------------------
        self.print_separator("[ШАГ 3] Проверка всех place_id через GET")

        existing_ids: list[str] = []
        non_existing_ids: list[str] = []

        print("\n   Результаты проверки:")

        for i, place_id in enumerate(all_place_ids, 1):
            print(f"\n   --- Проверка #{i}: {place_id[:20]}... ---")

            details = self.api.get_place_details(place_id)

            if details is not None:
                existing_ids.append(place_id)
                print(f"   ✅ Место СУЩЕСТВУЕТ")
            else:
                non_existing_ids.append(place_id)
                print(f"   ❌ Место НЕ СУЩЕСТВУЕТ")

            time.sleep(0.3)

        # --------------------------------------------------------------------
        # ШАГ 4: Создание нового файла с существующими локациями
        # --------------------------------------------------------------------
        self.print_separator("[ШАГ 4] Создание нового файла с существующими place_id")

        self.save_place_ids(existing_ids, self.output_file)

        # --------------------------------------------------------------------
        # РЕЗУЛЬТАТЫ ТЕСТА
        # --------------------------------------------------------------------
        self.print_separator("РЕЗУЛЬТАТЫ ТЕСТА")

        print(f"\n📊 СТАТИСТИКА:")
        print(f"   Всего place_id в исходном файле: {len(all_place_ids)}")
        print(f"   Удалено через DELETE: {len(indexes_to_delete)} (2-й и 4-й)")
        print(f"   ✅ Существующих мест после DELETE: {len(existing_ids)}")
        print(f"   ❌ Несуществующих мест после DELETE: {len(non_existing_ids)}")

        print(f"\n📁 ФАЙЛЫ:")
        print(f"   Исходный файл: {self.input_file}")
        print(f"   Новый файл: {self.output_file}")
        print(f"   Сохранено существующих place_id: {len(existing_ids)}")

        if existing_ids:
            print(f"\n📋 СУЩЕСТВУЮЩИЕ PLACE_ID (в новом файле):")
            for i, pid in enumerate(existing_ids, 1):
                print(f"   {i}. {pid}")

        if non_existing_ids:
            print(f"\n📋 НЕСУЩЕСТВУЮЩИЕ PLACE_ID (удаленные):")
            for i, pid in enumerate(non_existing_ids, 1):
                print(f"   {i}. {pid}")

        assert len(existing_ids) == 3, \
            f"Ожидалось 3 существующих места, получено: {len(existing_ids)}"

        print("\n" + "="*70)
        print("✅ ТЕСТ ПРОЙДЕН УСПЕШНО!")
        print("="*70)
        print(f"\n   Исходный файл содержит {len(all_place_ids)} place_id")
        print(f"   2-й и 4-й place_id удалены через DELETE")
        print(f"   GET запрос подтвердил: {len(existing_ids)} места существуют")
        print(f"   Новый файл создан с {len(existing_ids)} существующими place_id")


if __name__ == "__main__":
    test: TestDeleteMethod = TestDeleteMethod()
    test.test_delete_and_filter()