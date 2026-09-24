"""Обработка системных диалогов: разрешения, нативные alert, выбор APK.

Два уровня:
- грант без UI: auto_grant_runtime_permissions() выдаёт все RUNTIME-разрешения
  через `mobile: changePermissions` (Android) — диалоги вообще не появляются;
- закрытие UI: grant_permissions() тапает кнопки «Разрешить»/Allow у уже
  показанных диалогов (запасной путь, медленный).

Стратегии отличаются по платформам:
- Android: разрешения — `pm grant` или кнопки «Разрешить» по тексту,
  системные alert — через driver.switch_to.alert.
- iOS: нативные alert — driver.switch_to.alert (accept/dismiss).
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


def auto_grant_runtime_permissions(driver, package: str | None = None) -> bool:
    """Выдать приложению все RUNTIME-разрешения через Appium (pm grant).

    Использует мобильное расширение UiAutomator2 `mobile: changePermissions`
    с командным словом 'all' — Appium запрашивает manifest пакета и выдаёт
    каждое запрошенное разрешение командой `pm grant`. Работает даже когда
    приложение уже установлено и no_reset: true (в отличие от capability
    autoGrantPermissions, которая срабатывает только при установке APK или
    pm clear).

    Возвращает True, если грант выполнен (или нечего выдавать), False при
    ошибке расширения (не та платформа/драйвер). Не бросает исключений —
    используется на сессии-fixtурах, где падение хуже, чем отсутствие прав.
    """
    try:
        args: dict = {"permissions": "all", "action": "grant", "type": "pm"}
        if package:
            args["appPackage"] = package
        driver.execute_script("mobile: changePermissions", args)
        log.info("RUNTIME-разрешения выданы через mobile: changePermissions")
        return True
    except Exception as exc:  # noqa: BLE001
        log.warning("mobile: changePermissions недоступен: %s", exc)
        return False


class PermissionsHandler:
    """Закрывает системные диалоги (разрешения, alert, APK-installer)."""

    def __init__(self, driver):
        self.driver = driver

    # --- грант без UI (Android) ---
    def grant_runtime_permissions(self, package: str | None = None) -> bool:
        """Выдать все RUNTIME-разрешения без UI. См. auto_grant_runtime_permissions."""
        return auto_grant_runtime_permissions(self.driver, package)

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
