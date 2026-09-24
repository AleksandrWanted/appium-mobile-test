"""Page Object экрана «Карточка звонка» (детальная информация о звонке)
приложения МТС Optimus (ru.mts.mvats).

Открывается с экрана «Звонки» тапом по карточке звонка (calls_page CallsPage.
open_call(card)); закрывается кнопкой «Назад» (BACK) в тулбаре.

Разметка нативная (не Compose, в отличие от списка звонков), локаторы сняты с
реального устройства (Samsung S21 FE, Android 15, версия приложения 2.15.0)
и уникальны на экране. Приоритет: id (resource-id) → текст (uiautomator).

Структура экрана (v2.15.0):
    toolbar: back, avatar, favourite_indicator (иконка «избранного» звонка),
             more («…»)
    contact info: datetime «Вчера, 20:45», dot «|», duration «1 мин 48 c»,
             status_call, name (имя клиента — TextView, кликабелен,
             открывает карточку контакта), phone «+7 (800) 250-22-20»
    button_panel: action_call «Вызов» (кнопка трубки; нажатие начинает
             звонок — осторожно в автотестах), aboutContactButton
             «О контакте» (обёрнут в LinearLayout aboutContact)
    tab_of_speech_data: две CardView-вкладки — summary «Главное»
             (выбрана по умолчанию) и speech_to_text «Расшифровка».
             Отдельной вкладки «Задачи» (id/ai_create) в v2.15.0 больше нет —
             встречи и задачи переехали в разворачиваемый блок на «Главном»
    content «Главное»: блок meeting_and_tasks (ComposeView) «Встречи и
             задачи» — сворачиваемая секция с кнопкой content-desc
             «Развернуть»/«Свернуть»; ниже summary_view — текст саммари
             звонка (длинный TextView) внутри ScrollView nsv
    content «Расшифровка»: чат в контейнере dialog — строки llItem
             (avatarTextView с инициалами, name, time, message)
    mini player: mini_player с button_play / image_button_mini_play
             (аудиозапись)

Неавторизованное состояние: вместо авторских данных подписки внизу экрана
кнопка buttonEnableSubAlternative «ВОЙТИ В МТС OPTIMUS» — та же, что на
остальных вкладках, вынесена в common_elements.
"""
from __future__ import annotations

import allure
from appium.webdriver.common.appiumby import AppiumBy

from src.pages.base_page import BasePage


