"""Компонентные тесты авторизации через MTS ID.

Сценарии (component/android/authorization) для версии приложения 2.17.1+:
    - «Открыть вкладку «Профиль» -> нажать «Войти в МТС Optimus» -> ввести
      номер телефона -> ввести код из СМС -> профиль авторизован»;
    - «...нажать «Войти в МТС Optimus» -> в SSO-окне свайпнуть вниз ->
      окно входа закрылось, авторизация не выполнена»;
    - «Открыть вкладку «Звонки» -> нажать баннер «Войти в МТС Optimus» ->
      ввести номер телефона -> ввести код из СМС -> вкладка «Звонки»
      доступна, SSO-окно закрылось»;
    - «Открыть вкладку «Контакты» -> нажать баннер «Войти в МТС Optimus» ->
      ввести номер телефона -> ввести код из СМС -> вкладка «Контакты»
      доступна, SSO-окно закрылось».

MTS ID SSO открывается WebView-формой внутри bottom sheet
(ru.mts.mvats:id/design_bottom_sheet). WebView не отладочный (нет
_devtools_remote), но все элементы видны в нативном a11y-дереве —
локаторы работают как для нативных экранов, отдельный контекст не нужен.
Тот же bottom sheet — цель отмены входа: свайп вниз за верхнюю кромку
закрывает окно без входа (LoginPage.cancel_login_by_swipe_down тянет сам
container sheet'а, а не контент WebView внутри).

Флоу экранный: ввод номера -> «Введите код из СМС»; перед вводом номера
может показываться fast-track «Рады видеть вас снова» (SDK помнит номер) —
Behavior нестабилен между состояниями SDK, первый экран приводится к вводу
номера через LoginPage.open_phone_input_screen (fast-track опционален).
Флоу проходит целиком в LoginPage; номер и код
берутся из тестовых кредов (.env: MSISDN, VERIFICATION_CODE).

Пер-тестовое чистое состояние гарантирует no_reset: false (driver
function-scoped): Appium делает pm clear при создании сессии, каждый
тест стартует с чистым приложением и неавторизованным профилем.
"""
from __future__ import annotations

import allure
import pytest

from src.pages.calls_page import CallsPageLocators
from src.pages.contacts_page import ContactsPageLocators
from src.pages.login_page import LoginPageLocators
from tests.constants import (
    NEGATIVE_PROBE_TIMEOUT,
    PAGE_LOAD_TIMEOUT,
)


