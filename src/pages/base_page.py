"""Базовая страница Page Object Pattern."""
from __future__ import annotations

import logging

import allure

from src.driver.driver_wrapper import DriverWrapper
from src.pages.common_elements import CommonElements
from src.pages.page_context import PageContext


class BasePage:
    """Базовый класс для всех Page Object'ов.

    Получает мобильный контекст (driver, config, таймауты, общие элементы),
    а не «голый» driver — так страницы единообразно получают таймауты и
    кросс-экранные действия из common_elements.

    Содержит общие методы работы с элементами. Конкретные страницы
    описывают свои локаторы и шаги.
    """

    def __init__(self, ctx: PageContext):
        self.ctx = ctx
        self.driver: DriverWrapper = ctx.driver
        self.timeout = ctx.timeout
        self.logger = logging.getLogger(__name__)
        self.common: CommonElements = ctx.common

    # --- общие шаги ---
    @allure.step("Нажать элемент {locator}")
    def tap(self, locator: tuple):
        self.driver.tap(locator, timeout=self.timeout)

    @allure.step("Ввести текст в элемент {locator}")
    def type_text(self, locator: tuple, text: str):
        self.driver.type_text(locator, text, timeout=self.timeout)

    @allure.step("Получить текст элемента {locator}")
    def get_text(self, locator: tuple) -> str:
        return self.driver.get_text(locator, timeout=self.timeout)

    @allure.step("Проверить видимость элемента {locator}")
    def is_displayed(self, locator: tuple, timeout: int | None = None) -> bool:
        timeout = timeout if timeout is not None else min(self.timeout, 3)
        return self.driver.is_present(locator, timeout)

    @allure.step("Получить все элементы по локатору {locator}")
    def get_elements(self, locator: tuple, timeout: int | None = None) -> list:
        """Все элементы по локатору; сложные комбинированные локаторы, когда
        нужна коллекция (список карточек, позиционные поля внутри них)."""
        if timeout:
            self.driver.wait_present(locator, timeout)
        return self.driver.find_elements(locator)
