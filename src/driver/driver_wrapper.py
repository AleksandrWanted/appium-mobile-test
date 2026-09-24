"""Обёртка над driver: ожидания, скриншоты, перехват системных диалогов."""
from __future__ import annotations

import time
from pathlib import Path

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

SCREENSHOT_DIR = Path("reports/screenshots")


class DriverWrapper:
    """Тонкая обёртка, добавляющая удобные методы ожидания и скриншоты."""

    def __init__(self, driver, timeout: int = 10):
        self.driver = driver
        self.timeout = timeout

    @property
    def raw(self):
        """Доступ к «голому» driver для редких случаев."""
        return self.driver

    # --- ожидания ---
    def wait_visible(self, locator: tuple, timeout: int | None = None):
        return WebDriverWait(self.driver, timeout or self.timeout).until(
            EC.visibility_of_element_located(locator)
        )

    def wait_clickable(self, locator: tuple, timeout: int | None = None):
        return WebDriverWait(self.driver, timeout or self.timeout).until(
            EC.element_to_be_clickable(locator)
        )

    def wait_present(self, locator: tuple, timeout: int | None = None):
        return WebDriverWait(self.driver, timeout or self.timeout).until(
            EC.presence_of_element_located(locator)
        )

    def is_present(self, locator: tuple, timeout: int | None = None) -> bool:
        try:
            WebDriverWait(self.driver, timeout or self.timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except Exception:
            return False

    # --- действия ---
    def tap(self, locator: tuple, timeout: int | None = None):
        self.wait_clickable(locator, timeout).click()

    def tap_element(self, element, timeout: int | None = None):
        """Клик по уже найденному элементу (например, карточке из списка)."""
        element.click()

    def type_text(self, locator: tuple, text: str, clear: bool = True, timeout: int | None = None):
        el = self.wait_visible(locator, timeout)
        if clear:
            el.clear()
        el.send_keys(text)

    def get_text(self, locator: tuple, timeout: int | None = None) -> str:
        return self.wait_visible(locator, timeout).text

    def find_elements(self, locator: tuple) -> list:
        """Найти все элементы по локатору; без ожидания, пусто → пустой список."""
        return self.raw.find_elements(*locator)

    def scroll_to(self, end_locator: tuple, timeout: int | None = None):
        """Прокрутить scrollable-контейнер до элемента и вернуть его.

        Реализация через UiScrollable (вниз до 50 экранов) — appium_gesture
        scroll_to_element недоступен через python-клиент, а uiScrollable
        локатор работает и внутри page objects, и в тестах.
        """
        timeout = timeout or self.timeout
        end_by, end_value = end_locator
        inner = f'new UiSelector().{self._ui_selector(end_by, end_value)}'
        ui = (AppiumBy.ANDROID_UIAUTOMATOR, (
            'new UiScrollable(new UiSelector().scrollable(true))'
            f'.scrollIntoView({inner})'
        ))
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(ui)
        )

    @staticmethod
    def _ui_selector(by: str, value: str) -> str:
        """Перевод (by, value) в выражение UiSelector для UiScrollable."""
        if by == AppiumBy.ID:
            escaped = value.replace('"', '\\"')
            return f'resourceId("{escaped}")'
        if by == AppiumBy.ACCESSIBILITY_ID:
            escaped = value.replace('"', '\\"')
            return f'description("{escaped}")'
        if by == AppiumBy.ANDROID_UIAUTOMATOR:
            stripped = value.strip()
            prefix = "new UiSelector()."
            if stripped.startswith(prefix):
                return stripped[len(prefix):]
        raise ValueError(f"Локатор не поддерживается scroll_to: ({by}, {value})")

    # --- скриншоты ---
    def screenshot(self, name: str | None = None) -> str:
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        name = name or f"scr_{int(time.time())}"
        path = SCREENSHOT_DIR / f"{name}.png"
        self.driver.save_screenshot(str(path))
        return str(path)
