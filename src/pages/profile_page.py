"""Page Object вкладки «Профиль» приложения МТС Optimus (ru.mts.mvats),
актуализирован под разметку версии 2.17.1 (Samsung S21 FE, Android 15).
Экран — нативный (не Compose): внутри nav_host_fragment_profile живут
обычные View. Внизу экрана закреплена кнопка входа (rootLayout /
buttonEnableSubAlternative) и нижнее навигационное меню.

Неавторизованный экран (не содержит id notAuthZone с версии 2.17.1):
карточки подписок «Запись звонков» (Абонентам МТС) и «ИИ-диктофон»
(Абонентам всех операторов), блок «350 минут ИИ-диктофона…» + «Подробнее»,
секции «Доступы к звонкам» / «Поддержка» / «Справка» и строка версии.

Нижнее навигационное меню и кнопка входа «ВОЙТИ В МТС OPTIMUS» — общие,
живут в common_elements (BottomNavLocators / UnauthorizedStateLocators).
"""
from __future__ import annotations

import re
import time

import allure
from appium.webdriver.common.appiumby import AppiumBy

from src.pages.base_page import BasePage


class ProfilePageLocators:
    """Локаторы вкладки «Профиль» (МТС Optimus, разметка 2.17.1+).

    Приоритет локаторов: id (resource-id) → текст (uiautomator)
    → accessibility id. XPath — последний вариант.
    """

    # --- контейнер экрана ---
    SCREEN_ROOT = (AppiumBy.ID, "ru.mts.mvats:id/nav_host_fragment_profile")
    # Скролл-контейнер карточек (один на весь экран до нижнего меню)
    SCROLL_CONTAINER = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().scrollable(true)')

    # --- кнопка входа (закреплена внизу экрана, общая для неавторизованного) ---
    # Кнопка входа: content-desc "Войти в МТС Optimus" на rootLayout (Button),
    # внутри неё TextView с текстом «ВОЙТИ В МТС OPTIMUS».
    LOGIN_CARD = (AppiumBy.ACCESSIBILITY_ID, "Войти в МТС Optimus")
    LOGIN_CARD_TEXT = (AppiumBy.ANDROID_UIAUTOMATOR,
                       'new UiSelector().text("ВОЙТИ В МТС OPTIMUS")')

    # --- авторизованное состояние ---
    # После входа вместо кнопки входа — карточка пользователя (имя + номер)
    # с изображением МТС ID; в самом низу профиля — кнопка выхода.
    USER_AVATAR = (AppiumBy.ACCESSIBILITY_ID, "Изображение МТС ID")
    LOGOUT_TEXT = (AppiumBy.ANDROID_UIAUTOMATOR,
                   'new UiSelector().text("Выйти из профиля")')
    # Диалог подтверждения выхода
    LOGOUT_CONFIRM = (AppiumBy.ANDROID_UIAUTOMATOR,
                      'new UiSelector().text("ВЫЙТИ")')
    LOGOUT_CANCEL = (AppiumBy.ANDROID_UIAUTOMATOR,
                     'new UiSelector().text("ОТМЕНА")')

    # --- карточка «Запись звонков» (Абонентам МТС) ---
    SUBSCRIPTION_CARD_TITLE = (AppiumBy.ANDROID_UIAUTOMATOR,
                               'new UiSelector().text("Запись звонков")')
    SUBSCRIPTION_CARD_AUDIENCE = (AppiumBy.ANDROID_UIAUTOMATOR,
                                  'new UiSelector().text("Абонентам МТС")')
    SUBSCRIPTION_CARD_DESCRIPTION = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().text("Запись и ИИ-расшифровка звонков. Превратит '
        'договорённости в задачи и подскажет следующие шаги")',
    )
    SUBSCRIBE_BUTTON_TEXT = (AppiumBy.ANDROID_UIAUTOMATOR,
                             'new UiSelector().text("ПОДКЛЮЧИТЬ")')
    SUBSCRIBE_BUTTON_MORE = (AppiumBy.ANDROID_UIAUTOMATOR,
                             'new UiSelector().text("Подробнее")')

    # --- карточка «ИИ-диктофон» (Абонентам всех операторов) ---
    AI_RECORDER_TITLE = (AppiumBy.ANDROID_UIAUTOMATOR,
                         'new UiSelector().text("ИИ-диктофон")')

    # --- заголовок ---
    TITLE = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Профиль")')

    # --- нижние карточки-секции (видны после доскролла; id not_auth-* пропали) ---
    # Карточка «Доступы к звонкам», подпись «350 минут ИИ-диктофона в месяц»
    AI_RECORDER_LIMIT = (AppiumBy.ANDROID_UIAUTOMATOR,
                         'new UiSelector().text("350 минут ИИ-диктофона в месяц")')
    CALL_ACCESS_TITLE = (AppiumBy.ANDROID_UIAUTOMATOR,
                         'new UiSelector().text("Доступы к звонкам")')
    SUPPORT_TITLE = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Поддержка")')
    REFERENCE_TITLE = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Справка")')

    # Подпись версии приложения рядом со «Справка» (id version_app_not_auth
    # пропал в 2.17.1 — теперь TextView без resource-id, ищем по префиксу текста)
    APP_VERSION_TEXT = (AppiumBy.ANDROID_UIAUTOMATOR,
                        'new UiSelector().textStartsWith("Версия")')


