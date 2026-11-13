"""Page Object экрана «Карточка записи» ИИ-диктофона (МТС Optimus).

Открывается с вкладки «ИИ-диктофон» тапом по карточке записи
(VoiceRecorderPage.open_record(card)); закрывается кнопкой «Назад»
(content-desc «Изображение вернуться назад»).

Разметка — Compose (контент внутри nav_host_fragment_voice_recorder),
resource-id почти нет, поэтому локализация через текст и accessibility id.

Структура экрана (снята с реального устройства, Samsung S21 FE / Android 15):
    toolbar: назад (desc «Изображение вернуться назад»), заголовок записи
             (произвольный), «Дополнительные действия» (desc)
    subtitle: строка «12 ноября, 19:04 | 2 мин 9 с» (дата, время, длительность)
    tab_of_speech_data: две вкладки — «Главное» (выбрана по умолчанию)
             и «Расшифровка»; кликабельные контейнеры с TextView-подписью
    content «Главное»: карточка «Встречи и задачи» (иконка + заголовок +
             кнопка сворачивания desc «Свернуть»/«Развернуть»); внутри —
             строки задач (текст, «Без срока», «Кнопка добавить в календарь»);
             ниже промо-текст про возможности ИИ-диктофона
    content «Расшифровка»: реплики разговора — на каждую: «Иконка спикера»,
             имя «Спикер …», таймкод («00:27») и текст реплики
    mini player: container_player → mini_player → image_button_mini_play
"""
from __future__ import annotations

import allure
from appium.webdriver.common.appiumby import AppiumBy

from src.pages.base_page import BasePage


class VoiceRecordDetailPageLocators:
    """Локаторы экрана «Карточка записи» ИИ-диктофона (МТС Optimus).

    Тексты зашиты в статичные элементы (вкладки, карточка задач); контент
    записи (заголовок, реплики) — произвольный, локализуется по desc/структурно.
    """

    # --- тулбар ---
    BACK_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "Изображение вернуться назад")
    MORE_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "Дополнительные действия")

    # --- вкладки аудиоданных (клик по подписи внутри кликабельного контейнера) ---
    SUMMARY_TAB = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Главное")')
    TRANSCRIPT_TAB = (AppiumBy.ANDROID_UIAUTOMATOR,
                      'new UiSelector().text("Расшифровка")')

    # --- вкладка «Главное»: карточка «Встречи и задачи» ---
    TITLE_TASKS = (AppiumBy.ANDROID_UIAUTOMATOR,
                   'new UiSelector().text("Встречи и задачи")')
    TOGGLE_COLLAPSE = (AppiumBy.ACCESSIBILITY_ID, "Свернуть")
    TOGGLE_EXPAND = (AppiumBy.ACCESSIBILITY_ID, "Развернуть")

    # --- вкладка «Расшифровка»: реплики разговора ---
    SPEAKER_ICON = (AppiumBy.ACCESSIBILITY_ID, "Иконка спикера")

    # --- мини-плеер ---
    MINI_PLAYER = (AppiumBy.ID, "ru.mts.mvats:id/mini_player")


