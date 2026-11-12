"""Фикстуры Appium-драйвера и Page Objects."""
from __future__ import annotations

import time

import allure
import pytest

from config.config import AppConfig
from config.credentials import Credentials
from fixtures.appium_server_fixtures import appium_server  # noqa: F401 — фикстура driver
from fixtures.config_fixtures import app_config  # noqa: F401 — зависимость фикстур driver/pages
from fixtures.config_fixtures import credentials  # noqa: F401 — реэкспорт фикстуры
from src.driver.driver_wrapper import DriverWrapper
from src.driver.factory import create_driver
from src.pages.pages import Pages
from src.utils.permissions import auto_grant_runtime_permissions


def _wait_foreground(raw_driver, package: str, timeout: int = 20) -> bool:
    """Ждёт, пока приложение (package) реально окажется на переднем плане.

    Сессия Appium отдаёт управление раньше, чем приложение выходит на
    передний план (особенно на холодном старте) — тест начинает искать
    элементы, а на экране ещё лаунчер. Возвращает True, когда приложение
    в форграунде, False если так и не вышло.
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            current = raw_driver.execute_script("mobile: getCurrentPackage")
        except Exception:  # noqa: BLE001
            current = None
        if current == package:
            return True
        try:
            raw_driver.execute_script("mobile: activateApp", {"appId": package})
        except Exception:  # noqa: BLE001
            pass
        time.sleep(0.5)
    return False


@pytest.fixture
def driver(appium_server, app_config: AppConfig) -> DriverWrapper:
    """Создаёт Appium-сессию на каждый тест.

    Сессия на тест, а не на прогон, вместе с no_reset: false в YAML-профиле
    даёт каждому тесту гарантированно чистое состояние приложения: создание
    сессии делает uninstall+install APK (full_reset) или pm clear (no_reset:
    false), сбрасывая и авторизацию, и SSO-состояние, и системные диалоги
    first-launch. Разные тесты не влияют друг на друга — включая сценарии
    с авторизацией (fixture authorized_app) и её teardown'ом.

    Для ускорения прогона можно включить session-режим: поставьте scope=
    "session" В ЭТОЙ фикстуре и no_reset: true в YAML — тогда состояние
    переживает тесты (быстрее, но тесты зависят друг от друга).

    Зависит от appium_server: если сервер не был запущен — фикстура поднимет
    его до создания driver'а.
    """
    raw_driver = create_driver(app_config)
    wrapper = DriverWrapper(raw_driver)

    if app_config.auto_grant_permissions and app_config.platform == "android":
        # После pm clear все RUNTIME-разрешения сброшены: держать приложение
        # без системных permission-диалогов (например, «Разрешить отправку
        # уведомлений?» на первом запуске). capability autoGrantPermissions
        # срабатывает при установке APK/pm clear — дополняем прямым грантом
        # через mobile: changePermissions (iOS обрабатывает alerts сама,
        # см. factory.py).
        auto_grant_runtime_permissions(raw_driver)

    # pm clear-старт: убедиться, что приложение реально в форграунде, прежде
    # чем тест начнёт искать элементы (см. _wait_foreground).
    package = raw_driver.capabilities.get("appPackage")
    if package:
        _wait_foreground(raw_driver, package)

    yield wrapper
    raw_driver.quit()


@pytest.fixture
def pages(driver: DriverWrapper, app_config: AppConfig, credentials: Credentials | None):
    """Инициализирует фасад Page Objects над живым driver.

    credentials приходит как None, когда переменные MSISDN/VERIFICATION_CODE
    не заданы: неавторизованные тесты работают без них, авторизационные
    сами решают, использовать их или нет (ctx.credentials).
    """
    with allure.step("Инициализировать Page Objects"):
        return Pages(driver=driver, config=app_config, credentials=credentials)


@pytest.fixture
def authorized_app(pages):
    """Авторизует пользователя в приложении (fixture-pages поверх чистого старта).

    Порядок (реальный сценарий входа MTS ID, SSO bottom sheet на вкладке
    «Профиль»):
        вкладка «Профиль» → кнопка «Войти в МТС Optimus» → (fast-track
        «Рады видеть вас снова» → «Войти с другим номером») → ввод MSISDN →
        «ДАЛЕЕ» → экран «Введите код из СМС» → ввод VERIFICATION_CODE →
        вход выполняется автоматически после последней цифры.

    Номер и код берутся из фикстуры credentials (переменные MSISDN /
    VERIFICATION_CODE из .env). Если они не заданы — тест падает сразу
    с понятной ошибкой, а не с поздним NoSuchElement на экране логина.

    Возвращает Pages — тест продолжает работать с pages.profile уже в
    авторизованном состоянии.

    Teardown-логаут НЕ нужен: driver function-scoped + no_reset: false —
    следующая сессия стартует с pm clear, и состояние «вышел из профиля»
    обеспечено сбросом данных, а не UI-выходом.
    """
    from src.pages.login_page import LoginPage

    if pages.ctx.credentials is None:
        pytest.fail(
            "Тест требует авторизации, но учётные данные не заданы: добавьте "
            "MSISDN и VERIFICATION_CODE в .env — см. .env.example")

    with allure.step("Авторизоваться в МТС Optimus через MTS ID"):
        login: LoginPage = pages.common.open_login_screen()
        # login_with_credentials сам ждёт открытие и загрузку формы —
        # не дублируем ожидания здесь (иначе они выполнялись бы дважды).
        login.login_with_credentials(
            msisdn=pages.ctx.credentials.msisdn,
            code=pages.ctx.credentials.verification_code,
        )
        assert login.wait_login_completed(), (
            "Вход не завершился: аватар профиля не появился")

    yield pages
