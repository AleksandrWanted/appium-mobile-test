"""Тесты экрана логина."""
from __future__ import annotations

import allure
import pytest

from src.pages.home_page import HomePage
from src.pages.login_page import LoginPage


@allure.epic("Авторизация")
@allure.feature("Логин")
@pytest.mark.android
def test_login_success(driver, test_data):
    """Позитивный логин: после входа открывается главный экран."""
    with allure.step("Войти валидным пользователем"):
        login_page = LoginPage(driver)
        user = test_data["valid_user"]
        login_page.login(user["username"], user["password"])

    home_page = HomePage(driver)
    with allure.step("Проверить, что главный экран открыт"):
        assert home_page.is_loaded(), "Главный экран не открылся после логина"


@allure.epic("Авторизация")
@allure.feature("Логин")
@pytest.mark.android
def test_login_invalid_credentials(driver, test_data):
    """Негативный логин: показывается сообщение об ошибке."""
    login_page = LoginPage(driver)
    user = test_data["invalid_user"]

    with allure.step("Войти невалидным пользователем"):
        login_page.login(user["username"], user["password"])

    with allure.step("Проверить наличие сообщения об ошибке"):
        assert login_page.is_error_shown(), "Сообщение об ошибке не появилось"
