"""Фикстуры Appium-драйвера и Page Objects."""
from __future__ import annotations

import allure
import pytest

from config.config import AppConfig
from fixtures.appium_server_fixtures import appium_server  # noqa: F401 — фикстура driver
from fixtures.config_fixtures import app_config  # noqa: F401 — зависимость фикстур driver/pages
from src.driver.driver_wrapper import DriverWrapper
from src.driver.factory import create_driver
from src.pages.pages import Pages
from src.utils.permissions import auto_grant_runtime_permissions


@pytest.fixture(scope="session")
def driver(appium_server, app_config: AppConfig) -> DriverWrapper:
    """Создаёт и держит Appium-драйвер на всю сессию.

    Зависит от appium_server: если сервер не был запущен — фикстура поднимет его
    до создания driver'а.

    Для параллельных запусков (pytest-xdist) замени scope на 'function'
    или используй отдельный udid/порт на воркер.
    """
    raw_driver = create_driver(app_config)
    wrapper = DriverWrapper(raw_driver)

    if app_config.auto_grant_permissions and app_config.platform == "android":
        # Держать приложение без системных permission-диалогов (например,
        # «Разрешить отправку уведомлений?» при первом запуске). capability
        # autoGrantPermissions срабатывает только при установке APK или
        # pm clear; при no_reset: true и уже установленном приложении она
        # пропускается — поэтому дополняем прямым грантом через
        # mobile: changePermissions. iOS обрабатывает alerts сама
        # (autoAcceptAlerts в capabilities, см. factory.py).
        auto_grant_runtime_permissions(raw_driver)

    yield wrapper
    raw_driver.quit()


@pytest.fixture
def pages(driver: DriverWrapper, app_config: AppConfig):
    """Инициализирует фасад Page Objects над живым driver."""
    with allure.step("Инициализировать Page Objects"):
        return Pages(driver=driver, config=app_config)


@pytest.fixture(scope="session")
def _first_app_test_done() -> dict:
    """Сессионный флаг: прошёл ли уже первый тест на свежезапущенном приложении.

    Appium запускает приложение при старте сессии (autoLaunch), поэтому перед
    первым тестом terminate+activate не нужны — это был бы второй подряд старт.
    Флаг выставляется в teardown первого теста; всё, что до него, работает на
    чистом старте от Appium, а каждый следующий тест получает честный рестарт.
    """
    return {"done": False}


@pytest.fixture(autouse=True)
def _restart_app_per_test(driver: DriverWrapper, _first_app_test_done: dict):
    """Гарантирует чистый UI-старт приложения для каждого теста.

    Appium-сессия одна на весь запуск (session-scoped driver), поэтому
    состояние между тестами приходится приведённым ниже циклом:

    - до теста: terminateApp (убить, если остался жив после прошлого теста)
      + activateApp (запустить заново) — без этого после terminateApp прошлого
      теста приложение мертво и следующий тест падает на поиске элементов
      (Appium не перезапускает приложение внутри живой сессии);
    - после теста: terminateApp — процесс не висит в фоне.

    terminateApp/activateApp не трогают данные приложения (shared prefs,
    файлы) — логин и пр. сохраняются между тестами (no_reset: true). Срабатывает
    только если сессия ещё жива — иначе тихо пропускает.

    Перед первым тестом сессии рестарт пропускается (см. _first_app_test_done),
    но teardown-терминация выполняется всегда.
    """
    raw = driver.raw
    package = raw.capabilities.get("appPackage")

    def _mobile(script: str):
        raw.execute_script(script, {"appId": package})

    def restart():
        if not package:
            return
        try:
            _mobile("mobile: terminateApp")
            _mobile("mobile: activateApp")
        except Exception as exc:  # noqa: BLE001
            print(f"\n[не удалось перезапустить приложение] {exc}")

    if _first_app_test_done["done"]:
        restart()
    yield
    try:
        if package:
            _mobile("mobile: terminateApp")
    except Exception as exc:  # noqa: BLE001
        print(f"\n[не удалось закрыть приложение] {exc}")
    _first_app_test_done["done"] = True
