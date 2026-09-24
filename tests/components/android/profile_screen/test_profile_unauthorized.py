"""Компонентные тесты вкладки «Профиль»: неавторизованное состояние.

Сценарий (component/android/profile_screen):
    «Перейти на вкладку «Профиль» -> пользователь не авторизован, видны
    элементы неавторизованного состояния».
"""
from __future__ import annotations

import allure
import pytest

from src.pages.profile_page import ProfilePageLocators


@allure.epic("Вкладка «Профиль»")
@allure.feature("Неавторизованное состояние")
@pytest.mark.android
class TestProfileUnauthorized:
    """Профиль без авторизации: карточка входа, контейнер контента, кнопка подписки."""

    @allure.title("Профиль без авторизации -> видны карточка входа, контент и "
                  "кнопка подписки")
    @allure.description(
        "Сценарий component/android/profile_screen.\n\n"
        "Шаги: открыть вкладку «Профиль» через нижнее меню; проверить переход "
        "(выбрана вкладка «Профиль», заголовок появился); проверить, что "
        "отображается контейнер неавторизованного состояния (notAuthZone — "
        "единственный контейнер контента профиля); проверить карточку входа "
        "«Войти в МТС Optimus» (видна, текст совпадает, карточка кликабельна); "
        "проверить кнопку «НАЧАТЬ ПОДКЛЮЧЕНИЕ» и карточку подписки "
        "(«Подписка» + «30 дней – 0 ₽, далее – 99 ₽/мес»).\n\n"
        "Ожидаемый результат: все элементы неавторизованного состояния видны "
        "и заполнены ожидаемыми текстами."
    )
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.id("")
    def test_profile_unauthorized_elements(self, pages):
        """Профиль без авторизации -> элементы неавторизованного состояния видны."""
        with allure.step("Перейти на вкладку «Профиль»"):
            profile = pages.common.open_profile_tab()

        with allure.step("Проверить, что вкладка «Профиль» открылась"):
            assert profile.is_loaded(), "Экран «Профиль» не загрузился"

        with allure.step("Проверить, что отображается неавторизованное состояние"):
            assert profile.is_not_auth_zone_visible(), (
                "Контейнер неавторизованного состояния (notAuthZone) не виден")

        with allure.step("Проверить карточку «Войти в МТС Optimus»"):
            assert profile.is_login_card_visible(), (
                "Карточка «Войти в МТС Optimus» не видна")
            assert profile.get_login_card_text() == "Войти в МТС Optimus", (
                "Текст карточки входа не совпадает")

        with allure.step("Проверить кнопку «Начать подключение»"):
            assert profile.is_subscribe_button_visible(), (
                "Кнопка «НАЧАТЬ ПОДКЛЮЧЕНИЕ» не видна")
            assert profile.is_displayed(
                ProfilePageLocators.SUBSCRIBE_BUTTON_CONTAINER), (
                "Контейнер кнопки подписки (buttonEnableSub) не виден")

        with allure.step("Проверить карточку «Подписка»"):
            assert profile.is_displayed(ProfilePageLocators.SUBSCRIPTION_TITLE), (
                "Заголовок «Подписка» не виден")
            assert profile.get_subscription_free_period() == (
                "30 дней – 0 ₽, далее – 99 ₽/мес"), (
                "Текст периода подписки не совпадает")
