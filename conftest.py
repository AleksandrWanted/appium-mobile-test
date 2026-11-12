"""Глобальные фикстуры и хуки pytest."""
from __future__ import annotations

import allure
import pytest
from dotenv import load_dotenv

# .env загружается до обращения к APP_CONFIG (например, android.local.real — см. .env)
load_dotenv()

from fixtures.appium_server_fixtures import appium_server  # noqa: E402,F401 — реэкспорт фикстуры
from fixtures.config_fixtures import app_config  # noqa: E402,F401 — реэкспорт фикстуры
from fixtures.config_fixtures import credentials  # noqa: E402,F401 — реэкспорт фикстуры
from fixtures.driver_fixtures import driver  # noqa: E402,F401 — реэкспорт фикстуры
from fixtures.driver_fixtures import authorized_app  # noqa: E402,F401 — реэкспорт фикстуры
from fixtures.driver_fixtures import pages  # noqa: E402,F401 — реэкспорт фикстуры
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
                # Диагностика: что реально на экране в момент падения
                raw = getattr(driver, "raw", None)
                if raw is not None:
                    try:
                        state = (
                            f"currentPackage={raw.execute_script('mobile: getCurrentPackage')}\n"
                            f"currentActivity={raw.execute_script('mobile: getCurrentActivity')}\n"
                            f"appPackage={raw.capabilities.get('appPackage')}"
                        )
                        allure.attach(
                            state,
                            name="app_state",
                            attachment_type=allure.attachment_type.TEXT,
                        )
                        print(f"\n[состояние приложения]\n{state}")
                    except Exception as exc:  # noqa: BLE001
                        print(f"\n[не удалось получить состояние приложения] {exc}")
            except Exception as exc:  # noqa: BLE001
                print(f"\n[не удалось сделать скриншот] {exc}")