class CallDetailPageLocators:
    """Локаторы экрана «Карточка звонка» (МТС Optimus).

    Приоритет локаторов: id (resource-id) → текст (uiautomator).
    resource-id на экране уникальны (проверено по разметке устройства).
    """

    # --- тулбар ---
    BACK_BUTTON = (AppiumBy.ID, "ru.mts.mvats:id/back")
    # Иконка «избранного» звонка в шапке; состояние (вкл/выкл) не проверяли.
    FAVORITE_INDICATOR = (AppiumBy.ID, "ru.mts.mvats:id/favourite_indicator")
    MORE_BUTTON = (AppiumBy.ID, "ru.mts.mvats:id/more")

    # --- карточка контакта ---
    # Строка «Сегодня, 16:11 | 1 мин 48 c»: дата-время и длительность раздельно.
    DATETIME = (AppiumBy.ID, "ru.mts.mvats:id/datetime")
    DURATION = (AppiumBy.ID, "ru.mts.mvats:id/duration")
    CALLER_NAME = (AppiumBy.ID, "ru.mts.mvats:id/name")
    PHONE_NUMBER = (AppiumBy.ID, "ru.mts.mvats:id/phone")

    # --- панель действий ---
    # Кнопка «Вызов» — начинает звонок на номер из карточки: в автотестах
    # проверять только видимость, не нажимать.
    ACTION_CALL = (AppiumBy.ID, "ru.mts.mvats:id/action_call")
    # Кнопка «О контакте» — в v2.15.0 обёрнута в LinearLayout aboutContact.
    ABOUT_CONTACT = (AppiumBy.ID, "ru.mts.mvats:id/aboutContactButton")

    # --- вкладки аудиоданных («Главное» / «Расшифровка») ---
    # С версии 2.15.0 вкладок две: «Задачи» (id/ai_create) удалена из тулбара
    # вкладок и переехала в блок «Встречи и задачи» на «Главном» (TASKS_CARD).
    TAB_SUMMARY = (AppiumBy.ID, "ru.mts.mvats:id/summary")
    TAB_TRANSCRIPT = (AppiumBy.ID, "ru.mts.mvats:id/speech_to_text")

    # --- контент вкладки «Главное» ---
    # Разворачиваемый блок «Встречи и задачи» (ComposeView): карточка с
    # content-desc «Развернуть» → «Свернуть». Развернутый вид содержит пункт
    # с датой и кнопкой content-desc «Кнопка добавить в календарь».
    TASKS_CARD = (AppiumBy.ID, "ru.mts.mvats:id/meeting_and_tasks")
    TASKS_AUTHORIZED_TITLE = (
        AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Встречи и задачи")')
    TASKS_SECTION_EXPAND = (
        AppiumBy.ACCESSIBILITY_ID, "Развернуть")
    TASKS_SECTION_COLLAPSE = (
        AppiumBy.ACCESSIBILITY_ID, "Свернуть")
    TASKS_CALENDAR_BUTTON = (
        AppiumBy.ACCESSIBILITY_ID, "Кнопка добавить в календарь")

    # Текст саммари «Главного» (внутри ScrollView nsv).
    SUMMARY_VIEW = (AppiumBy.ID, "ru.mts.mvats:id/summary_view")

    # --- контент вкладки «Расшифровка» ---
    # Скроллируемый контейнер чата; строки разговора — llItem с детьми
    # avatarTextView (инициалы), name (автор), time («00:01»), message (текст).
    TRANSCRIPT_CONTAINER = (AppiumBy.ID, "ru.mts.mvats:id/dialog")
    TRANSCRIPT_ITEM = (AppiumBy.ID, "ru.mts.mvats:id/llItem")
    TRANSCRIPT_MESSAGE = (AppiumBy.ID, "ru.mts.mvats:id/message")

    # --- мини-плеер аудиозаписи ---
    MINI_PLAYER = (AppiumBy.ID, "ru.mts.mvats:id/mini_player")
    PLAY_BUTTON = (AppiumBy.ID, "ru.mts.mvats:id/button_play")
    MINI_PLAY_ICON = (AppiumBy.ID, "ru.mts.mvats:id/image_button_mini_play")


class CallDetailPage(BasePage):
    """Карточка звонка приложения МТС Optimus.

    Открывается тапом по карточке в списке звонков: pages.calls.open_call(
    card). Закрытие — common.press_back() или tap_back() (кнопка «Назад»
    в тулбаре). Кнопку «Вызов» не нажимать — начинает звонок.
    """

    # --- проверки состояния экрана ---
    @allure.step("Проверить, что карточка звонка открыта")
    def is_loaded(self) -> bool:
        return self.is_displayed(CallDetailPageLocators.DATETIME)

    # --- заголовок ---
    @allure.step("Получить дату и время звонка")
    def get_datetime(self) -> str:
        return self.get_text(CallDetailPageLocators.DATETIME)

    @allure.step("Получить длительность звонка")
    def get_duration(self) -> str:
        return self.get_text(CallDetailPageLocators.DURATION)

    @allure.step("Получить имя клиента")
    def get_caller_name(self) -> str:
        return self.get_text(CallDetailPageLocators.CALLER_NAME)

    @allure.step("Получить номер телефона")
    def get_phone_number(self) -> str:
        return self.get_text(CallDetailPageLocators.PHONE_NUMBER)

    # --- элементы управления ---
    @allure.step("Проверить видимость кнопки «Назад»")
    def is_back_button_visible(self) -> bool:
        return self.is_displayed(CallDetailPageLocators.BACK_BUTTON)

    @allure.step("Проверить видимость индикатора «Избранный звонок»")
    def is_favorite_indicator_visible(self) -> bool:
        return self.is_displayed(CallDetailPageLocators.FAVORITE_INDICATOR)

    @allure.step("Проверить видимость кнопки «Ещё»")
    def is_more_button_visible(self) -> bool:
        return self.is_displayed(CallDetailPageLocators.MORE_BUTTON)

    @allure.step("Проверить видимость кнопки «Вызов»")
    def is_call_button_visible(self) -> bool:
        return self.is_displayed(CallDetailPageLocators.ACTION_CALL)

    @allure.step("Проверить видимость кнопки «О контакте»")
    def is_about_contact_visible(self) -> bool:
        return self.is_displayed(CallDetailPageLocators.ABOUT_CONTACT)

    # --- вкладки аудиоданных ---
    def _tab_label(self, tab_locator: tuple) -> str:
        """Видимый текст вкладки — TextView-ребёнок CardView."""
        from selenium.webdriver.common.by import By

        labels = self.get_elements(tab_locator)[0].find_elements(
            By.CLASS_NAME, "android.widget.TextView")
        return labels[0].text if labels else ""

    @allure.step("Получить название вкладки «Главное»")
    def get_summary_tab_label(self) -> str:
        return self._tab_label(CallDetailPageLocators.TAB_SUMMARY)

    @allure.step("Получить название вкладки «Расшифровка»")
    def get_transcript_tab_label(self) -> str:
        return self._tab_label(CallDetailPageLocators.TAB_TRANSCRIPT)

    # --- блок «Встречи и задачи» (вкладка «Главное») ---
    @allure.step("Проверить видимость блока «Встречи и задачи»")
    def is_tasks_card_visible(self) -> bool:
        return self.is_displayed(CallDetailPageLocators.TASKS_CARD)

    @allure.step("Проверить видимость заголовка «Встречи и задачи»")
    def is_tasks_title_visible(self) -> bool:
        return self.is_displayed(CallDetailPageLocators.TASKS_AUTHORIZED_TITLE)

    @allure.step("Проверить, что блок «Встречи и задачи» свёрнут")
    def is_tasks_collapsed(self) -> bool:
        """Свёрнут: доступна кнопка «Развернуть». Развернут: вместо неё
        «Свернуть», поэтому «Развернуть» не находится."""
        return self.is_displayed(CallDetailPageLocators.TASKS_SECTION_EXPAND)

    @allure.step("Проверить, что блок «Встречи и задачи» развернут")
    def is_tasks_expanded(self) -> bool:
        """Развернут: видна кнопка content-desc «Свернуть» и пункт списка
        задач с кнопкой «Добавить в календарь»."""
        return self.is_displayed(CallDetailPageLocators.TASKS_SECTION_COLLAPSE)

    @allure.step("Развернуть блок «Встречи и задачи»")
    def expand_tasks(self) -> None:
        self.tap(CallDetailPageLocators.TASKS_SECTION_EXPAND)

    @allure.step("Свернуть блок «Встречи и задачи»")
    def collapse_tasks(self) -> None:
        self.tap(CallDetailPageLocators.TASKS_SECTION_COLLAPSE)

    @allure.step("Проверить видимость кнопки «Добавить в календарь»")
    def is_add_to_calendar_button_visible(self) -> bool:
        """Кнопка присутствует в развернутом блоке (неавторизованное
        состояние — пункт «Зайти в МТС Optimus» без календаря)."""
        return self.is_displayed(
            CallDetailPageLocators.TASKS_CALENDAR_BUTTON)

    # --- детальная информация ---
    @allure.step("Получить текст саммари звонка")
    def get_summary_text(self) -> str:
        """Длинный текст саммари на вкладке «Главное»."""
        return self.get_text(CallDetailPageLocators.SUMMARY_VIEW)

    @allure.step("Открыть вкладку «Расшифровка»")
    def open_transcript_tab(self) -> None:
        self.tap(CallDetailPageLocators.TAB_TRANSCRIPT)

    @allure.step("Открыть вкладку «Главное»")
    def open_summary_tab(self) -> None:
        self.tap(CallDetailPageLocators.TAB_SUMMARY)

    # --- расшифровка разговора ---
    @allure.step("Проверить, что расшифровка разговора отображается")
    def is_transcript_visible(self) -> bool:
        """Живая разметка: контейнер чата и хотя бы одна реплика."""
        return (self.is_displayed(CallDetailPageLocators.TRANSCRIPT_CONTAINER)
                and self.is_displayed(CallDetailPageLocators.TRANSCRIPT_ITEM))

    @allure.step("Получить тексты реплик расшифровки")
    def get_transcript_messages(self) -> list[str]:
        """Все видимые реплики разговора (элементы message строк llItem).

        Возвращает список неупорядоченно сверху вниз по документной
        последовательности разметки (сверху вниз на экране).
        """
        return [el.text for el in self.get_elements(
            CallDetailPageLocators.TRANSCRIPT_MESSAGE) if el.text]

    # --- действия ---
    @allure.step("Вернуться к списку звонков (кнопка «Назад»)")
    def tap_back(self) -> None:
        self.tap(CallDetailPageLocators.BACK_BUTTON)
