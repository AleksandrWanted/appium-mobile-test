"""Page Object вкладки «ИИ-диктофон» приложения МТС Optimus (ru.mts.mvats).

Локаторы сняты с разметки реального устройства (Samsung S21 FE, Android 15,
версия приложения 2.17.1). Контент вкладки — Compose (как список звонков):
внутри nav_host_fragment_voice_recorder живут Compose-элементы без
resource-id, поэтому локализация через текст и accessibility id.

Экран состоит из заголовка «ИИ-диктофон» с иконкой поиска (общий
Search call button icon, как на экране «Звонки»), списка записей и блока
промо (виден, пока записей нет / список короткий): «Запишите первую заметку
или разговор — 30 минут в неделю бесплатно» и две карточки-действия
«ВОЙТИ И ЗАГРУЗИТЬ» / «ВОЙТИ И ЗАПИСАТЬ» — обе ведут на вход MTS ID.

Карточка записи в списке: кликабельный View с текстами — заголовок записи
(произвольный), строка «время | длительность», опционально иконка
«Успешная генерация самари». Время и длительность разделяются «|», но это
разные TextView, поэтому карточка локализуется структурно: кликабельный ряд
с TextView-детьми, поля берутся позиционно (аналог карточки звонка —
get_record_cards / get_record_*).

Нижнее меню — общее, четыре вкладки: voiceRecorderFlowFragment добавлен
четвёртой (после «Звонки» и «Контакты», перед «Профиль»); живёт в
common_elements (BottomNavLocators).
"""
from __future__ import annotations

import allure
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.by import By

from src.pages.base_page import BasePage


class VoiceRecorderPageLocators:
    """Локаторы вкладки «ИИ-диктофон» (МТС Optimus).

    Тексты зашиты только в статичные элементы (заголовок, промо, кнопки);
    данные списка записей — произвольные, поэтому карточка записи ищется
    структурно, а её поля берутся позиционно.
    """

    # --- контейнер экрана ---
    SCREEN_ROOT = (AppiumBy.ID, "ru.mts.mvats:id/nav_host_fragment_voice_recorder")

    # --- заголовок и поиск ---
    TITLE = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("ИИ-диктофон")')
    SEARCH_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "Search call button icon")
    # Кнопка загрузки записи в тулбаре вверху справа: content-desc совпадает
    # с кнопкой поиска на «Звонках» (одна иконка), но по смыслу это загрузка.
    UPLOAD_TOOLBAR_BUTTON = SEARCH_BUTTON

    # --- список записей ---
    # Карточка записи — кликабельный ряд, у которого тексты живут в прямых
    # TextView-детях. Признаку «кликабельный ряд с >= 2 TextView» на экране
    # удовлетворяет только карточка: у карточек-действий промо по одному
    # TextView («ВОЙТИ И ЗАГРУЗИТЬ»/«ВОЙТИ И ЗАПИСАТЬ»), у фильтров и прочих
    # элементов — ноль. «>= N детей» в UiSelector не выразить — XPath.
    RECORD_CARD = (AppiumBy.XPATH,
                   "//android.view.View[@clickable='true' and "
                   "count(android.widget.TextView)>=2]")

    # --- промо-блок (неавторизованное / пустое состояние) ---
    PROMO_TEXT = (AppiumBy.ANDROID_UIAUTOMATOR,
                  'new UiSelector().textStartsWith("Запишите первую заметку")')
    UPLOAD_ACTION = (AppiumBy.ACCESSIBILITY_ID, "Иконка загрузить")
    RECORD_ACTION = (AppiumBy.ACCESSIBILITY_ID, "Иконка записать")
    # Тексты карточек-действий — для проверки надписей. В разметке перенос
    # строки настоящий (text() матчит его как '\n'), во второй карточке
    # ещё и пробел перед переносом — тексты выверены по repr с устройства.
    UPLOAD_ACTION_TEXT = (AppiumBy.ANDROID_UIAUTOMATOR,
                          'new UiSelector().text("ВОЙТИ\nИ ЗАГРУЗИТЬ")')
    RECORD_ACTION_TEXT = (AppiumBy.ANDROID_UIAUTOMATOR,
                          'new UiSelector().text("ВОЙТИ \nИ ЗАПИСАТЬ")')


