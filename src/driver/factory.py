"""Фабрика создания Appium-драйвера по конфигу."""
from __future__ import annotations

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions

from config.config import AppConfig


def _to_options(cfg: AppConfig):
    if cfg.platform == "android":
        opts = UiAutomator2Options()
        opts.platform_version = cfg.platform_version
        opts.device_name = cfg.device_name
        if cfg.udid:
            opts.udid = cfg.udid
    elif cfg.platform == "ios":
        opts = XCUITestOptions()
        opts.platform_version = cfg.platform_version
        opts.device_name = cfg.device_name
        if cfg.udid:
            opts.udid = cfg.udid
        # iOS: авто-принятие нативных alert через WDA (аналог гранта на Android).
        if cfg.auto_grant_permissions:
            opts.auto_accept_alerts = True
    else:
        raise ValueError(f"Неподдерживаемая платформа: {cfg.platform}")

    opts.app = cfg.app
    opts.no_reset = cfg.no_reset
    opts.full_reset = cfg.full_reset
    # Android: Appium выдаёт RUNTIME-разрешения через pm grant — системный
    # диалог «Разрешить…» (например, уведомления при первом запуске) не появится.
    if cfg.platform == "android" and cfg.auto_grant_permissions:
        opts.auto_grant_permissions = True
    opts.set_capability("newCommandTimeout", cfg.new_command_timeout)
    return opts


def create_driver(cfg: AppConfig):
    """Создаёт и возвращает driver, подключённый к Appium-серверу."""
    options = _to_options(cfg)
    driver = webdriver.Remote(cfg.remote_url, options=options)
    return driver
