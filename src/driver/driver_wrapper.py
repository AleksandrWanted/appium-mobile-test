"""Обёртка над driver: ожидания, скриншоты, перехват системных диалогов."""
from __future__ import annotations

import time
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

SCREENSHOT_DIR = Path("reports/screenshots")


class DriverWrapper:
    """Тонкая обёртка, добавляющая удобные методы ожидания и скриншоты."""

    def __init__(self, driver):
        self.driver = driver

    @property
    def raw(self):
        """Доступ к «голому» driver для редких случаев."""
        return self.driver

    # --- ожидания ---
    def wait_visible(self, locator: tuple, timeout: int = 10):
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )

    def wait_clickable(self, locator: tuple, timeout: int = 10):
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )

    def wait_present(self, locator: tuple, timeout: int = 10):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )

    def is_present(self, locator: tuple, timeout: int = 3) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except Exception:
            return False

    # --- действия ---
    def tap(self, locator: tuple):
        self.wait_clickable(locator).click()

    def type_text(self, locator: tuple, text: str, clear: bool = True):
        el = self.wait_visible(locator)
        if clear:
            el.clear()
        el.send_keys(text)

    def get_text(self, locator: tuple) -> str:
        return self.wait_visible(locator).text

    # --- скриншоты ---
    def screenshot(self, name: str | None = None) -> str:
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        name = name or f"scr_{int(time.time())}"
        path = SCREENSHOT_DIR / f"{name}.png"
        self.driver.save_screenshot(str(path))
        return str(path)
