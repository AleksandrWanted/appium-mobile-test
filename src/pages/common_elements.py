"""Общие (кросс-экранные) элементы и действия мобильного приложения."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import allure
from appium.webdriver.common.appiumby import AppiumBy

if TYPE_CHECKING:
    from src.pages.page_context import PageContext


class SystemDialogLocators:
    """Локаторы системных диалогов (разрешения, alert, установщик APK)."""

    ALLOW_TEXTS = (
        "Allow", "Allow while using the app", "Allow only while using the app",
        "Always Allow", "Разрешить", "Разрешить во время использования",
        "ALLOW", "OK", "ОК",
    )
    WHILE_USING_TEXTS = ("While using the app", "Только во время использования")
    INSTALL_TEXTS = ("Install", "Установить", "Done", "Готово")

    def __init__(self, driver):
        self.driver = driver

    @staticmethod
    def text_button_locator(text: str) -> tuple:
        """Кнопка системного диалога по видимому тексту (Android + iOS fallback)."""
        return (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{text}")')


class BottomNavLocators:
    """Локаторы нижнего навигационного меню приложения (общие для всех вкладок).

    Меню — нативные View'ы с resource-id: каждая вкладка — FrameLayout
    с уникальным id (callsFlowFragment / membersFlowFragment / profileFlowFragment).
    """

    TAB_CALLS = (AppiumBy.ID, "ru.mts.mvats:id/callsFlowFragment")
    TAB_CONTACTS = (AppiumBy.ID, "ru.mts.mvats:id/membersFlowFragment")
    TAB_PROFILE = (AppiumBy.ID, "ru.mts.mvats:id/profileFlowFragment")


class UnauthorizedStateLocators:
    """Локаторы элементов неавторизованного состояния приложения.

    Видны во всех вкладках, пока пользователь не вошёл в аккаунт, —
    поэтому относятся к общим элементам, а не к конкретному экрану.
    """

    # Баннер «Войти в МТС Optimus» на вкладке «Звонки»
    LOGIN_BANNER_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "Войти в МТС Optimus")


class CommonElements:
    """Действия, доступные с любого экрана: системные окна, нижнее меню, back/клавиатура."""

    def __init__(self, ctx: PageContext):
        self.ctx = ctx
        self.driver = ctx.driver
        self.logger = logging.getLogger(__name__)
        self.system_dialog = SystemDialogLocators(self.driver.raw)
        self.bottom_nav = BottomNavLocators
        self.unauthorized_state = UnauthorizedStateLocators

    # --- системные диалоги (делегируют PermissionsHandler) ---
    def grant_permissions(self) -> None:
        """Закрыть permission-диалоги, если приложение их показывает."""
        from src.utils.permissions import PermissionsHandler

        PermissionsHandler(self.driver.raw).grant_permissions()

    def dismiss_apk_installer(self) -> None:
        """Закрыть системный установщик APK, если он появился."""
        from src.utils.permissions import PermissionsHandler

        PermissionsHandler(self.driver.raw).dismiss_apk_installer()

    # --- навигация приложения ---
    def press_back(self) -> None:
        """Системная кнопка «Назад» (Android); на iOS закрывает текущий экран."""
        self.logger.info("Нажимаем системную кнопку «Назад»")
        self.driver.raw.back()

    def hide_keyboard(self) -> bool:
        """Скрыть клавиатуру, если открыта. Возвращает True, если была открыта."""
        self.logger.info("Скрываем клавиатуру")
        try:
            return self.driver.raw.hide_keyboard()
        except Exception:
            return False

    def go_home(self) -> None:
        """Уйти на домашний экран устройства (свернуть приложение)."""
        self.logger.info("Уходим на домашний экран устройства")
        self.driver.raw.press_keycode(3)  # KEYCODE_HOME

    # --- нижнее навигационное меню (общее для всех вкладок) ---
    @allure.step("Открыть вкладку «Звонки»")
    def open_calls_tab(self):
        from src.pages.calls_page import CallsPage

        self.logger.info("Открываем вкладку «Звонки»")
        self.driver.tap(BottomNavLocators.TAB_CALLS, timeout=self.ctx.timeout)
        return CallsPage(self.ctx)

    @allure.step("Открыть вкладку «Контакты»")
    def open_contacts_tab(self):
        from src.pages.contacts_page import ContactsPage

        self.logger.info("Открываем вкладку «Контакты»")
        self.driver.tap(BottomNavLocators.TAB_CONTACTS, timeout=self.ctx.timeout)
        return ContactsPage(self.ctx)

    @allure.step("Открыть вкладку «Профиль»")
    def open_profile_tab(self):
        from src.pages.profile_page import ProfilePage

        self.logger.info("Открываем вкладку «Профиль»")
        self.driver.tap(BottomNavLocators.TAB_PROFILE, timeout=self.ctx.timeout)
        return ProfilePage(self.ctx)

    # --- элементы неавторизованного состояния ---
    @allure.step("Нажать баннер «Войти в МТС Optimus»")
    def tap_login_banner(self) -> None:
        """Баннер входа виден только неавторизованному пользователю."""
        self.driver.tap(UnauthorizedStateLocators.LOGIN_BANNER_BUTTON,
                        timeout=self.ctx.timeout)
