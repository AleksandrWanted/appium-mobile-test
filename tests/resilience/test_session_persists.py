"""Resilience-тест: сессия авторизации переживает закрытие приложения.

Сценарий (component/android/authorization) для версии приложения 2.17.1+:
    «Авторизоваться -> закрыть приложение -> открыть приложение снова ->
    сессия сохранена, повторный вход не требуется».

Закрытие — terminateApp: force-stop процесса (как свайп приложения из
списка недавних). Из оперативной памяти уходит всё, включая UI и ход
SSO; остаётся только то, что приложение сохранило на диске — токен
MTS ID. Повторное открытие — activateApp того же Appium-сеанса.

Вторую сессию создавать нельзя: создание Appium-сессии с профилем
no_reset: false делает pm clear и стёрло бы авторизацию вместо проверки
её сохранности (см. fixtures/driver_fixtures.py, фикстура driver).

Признаки сохранённой сессии — те же, что сразу после входа
(test_mts_id_login.py): аватар «Изображение МТС ID» на вкладке
«Профиль» и отсутствие баннера входа «Войти в МТС Optimus».
"""
from __future__ import annotations

import time

import allure
import pytest

from src.pages.common_elements import BottomNavLocators
from src.pages.profile_page import ProfilePageLocators
from tests.constants import (
    COLD_START_TIMEOUT,
    NEGATIVE_PROBE_TIMEOUT,
    PAGE_LOAD_TIMEOUT,
)

# Константа mobile: queryAppState «не запущено» — enum ApplicationState
# в используемой версии python-клиента не экспортируется.
_APP_STATE_NOT_RUNNING = 1


@allure.epic("Проверка стабильности")
@allure.feature("Сохранение сессии MTS ID")
@pytest.mark.android
class TestMtsIdSessionResilience:
    """Сессия авторизации сохраняется при закрытии и повторном открытии приложения."""

    @allure.title(
        "Закрыть приложение при активной сессии -> после повторного открытия вход сохранён")
    @allure.description(
        "Сценарий component/android/resilience (приложение 2.17.1+).\n\n"
        "Шаги: войти через MTS ID (фикстура authorized_app), убедиться в "
        "активной сессии; закрыть приложение terminateApp (force-stop, как "
        "свайп из списка недавних) и проверить, что процесс остановлен; "
        "открыть приложение повторно activateApp и дождаться холодного "
        "старта; перейти на вкладку «Профиль».\n\n"
        "Ожидаемый результат: сессия авторизации сохранена — карточка "
        "пользователя (аватар «Изображение МТС ID») видна, баннер входа "
        "«Войти в МТС Optimus» не показывается, повторный вход не "
        "требуется.\n\n"
        "Примечание: открытие выполняется в том же Appium-сеансе — новая "
        "сессия с no_reset: false сделала бы pm clear и стёрла бы "
        "авторизацию вместо проверки её сохранности."
    )
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.id("")
    def test_session_persists_after_app_restart(self, authorized_app):
        """Force-stop при активной сессии -> повторный вход не требуется."""
        pages = authorized_app
        raw = pages.ctx.driver.raw
        app_id = raw.capabilities.get("appPackage")

        with allure.step("Убедиться, что сессия активна до закрытия"):
            profile = pages.profile
            assert profile.is_loaded(), "Вкладка «Профиль» не загрузилась"
            assert profile.is_user_card_visible(), (
                "Карточка пользователя не видна — сессия не активна")

        with allure.step("Закрыть приложение (force-stop процесса)"):
            assert raw.terminate_app(app_id), (
                "Приложение не завершилось: terminateApp вернул False")

        with allure.step("Проверить, что процесс приложения остановлен"):
            state = raw.query_app_state(app_id)
            assert state == _APP_STATE_NOT_RUNNING, (
                f"Приложение не остановлено: state={state}, ожидалось "
                f"{_APP_STATE_NOT_RUNNING} (не запущено)")

        with allure.step("Открыть приложение повторно (холодный старт)"):
            raw.activate_app(app_id)
            assert self._wait_app_started(pages), (
                "Приложение не стартовало: нижнее меню не появилось "
                f"за {COLD_START_TIMEOUT} с")

        with allure.step("Проверить, что сессия сохранена после перезапуска"):
            pages.common.open_profile_tab()
            assert pages.ctx.driver.is_present(
                ProfilePageLocators.USER_AVATAR, timeout=PAGE_LOAD_TIMEOUT), (
                "Карточка пользователя не видна после повторного открытия — "
                "сессия авторизации не сохранилась")
            banner = pages.common.unauthorized_state.LOGIN_BANNER_BUTTON
            assert not pages.ctx.driver.is_present(banner, timeout=NEGATIVE_PROBE_TIMEOUT), (
                "Баннер входа «Войти в МТС Optimus» виден после перезапуска — "
                "пользователь разлогинен, повторный вход не выполнен")

    @staticmethod
    def _wait_app_started(pages) -> bool:
        """Ждёт первого отклика UI после холодного старта.

        Стартовую вкладку после force-stop не фиксируем — критерий
        готовности: появление нижнего навигационного меню (любой вкладки).
        """
        deadline = time.monotonic() + COLD_START_TIMEOUT
        while time.monotonic() < deadline:
            for locator in (BottomNavLocators.TAB_CALLS,
                            BottomNavLocators.TAB_CONTACTS,
                            BottomNavLocators.TAB_PROFILE):
                if pages.ctx.driver.find_elements(locator):
                    return True
            time.sleep(1)
        return False
