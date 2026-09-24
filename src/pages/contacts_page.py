"""Page Object вкладки «Контакты» приложения МТС Optimus (ru.mts.mvats).

Локаторы сняты с разметки реального устройства (Samsung S21 FE, Android 15).
Экран — нативный (не Compose): внутри nav_host_fragment_members живут обычные
View с resource-id.

Экран состоит из шапки (заголовок + поле поиска — поле есть только на вкладке
«Optimus»), горизонтального переключателя вкладок (Optimus / Личные) и контента
выбранной вкладки. Контент вкладки «Optimus» — список контактов
(clients_legacy_page: RecyclerView с карточками). Контент вкладки «Личные» —
контейнеры состояний notAuthZone (не авторизован) / notExist (авторизован,
но контакт нет); оба присутствуют в разметке одновременно, реальную видимость
проверяем через is_displayed.

Нижний блок с баннером «Войти в МТС Optimus» и нижнее навигационное меню —
общие, живут в common_elements (BottomNavLocators / UnauthorizedStateLocators).
"""
from __future__ import annotations

import allure
from appium.webdriver.common.appiumby import AppiumBy

from src.pages.base_page import BasePage


class ContactsPageLocators:
    """Локаторы вкладки «Контакты» (МТС Optimus).

    Приоритет локаторов: id (resource-id) → accessibility id (content-desc)
    → текст (uiautomator). XPath — последний вариант.
    """

    # --- контейнер экрана ---
    SCREEN_ROOT = (AppiumBy.ID, "ru.mts.mvats:id/nav_host_fragment_members")

    # --- шапка (navBar) ---
    TITLE = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Контакты")')
    # Поле поиска есть только на вкладке «Optimus»: контейнер navBar
    # перестраивается, и на вкладке «Личные» фрейма search в разметке нет.
    SEARCH_FIELD = (AppiumBy.ID, "ru.mts.mvats:id/searchEditText")
    SEARCH_CONTAINER = (AppiumBy.ID, "ru.mts.mvats:id/search")

    # --- переключатель вкладок (tabBar, HorizontalScrollView) ---
    # У обеих вкладок text = android:id/text1, поэтому ищем по content-desc.
    TAB_OPTIMUS = (AppiumBy.ACCESSIBILITY_ID, "Optimus")
    TAB_PERSONAL = (AppiumBy.ACCESSIBILITY_ID, "Личные")

    # --- вкладка «Optimus»: список контактов (clients_legacy_page) ---
    CLIENTS_CONTAINER = (AppiumBy.ID, "ru.mts.mvats:id/clients_legacy_page")
    PULL_TO_REFRESH = (AppiumBy.ID, "ru.mts.mvats:id/pullToRefresh")
    CLIENT_LIST = (AppiumBy.ID, "ru.mts.mvats:id/client_list")
    # Индексная буква секции списка («П» для «Привет от МТС Optimus»)
    SECTION_LETTER = (AppiumBy.ID, "ru.mts.mvats:id/letter")
    # Первая карточка контакта
    FIRST_CONTACT_NAME = (AppiumBy.ID, "ru.mts.mvats:id/name")
    CONTACT_AVATAR = (AppiumBy.ACCESSIBILITY_ID, "Аватар с загруженным фото")

    # --- вкладка «Личные»: контейнеры состояний (contacts_page) ---
    PERSONAL_CONTAINER = (AppiumBy.ID, "ru.mts.mvats:id/contacts_page")
    # Не авторизован: приглашение войти в профиль
    NOT_AUTH_ZONE = (AppiumBy.ID, "ru.mts.mvats:id/notAuthZone")
    NOT_AUTH_TITLE = (AppiumBy.ANDROID_UIAUTOMATOR,
                      'new UiSelector().text("Здесь будут ваши личные контакты")')
    NOT_AUTH_DESCRIPTION = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().text('
        '"Войдите в профиль, чтобы синхронизировать их с приложением")',
    )
    # Авторизован, но личных контактов нет
    NOT_EXIST_ZONE = (AppiumBy.ID, "ru.mts.mvats:id/notExist")
    NOT_EXIST_TITLE = (AppiumBy.ANDROID_UIAUTOMATOR,
                       'new UiSelector().text("Здесь пока пусто")')
    NOT_EXIST_DESCRIPTION = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().textContains("Добавьте номер в «Контакты»")',
    )


class ContactsPage(BasePage):
    """Вкладка «Контакты» приложения МТС Optimus.

    Нижнее меню (переход между вкладками) и баннер входа — общие элементы:
    pages.common.open_contacts_tab() / pages.common.tap_login_banner().
    """

    # --- проверки состояния экрана ---
    @allure.step("Проверить, что вкладка «Контакты» загружена")
    def is_loaded(self) -> bool:
        return self.is_displayed(ContactsPageLocators.TITLE)

    @allure.step("Получить заголовок вкладки")
    def get_title(self) -> str:
        return self.get_text(ContactsPageLocators.TITLE)

    # --- вкладки (Optimus / Личные) ---
    @allure.step("Открыть вкладку «Optimus»")
    def open_optimus_tab(self) -> None:
        self.tap(ContactsPageLocators.TAB_OPTIMUS)

    @allure.step("Открыть вкладку «Личные»")
    def open_personal_tab(self) -> None:
        self.tap(ContactsPageLocators.TAB_PERSONAL)

    @allure.step("Проверить, что выбрана вкладка «Optimus»")
    def is_optimus_container_visible(self) -> bool:
        return self.is_displayed(ContactsPageLocators.CLIENTS_CONTAINER)

    @allure.step("Проверить, что выбрана вкладка «Личные»")
    def is_personal_container_visible(self) -> bool:
        return self.is_displayed(ContactsPageLocators.PERSONAL_CONTAINER)

    # --- поле поиска (только на вкладке «Optimus») ---
    @allure.step("Проверить видимость поля поиска")
    def is_search_field_visible(self) -> bool:
        return self.is_displayed(ContactsPageLocators.SEARCH_FIELD)

    @allure.step("Ввести запрос в поле поиска")
    def type_search_query(self, query: str) -> None:
        self.type_text(ContactsPageLocators.SEARCH_FIELD, query)

    @allure.step("Получить текст поля поиска")
    def get_search_query(self) -> str:
        return self.get_text(ContactsPageLocators.SEARCH_FIELD)

    # --- список контактов (вкладка «Optimus») ---
    @allure.step("Проверить видимость списка контактов")
    def is_client_list_visible(self) -> bool:
        return self.is_displayed(ContactsPageLocators.CLIENT_LIST)

    @allure.step("Получить имя первого контакта")
    def get_first_contact_name(self) -> str:
        return self.get_text(ContactsPageLocators.FIRST_CONTACT_NAME)

    @allure.step("Проверить наличие индексной буквы секции")
    def is_section_letter_visible(self) -> bool:
        return self.is_displayed(ContactsPageLocators.SECTION_LETTER)

    # --- вкладка «Личные»: состояния ---
    @allure.step("Проверить видимость пустой зоны «Личные» (не авторизован)")
    def is_personal_not_auth_zone_visible(self) -> bool:
        return self.is_displayed(ContactsPageLocators.NOT_AUTH_ZONE)

    @allure.step("Проверить видимость пустой зоны «Личные» (контакт нет)")
    def is_personal_not_exist_zone_visible(self) -> bool:
        return self.is_displayed(ContactsPageLocators.NOT_EXIST_ZONE)
