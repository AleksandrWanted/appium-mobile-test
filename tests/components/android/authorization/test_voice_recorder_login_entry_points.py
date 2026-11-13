"""Компонентные тесты авторизации: вход с точек входа вкладки «ИИ-диктофон».

Сценарии (component/android/authorization):
    «В неавторизованном состоянии на вкладке «ИИ-диктофон» нажать точку
    входа в авторизацию -> открылась форма входа MTS ID -> ввести номер
    телефона и код из СМС -> профиль авторизован».

Проверяются три точки входа (отдельный тест на каждую):
    - карточка промо-блока «ВОЙТИ И ЗАГРУЗИТЬ»;
    - карточка промо-блока «ВОЙТИ И ЗАПИСАТЬ»;
    - кнопка загрузки записи в тулбаре вверху справа (content-desc
      Search call button icon — та же иконка, что у поиска на «Звонках»).
Точка входа отличает сценарии так же, как в test_mts_id_login (кнопка
на «Профиле», баннер на «Звонках»/«Контактах»).

Вход выполняется по-настоящему: fast-track (если SDK помнит номер —
«Войти с другим номером») -> ввод MSISDN -> «ДАЛЕЕ» -> экран «Введите
код из СМС» -> VERIFICATION_CODE (вход выполняется автоматически после
последней цифры). Форма входа — LoginPage.pass_login_flow: вход запущен
с вкладки «ИИ-диктофон», после закрытия SSO приложение остаётся на этой
вкладке (не на «Профиле»), поэтому финальное ожидание аватара в SSO не
подходит — вместо него проверяем вкладки.

Сразу после ввода кода SSO закрывается сам, а приложение на 1–2 секунды
показывает переходный экран загрузки авторизации
(nav_host_fragment_auth) — авторизованное состояние проверяем после
этого перехода: карточка пользователя на «Профиле» (кнопка входа
исчезла) и отсутствие промо-блока на вкладке «ИИ-диктофон».

Тесты стартуют в неавторизованном состоянии: сессия создаётся с
no_reset: false, приложение стартует с чистым профилем без входа в
MTS ID. Номер и код берутся из credentials (.env: MSISDN,
VERIFICATION_CODE); без них тест сразу падает с понятной ошибкой.
"""
from __future__ import annotations

import allure
import pytest

from src.pages.voice_recorder_page import VoiceRecorderPage


@pytest.fixture
def login_creds(pages):
    """Креды для входа; без MSISDN/VERIFICATION_CODE тест не имеет смысла."""
    if pages.ctx.credentials is None:
        pytest.fail(
            "Тест требует авторизации, но учётные данные не заданы: добавьте "
            "MSISDN и VERIFICATION_CODE в .env — см. .env.example")
    return pages.ctx.credentials


