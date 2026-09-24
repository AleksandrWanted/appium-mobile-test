"""Page Object вкладки «Профиль» приложения МТС Optimus (ru.mts.mvats).

Локаторы сняты с разметки реального устройства (Samsung S21 FE, Android 15).
Экран — нативный (не Compose): внутри nav_host_fragment_profile живут обычные
View с resource-id, плюс один scrollable-контейнер до нижнего меню.

Текущий контент экрана соответствует неавторизованному состоянию:
карточка «Подписка» с описанием тарифов и кнопка подключения. Элементы
авторизованного состояния (логин, зоны контента) уже присутствуют
в разметке как скрытые контейнеры (login / notAuthZone) — добавлять их
в локаторы стоит по мере надобности, когда появится доступ к устройству
в авторизованном состоянии.

Нижнее навигационное меню и элементы неавторизованного состояния (баннер
«Войти в МТС Optimus») — общие, живут в common_elements
(BottomNavLocators / UnauthorizedStateLocators).
"""
from __future__ import annotations

import allure
from appium.webdriver.common.appiumby import AppiumBy

from src.pages.base_page import BasePage


class ProfilePageLocators:
    """Локаторы вкладки «Профиль» (МТС Optimus).

    Приоритет локаторов: id (resource-id) → текст (uiautomator)
    → accessibility id. XPath — последний вариант.
    """

    # --- контейнер экрана ---
    SCREEN_ROOT = (AppiumBy.ID, "ru.mts.mvats:id/nav_host_fragment_profile")
    # Скролл-контейнер карточек (один на весь экран до нижнего меню)
    SCROLL_CONTAINER = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().scrollable(true)')
    # Compose-контента на экране нет — только нативные View.

    # --- контейнер неавторизованного состояния ---
    # Внутри nav_host_fragment_profile это единственный контейнер контента:
    # авторизованный (login-* заглушки скрыты) в разметку карточек не входит.
    # notAuthZone (ScrollView) есть и на вкладке «Контакты» (см. contacts_page),
    # поэтому для неавторизованного состояния профиля используем вложенный scope.
    NOT_AUTH_ZONE = (AppiumBy.ID, "ru.mts.mvats:id/notAuthZone")
    # Карточка входа: кликабельный LinearLayout с текстом «Войти в МТС Optimus»
    # (у текста-потомка своего resource-id нет)
    LOGIN_CARD = (AppiumBy.ID, "ru.mts.mvats:id/login")
    LOGIN_CARD_TEXT = (AppiumBy.ANDROID_UIAUTOMATOR,
                       'new UiSelector().text("Войти в МТС Optimus")')
    # Кнопка подключения (FrameLayout с id buttonEnableSub) и её текст
    SUBSCRIBE_BUTTON_CONTAINER = (AppiumBy.ID, "ru.mts.mvats:id/buttonEnableSub")
    SUBSCRIBE_BUTTON_TEXT = (AppiumBy.ANDROID_UIAUTOMATOR,
                             'new UiSelector().text("НАЧАТЬ ПОДКЛЮЧЕНИЕ")')

    # --- заголовок ---
    TITLE = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Профиль")')

    # --- карточка «Подписка» ---
    SUBSCRIPTION_CARD = (AppiumBy.ID, "ru.mts.mvats:id/profi_layout")
    SUBSCRIPTION_TITLE = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Подписка")')
    SUBSCRIPTION_PRICE = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("99 ₽/мес")')
    SUBSCRIPTION_FREE_PERIOD = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().text("30 дней – 0 ₽, далее – 99 ₽/мес")',
    )
    SUBSCRIPTION_DESCRIPTION = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().text("Звоните и отвечайте со смартфона, '
        'а МТС Optimus сохранит всё важное")',
    )
    # Блок «Ещё в подписке»
    OTHER_TARIFFS_SECTION = (AppiumBy.ID, "ru.mts.mvats:id/profiInfo")
    # Карточки «Для МТС Супер...» и «Для других тарифов»
    CARD_IS_NOT_MTS = (AppiumBy.ID, "ru.mts.mvats:id/card_is_not_mts")
    FIRST_PROFILE_CARD = (AppiumBy.ID, "ru.mts.mvats:id/firstProfiCard")
    # Кнопка подключения (нативная Button, content-desc "Начать подключение")
    SUBSCRIBE_BUTTON = (AppiumBy.ANDROID_UIAUTOMATOR,
                        'new UiSelector().description("Начать подключение")')

    # --- нижние карточки-секции (видны после доскролла) ---
    # Карточка «Как подключить подписку» с шагами 1-2-3
    HOW_TO_SUBSCRIBE_CARD = (AppiumBy.ID, "ru.mts.mvats:id/how_to_subscribe")
    SUBSCRIBE_STEP_1 = (AppiumBy.ANDROID_UIAUTOMATOR,
                        'new UiSelector().text("1. Начните подключение с номером МТС")')
    SUBSCRIBE_STEP_2 = (AppiumBy.ANDROID_UIAUTOMATOR,
                        'new UiSelector().text("2. Войдите в приложение через МТС ID")')
    SUBSCRIBE_STEP_3 = (AppiumBy.ANDROID_UIAUTOMATOR,
                        'new UiSelector().text("3. Подключите подписку из приложения")')

    # Инфошеринг-баннер «Хотите смотреть звонки коллег?»
    INFO_BANNER_CONTAINER = (AppiumBy.ID, "ru.mts.mvats:id/banners_not_auth_container")
    INFO_BANNER_IMAGE = (AppiumBy.ANDROID_UIAUTOMATOR,
                         'new UiSelector().description("Изображение инфошеринг баннера")')

    # Кнопка/строка «ПОДРОБНЕЕ» под баннером (текст кириллицей, у View нет id)
    INFO_BANNER_MORE_BUTTON = (AppiumBy.ANDROID_UIAUTOMATOR,
                               'new UiSelector().text("ПОДРОБНЕЕ")')

    # Секции меню доступа (кликабельные LinearLayout с текстовыми заголовками)
    CALL_ACCESS_CARD = (AppiumBy.ID, "ru.mts.mvats:id/call_access_not_auth")
    CALL_ACCESS_TITLE = (AppiumBy.ANDROID_UIAUTOMATOR,
                         'new UiSelector().text("Доступы к звонкам")')
    SUPPORT_CARD = (AppiumBy.ID, "ru.mts.mvats:id/support_not_auth")
    SUPPORT_TITLE = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Поддержка")')
    REFERENCE_CARD = (AppiumBy.ID, "ru.mts.mvats:id/reference_not_auth")
    REFERENCE_TITLE = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Справка")')

    # Подпись версии приложения рядом с «Справка»
    APP_VERSION_TEXT = (AppiumBy.ID, "ru.mts.mvats:id/version_app_not_auth")


