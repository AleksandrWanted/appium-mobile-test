"""Дымовой тест: после старта сессии процесс приложения жив.

Приложение «МТС Optimus» — release-сборка с Play Integrity: на эмуляторе
проверка не проходит, splash закрывается и UI не появляется. Поэтому
прохождение сплэша ожидаем best-effort (по таймауту), а твёрдая проверка
запуска — живой процесс приложения (mobile: queryAppState: 0=не установлено,
1=не запущено, 2=фон suspended, 3=фон running, 4=foreground).
"""
from __future__ import annotations

import time

import allure
import pytest

# Splash-активность приложения: сплэш пройден, когда в фокусе уже другая активность.
SPLASH_ACTIVITY = "SplashActivity"
SPLASH_WAIT_TIMEOUT = 10  # сколько секунд ждать прохождения сплэша
SPLASH_POLL_INTERVAL = 1

# Состояния queryAppState, при которых приложение считается запущенным.
RUNNING_STATES = {2, 3, 4}


def _focused_activity(driver) -> tuple[str, str]:
    """Возвращает (current_package, current_activity); ('', '') при ошибке."""
    try:
        return (driver.current_package or "", driver.current_activity or "")
    except Exception:
        return ("", "")


def _wait_splash_passed(driver, package: str, timeout: int) -> tuple[bool, str, str]:
    """Ожидать прохождения сплэша; вернуть (passed, focused_pkg, focused_act).

    Сплэш пройден, когда в фокусе наш пакет, но активность уже не
    SplashActivity (приложение перешло на следующий экран). На эмуляторе за
    Integrity-стеной этого не происходит — по таймауту вернётся passed=False
    с последними значениями фокуса для аттача в отчёт.
    """
    deadline = time.monotonic() + timeout
    while True:
        pkg, act = _focused_activity(driver)
        if pkg == package and SPLASH_ACTIVITY not in act:
            return True, pkg, act
        if time.monotonic() >= deadline:
            return False, pkg, act
        time.sleep(SPLASH_POLL_INTERVAL)


@allure.epic("Проверка стабильности")
@allure.feature("Запуск")
@pytest.mark.android
class TestAppLaunch:
    """Запуск приложения: процесс жив после старта Appium-сессии."""

    @allure.title("Запустить приложение -> процесс приложения жив")
    @allure.description(
        "Сценарий resilience/app_launch.\n\n"
        "Шаги: стартовать Appium-сессию с приложением из конфига; дождаться "
        "прохождения splash-активности (best-effort, до 10 с — на эмуляторе "
        "Play Integrity не проходит, UI не появляется, шаг честно "
        "таймаутится); запросить состояние приложения через "
        "mobile: queryAppState.\n\n"
        "Ожидаемый результат: процесс приложения жив — состояние 2 (фон, "
        "suspended), 3 (фон, running) или 4 (foreground); у мёртвого процесса "
        "было бы 1 (не запущено), у отсутствующего в системе — 0 (не установлено)."
    )
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @allure.id("")
    def test_app_is_running(self, driver):
        """Запустить приложение -> процесс приложения жив."""
        raw = driver.raw
        # Пакет берём из capabilities сессии — Appium определил его из APK
        # (тот же источник, что у _restart_app_per_test в fixtures/driver_fixtures.py).
        package = raw.capabilities.get("appPackage")

        with allure.step("Проверить, что Appium-сессия активна"):
            # current_package ходит в драйвер — если сессия мертва, упадёт здесь.
            session_package = raw.current_package
            allure.attach(
                session_package or "<empty>",
                name="session_current_package",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step(f"Дождаться прохождения сплэша (до {SPLASH_WAIT_TIMEOUT} с)"):
            if not package:
                pytest.fail("appPackage не определён в capabilities сессии")
            splash_ok, focused_pkg, focused_act = _wait_splash_passed(
                raw, package, SPLASH_WAIT_TIMEOUT)
            allure.attach(
                f"focused_package={focused_pkg!r}\n"
                f"focused_activity={focused_act!r}\n"
                f"splash_passed={splash_ok}",
                name="splash_wait_result",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("Проверить, что приложение запущено (процесс жив)"):
            state = raw.execute_script("mobile: queryAppState", {"appId": package})
            allure.attach(
                str(state),
                name="app_state",
                attachment_type=allure.attachment_type.TEXT,
            )
            assert state in RUNNING_STATES, (
                f"Приложение {package} не запущено: queryAppState={state} "
                "(0=не установлено, 1=не запущено)."
            )