class VoiceRecordDetailPage(BasePage):
    """Экран «Карточка записи» ИИ-диктофона.

    Открывается с вкладки «ИИ-диктофон»: pages.voice_recorder.open_record(card).
    Возврат на вкладку — tap_back().
    """

    # --- проверки состояния экрана ---
    @allure.step("Проверить, что карточка записи открылась (есть вкладки аудиоданных)")
    def is_loaded(self) -> bool:
        # Заголовок записи произвольный, поэтому ориентироваться на вкладку
        # «Главное»: она есть только на экране записи.
        return self.is_displayed(VoiceRecordDetailPageLocators.SUMMARY_TAB)

    # --- тулбар ---
    @allure.step("Проверить видимость кнопки «Назад»")
    def is_back_button_visible(self) -> bool:
        return self.is_displayed(VoiceRecordDetailPageLocators.BACK_BUTTON)

    @allure.step("Проверить видимость кнопки «Дополнительные действия»")
    def is_more_button_visible(self) -> bool:
        return self.is_displayed(VoiceRecordDetailPageLocators.MORE_BUTTON)

    # --- вкладки аудиоданных ---
    @allure.step("Получить подпись вкладки «Главное»")
    def get_summary_tab_label(self) -> str:
        return self.get_text(VoiceRecordDetailPageLocators.SUMMARY_TAB)

    @allure.step("Получить подпись вкладки «Расшифровка»")
    def get_transcript_tab_label(self) -> str:
        return self.get_text(VoiceRecordDetailPageLocators.TRANSCRIPT_TAB)

    @allure.step("Открыть вкладку «Расшифровка»")
    def open_transcript_tab(self) -> None:
        self.tap(VoiceRecordDetailPageLocators.TRANSCRIPT_TAB)

    @allure.step("Открыть вкладку «Главное»")
    def open_summary_tab(self) -> None:
        self.tap(VoiceRecordDetailPageLocators.SUMMARY_TAB)

    # --- вкладка «Главное»: карточка «Встречи и задачи» ---
    @allure.step("Проверить видимость карточки «Встречи и задачи»")
    def is_tasks_card_visible(self) -> bool:
        return self.is_displayed(VoiceRecordDetailPageLocators.TITLE_TASKS)

    @allure.step("Прокрутить до карточки «Встречи и задачи»")
    def scroll_to_tasks_card(self) -> None:
        self.driver.scroll_to(VoiceRecordDetailPageLocators.TITLE_TASKS,
                              timeout=self.timeout)

    @allure.step("Проверить, что карточка «Встречи и задачи» свёрнута")
    def is_tasks_collapsed(self) -> bool:
        """Свёрнутое состояние: видна кнопка «Развернуть»."""

        return self.is_displayed(VoiceRecordDetailPageLocators.TOGGLE_EXPAND)

    @allure.step("Проверить, что карточка «Встречи и задачи» развёрнута")
    def is_tasks_expanded(self) -> bool:
        """Развёрнутое состояние: видна кнопка «Свернуть»."""
        return self.is_displayed(VoiceRecordDetailPageLocators.TOGGLE_COLLAPSE)

    @allure.step("Развернуть карточку «Встречи и задачи»")
    def expand_tasks(self) -> None:
        self.tap(VoiceRecordDetailPageLocators.TOGGLE_EXPAND)

    @allure.step("Свернуть карточку «Встречи и задачи»")
    def collapse_tasks(self) -> None:
        self.tap(VoiceRecordDetailPageLocators.TOGGLE_COLLAPSE)

    # --- вкладка «Расшифровка»: реплики разговора ---
    @allure.step("Проверить наличие реплик на вкладке «Расшифровка»")
    def is_transcript_visible(self) -> bool:
        # Реплика идентифицируется иконкой спикера (desc уникален).
        return self.is_displayed(VoiceRecordDetailPageLocators.SPEAKER_ICON)

    @allure.step("Получить реплики разговора")
    def get_transcript_texts(self) -> list[str]:
        """Тексты реплик (TextView, к которым НЕ ведёт «Иконка спикера»).

        Спикеры, имя и таймкод завязаны на иконку слева; реплика — большой
        TextView справа/снизу. Берём все длинные тексты — их достаточно,
        чтобы убедиться, что расшифровка заполнена.
        """
        return [el for el in
                self.driver.find_elements((AppiumBy.CLASS_NAME,
                                           "android.widget.TextView"))
                if len(el.text) > 60]

    # --- мини-плеер ---
    @allure.step("Проверить наличие мини-плеера аудиозаписи")
    def is_mini_player_visible(self) -> bool:
        return self.is_displayed(VoiceRecordDetailPageLocators.MINI_PLAYER)

    # --- возвращение к списку ---
    @allure.step("Нажать «Назад» (возврат на вкладку «ИИ-диктофон»)")
    def tap_back(self) -> None:
        self.tap(VoiceRecordDetailPageLocators.BACK_BUTTON)