@allure.epic("Авторизация")
@allure.feature("Вход через MTS ID (вкладка «ИИ-диктофон»)")
@pytest.mark.android
class TestVoiceRecorderLoginEntryPoints:
    """Вход в MTS ID с точек входа вкладки «ИИ-диктофон».

    В неавторизованном состоянии карточки промо-блока и кнопка загрузки
    записи в тулбаре ведут на форму входа MTS ID; после флоу входа
    (номер + код из СМС) пользователь авторизован — проверяем карточку
    пользователя на «Профиле» и исчезновение промо-блока на вкладке.

    Сессия создаётся с no_reset: false — приложение стартует с чистым
    профилем, без входа в MTS ID.
    """

    @allure.title(
        "Вход через «ВОЙТИ И ЗАГРУЗИТЬ»: номер телефона и код из СМС -> "
        "профиль авторизован"
    )
    @allure.description(
        "Сценарий component/android/authorization.\n\n"
        "Старт в неавторизованном состоянии (вход в MTS ID не выполнен).\n\n"
        "Шаги: открыть вкладку «ИИ-диктофон» через нижнее меню; нажать "
        "карточку промо-блока «ВОЙТИ И ЗАГРУЗИТЬ»; дождаться открытия "
        "SSO-формы MTS ID и загрузки первого экрана флоу; на fast-track "
        "«Рады видеть вас снова» нажать «Войти с другим номером»; ввести "
        "MSISDN тестового пользователя и нажать «ДАЛЕЕ»; дождаться экрана "
        "«Введите код из СМС» и ввести VERIFICATION_CODE; дождаться "
        "закрытия SSO bottom sheet; проверить вкладку «Профиль» и возврат "
        "на вкладку «ИИ-диктофон».\n\n"
        "Ожидаемый результат: авторизация выполнена — на вкладке "
        "«Профиль» видна карточка пользователя (аватар «Изображение МТС "
        "ID»), кнопка входа исчезла; SSO-окно закрылось само; на вкладке "
        "«ИИ-диктофон» больше нет промо-блока «Запишите первую заметку…»."
    )
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.id("")
    def test_login_from_upload_action(self, pages, login_creds):
        """Карточка «ВОЙТИ И ЗАГРУЗИТЬ» -> флоу входа -> профиль авторизован."""
        with allure.step("Открыть вкладку «ИИ-диктофон» (неавторизованный)"):
            recorder = pages.common.open_voice_recorder_tab()
            assert recorder.is_loaded(), "Вкладка «ИИ-диктофон» не загрузилась"

        with allure.step("Нажать карточку «ВОЙТИ И ЗАГРУЗИТЬ»"):
            recorder.tap_upload_action()

        with allure.step("Проверить, что открылась форма входа MTS ID"):
            login = pages.login
            assert login.wait_opened(), (
                "После «ВОЙТИ И ЗАГРУЗИТЬ» не открылась форма входа MTS ID")
            assert login.wait_form_loaded(), (
                "После «ВОЙТИ И ЗАГРУЗИТЬ» форма входа не загрузилась: ни "
                "fast-track, ни экран ввода номера, ни OTP не появились")

        with allure.step("Авторизоваться: номер телефона и код из СМС"):
            login.pass_login_flow(login_creds.msisdn,
                                  login_creds.verification_code)

        with allure.step("Дождаться закрытия SSO-окна после входа"):
            assert login.wait_sheet_closed(), (
                "SSO-окно MTS ID не закрылось после ввода кода из СМС")

        with allure.step("Проверить авторизацию на вкладке «Профиль»"):
            profile = pages.common.open_profile_tab()
            assert profile.is_user_card_visible(), (
                "Карточка пользователя не видна после входа")
            assert not profile.is_login_card_visible(), (
                "Кнопка входа «ВОЙТИ В МТС OPTIMUS» осталась на экране "
                "после выполненного входа")

        with allure.step("Проверить вкладку «ИИ-диктофон» в авторизованном виде"):
            recorder = pages.common.open_voice_recorder_tab()
            assert recorder.is_loaded(), (
                "Вкладка «ИИ-диктофон» не загрузилась после входа")
            assert not recorder.is_promo_text_visible(), (
                "Промо-блок «Запишите первую заметку…» остался после "
                "входа — вкладка по-прежнему в неавторизованном виде")

    @allure.title(
        "Вход через «ВОЙТИ И ЗАПИСАТЬ»: номер телефона и код из СМС -> "
        "профиль авторизован"
    )
    @allure.description(
        "Сценарий component/android/authorization.\n\n"
        "Старт в неавторизованном состоянии (вход в MTS ID не выполнен).\n\n"
        "Шаги: открыть вкладку «ИИ-диктофон» через нижнее меню; нажать "
        "карточку промо-блока «ВОЙТИ И ЗАПИСАТЬ»; дождаться открытия "
        "SSO-формы MTS ID и загрузки первого экрана флоу; на fast-track "
        "«Рады видеть вас снова» нажать «Войти с другим номером»; ввести "
        "MSISDN тестового пользователя и нажать «ДАЛЕЕ»; дождаться экрана "
        "«Введите код из СМС» и ввести VERIFICATION_CODE; дождаться "
        "закрытия SSO bottom sheet; проверить вкладку «Профиль» и возврат "
        "на вкладку «ИИ-диктофон».\n\n"
        "Ожидаемый результат: авторизация выполнена — на вкладке "
        "«Профиль» видна карточка пользователя (аватар «Изображение МТС "
        "ID»), кнопка входа исчезла; SSO-окно закрылось само; на вкладке "
        "«ИИ-диктофон» больше нет промо-блока «Запишите первую заметку…»."
    )
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.id("")
    def test_login_from_record_action(self, pages, login_creds):
        """Карточка «ВОЙТИ И ЗАПИСАТЬ» -> флоу входа -> профиль авторизован."""
        with allure.step("Открыть вкладку «ИИ-диктофон» (неавторизованный)"):
            recorder = pages.common.open_voice_recorder_tab()
            assert recorder.is_loaded(), "Вкладка «ИИ-диктофон» не загрузилась"

        with allure.step("Нажать карточку «ВОЙТИ И ЗАПИСАТЬ»"):
            recorder.tap_record_action()

        with allure.step("Проверить, что открылась форма входа MTS ID"):
            login = pages.login
            assert login.wait_opened(), (
                "После «ВОЙТИ И ЗАПИСАТЬ» не открылась форма входа MTS ID")
            assert login.wait_form_loaded(), (
                "После «ВОЙТИ И ЗАПИСАТЬ» форма входа не загрузилась: ни "
                "fast-track, ни экран ввода номера, ни OTP не появились")

        with allure.step("Авторизоваться: номер телефона и код из СМС"):
            login.pass_login_flow(login_creds.msisdn,
                                  login_creds.verification_code)

        with allure.step("Дождаться закрытия SSO-окна после входа"):
            assert login.wait_sheet_closed(), (
                "SSO-окно MTS ID не закрылось после ввода кода из СМС")

        with allure.step("Проверить авторизацию на вкладке «Профиль»"):
            profile = pages.common.open_profile_tab()
            assert profile.is_user_card_visible(), (
                "Карточка пользователя не видна после входа")
            assert not profile.is_login_card_visible(), (
                "Кнопка входа «ВОЙТИ В МТС OPTIMUS» осталась на экране "
                "после выполненного входа")

        with allure.step("Проверить вкладку «ИИ-диктофон» в авторизованном виде"):
            recorder = pages.common.open_voice_recorder_tab()
            assert recorder.is_loaded(), (
                "Вкладка «ИИ-диктофон» не загрузилась после входа")
            assert not recorder.is_promo_text_visible(), (
                "Промо-блок «Запишите первую заметку…» остался после "
                "входа — вкладка по-прежнему в неавторизованном виде")

    @allure.title(
        "Вход через кнопку загрузки записи в тулбаре: номер телефона и код "
        "из СМС -> профиль авторизован"
    )
    @allure.description(
        "Сценарий component/android/authorization.\n\n"
        "Старт в неавторизованном состоянии (вход в MTS ID не выполнен).\n\n"
        "Шаги: открыть вкладку «ИИ-диктофон» через нижнее меню; нажать "
        "кнопку загрузки записи в тулбаре вверху справа (Search call "
        "button icon — та же иконка, что у поиска на «Звонках»); дождаться "
        "открытия SSO-формы MTS ID и загрузки первого экрана флоу; на "
        "fast-track «Рады видеть вас снова» нажать «Войти с другим "
        "номером»; ввести MSISDN тестового пользователя и нажать «ДАЛЕЕ»; "
        "дождаться экрана «Введите код из СМС» и ввести VERIFICATION_CODE; "
        "дождаться закрытия SSO bottom sheet; проверить вкладку «Профиль» "
        "и возврат на вкладку «ИИ-диктофон».\n\n"
        "Ожидаемый результат: авторизация выполнена — на вкладке "
        "«Профиль» видна карточка пользователя (аватар «Изображение МТС "
        "ID»), кнопка входа исчезла; SSO-окно закрылось само; на вкладке "
        "«ИИ-диктофон» больше нет промо-блока «Запишите первую заметку…»."
    )
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.id("")
    def test_login_from_upload_toolbar_button(self, pages, login_creds):
        """Кнопка загрузки в тулбаре -> флоу входа -> профиль авторизован."""
        with allure.step("Открыть вкладку «ИИ-диктофон» (неавторизованный)"):
            recorder = pages.common.open_voice_recorder_tab()
            assert recorder.is_loaded(), "Вкладка «ИИ-диктофон» не загрузилась"

        with allure.step("Нажать кнопку загрузки записи в тулбаре"):
            recorder.tap_upload_toolbar_button()

        with allure.step("Проверить, что открылась форма входа MTS ID"):
            login = pages.login
            assert login.wait_opened(), (
                "После нажатия кнопки загрузки не открылась форма входа "
                "MTS ID")
            assert login.wait_form_loaded(), (
                "После нажатия кнопки загрузки форма входа не загрузилась: "
                "ни fast-track, ни экран ввода номера, ни OTP не появились")

        with allure.step("Авторизоваться: номер телефона и код из СМС"):
            login.pass_login_flow(login_creds.msisdn,
                                  login_creds.verification_code)

        with allure.step("Дождаться закрытия SSO-окна после входа"):
            assert login.wait_sheet_closed(), (
                "SSO-окно MTS ID не закрылось после ввода кода из СМС")

        with allure.step("Проверить авторизацию на вкладке «Профиль»"):
            profile = pages.common.open_profile_tab()
            assert profile.is_user_card_visible(), (
                "Карточка пользователя не видна после входа")
            assert not profile.is_login_card_visible(), (
                "Кнопка входа «ВОЙТИ В МТС OPTIMUS» осталась на экране "
                "после выполненного входа")

        with allure.step("Проверить вкладку «ИИ-диктофон» в авторизованном виде"):
            recorder = pages.common.open_voice_recorder_tab()
            assert recorder.is_loaded(), (
                "Вкладка «ИИ-диктофон» не загрузилась после входа")
            assert not recorder.is_promo_text_visible(), (
                "Промо-блок «Запишите первую заметку…» остался после "
                "входа — вкладка по-прежнему в неавторизованном виде")
