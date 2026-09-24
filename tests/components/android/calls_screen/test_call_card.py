"""Компонентные тесты экрана «Звонки»: карточка звонка.

Сценарий (component/android/calls_screen):
    «Открыть карточку звонка -> карточка открыта, есть элементы управления
    и детальная информация».
"""
from __future__ import annotations

import allure
import pytest

from src.pages.call_detail_page import CallDetailPageLocators


@allure.epic("Экран «Звонки»")
@allure.feature("Карточка звонка")
@pytest.mark.android
class TestCallCard:
    """Карточка звонка: открытие, элементы управления, детальная информация."""

    @allure.title(
        "Открыть карточку звонка -> карточка открыта, есть элементы управления "
        "и детальная информация"
    )
    @allure.description(
        "Сценарий component/android/calls_screen.\n\n"
        "Шаги: открыть вкладку «Звонки» и тапнуть по карточке звонка в списке.\n\n"
        "Ожидаемый результат: карточка звонка открылась; есть элементы управления "
        "(«Назад», индикатор «Избранный звонок», «Ещё», «Вызов», «О контакте»); "
        "на месте вкладки аудиоданных «Главное» / «Расшифровка»; "
        "детальная информация заполнена (дата/время, длительность, имя клиента, "
        "номер телефона, саммари); на «Главном» есть свёрнутый блок «Встречи и "
        "задачи», который разворачивается и сворачивается; вкладка «Расшифровка» "
        "показывает чат с репликами разговора; есть мини-плеер аудиозаписи; "
        "кнопка «Назад» возвращает к списку звонков."
    )
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.id("")
    def test_open_call_card(self, pages):
        """Открыть карточку звонка -> карточка открыта, есть элементы
        управления и детальная информация."""
        with allure.step("Открыть вкладку «Звонки»"):
            calls = pages.common.open_calls_tab()
            assert calls.is_loaded(), "Экран «Звонки» не загрузился"

        with allure.step("Проверить, что в списке есть хотя бы один звонок"):
            assert calls.has_calls(), "В списке нет ни одного звонка"

        with allure.step("Открыть карточку звонка тапом по первой карточке"):
            card = calls.get_call_cards()[0]
            calls.open_call(card)
            call_detail = pages.call_detail

        with allure.step("Проверить, что карточка звонка открылась"):
            assert call_detail.is_loaded(), "Карточка звонка не открылась"

        with allure.step("Проверить элементы управления карточки"):
            assert call_detail.is_back_button_visible(), "Нет кнопки «Назад»"
            assert call_detail.is_favorite_indicator_visible(), (
                "Нет индикатора «Избранный звонок»")
            assert call_detail.is_more_button_visible(), "Нет кнопки «Ещё»"
            assert call_detail.is_call_button_visible(), "Нет кнопки «Вызов»"
            assert call_detail.is_about_contact_visible(), "Нет кнопки «О контакте»"

        with allure.step("Проверить вкладки аудиоданных (Главное / Расшифровка)"):
            assert call_detail.get_summary_tab_label() == "Главное"
            assert call_detail.get_transcript_tab_label() == "Расшифровка"

        with allure.step("Проверить детальную информацию о звонке"):
            assert call_detail.get_datetime(), "Дата/время звонка пустые"
            assert call_detail.get_duration(), "Длительность звонка пустая"
            assert call_detail.get_caller_name(), "Имя клиента пустое"
            assert call_detail.get_phone_number(), "Номер телефона пустой"
            assert call_detail.get_summary_text(), "Саммари звонка пустое"

        with allure.step("Проверить наличие мини-плеера аудиозаписи"):
            assert call_detail.is_displayed(
                CallDetailPageLocators.MINI_PLAYER), "Нет мини-плеера аудиозаписи"

        with allure.step("Проверить, что блок «Встречи и задачи» свёрнут"):
            assert call_detail.is_tasks_card_visible(), (
                "Нет блока «Встречи и задачи»")
            assert call_detail.is_tasks_title_visible(), (
                "Нет заголовка «Встречи и задачи»")
            assert call_detail.is_tasks_collapsed(), (
                "Блок «Встречи и задачи» должен быть свёрнут по умолчанию")

        with allure.step("Развернуть блок «Встречи и задачи»"):
            call_detail.expand_tasks()
            assert call_detail.is_tasks_expanded(), (
                "После тапа «Развернуть» блок не развернулся")
            assert call_detail.is_add_to_calendar_button_visible(), (
                "Нет кнопки «Добавить в календарь» в развернутом блоке")

        with allure.step("Свернуть блок «Встречи и задачи»"):
            call_detail.collapse_tasks()
            assert call_detail.is_tasks_collapsed(), (
                "После тапа «Свернуть» блок не свернулся")

        with allure.step("Открыть вкладку «Расшифровка»"):
            call_detail.open_transcript_tab()

        with allure.step("Проверить расшифровку разговора"):
            assert call_detail.is_transcript_visible(), (
                "На вкладке «Расшифровка» нет чата с репликами")
            messages = call_detail.get_transcript_messages()
            assert messages, (
                "На вкладке «Расшифровка» нет ни одной реплики разговора")

        with allure.step("Вернуться на вкладку «Главное»"):
            call_detail.open_summary_tab()
            assert call_detail.get_summary_text(), (
                "После возврата на «Главное» саммари звонка пустое")

        with allure.step("Вернуться к списку звонков кнопкой «Назад»"):
            call_detail.tap_back()
            assert calls.is_loaded(), "После «Назад» не вернулись на экран «Звонки»"