class ProfilePage(BasePage):
    """Вкладка «Профиль» приложения МТС Optimus.

    Нижнее меню (переход между вкладками) и баннер входа — общие элементы:
    pages.common.open_profile_tab() / pages.common.tap_login_banner().
    """

    # --- проверки состояния экрана ---
    @allure.step("Проверить, что вкладка «Профиль» загружена")
    def is_loaded(self) -> bool:
        return self.is_displayed(ProfilePageLocators.TITLE)

    @allure.step("Получить заголовок вкладки")
    def get_title(self) -> str:
        return self.get_text(ProfilePageLocators.TITLE)

    # --- неавторизованное состояние ---
    @allure.step("Проверить видимость контейнера неавторизованного состояния")
    def is_not_auth_zone_visible(self) -> bool:
        return self.is_displayed(ProfilePageLocators.NOT_AUTH_ZONE)

    @allure.step("Проверить видимость карточки «Войти в МТС Optimus»")
    def is_login_card_visible(self) -> bool:
        return self.is_displayed(ProfilePageLocators.LOGIN_CARD)

    @allure.step("Проверить текст карточки входа")
    def get_login_card_text(self) -> str:
        return self.get_text(ProfilePageLocators.LOGIN_CARD_TEXT)

    @allure.step("Проверить видимость кнопки «Начать подключение»")
    def is_subscribe_button_visible(self) -> bool:
        return self.is_displayed(ProfilePageLocators.SUBSCRIBE_BUTTON_TEXT)

    # --- карточка «Подписка» ---
    @allure.step("Получить описание подписки")
    def get_subscription_description(self) -> str:
        return self.get_text(ProfilePageLocators.SUBSCRIPTION_DESCRIPTION)

    @allure.step("Получить цену подписки")
    def get_subscription_free_period(self) -> str:
        return self.get_text(ProfilePageLocators.SUBSCRIPTION_FREE_PERIOD)

    @allure.step("Прокрутить экран до кнопки подключения")
    def scroll_to_subscribe_button(self) -> None:
        self.driver.scroll_to_element(
            ProfilePageLocators.SUBSCRIBE_BUTTON, timeout=self.timeout
        )

    @allure.step("Нажать кнопку «Начать подключение»")
    def tap_subscribe_button(self) -> None:
        self.tap(ProfilePageLocators.SUBSCRIBE_BUTTON)

    # --- нижние карточки-секции ---
    @allure.step("Проверить видимость карточки «Доступы к звонкам»")
    def is_call_access_card_visible(self) -> bool:
        return self.is_displayed(ProfilePageLocators.CALL_ACCESS_CARD)

    @allure.step("Прокрутить до карточки «Доступы к звонкам»")
    def scroll_to_call_access_card(self) -> None:
        self.driver.scroll_to_element(
            ProfilePageLocators.CALL_ACCESS_TITLE, timeout=self.timeout
        )

    @allure.step("Проверить видимость карточки «Поддержка»")
    def is_support_card_visible(self) -> bool:
        return self.is_displayed(ProfilePageLocators.SUPPORT_CARD)

    @allure.step("Проверить видимость карточки «Справка»")
    def is_reference_card_visible(self) -> bool:
        return self.is_displayed(ProfilePageLocators.REFERENCE_CARD)

    @allure.step("Проверить видимость карточки «Как подключить подписку»")
    def is_how_to_subscribe_card_visible(self) -> bool:
        return self.is_displayed(ProfilePageLocators.HOW_TO_SUBSCRIBE_CARD)

    @allure.step("Проверить видимость инфошеринг-баннера")
    def is_info_banner_visible(self) -> bool:
        return self.is_displayed(ProfilePageLocators.INFO_BANNER_CONTAINER)

    @allure.step("Проверить наличие кнопки «ПОДРОБНЕЕ» под баннером")
    def is_info_banner_more_button_visible(self) -> bool:
        return self.is_displayed(ProfilePageLocators.INFO_BANNER_MORE_BUTTON)

    @allure.step("Нажать «ПОДРОБНЕЕ» под баннером")
    def tap_info_banner_more_button(self) -> None:
        self.tap(ProfilePageLocators.INFO_BANNER_MORE_BUTTON)

    @allure.step("Получить версию приложения")
    def get_app_version(self) -> str:
        return self.get_text(ProfilePageLocators.APP_VERSION_TEXT)