@allure.epic("Авторизация")
@allure.feature("Вход через MTS ID")
@pytest.mark.android
class TestMtsIdLogin:
    """Вход через MTS ID со вкладок «Профиль»/«Звонки»/«Контакты», отмена входа свайпом.

    Точка входа различает сценарии: кнопка входа на неавторизованной
    вкладке «Профиль» (login_from_profile_tab), баннер на вкладках
    «Звонки» и «Контакты» (login_from_calls_tab,
    login_from_contacts_tab); отмена — свайп SSO-окна вниз.
    """

    @allure.title("Вход с вкладки «Профиль»: номер телефона и код из СМС -> профиль авторизован")
    @allure.description(
        "Сценарий component/android/authorization (приложение 2.17.1+). "
        "Вход запускается из вкладки «Профиль».\n\n"
        "Шаги: открыть вкладку «Профиль» (неавторизованное состояние); нажать "
        "кнопку входа «Войти в МТС Optimus»; дождаться открытия SSO-формы и "
        "прогрузки первого экрана флоу (fast-track «Рады видеть вас снова» "
        "опционален — при необходимости «Войти с другим номером»); на "
        "экране ввода номера ввести MSISDN "
        "тестового пользователя и нажать «ДАЛЕЕ»; дождаться экрана «Введите "
        "код из СМС» и ввести VERIFICATION_CODE; дождаться закрытия SSO "
        "bottom sheet; проверить карточку авторизованного профиля.\n\n"
        "Ожидаемый результат: вход завершён, на вкладке «Профиль» видна "
        "карточка пользователя (аватар «Изображение МТС ID»), а кнопка входа "
        "«ВОЙТИ В МТС OPTIMUS» исчезла."
    )
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.id("")
    def test_login_from_profile_tab(self, pages):
        """Вход со вкладки «Профиль»: номер + код из СМС -> авторизованный профиль."""
        with allure.step("Перейти на вкладку «Профиль» (неавторизованный)"):
            login = pages.common.open_login_screen()

        with allure.step("Дождаться открытия и загрузки SSO-формы MTS ID"):
            assert login.wait_opened(), "Экран входа MTS ID не открылся"
            assert login.wait_form_loaded(), (
                "Форма входа не загрузилась (fast-track/номер/код не появились)")

        with allure.step("Войти с другим номером (fast-track опционален)"):
            # Первый экран зависит от состояния SDK: fast-track «Рады видеть
            # вас снова» или сразу ввод номера. open_phone_input_screen
            # приводит форму к вводу номера в обоих случаях.
            login.open_phone_input_screen()

        with allure.step("Ввести номер телефона и нажать «ДАЛЕЕ»"):
            login.type_phone(pages.ctx.credentials.msisdn)
            login.submit_phone()

        with allure.step("Проверить, что открылся экран «Введите код из СМС»"):
            assert login.is_otp_screen(), (
                "Экран ввода кода из СМС не открылся")

        with allure.step("Ввести код из СМС"):
            login.type_otp(pages.ctx.credentials.verification_code)

        with allure.step("Дождаться завершения входа"):
            assert login.wait_login_completed(), (
                "Вход не завершился: карточка пользователя не появилась")

        with allure.step("Проверить авторизованное состояние профиля"):
            profile = pages.profile
            assert profile.is_user_card_visible(), (
                "Карточка пользователя не видна после входа")
            assert not profile.is_login_card_visible(), (
                "Кнопка входа «ВОЙТИ В МТС OPTIMUS» осталась на экране")

    @allure.title("Свайп окна MTS ID вниз -> окно закрылось, авторизация не выполнена")
    @allure.description(
        "Сценарий component/android/authorization (приложение 2.17.1+).\n\n"
        "Шаги: открыть вкладку «Профиль» (неавторизованное состояние); нажать "
        "кнопку входа «Войти в МТС Optimus»; дождаться открытия SSO-формы и "
        "прогрузки первого экрана флоу; выполнить свайп окна MTS ID вниз (закрытие "
        "bottom sheet жестом за верхнюю кромку); дождаться закрытия окна; "
        "проверить неавторизованное состояние вкладки «Профиль».\n\n"
        "Ожидаемый результат: окно входа MTS ID закрылось свайпом, вход НЕ "
        "выполнен — пользователь остаётся на вкладке «Профиль» в "
        "неавторизованном состоянии: кнопка входа «ВОЙТИ В МТС OPTIMUS» на "
        "месте, карточка пользователя (аватар «Изображение МТС ID») "
        "отсутствует."
    )
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.id("")
    def test_login_cancel_by_swipe_down(self, pages):
        """Свайп окна MTS ID вниз -> окно закрылось, вход не выполнен."""
        with allure.step("Открыть вкладку «Профиль» (неавторизованный)"):
            login = pages.common.open_login_screen()
            profile = pages.profile

        with allure.step("Проверить карточку пользователя отсутствует до входа"):
            assert not profile.driver.is_present(
                LoginPageLocators.MTS_ID_AVATAR, timeout=NEGATIVE_PROBE_TIMEOUT), (
                "Карточка пользователя видна до входа — состояние не чистое")

        with allure.step("Дождаться открытия и загрузки SSO-формы MTS ID"):
            assert login.wait_opened(), "Экран входа MTS ID не открылся"
            assert login.wait_form_loaded(), (
                "Форма входа не загрузилась (fast-track/номер/код не появились)")

        with allure.step("Свайпнуть окно MTS ID вниз для отмены входа"):
            login.cancel_login_by_swipe_down()

        with allure.step("Проверить, что окно входа MTS ID закрылось"):
            assert not profile.driver.is_present(
                LoginPageLocators.SCREEN_ROOT, timeout=NEGATIVE_PROBE_TIMEOUT), (
                "SSO-окно MTS ID осталось на экране после свайпа вниз")

        with allure.step("Проверить, что пользователь не авторизован"):
            assert profile.is_login_card_visible(), (
                "Кнопка входа «ВОЙТИ В МТС OPTIMUS» не видна — вход был "
                "выполнен или экран не вернулся на «Профиль»")
            assert not profile.driver.is_present(
                LoginPageLocators.MTS_ID_AVATAR, timeout=NEGATIVE_PROBE_TIMEOUT), (
                "Карточка пользователя видна — вход выполнен вопреки отмене")

    @allure.title("Вход через баннер на вкладке «Звонки» -> окно закрылось, звонки доступны")
    @allure.description(
        "Сценарий component/android/authorization (приложение 2.17.1+).\n\n"
        "Шаги: открыть вкладку «Звонки» (неавторизованное состояние); нажать "
        "баннер «Войти в МТС Optimus»; дождаться открытия SSO-формы и "
        "прогрузки первого экрана флоу (fast-track «Рады видеть вас снова» "
        "опционален — при необходимости «Войти с другим номером»); на "
        "экране ввода номера ввести MSISDN "
        "тестового пользователя и нажать «ДАЛЕЕ»; дождаться экрана «Введите "
        "код из СМС» и ввести VERIFICATION_CODE; дождаться закрытия SSO "
        "bottom sheet; проверить, что вкладка «Звонки» доступна.\n\n"
        "Ожидаемый результат: вход завершён, SSO-окно закрылось — "
        "пользователь остаётся на вкладке «Звонки»: заголовок «Звонки» и "
        "контент экрана доступны (заголовок + кнопка поиска; FAB набора "
        "номера на авторизованном экране заменён промо-кнопкой ИИ-диктофона), "
        "баннер входа «Войти в МТС Optimus» исчез."
    )
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.id("")
    def test_login_from_calls_tab(self, pages):
        """Вход, запущенный с вкладки «Звонки» -> SSO закрылось, звонки доступны."""
        with allure.step("Открыть вкладку «Звонки» (неавторизованный)"):
            calls = pages.common.open_calls_tab()
            assert calls.is_loaded(), "Вкладка «Звонки» не загрузилась"

        with allure.step("Проверить баннер «Войти в МТС Optimus» на вкладке «Звонки»"):
            banner = pages.common.unauthorized_state.LOGIN_BANNER_BUTTON
            assert pages.ctx.driver.is_present(banner, timeout=PAGE_LOAD_TIMEOUT), (
                "Баннер входа «Войти в МТС Optimus» не виден на вкладке «Звонки»")

        with allure.step("Нажать баннер «Войти в МТС Optimus»"):
            pages.common.tap_login_banner()

        with allure.step("Дождаться открытия и загрузки SSO-формы MTS ID"):
            login = pages.login
            assert login.wait_opened(), "Экран входа MTS ID не открылся"
            assert login.wait_form_loaded(), (
                "Форма входа не загрузилась (fast-track/номер/код не появились)")

        with allure.step("Войти с другим номером (fast-track опционален)"):
            # Первый экран зависит от состояния SDK: fast-track «Рады видеть
            # вас снова» или сразу ввод номера. open_phone_input_screen
            # приводит форму к вводу номера в обоих случаях.
            login.open_phone_input_screen()

        with allure.step("Ввести номер телефона и нажать «ДАЛЕЕ»"):
            login.type_phone(pages.ctx.credentials.msisdn)
            login.submit_phone()

        with allure.step("Проверить, что открылся экран «Введите код из СМС»"):
            assert login.is_otp_screen(), (
                "Экран ввода кода из СМС не открылся")

        with allure.step("Ввести код из СМС"):
            login.type_otp(pages.ctx.credentials.verification_code)

        with allure.step("Дождаться закрытия SSO-окна после входа"):
            assert login.wait_sheet_closed(), (
                "SSO-окно MTS ID не закрылось: контейнер mts_id остался "
                "в разметке после успешного входа")

        with allure.step("Дождаться возврата вкладки «Звонки» после закрытия SSO"):
            # Сразу после закрытия SSO приложение 1–2 секунды дорисовывает
            # вкладку (промежуточное состояние: хвост sheet'а, контента нет) —
            # тап по меню в этот момент бесполезен, ждём рендер контента.
            assert pages.ctx.driver.is_present(
                CallsPageLocators.SCREEN_ROOT, timeout=PAGE_LOAD_TIMEOUT), (
                "Вкладка «Звонки» не вернулась после входа")

        with allure.step("Проверить вкладку «Звонки» после входа"):
            assert calls.is_loaded(), (
                "Заголовок «Звонки» не виден после входа")
            assert pages.ctx.driver.is_present(
                CallsPageLocators.SEARCH_BUTTON, timeout=PAGE_LOAD_TIMEOUT), (
                "Кнопка поиска по звонкам не видна на вкладке «Звонки»")
            banner = pages.common.unauthorized_state.LOGIN_BANNER_BUTTON
            assert not pages.ctx.driver.is_present(banner, timeout=NEGATIVE_PROBE_TIMEOUT), (
                "Баннер входа «Войти в МТС Optimus» остался — вход не применён")

    @allure.title("Вход через баннер на вкладке «Контакты» -> окно закрылось, контакты доступны")
    @allure.description(
        "Сценарий component/android/authorization (приложение 2.17.1+).\n\n"
        "Шаги: открыть вкладку «Контакты» (неавторизованное состояние); нажать "
        "баннер «Войти в МТС Optimus»; дождаться открытия SSO-формы и "
        "прогрузки первого экрана флоу (fast-track «Рады видеть вас снова» "
        "опционален — при необходимости «Войти с другим номером»); на "
        "экране ввода номера ввести MSISDN "
        "тестового пользователя и нажать «ДАЛЕЕ»; дождаться экрана «Введите "
        "код из СМС» и ввести VERIFICATION_CODE; дождаться закрытия SSO "
        "bottom sheet; проверить, что вкладка «Контакты» доступна.\n\n"
        "Ожидаемый результат: вход завершён, SSO-окно закрылось — "
        "пользователь остаётся на вкладке «Контакты»: заголовок «Контакты» и "
        "контент вкладки «Optimus» доступны (список контактов), баннер входа "
        "«Войти в МТС Optimus» исчез."
    )
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.id("")
    def test_login_from_contacts_tab(self, pages):
        """Вход, запущенный с вкладки «Контакты» -> SSO закрылось, контакты доступны."""
        with allure.step("Открыть вкладку «Контакты» (неавторизованный)"):
            contacts = pages.common.open_contacts_tab()
            assert contacts.is_loaded(), "Вкладка «Контакты» не загрузилась"

        with allure.step("Проверить баннер «Войти в МТС Optimus» на вкладке «Контакты»"):
            banner = pages.common.unauthorized_state.LOGIN_BANNER_BUTTON
            assert pages.ctx.driver.is_present(banner, timeout=PAGE_LOAD_TIMEOUT), (
                "Баннер входа «Войти в МТС Optimus» не виден на вкладке «Контакты»")

        with allure.step("Нажать баннер «Войти в МТС Optimus»"):
            pages.common.tap_login_banner()

        with allure.step("Дождаться открытия и загрузки SSO-формы MTS ID"):
            login = pages.login
            assert login.wait_opened(), "Экран входа MTS ID не открылся"
            assert login.wait_form_loaded(), (
                "Форма входа не загрузилась (fast-track/номер/код не появились)")

        with allure.step("Войти с другим номером (fast-track опционален)"):
            # Первый экран зависит от состояния SDK: fast-track «Рады видеть
            # вас снова» или сразу ввод номера. open_phone_input_screen
            # приводит форму к вводу номера в обоих случаях.
            login.open_phone_input_screen()

        with allure.step("Ввести номер телефона и нажать «ДАЛЕЕ»"):
            login.type_phone(pages.ctx.credentials.msisdn)
            login.submit_phone()

        with allure.step("Проверить, что открылся экран «Введите код из СМС»"):
            assert login.is_otp_screen(), (
                "Экран ввода кода из СМС не открылся")

        with allure.step("Ввести код из СМС"):
            login.type_otp(pages.ctx.credentials.verification_code)

        with allure.step("Дождаться закрытия SSO-окна после входа"):
            assert login.wait_sheet_closed(), (
                "SSO-окно MTS ID не закрылось: контейнер mts_id остался "
                "в разметке после успешного входа")

        with allure.step("Дождаться возврата вкладки «Контакты» после закрытия SSO"):
            # Как и на «Звонках»: сразу после закрытия SSO приложение
            # 1–2 секунды дорисовывает вкладку (хвост sheet'а, контента
            # нет) — тап по меню бесполезен, ждём рендер контента.
            assert pages.ctx.driver.is_present(
                ContactsPageLocators.SCREEN_ROOT, timeout=PAGE_LOAD_TIMEOUT), (
                "Вкладка «Контакты» не вернулась после входа")

        with allure.step("Проверить вкладку «Контакты» после входа"):
            assert contacts.is_loaded(), (
                "Заголовок «Контакты» не виден после входа")
            assert pages.ctx.driver.is_present(
                ContactsPageLocators.CLIENT_LIST, timeout=PAGE_LOAD_TIMEOUT), (
                "Список контактов не виден на вкладке «Контакты»")
            banner = pages.common.unauthorized_state.LOGIN_BANNER_BUTTON
            assert not pages.ctx.driver.is_present(banner, timeout=NEGATIVE_PROBE_TIMEOUT), (
                "Баннер входа «Войти в МТС Optimus» остался — вход не применён")
