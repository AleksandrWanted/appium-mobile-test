"""Page Object экрана «Звонки» приложения МТС Optimus (ru.mts.mvats).

Контент экрана построен на Jetpack Compose (заголовок, фильтры, список
звонков), поэтому устойчивее всего локализуется через accessibility id
(content-desc) и text (Android uiautomator). Нижнее навигационное меню и
элементы неавторизованного состояния — общие, вынесены в common_elements
(BottomNavLocators / UnauthorizedStateLocators).

Карточка звонка: кликабельный ряд в Compose-списке без resource-id и
content-desc у самого ряда. Имя, длительность и время звонка произвольны
(в списке может быть много карточек), поэтому карточка локализуется
структурно — кликабельный ряд с тремя TextView-детьми, а её поля берутся
позиционно из найденного ряда (get_call_cards / call_card_*). Тексты
зафиксированы только в статичных элементах: заголовок «Звонки», фильтры
«Все»/«Избранные».

Структура ряда (снята с реального устройства, Samsung S21 FE / Android 15):
    View (clickable, 6 детей)
      ├─ View        content-desc «Изображение статуса вызова»
      ├─ TextView    имя звонка/контакта (произвольный текст)
      ├─ TextView    длительность («1 мин 48 c»)
      ├─ View        content-desc «Успешная генерация самари» (опционально)
      ├─ TextView    время («16:11»)
      └─ View        content-desc «Избранный звонок» (опционально)
"""
from __future__ import annotations

import allure

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.by import By

from src.pages.base_page import BasePage


class CallsPageLocators:
    """Локаторы экрана «Звонки» (МТС Optimus).

    Тексты зашиты только в статичные элементы (заголовок, фильтры, кнопки);
    данные списка звонков — произвольные и множественные, поэтому карточка
    звонка ищется структурно (см. CALL_CARD).
    """

    # --- контейнер экрана ---
    SCREEN_ROOT = (AppiumBy.ID, "ru.mts.mvats:id/nav_host_fragment_calls")
    # Compose-контент экрана звонков
    COMPOSE_CONTENT = (AppiumBy.CLASS_NAME, "androidx.compose.ui.platform.ComposeView")

    # --- заголовок и поиск ---
    TITLE = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Звонки")')
    SEARCH_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "Search call button icon")

    # --- фильтры списка звонков ---
    FILTER_ALL = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Все")')
    FILTER_FAVORITES = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Избранные")')

    # --- список звонков ---
    # Карточка звонка — кликабельный ряд с ровно тремя прямыми TextView-детьми
    # (имя, длительность, время). Признак уникален на экране: у фильтров по
    # одному TextView, у FAB/поиска/кнопок — ноль, у промо-баннера два (снимок
    # неавторизованного экрана). Текстов нет намеренно: имя и время каждого
    # звонка произвольны, а карточек в списке много.
    # «Ровно N детей» в UiSelector не выразить (childSelector матчит «хотя бы
    # один» и цепляется за фильтры), поэтому XPath — осознанный последний
    # вариант, который не опирается ни на один меняющийся текст.
    CALL_CARD = (AppiumBy.XPATH,
                 "//android.view.View[@clickable='true' and "
                 "count(android.widget.TextView)=3]")

    # --- кнопка набора номера (FAB) ---
    DIALER_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "Dialer button icon")


