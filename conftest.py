"""Глобальные фикстуры и хуки pytest."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from config.config import AppConfig, load_config
from src.driver.driver_wrapper import DriverWrapper
from src.driver.factory import create_driver
from src.utils.permissions import PermissionsHandler


@pytest.fixture(scope="session")
def app_config() -> AppConfig:
    """Конфигурация запуска (одна на всю сессию)."""
    return load_config(os.getenv("APP_CONFIG", "android.local"))


@pytest.fixture(scope="session")
def test_data() -> dict:
    """Тестовые данные из resources/data/users.json."""
    path = Path("resources/data/users.json")
    with path.open(encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def driver(app_config: AppConfig) -> DriverWrapper:
    """Создаёт и держит Appium-драйвер на всю сессию.

    Для параллельных запусков (pytest-xdist) замени scope на 'function'
    или используй отдельный udid/порт на воркер.
    """
    raw_driver = create_driver(app_config)
    wrapper = DriverWrapper(raw_driver)

    # Закрыть системные диалоги (разрешения), всплывающие при старте приложения.
    # Только если явно включено в конфиге (handle_permissions: true) — иначе
    # grant_permissions впустую тратит время на поиск несуществующих кнопок.
    if app_config.handle_permissions:
        PermissionsHandler(raw_driver).grant_permissions()

    yield wrapper
    raw_driver.quit()


@pytest.fixture(autouse=True)
def _close_app_after_test(driver: DriverWrapper):
    """Автоматически закрывает приложение после каждого теста.

    Берёт package из capabilities драйвера и вызывает mobile: terminateApp,
    чтобы каждый тест стартовал с чистого состояния приложения. Срабатывает
    только если сессия ещё жива — иначе тихо пропускает.
    """
    yield
    raw = driver.raw
    try:
        package = raw.capabilities.get("appPackage")
        if package:
            raw.execute_script("mobile: terminateApp", {"appId": package})
    except Exception as exc:  # noqa: BLE001
        print(f"\n[не удалось закрыть приложение] {exc}")


# --- хук: скриншот при падении теста ---
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        driver: DriverWrapper | None = item.funcargs.get("driver")
        if driver is not None:
            try:
                import allure

                path = driver.screenshot(item.name)
                allure.attach.file(
                    path,
                    name="screenshot",
                    attachment_type=allure.attachment_type.PNG,
                )
                print(f"\n[скриншот падения] {path}")
            except Exception as exc:  # noqa: BLE001
                print(f"\n[не удалось сделать скриншот] {exc}")
