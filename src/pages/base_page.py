"""Базовая страница Page Object Pattern."""
from __future__ import annotations

import allure

from src.driver.driver_wrapper import DriverWrapper


class BasePage:
    """Базовый класс для всех Page Object'ов.

    Содержит общие методы работы с элементами. Конкретные страницы
    описывают свои локаторы и шаги.
    """

    def __init__(self, driver: DriverWrapper):
        self.driver = driver

    @allure.step("Нажать элемент {locator}")
    def tap(self, locator: tuple):
        self.driver.tap(locator)

    @allure.step("Ввести текст в элемент {locator}")
    def type_text(self, locator: tuple, text: str):
        self.driver.type_text(locator, text)

    @allure.step("Получить текст элемента {locator}")
    def get_text(self, locator: tuple) -> str:
        return self.driver.get_text(locator)

    @allure.step("Проверить видимость элемента {locator}")
    def is_displayed(self, locator: tuple, timeout: int = 3) -> bool:
        return self.driver.is_present(locator, timeout)
