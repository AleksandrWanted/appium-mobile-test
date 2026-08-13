"""Обработка системных диалогов: разрешения, нативные alert, выбор APK.

Стратегии отличаются по платформам:
- Android: разрешения — кнопки «Разрешить» по тексту/ресурс-id,
  системные alert — через driver.switch_to.alert.
- iOS: нативные alert — driver.switch_to.alert (accept/dismiss).

Универсальный grant_permissions() пытается закрыть все всплывающие
системные окна, не падая, если их нет.
"""
from __future__ import annotations

import logging

from appium.webdriver.common.appiumby import AppiumBy

log = logging.getLogger(__name__)

# Возможные надписи кнопок согласия на разных языках/платформах
ALLOW_TEXTS = (
    "Allow", "Allow while using the app", "Allow only while using the app",
    "Always Allow", "Разрешить", "Разрешить во время использования",
    "ALLOW", "OK", "ОК",
)
WHILE_USING_TEXTS = ("While using the app", "Только во время использования")


class PermissionsHandler:
    """Закрывает системные диалоги (разрешения, alert, APK-installer)."""

    def __init__(self, driver):
        self.driver = driver

    # --- нативные alert (iOS + часть Android) ---
    def accept_alert(self) -> bool:
        """Принимает системный alert, если он есть. Возвращает True при успехе."""
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
            log.info("Системный alert принят")
            return True
        except Exception:
            return False

    def dismiss_alert(self) -> bool:
        try:
            alert = self.driver.switch_to.alert
            alert.dismiss()
            return True
        except Exception:
            return False

    # --- кнопки разрешений по тексту ---
    def _tap_by_visible_text(self, texts: tuple[str, ...], timeout: int = 2) -> bool:
        """Ищет и нажимает первую видимую кнопку по одному из текстов."""
        for text in texts:
            # Android UIAutomator: поиск по тексту
            android_locator = (
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiSelector().text("{text}")',
            )
            if self._try_tap(android_locator, timeout):
                log.info("Нажата кнопка системного диалога: %s", text)
                return True
            # iOS / общий — accessibility id по тексту
            ios_locator = (AppiumBy.ACCESSIBILITY_ID, text)
            if self._try_tap(ios_locator, timeout):
                log.info("Нажата кнопка системного диалога: %s", text)
                return True
        return False

    def _try_tap(self, locator: tuple, timeout: int) -> bool:
        try:
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.support.ui import WebDriverWait

            el = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            el.click()
            return True
        except Exception:
            return False

    # --- публичный API ---
    def grant_permissions(self, max_attempts: int = 5) -> None:
        """Циклически закрывает всплывающие системные диалоги.

        Диалоги могут идти подряд (камера → геолокация → уведомления),
        поэтому обрабатываем в цикле, пока не перестанут появляться.
        """
        for attempt in range(max_attempts):
            handled = (
                self._tap_by_visible_text(WHILE_USING_TEXTS)
                or self._tap_by_visible_text(ALLOW_TEXTS)
                or self.accept_alert()
            )
            if not handled:
                break
            log.info("Системный диалог закрыт (попытка %d)", attempt + 1)

    def dismiss_apk_installer(self) -> None:
        """Закрывает системный установщик APK ('Установить' / 'Install')."""
        self._tap_by_visible_text(("Install", "Установить", "Done", "Готово"))
