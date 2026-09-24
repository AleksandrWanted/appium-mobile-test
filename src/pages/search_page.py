"""Page Object экрана «Поиск звонков» приложения МТС Optimus (ru.mts.mvats).

Локаторы сняты с разметки реального устройства (Samsung S21 FE, Android 15).
Экран — нативный (не Compose): внутри nav_host_fragment_calls живут обычные
View с resource-id. Открывается с экрана «Звонки» кликом по иконке поиска
(CallsPageLocators.SEARCH_BUTTON); нижнее меню остаётся с активной вкладкой
«Звонки» — это destination внутри nav_host_fragment_calls.

Экран состоит из строки поиска (FrameLayout id=search: поле, иконка очистки,
кнопка «Отмена») и контейнера результатов (RecyclerView id=search_result).
В пустом состоянии внутри результата видна подсказка text_info. Иконка
очистки (clearIcon, desc «Очистить») присутствует в разметке только при
непустом тексте поля: проверку «иконка видна» делать после ввода текста,
проверку «отсутствует» — на пустом поле.

Строка поиска использует общие с экраном «Контакты» resource-id (search,
searchEditText) — это общий компонент; в тестах звонков не полагаться на
видимость id=search для различения экранов. Баннер входа и нижнее меню —
общие, живут в common_elements (BottomNavLocators / UnauthorizedStateLocators).
"""
from __future__ import annotations

import allure
from appium.webdriver.common.appiumby import AppiumBy

from src.pages.base_page import BasePage


class SearchPageLocators:
    """Локаторы экрана «Поиск звонков» (МТС Optimus).

    Приоритет локаторов: id (resource-id) → accessibility id (content-desc)
    → текст (uiautomator). XPath — последний вариант.
    """

    # --- контейнер экрана ---
    SCREEN_ROOT = (AppiumBy.ID, "ru.mts.mvats:id/nav_host_fragment_calls")

    # --- строка поиска (FrameLayout id=search) ---
    SEARCH_BAR = (AppiumBy.ID, "ru.mts.mvats:id/search")
    SEARCH_FIELD = (AppiumBy.ID, "ru.mts.mvats:id/searchEditText")
    # Появляется только при непустом тексте поля (desc «Очистить»).
    CLEAR_BUTTON = (AppiumBy.ID, "ru.mts.mvats:id/clearIcon")
    CANCEL_BUTTON = (AppiumBy.ANDROID_UIAUTOMATOR,
                     'new UiSelector().text("Отмена")')

    # --- результаты поиска (RecyclerView id=search_result) ---
    RESULT_LIST = (AppiumBy.ID, "ru.mts.mvats:id/search_result")
    # Подсказка пустого состояния; текст содержит перенос строки, поэтому
    # textContains вместо точного text.
    EMPTY_INFO = (AppiumBy.ANDROID_UIAUTOMATOR,
                  'new UiSelector().textContains("Поиск звонков")')


class SearchPage(BasePage):
    """Экран «Поиск звонков» приложения МТС Optimus.

    Открывается с экрана «Звонки»: pages.calls.open_search() (клик по иконке
    поиска возвращает SearchPage). Возврат на «Звонки» — close(), кнопка
    «Отмена». Нижнее меню и баннер входа — общие элементы
    (pages.common / common_elements).
    """

    # --- проверки состояния экрана ---
    @allure.step("Проверить, что экран поиска загружен")
    def is_loaded(self) -> bool:
        return self.is_displayed(SearchPageLocators.SEARCH_FIELD)

    # --- строка поиска ---
    @allure.step("Ввести запрос в поле поиска")
    def type_query(self, query: str) -> None:
        self.type_text(SearchPageLocators.SEARCH_FIELD, query)

    @allure.step("Получить текст поля поиска")
    def get_query(self) -> str:
        return self.get_text(SearchPageLocators.SEARCH_FIELD)

    @allure.step("Проверить видимость иконки очистки (только при непустом запросе)")
    def is_clear_button_visible(self) -> bool:
        return self.is_displayed(SearchPageLocators.CLEAR_BUTTON)

    # --- результаты ---
    @allure.step("Проверить видимость контейнера результатов")
    def is_result_list_visible(self) -> bool:
        return self.is_displayed(SearchPageLocators.RESULT_LIST)

    @allure.step("Проверить видимость подсказки пустого состояния")
    def is_empty_info_visible(self) -> bool:
        return self.is_displayed(SearchPageLocators.EMPTY_INFO)

    # --- действия ---
    @allure.step("Очистить запрос иконкой очистки")
    def clear_query(self) -> None:
        self.tap(SearchPageLocators.CLEAR_BUTTON)

    @allure.step("Закрыть поиск кнопкой «Отмена» (возврат на «Звонки»)")
    def close(self) -> None:
        self.tap(SearchPageLocators.CANCEL_BUTTON)
