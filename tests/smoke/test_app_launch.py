"""Дымовой тест: запуск приложения и проверка, что оно запущено.

Приложение «МТС Optimus» (ru.mts.mvats) — release-сборка с Play Integrity.
На эмуляторе Integrity-проверка не проходит, поэтому splash-активность
закрывается и UI не выходит в фон. Поэтому:

- ждём прохождения сплэша (SplashActivity сменится другой активностью
  приложения) с таймаутом — это best-effort шаг: на реальном устройстве
  он завершится успехом, на эмуляторе за Integrity-стеной — таймаутится;
- твёрдой проверкой остаётся «процесс приложения жив» (mobile: queryAppState).

queryAppState возвращает: 0 not installed, 1 not running,
2 background (suspended), 3 background running, 4 foreground.
"""
from __future__ import annotations

import time

import allure
import pytest

# Пакет и splash-активность приложения из resources/app/mts-optimus.apk (МТС Optimus)
APP_PACKAGE = "ru.mts.mvats"
SPLASH_ACTIVITY = "SplashActivity"

# Сколько секунд ждать прохождения сплэша.
SPLASH_WAIT_TIMEOUT = 10
SPLASH_POLL_INTERVAL = 1

# Допустимые состояния приложения, при которых считаем его «запущенным».
RUNNING_STATES = {2, 3, 4}


def _focused_activity(driver) -> tuple[str, str]:
    """Возвращает (current_package, current_activity); ('', '') при ошибке."""
    try:
        return (driver.current_package or "", driver.current_activity or "")
    except Exception:
        return ("", "")


def _splash_passed(driver, package: str) -> bool:
    """True, если приложение в фоне и splash-активность уже пройдена.

    Сплэш считается пройденным, когда в фокусе наш пакет, но активность
    уже не SplashActivity (значит, приложение перешло на следующий экран).
    """
    pkg, act = _focused_activity(driver)
    if pkg != package:
        return False
    return SPLASH_ACTIVITY not in act


@allure.epic("Старт приложения")
@allure.feature("Запуск")
@pytest.mark.android
@pytest.mark.smoke
def test_app_is_running(driver):
    """После старта сессии процесс приложения жив (сплэш ожидается best-effort)."""
    raw = driver.raw

    with allure.step("Проверить, что Appium-сессия активна"):
        # current_package ходит в драйвер — если сессия мертва, упадёт здесь.
        session_package = raw.current_package
        allure.attach(
            session_package or "<empty>",
            name="session_current_package",
            attachment_type=allure.attachment_type.TEXT,
        )

    with allure.step(f"Дождаться прохождения сплэша (до {SPLASH_WAIT_TIMEOUT} с)"):
        # Опрашиваем активность в фокусе, пока SplashActivity не сменится
        # другой активностью приложения. На эмуляторе за Integrity-стеной
        # сплэш в UI не проходит — шаг честно таймаутится и фиксируется в аттаче.
        last_pkg, last_act = _focused_activity(raw)
        deadline = time.monotonic() + SPLASH_WAIT_TIMEOUT
        while time.monotonic() < deadline:
            last_pkg, last_act = _focused_activity(raw)
            if _splash_passed(raw, APP_PACKAGE):
                break
            time.sleep(SPLASH_POLL_INTERVAL)

        splash_ok = _splash_passed(raw, APP_PACKAGE)
        allure.attach(
            f"focused_package={last_pkg!r}\n"
            f"focused_activity={last_act!r}\n"
            f"splash_passed={splash_ok}",
            name="splash_wait_result",
            attachment_type=allure.attachment_type.TEXT,
        )

    with allure.step(f"Запросить состояние приложения {APP_PACKAGE}"):
        state = raw.execute_script("mobile: queryAppState", {"appId": APP_PACKAGE})
        allure.attach(
            str(state),
            name="app_state",
            attachment_type=allure.attachment_type.TEXT,
        )

    with allure.step("Проверить, что приложение запущено (процесс жив)"):
        assert state in RUNNING_STATES, (
            f"Приложение {APP_PACKAGE} не запущено: queryAppState={state} "
            "(0=не установлено, 1=не запущено)."
        )
