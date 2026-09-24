"""Resilience-тест: полный цикл «свернуть/развернуть» — приложение переживает оба.

Приложение сворачивается через mobile: backgroundApp (seconds=-1 — остаться
в фоне, как после нажатия «Домой») и разворачивается обратно через
mobile: activateApp. Проверки твёрдые, через mobile: queryAppState
(0=не установлено, 1=не запущено, 2=фон suspended, 3=фон running,
4=foreground):

- после сворачивания процесс жив и в фоне ({2,3}) — 1 значило бы, что
  система прибила приложение при уходе в фон;
- после разворачивания состояние ровно 4 (foreground) — 2/3 значило бы,
  что приложение не вернулось, 1 — что процесс умер за время разворачивания.

Как и в test_app_launch, прохождение сплэша ожидаем best-effort: на эмуляторе
Play Integrity не проходит и UI не появляется; на реальном устройстве сплэш
сменяется MainActivity.
"""
from __future__ import annotations

import time

import allure
import pytest

# Хелперы из дымового теста запуска: общий алгоритм прохождения сплэша.
from tests.resilience.test_app_launch import (
    SPLASH_WAIT_TIMEOUT,
    RUNNING_STATES,
    _wait_splash_passed,
)

# Состояния queryAppState, при которых приложение живо и находится в фоне:
# 2=фон suspended, 3=фон running.
BACKGROUND_STATES = {2, 3}
FOREGROUND_STATE = 4

# Сколько секунд подождать после сворачивания перед проверкой процесса:
# если бы система прибила приложение при уходе в фон, это произошло бы быстро.
BACKGROUND_SETTLE_S = 3

# Сколько секунд ждать, пока приложение вернётся в foreground после разворачивания.
FOREGROUND_WAIT_TIMEOUT = 10
FOREGROUND_POLL_INTERVAL = 1


@allure.epic("Проверка стабильности")
@allure.feature("Сворачивание/разворачивание")
@pytest.mark.android
class TestAppBackground:
    """Сворачивание не убивает процесс, разворачивание возвращает на передний план."""

    @allure.title(
        "Свернуть и развернуть приложение -> процесс жив, потом фон, потом foreground")
    @allure.description(
        "Сценарий resilience/app_background.\n\n"
        "Шаги: стартовать Appium-сессию с приложением из конфига; дождаться "
        "прохождения splash-активности (best-effort, до 10 с); убедиться, что "
        "приложение запущено; свернуть приложение через mobile: backgroundApp "
        "(seconds=-1); выждать 3 с и проверить, что процесс жив и в фоне; "
        "развернуть приложение (mobile: activateApp) и дождаться его возврата "
        "в foreground (poll mobile: queryAppState, до 10 с).\n\n"
        "Ожидаемый результат: после сворачивания процесс не закрывается — "
        "состояние 2 (фон, suspended) или 3 (фон, running); после "
        "разворачивания приложение снова в foreground — состояние 4."
    )
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.id("")
    def test_app_survives_background_and_foreground(self, driver):
        """Свернуть и развернуть приложение -> процесс жив, потом фон, потом foreground."""
        raw = driver.raw
        # Пакет берём из capabilities сессии — Appium определил его из APK
        # (тот же источник, что в test_app_launch и _restart_app_per_test).
        package = raw.capabilities.get("appPackage")

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
            state_before = raw.execute_script(
                "mobile: queryAppState", {"appId": package})
            allure.attach(
                str(state_before),
                name="app_state_before_background",
                attachment_type=allure.attachment_type.TEXT,
            )
            assert state_before in RUNNING_STATES, (
                f"Приложение {package} не запущено перед сворачиванием: "
                f"queryAppState={state_before} "
                "(0=не установлено, 1=не запущено)."
            )

        with allure.step("Свернуть приложение (mobile: backgroundApp, seconds=-1)"):
            raw.execute_script("mobile: backgroundApp", {"seconds": -1})

        with allure.step(f"Выждать {BACKGROUND_SETTLE_S} с и проверить, что оно живо в фоне"):
            time.sleep(BACKGROUND_SETTLE_S)
            state_bg = raw.execute_script("mobile: queryAppState", {"appId": package})
            allure.attach(
                str(state_bg),
                name="app_state_background",
                attachment_type=allure.attachment_type.TEXT,
            )
            assert state_bg in BACKGROUND_STATES, (
                f"Приложение {package} закрылось при сворачивании: "
                f"queryAppState={state_bg} "
                "(1=не запущено; 4=всё ещё foreground — сворачивание не сработало)."
            )

        with allure.step("Развернуть приложение (mobile: activateApp)"):
            raw.execute_script("mobile: activateApp", {"appId": package})

        with allure.step(
            f"Дождаться возврата в foreground (до {FOREGROUND_WAIT_TIMEOUT} с)"
        ):
            state_final = 0
            deadline = time.monotonic() + FOREGROUND_WAIT_TIMEOUT
            while True:
                state_final = raw.execute_script(
                    "mobile: queryAppState", {"appId": package})
                if state_final == FOREGROUND_STATE:
                    break
                if time.monotonic() >= deadline:
                    break
                time.sleep(FOREGROUND_POLL_INTERVAL)
            allure.attach(
                str(state_final),
                name="app_state_after_foreground",
                attachment_type=allure.attachment_type.TEXT,
            )
            assert state_final == FOREGROUND_STATE, (
                f"Приложение {package} не вернулось в foreground после "
                f"activateApp: queryAppState={state_final} "
                "(2/3=осталось в фоне, 1=процесс умер)."
            )