class VoiceRecorderPage(BasePage):
    """Вкладка «ИИ-диктофон» приложения МТС Optimus.

    Переход между вкладками нижнего меню — через pages.common
    (CommonElements), т.к. меню общее для всех экранов.
    """

    # --- проверки состояния экрана ---
    @allure.step("Проверить, что вкладка «ИИ-диктофон» загружена")
    def is_loaded(self) -> bool:
        return self.is_displayed(VoiceRecorderPageLocators.TITLE)

    @allure.step("Получить заголовок вкладки")
    def get_title(self) -> str:
        return self.get_text(VoiceRecorderPageLocators.TITLE)

    # --- поиск ---
    @allure.step("Открыть поиск по записям")
    def open_search(self):
        from src.pages.search_page import SearchPage

        self.tap(VoiceRecorderPageLocators.SEARCH_BUTTON)
        return SearchPage(self.ctx)

    # --- список записей ---
    def _card_text_views(self, card) -> list:
        """TextView-дети карточки: заголовок записи, время, длительность."""
        return card.find_elements(By.CLASS_NAME, "android.widget.TextView")

    @allure.step("Получить карточки записей в списке")
    def get_record_cards(self) -> list:
        """Все видимые карточки записей. Пустой список — записей нет."""
        return self.get_elements(VoiceRecorderPageLocators.RECORD_CARD)

    @allure.step("Проверить наличие хотя бы одной записи в списке")
    def has_records(self) -> bool:
        """Ожидание карточки (до 3 с) — список Compose рендерится с запаздыванием."""
        return self.is_displayed(VoiceRecorderPageLocators.RECORD_CARD)

    def _get_field_from_card(self, card, index: int, name: str) -> str:
        tvs = self._card_text_views(card)
        try:
            return tvs[index].text
        except IndexError:
            raise AssertionError(
                f"В карточке записи нет поля «{name}» "
                f"(ожидалось >= {index + 2} TextView, найдено {len(tvs)})"
            )

    @allure.step("Получить заголовок записи из карточки")
    def get_record_title(self, card) -> str:
        """Заголовок записи — 1-й TextView ряда (произвольный текст)."""
        return self._get_field_from_card(card, 0, "заголовок")

    @allure.step("Получить строку «время | длительность» из карточки записи")
    def get_record_meta(self, card) -> str:
        """Метаданные — 2-й TextView ряда («18:41 | 2 мин 9 с»)."""
        return self._get_field_from_card(card, 1, "метаданные")

    @allure.step("Получить разделитель «|» из карточки записи")
    def get_record_separator(self, card) -> str:
        """Разделитель времени и длительности — 3-й TextView ряда."""
        return self._get_field_from_card(card, 2, "разделитель")

    @allure.step("Получить длительность из карточки записи")
    def get_record_duration(self, card) -> str:
        """Длительность — 4-й TextView ряда («2 мин 9 с»)."""
        return self._get_field_from_card(card, 3, "длительность")

    @allure.step("Проверить наличие саммари в карточке записи")
    def record_has_summary(self, card) -> bool:
        """Иконка «Успешная генерация самари» ищется внутри карточки."""
        return bool(card.find_elements(
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().description("Успешная генерация самари")'))

    @allure.step("Открыть запись")
    def open_record(self, card) -> None:
        self.driver.tap_element(card)

    # --- промо-блок ---
    @allure.step("Проверить видимость промо-текста «Запишите первую заметку…»")
    def is_promo_text_visible(self) -> bool:
        return self.is_displayed(VoiceRecorderPageLocators.PROMO_TEXT)

    @allure.step("Получить промо-текст")
    def get_promo_text(self) -> str:
        return self.get_text(VoiceRecorderPageLocators.PROMO_TEXT)

    @allure.step("Проверить видимость карточки действия «ВОЙТИ И ЗАГРУЗИТЬ»")
    def is_upload_action_visible(self) -> bool:
        return self.is_displayed(VoiceRecorderPageLocators.UPLOAD_ACTION)

    @allure.step("Проверить видимость карточки действия «ВОЙТИ И ЗАПИСАТЬ»")
    def is_record_action_visible(self) -> bool:
        return self.is_displayed(VoiceRecorderPageLocators.RECORD_ACTION)

    @allure.step("Проверить текст карточки «ВОЙТИ И ЗАГРУЗИТЬ»")
    def get_upload_action_text(self) -> str:
        return self.get_text(VoiceRecorderPageLocators.UPLOAD_ACTION_TEXT)

    @allure.step("Проверить текст карточки «ВОЙТИ И ЗАПИСАТЬ»")
    def get_record_action_text(self) -> str:
        return self.get_text(VoiceRecorderPageLocators.RECORD_ACTION_TEXT)

    # --- точки входа в авторизацию (неавторизованное состояние) ---
    # Три элемента вкладки в неавторизованном состоянии открывают одно и то
    # же SSO-окно MTS ID: обе карточки-действия промо-блока и кнопка
    # загрузки записи в тулбаре.
    @allure.step("Нажать карточку «ВОЙТИ И ЗАГРУЗИТЬ»")
    def tap_upload_action(self) -> None:
        self.tap(VoiceRecorderPageLocators.UPLOAD_ACTION)

    @allure.step("Нажать карточку «ВОЙТИ И ЗАПИСАТЬ»")
    def tap_record_action(self) -> None:
        self.tap(VoiceRecorderPageLocators.RECORD_ACTION)

    @allure.step("Нажать кнопку загрузки записи в тулбаре (вверху справа)")
    def tap_upload_toolbar_button(self) -> None:
        self.tap(VoiceRecorderPageLocators.UPLOAD_TOOLBAR_BUTTON)