class CallsPage(BasePage):
    """Экран «Звонки» приложения.

    Переход между вкладками нижнего меню — через pages.common (CommonElements),
    т.к. меню общее для всех экранов.
    """

    # --- проверки состояния экрана ---
    @allure.step("Проверить, что экран «Звонки» загружен")
    def is_loaded(self) -> bool:
        return self.is_displayed(CallsPageLocators.TITLE)

    @allure.step("Получить заголовок экрана")
    def get_title(self) -> str:
        return self.get_text(CallsPageLocators.TITLE)

    # --- поиск ---
    @allure.step("Открыть поиск по звонкам")
    def open_search(self):
        from src.pages.search_page import SearchPage

        self.tap(CallsPageLocators.SEARCH_BUTTON)
        return SearchPage(self.ctx)

    # --- фильтры ---
    @allure.step("Выбрать фильтр «Все»")
    def filter_all(self) -> None:
        self.tap(CallsPageLocators.FILTER_ALL)

    @allure.step("Выбрать фильтр «Избранные»")
    def filter_favorites(self) -> None:
        self.tap(CallsPageLocators.FILTER_FAVORITES)

    # --- список звонков ---
    def _card_text_views(self, card) -> list:
        """TextView-дети карточки в порядке разметки: имя, длительность, время."""
        return card.find_elements(By.CLASS_NAME, "android.widget.TextView")

    @allure.step("Получить карточки звонков в списке")
    def get_call_cards(self) -> list:
        """Все видимые карточки звонков. Пустой список — звонков нет."""
        return self.get_elements(CallsPageLocators.CALL_CARD)

    @allure.step("Проверить наличие хотя бы одного звонка в списке")
    def has_calls(self) -> bool:
        """Ожидание карточки (до 3 с) — список Compose может рендериться с запаздыванием."""
        return self.is_displayed(CallsPageLocators.CALL_CARD)

    @allure.step("Найти звонок по имени клиента «{name}»")
    def find_call_by_name(self, name: str, exact: bool = True):
        """Найти карточку звонка по имени клиента среди видимых в списке.

        Сравнение без учёта регистра, краевые пробелы отбрасываются (в
        разметке встречались имена с хвостовым пробелом). При exact=False
        достаточно вхождения имени как подстроки («иванов» найдёт
        «Иванов Иван»).

        Возвращает элемент карточки для дальнейших шагов (get_call_name,
        get_call_duration, call_is_favorite, open_call…) или None, если
        звонка нет в видимой части списка — список не скроллится.
        """
        wanted = name.strip().casefold()
        for card in self.get_call_cards():
            title = self._get_field_from_card(card, 0, "имя").strip().casefold()
            if title == wanted or (not exact and wanted in title):
                return card
        return None

    def _get_field_from_card(self, card, index: int, name: str) -> str:
        tvs = self._card_text_views(card)
        try:
            return tvs[index].text
        except IndexError:
            raise AssertionError(
                f"В карточке звонка нет поля «{name}» "
                f"(ожидалось >= {index + 1} TextView, найдено {len(tvs)})"
            )

    @allure.step("Получить имя клиента из карточки звонка")
    def get_call_name(self, card) -> str:
        """Имя звонка — 1-й TextView ряда (после статус-иконки)."""
        return self._get_field_from_card(card, 0, "имя")

    @allure.step("Получить длительность из карточки звонка")
    def get_call_duration(self, card) -> str:
        """Длительность — 2-й TextView ряда («1 мин 48 c»)."""
        return self._get_field_from_card(card, 1, "длительность")

    @allure.step("Получить время из карточки звонка")
    def get_call_time(self, card) -> str:
        """Время звонка — последний TextView ряда («16:11»)."""
        return self._get_field_from_card(card, -1, "время")

    @allure.step("Проверить отметку «Избранный» в карточке звонка")
    def call_is_favorite(self, card) -> bool:
        """Иконка «Избранный звонок» ищется внутри переданной карточки."""
        return bool(card.find_elements(
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().description("Избранный звонок")'))

    @allure.step("Проверить наличие саммари в карточке звонка")
    def call_has_summary(self, card) -> bool:
        """Иконка «Успешная генерация самари» ищется внутри карточки."""
        return bool(card.find_elements(
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().description("Успешная генерация самари")'))

    @allure.step("Открыть информацию о звонке")
    def open_call(self, card) -> None:
        self.driver.tap_element(card)

    # --- действия ---
    @allure.step("Открыть номеронабиратель (кнопка набора номера)")
    def open_dialer(self):
        from src.pages.dialer_page import DialerPage

        self.tap(CallsPageLocators.DIALER_BUTTON)
        return DialerPage(self.ctx)
