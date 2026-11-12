"""Компонентные тесты вкладки «Профиль»: авторизованное состояние.

Сценарий (component/android/profile_screen) для версии приложения 2.17.1+:
    «Авторизоваться -> перейти на вкладку «Профиль» -> видны элементы
    авторизованного состояния (карточка пользователя с именем и номером)».

Авторизация выполняется фикстурой authorized_app (fixtures/driver_fixtures):
вкладка «Профиль» → «Войти в МТС Optimus» → (fast-track → «Войти с другим
номером») → ввод MSISDN → «ДАЛЕЕ» → код из СМС → вход. Номер и код —
credential'ы из .env (MSISDN / VERIFICATION_CODE).
"""
from __future__ import annotations

import allure
import pytest


@allure.epic("Вкладка «Профиль»")
@allure.feature("Авторизованное состояние")
@pytest.mark.android
class TestProfileAuthorized:
    """Профиль авторизованного пользователя: карточка пользователя."""

    @allure.title("Авторизация через MTS ID -> в профиле видна карточка "
                  "пользователя")
    @allure.description(
        "Сценарий component/android/profile_screen (приложение 2.17.1+).\n\n"
        "Шаги: выполнить вход через MTS ID (фикстура authorized_app: "
        "вкладка «Профиль» → «Войти в МТС Optimus» → номер MSISDN → код из "
        "СМС); проверить вкладку «Профиль».\n\n"
        "Ожидаемый результат: аватар «Изображение МТС ID» виден, кнопка "
        "входа неавторизованного состояния исчезла. Возврат в "
        "неавторизованное состояние делает сброс данных следующей сессии "
        "(no_reset: false), а не teardown-выход."
    )
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.id("")
    def test_profile_authorized_elements(self, authorized_app):
        """Авторизация -> карточка пользователя в профиле, кнопки входа нет."""
        profile = authorized_app.profile

        with allure.step("Проверить, что вкладка «Профиль» открылась "
                         "авторизованной"):
            assert profile.is_loaded(), "Экран «Профиль» не загрузился"
            assert profile.is_user_card_visible(), (
                "Карточка пользователя (МТС ID) не видна после входа")

        with allure.step("Проверить, что кнопка входа неавторизованного "
                         "состояния исчезла"):
            assert not profile.is_login_card_visible(), (
                "Кнопка «Войти в МТС Optimus» видна — вход не сработал")