class ProfilePage(BasePage):
    """Вкладка «Профиль» приложения МТС Optimus.

    Нижнее меню (переход между вкладками) и кнопка входа — общие элементы:
    pages.common.open_profile_tab() / pages.common.tap_login_banner().
    """

    # --- проверки состояния экрана ---
    @allure.step("Проверить, что вкладка «Профиль» загружена")
    def is_loaded(self) -> bool:
        return self.is_displayed(ProfilePageLocators.TITLE)

    # --- авторизованное состояние ---
    @allure.step("Проверить видимость карточки пользователя (МТС ID)")
    def is_user_card_visible(self) -> bool:
        return self.is_displayed(ProfilePageLocators.USER_AVATAR, self.timeout)

    @allure.step("Проверить видимость кнопки «Выйти из профиля»")
    def is_logout_visible(self) -> bool:
        # Кнопка в самом низу профиля: доскролливаем и проверяем
        self.scroll_to_logout()
        return self.driver.is_present(ProfilePageLocators.LOGOUT_TEXT,
                                      timeout=5)

    @allure.step("Прокрутить до кнопки «Выйти из профиля»")
    def scroll_to_logout(self, max_swipes: int = 8) -> None:
        """Прокручивает вкладку «Профиль» вниз до кнопки выхода.

        UiScrollable.scrollIntoView здесь недотягивает: контент профиля
        частично Compose, и скролл останавливается раньше кнопки. Поэтому
        скроллим явными жестами (mobile: scrollGesture) по области контента,
        проверяя появление кнопки после каждого свайпа.
        """
        for _ in range(max_swipes):
            if self.driver.find_elements(ProfilePageLocators.LOGOUT_TEXT):
                return
            self.driver.raw.execute_script("mobile: scrollGesture", {
                "left": 100, "top": 500, "width": 880, "height": 1200,
                "percent": 0.8, "direction": "down", "speed": 5000,
            })
            time.sleep(1)
        # Финальная проверка без свайпа — элемент мог появиться на последнем
        # жесте, а find_elements выше отработал до обновления дерева

    @allure.step("Прокрутить вкладку «Профиль» вверх")
    def scroll_to_top(self, max_swipes: int = 8) -> None:
        """Возвращает вкладку «Профиль» наверх после доскролла.

        После прокрутки до кнопки выхода карточка пользователя оказывается
        за пределами экрана (и дерева) — поднимаемся теми же явными жестами,
        что и в scroll_to_logout, до появления аватара.
        """
        for _ in range(max_swipes):
            if self.driver.find_elements(ProfilePageLocators.USER_AVATAR):
                return
            self.driver.raw.execute_script("mobile: scrollGesture", {
                "left": 100, "top": 500, "width": 880, "height": 1200,
                "percent": 0.8, "direction": "up", "speed": 5000,
            })
            time.sleep(1)

    @allure.step("Нажать «Выйти из профиля»")
    def open_logout_dialog(self) -> None:
        """Открывает диалог «Вы уверены, что хотите выйти?» («ВЫЙТИ» /
        «ОТМЕНА»), сам выход этим шагом не выполняется.

        Локатор цепляется к TextView, а клик обрабатывает родитель-строка —
        тапаем по центру текста жестом.
        """
        self.scroll_to_logout()
        text_el = self.driver.wait_visible(ProfilePageLocators.LOGOUT_TEXT,
                                           self.timeout)
        self._tap_center(text_el)

    @allure.step("Нажать «Выйти из профиля» и подтвердить выход")
    def logout(self) -> None:
        """Выход из профиля: открыть диалог → «ВЫЙТИ».

        После подтверждения приложение открывает полноэкранную SSO-форму
        входа MTS ID (см. test_mts_id_logout.py).
        """
        self.open_logout_dialog()
        confirm = self.driver.wait_clickable(ProfilePageLocators.LOGOUT_CONFIRM,
                                             self.timeout)
        confirm.click()

    @allure.step("Отменить выход в диалоге подтверждения («ОТМЕНА»)")
    def cancel_logout(self) -> None:
        """Отмена выхода: в уже открытом диалоге подтверждения нажать
        «ОТМЕНА». Выход не выполняется — сессия сохраняется.
        """
        cancel = self.driver.wait_clickable(ProfilePageLocators.LOGOUT_CANCEL,
                                            self.timeout)
        cancel.click()

    def _tap_center(self, element) -> None:
        """Тап по центру границ элемента (когда клик обрабатывает родитель)."""
        bounds = element.get_attribute("bounds")
        m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
        x1, y1, x2, y2 = (int(g) for g in m.groups())
        self.driver.raw.execute_script(
            "mobile: clickGesture",
            {"x": (x1 + x2) // 2, "y": (y1 + y2) // 2},
        )

    @allure.step("Получить заголовок вкладки")
    def get_title(self) -> str:
        return self.get_text(ProfilePageLocators.TITLE)

    # --- неавторизованное состояние ---
    @allure.step("Проверить видимость кнопки входа «Войти в МТС Optimus»")
    def is_login_card_visible(self) -> bool:
        return self.is_displayed(ProfilePageLocators.LOGIN_CARD)

    @allure.step("Проверить текст кнопки входа")
    def get_login_card_text(self) -> str:
        return self.get_text(ProfilePageLocators.LOGIN_CARD_TEXT)

    @allure.step("Проверить видимость кнопки «ПОДКЛЮЧИТЬ»")
    def is_subscribe_button_visible(self) -> bool:
        return self.is_displayed(ProfilePageLocators.SUBSCRIBE_BUTTON_TEXT)

    # --- карточка «Запись звонков» ---
    @allure.step("Проверить видимость заголовка карточки «Запись звонков»")
    def is_subscription_card_visible(self) -> bool:
        # Карточки тарифов подрисовываются после ответа бэкенда — ждём полным
        # таймаутом (BasePage.is_displayed по умолчанию режет до 3 сек).
        return self.is_displayed(
            ProfilePageLocators.SUBSCRIPTION_CARD_TITLE, self.timeout
        )

    @allure.step("Получить описание карточки «Запись звонков»")
    def get_subscription_description(self) -> str:
        return self.get_text(ProfilePageLocators.SUBSCRIPTION_CARD_DESCRIPTION)

    # --- карточка «ИИ-диктофон» ---
    @allure.step("Проверить видимость карточки «ИИ-диктофон»")
    def is_ai_recorder_card_visible(self) -> bool:
        return self.is_displayed(ProfilePageLocators.AI_RECORDER_TITLE)

    # --- нижние карточки-секции ---
    @allure.step("Проверить видимость карточки «Доступы к звонкам»")
    def is_call_access_card_visible(self) -> bool:
        return self.is_displayed(ProfilePageLocators.CALL_ACCESS_TITLE)

    @allure.step("Прокрутить до карточки «Доступы к звонкам»")
    def scroll_to_call_access_card(self) -> None:
        self.driver.scroll_to_element(
            ProfilePageLocators.CALL_ACCESS_TITLE, timeout=self.timeout
        )

    @allure.step("Проверить видимость карточки «Поддержка»")
    def is_support_card_visible(self) -> bool:
        return self.is_displayed(ProfilePageLocators.SUPPORT_TITLE)

    @allure.step("Проверить видимость карточки «Справка»")
    def is_reference_card_visible(self) -> bool:
        return self.is_displayed(ProfilePageLocators.REFERENCE_TITLE)

    @allure.step("Получить версию приложения")
    def get_app_version(self) -> str:
        return self.get_text(ProfilePageLocators.APP_VERSION_TEXT)
