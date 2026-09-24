"""Фасад всех Page Objects приложения.

Аналог Pages из web-проекта: один объект собран над общим PageContext;
каждая страница доступна как атрибут (pages.login, pages.home, ...).
Страницы, зависящие от других, получают их через конструктор.
"""
from __future__ import annotations

from config.config import AppConfig
from src.driver.driver_wrapper import DriverWrapper
from src.pages.call_detail_page import CallDetailPage
from src.pages.calls_page import CallsPage
from src.pages.contacts_page import ContactsPage
from src.pages.dialer_page import DialerPage
from src.pages.page_context import PageContext
from src.pages.profile_page import ProfilePage
from src.pages.search_page import SearchPage


class Pages:
    def __init__(self, driver: DriverWrapper, config: AppConfig):
        self.ctx = PageContext(driver=driver, config=config)
        self._build_pages()

    def _build_pages(self) -> None:
        ctx = self.ctx
        self.profile = ProfilePage(ctx)
        self.calls = CallsPage(ctx)
        self.contacts = ContactsPage(ctx)
        self.search = SearchPage(ctx)
        self.dialer = DialerPage(ctx)
        self.call_detail = CallDetailPage(ctx)

    @property
    def common(self):
        """Кросс-экранные действия: системные диалоги, back, клавиатура, нижнее меню."""
        return self.ctx.common
