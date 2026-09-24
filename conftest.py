"""Глобальные фикстуры и хуки pytest."""
from __future__ import annotations

import allure
import pytest
from dotenv import load_dotenv

# .env загружается до обращения к APP_CONFIG (например, android.local.real — см. .env)
load_dotenv()

from fixtures.appium_server_fixtures import appium_server  # noqa: E402,F401 — реэкспорт фикстуры
from fixtures.config_fixtures import app_config  # noqa: E402,F401 — реэкспорт фикстуры
from fixtures.driver_fixtures import (  # noqa: E402,F401 — реэкспорт фикстур
    _first_app_test_done,
    _restart_app_per_test,
    driver,
    pages,
)
from src.driver.driver_wrapper import DriverWrapper  # noqa: E402 — тип в хуке ниже


# --- хук: скриншот при падении теста ---
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        driver: DriverWrapper = item.funcargs.get("driver")
        if driver is not None:
            try:
                path = driver.screenshot(item.name)
                allure.attach.file(
                    path,
                    name="screenshot",
                    attachment_type=allure.attachment_type.PNG,
                )
                print(f"\n[скриншот падения] {path}")
            except Exception as exc:  # noqa: BLE001
                print(f"\n[не удалось сделать скриншот] {exc}")
