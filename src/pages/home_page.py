"""Page Object главного экрана приложения."""
from __future__ import annotations

import allure
from appium.webdriver.common.appiumby import AppiumBy

from src.pages.base_page import BasePage


class HomePage(BasePage):
    TITLE = (AppiumBy.ACCESSIBILITY_ID, "home-title")
    PROFILE_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "profile-button")

    @allure.step("Получить заголовок главного экрана")
    def get_title(self) -> str:
        return self.get_text(self.TITLE)

    @allure.step("Проверить, что главный экран загружен")
    def is_loaded(self) -> bool:
        return self.is_displayed(self.TITLE)
