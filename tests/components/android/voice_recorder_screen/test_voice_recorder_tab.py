"""Компонентные тесты вкладки «ИИ-диктофон»: карточка записи.

Сценарий (component/android/voice_recorder_screen):
    «Открыть карточку записи (неавторизованное состояние) -> вкладка открыта,
    список записей и промо-блок заполнены, карточка содержит элементы
    управления и детальную информацию».

Тест выполняется в неавторизованном состоянии: сессия создаётся с
no_reset: false, поэтому приложение стартует с чистым профилем без входа
в MTS ID. Вкладка «ИИ-диктофон» при этом одинаково открывается и показывает
список записей и промо-блок.
"""
from __future__ import annotations

import allure
import pytest


@allure.epic("Вкладка «ИИ-диктофон»")
@allure.feature("Карточка записи (неавторизованный)")
@pytest.mark.android
class TestVoiceRecorderTab:
    """Карточка записи в неавторизованном состоянии: открытие, элементы
    управления, детальная информация.

    Сессия создаётся с no_reset: false — приложение стартует с чистым
    профилем, без входа в MTS ID.
    """

    @allure.title(
        "Открыть карточку записи (неавторизованный) -> вкладка открыта, список "
        "записей и промо-блок заполнены, карточка открыта, есть элементы "
        "управления и детальная информация"
    )
    @allure.description(
        "Сценарий component/android/voice_recorder_screen.\n\n"
        "Тест выполняется в неавторизованном состоянии (вход в MTS ID не "
        "выполнен — вкладка «Профиль» без карточки пользователя).\n\n"
        "Шаги: открыть вкладку «ИИ-диктофон» через нижнее меню (четвёртая "
        "вкладка, id voiceRecorderFlowFragment) и проверить её элементы "
        "(заголовок, список записей с полями карточки, промо-блок с "
        "карточками-действиями «ВОЙТИ И ЗАГРУЗИТЬ» / «ВОЙТИ И ЗАПИСАТЬ»); "
        "тапнуть по карточке записи в списке.\n\n"
        "Ожидаемый результат: вкладка открылась; список записей заполнен "
        "и заполнены все поля карточки записи; промо-блок виден, обе "
        "карточки-действия видны и подписаны ожидаемыми текстами; карточка "
        "записи открылась; в тулбаре есть кнопки «Назад» и «Дополнительные "
        "действия»; на месте вкладок аудиоданных «Главное» / «Расшифровка»; "
        "на «Главном» есть карточка «Встречи и задачи», развёрнутая по "
        "умолчанию, которая сворачивается и разворачивается; вкладка "
        "«Расшифровка» показывает реплики разговора; есть мини-плеер "
        "аудиозаписи; кнопка «Назад» возвращает к списку записей."
    )
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.id("")
    def test_open_record_card_unauthorized(self, pages):
        """Открыть карточку записи (неавторизованный) -> вкладка открыта,
        есть элементы управления и детальная информация."""
        with allure.step("Открыть вкладку «ИИ-диктофон»"):
            recorder = pages.common.open_voice_recorder_tab()
            assert recorder.is_loaded(), "Вкладка «ИИ-диктофон» не загрузилась"

        with allure.step("Проверить заголовок вкладки"):
            assert recorder.get_title() == "ИИ-диктофон", (
                "Заголовок вкладки не «ИИ-диктофон»")

        with allure.step("Проверить, что в списке есть хотя бы одна запись"):
            assert recorder.has_records(), "В списке нет ни одной записи"

        with allure.step("Проверить поля первой карточки записи"):
            card = recorder.get_record_cards()[0]
            assert recorder.get_record_title(card), "Заголовок записи пустой"
            assert recorder.get_record_meta(card), "Время записи пустое"
            assert recorder.get_record_separator(card) == "|", (
                "Нет разделителя «|» между временем и длительностью")
            assert recorder.get_record_duration(card), "Длительность записи пустая"
            assert recorder.record_has_summary(card), (
                "Нет иконки «Успешная генерация самари» в карточке записи")

        with allure.step("Проверить промо-блок «Запишите первую заметку…»"):
            assert recorder.is_promo_text_visible(), "Промо-текст не виден"
            assert "30 минут в неделю бесплатно" in recorder.get_promo_text(), (
                "Промо-текст не содержит «30 минут в неделю бесплатно»")

        with allure.step("Проверить карточки-действия промо-блока"):
            assert recorder.is_upload_action_visible(), (
                "Нет карточки «ВОЙТИ И ЗАГРУЗИТЬ»")
            assert recorder.is_record_action_visible(), (
                "Нет карточки «ВОЙТИ И ЗАПИСАТЬ»")
            assert recorder.get_upload_action_text() == "ВОЙТИ\nИ ЗАГРУЗИТЬ", (
                "Текст карточки загрузки не «ВОЙТИ И ЗАГРУЗИТЬ»")
            assert recorder.get_record_action_text() == "ВОЙТИ \nИ ЗАПИСАТЬ", (
                "Текст карточки записи не «ВОЙТИ И ЗАПИСАТЬ»")

        with allure.step("Открыть карточку записи тапом по первой карточке"):
            recorder.open_record(card)
            detail = pages.voice_record_detail

        with allure.step("Проверить, что карточка записи открылась"):
            assert detail.is_loaded(), "Карточка записи не открылась"

        with allure.step("Проверить элементы управления тулбара"):
            assert detail.is_back_button_visible(), "Нет кнопки «Назад»"
            assert detail.is_more_button_visible(), (
                "Нет кнопки «Дополнительные действия»")

        with allure.step("Проверить вкладки аудиоданных (Главное / Расшифровка)"):
            assert detail.get_summary_tab_label() == "Главное"
            assert detail.get_transcript_tab_label() == "Расшифровка"

        with allure.step("Проверить наличие мини-плеера аудиозаписи"):
            assert detail.is_mini_player_visible(), (
                "Нет мини-плеера аудиозаписи")

        with allure.step("Проверить, что карточка задач развёрнута по умолчанию"):
            assert detail.is_tasks_card_visible(), (
                "Нет карточки «Встречи и задачи»")
            assert detail.is_tasks_expanded(), (
                "Карточка «Встречи и задачи» не развёрнута по умолчанию")

        with allure.step("Свернуть карточку «Встречи и задачи»"):
            detail.collapse_tasks()
            assert detail.is_tasks_collapsed(), (
                "После тапа «Свернуть» карточка не свернулась")

        with allure.step("Развернуть карточку «Встречи и задачи»"):
            detail.expand_tasks()
            assert detail.is_tasks_expanded(), (
                "После тапа «Развернуть» карточка не развернулась")

        with allure.step("Открыть вкладку «Расшифровка»"):
            detail.open_transcript_tab()

        with allure.step("Проверить расшифровку разговора"):
            assert detail.is_transcript_visible(), (
                "На вкладке «Расшифровка» нет реплик разговора")
            assert detail.get_transcript_texts(), (
                "На вкладке «Расшифровка» нет ни одной реплики разговора")

        with allure.step("Вернуться на вкладку «Главное»"):
            detail.open_summary_tab()
            assert detail.is_tasks_card_visible(), (
                "После возврата на «Главное» нет карточки «Встречи и задачи»")

        with allure.step("Вернуться к списку записей кнопкой «Назад»"):
            detail.tap_back()
            assert recorder.is_loaded(), (
                "После «Назад» не вернулись на вкладку «ИИ-диктофон»")
