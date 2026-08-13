"""Тесты главного экрана."""
from __future__ import annotations

import allure
import pytest

from src.pages.home_page import HomePage
from src.pages.login_page import LoginPage


@pytest.fixture()
def logged_in(driver, test_data):
    """Предусловие: залогиниться перед тестом главного экрана."""
    LoginPage(driver).login(
        test_data["valid_user"]["username"],
        test_data["valid_user"]["password"],
    )
    return HomePage(driver)


@allure.epic("Главный экран")
@allure.feature("Навигация")
@pytest.mark.android
def test_home_title_displayed(logged_in: HomePage):
    with allure.step("Проверить, что главный экран загружен"):
        assert logged_in.is_loaded()
    with allure.step("Проверить наличие заголовка"):
        assert logged_in.get_title(), "Заголовок главного экрана пуст"
