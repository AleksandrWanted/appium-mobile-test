"""Контекст окружения для Page Objects (аналог UIContext из web-проекта)."""
from __future__ import annotations

import logging

from config.config import AppConfig
from src.driver.driver_wrapper import DriverWrapper
from src.pages.common_elements import CommonElements

# Базовый таймаут ожиданий, в секундах. Вынесен в контекст, чтобы page objects
# работали с одним таймаутом; отдельные шаги могут переопределять его точечно.
DEFAULT_TIMEOUT_S = 10


class PageContext:
    """Точка доступа page objects к driver/config/общим элементам.

    Единый объект передаётся во все страницы: вместо прокидывания driver
    в каждый page object по отдельности создаётся один контекст, а страницы
    берут из него driver, таймауты и общий (common) набор элементов.
    """

    def __init__(self, driver: DriverWrapper, config: AppConfig):
        self.driver = driver
        self.config = config
        self.timeout = DEFAULT_TIMEOUT_S
        self.logger = logging.getLogger("src.pages.context")
        self.common = CommonElements(self)

    @property
    def platform(self) -> str:
        """Платформа текущей сессии ('android' | 'ios') — для платформозависимой логики."""
        return self.config.platform

    def apply_timeout(self, timeout_s: int) -> None:
        """Сменить базовый таймаут ожиданий (например, увеличить на медленном CI)."""
        self.timeout = timeout_s
