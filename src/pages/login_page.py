"""Page Object экрана логина."""
from __future__ import annotations

import allure
from appium.webdriver.common.appiumby import AppiumBy

from src.pages.base_page import BasePage


class LoginPage(BasePage):
    # Локаторы через accessibility id — кроссплатформенные
    USERNAME_FIELD = (AppiumBy.ACCESSIBILITY_ID, "username-input")
    PASSWORD_FIELD = (AppiumBy.ACCESSIBILITY_ID, "password-input")
    LOGIN_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "login-button")
    ERROR_MESSAGE = (AppiumBy.ACCESSIBILITY_ID, "login-error")

    @allure.step("Войти как {username}")
    def login(self, username: str, password: str) -> None:
        """Выполняет вход в приложение."""
        self.type_text(self.USERNAME_FIELD, username)
        self.type_text(self.PASSWORD_FIELD, password)
        self.tap(self.LOGIN_BUTTON)

    @allure.step("Получить текст ошибки авторизации")
    def get_error(self) -> str:
        """Возвращает текст ошибки авторизации."""
        return self.get_text(self.ERROR_MESSAGE)

    @allure.step("Проверить наличие сообщения об ошибке")
    def is_error_shown(self) -> bool:
        return self.is_displayed(self.ERROR_MESSAGE)
