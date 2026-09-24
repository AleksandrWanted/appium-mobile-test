"""Пакет Page Objects: фасад Pages + отдельные экраны приложения."""
from src.pages.base_page import BasePage
from src.pages.call_detail_page import CallDetailPage, CallDetailPageLocators
from src.pages.calls_page import CallsPage, CallsPageLocators
from src.pages.common_elements import (
    BottomNavLocators,
    CommonElements,
    SystemDialogLocators,
    UnauthorizedStateLocators,
)
from src.pages.contacts_page import ContactsPage, ContactsPageLocators
from src.pages.dialer_page import DialerPage, DialerPageLocators
from src.pages.page_context import PageContext
from src.pages.pages import Pages
from src.pages.profile_page import ProfilePage, ProfilePageLocators
from src.pages.search_page import SearchPage, SearchPageLocators

__all__ = [
    "BasePage",
    "BottomNavLocators",
    "CallDetailPage",
    "CallDetailPageLocators",
    "CallsPage",
    "CallsPageLocators",
    "CommonElements",
    "ContactsPage",
    "ContactsPageLocators",
    "DialerPage",
    "DialerPageLocators",
    "PageContext",
    "Pages",
    "ProfilePage",
    "ProfilePageLocators",
    "SearchPage",
    "SearchPageLocators",
    "SystemDialogLocators",
    "UnauthorizedStateLocators",
]

