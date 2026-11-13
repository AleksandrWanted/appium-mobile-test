"""Page Objects экранов входа MTS ID (SSO-флоу приложения МТС Optimus).

Экран отображается в bottom sheet (ru.mts.mvats:id/design_bottom_sheet) как
WebView (ru.mts.mvats:id/sdkSsoWebLoginForm). Содержимое WebView в релизной
сборке недоступно через webview-контекст (нет devtools-сокета), но полностью
видно в нативном a11y-дереве — локаторы по тексту/resource-id работают как
для нативных элементов.

Экраны флоу (разметка версии 2.17.1, Samsung S21 FE, Android 15):

1. «Рады видеть вас снова» — fast-track, показывается, если SDK помнит номер.
   Кнопки «ДАЛЕЕ» (подтвердить вход по сохранённому номеру) и
   «Войти с другим номером».
2. «Войдите с номером телефона любого оператора» — ввод MSISDN:
   EditText resource-id=login, кнопка «ДАЛЕЕ», «Не могу войти».
3. «Введите код из СМС» — OTP: EditText resource-id=otp (4 цифры),
   вход выполняется автоматически после ввода последней цифры.
4. Успех: закрывается bottom sheet, вкладка «Профиль» показывает имя
   пользователя (ImageView с content-desc «Изображение МТС ID»).

Экраны 1–3 — контент WebView inside bottom sheet: element ids (login/otp)
и тексты уникальны в рамках активного окна, поэтому ищем без префиксов.

Выход из профиля здесь не автоматизируется: возврат в неавторизованное
состояние обеспечивает сброс данных следующей сессии (no_reset: false в
YAML-профиле, см. fixture driver) — UI-выход оставлял бы SSO-хвост, который
ломал бы следующие неавторизованные тесты.
"""
from __future__ import annotations

import re
import time

import allure
from appium.webdriver.common.appiumby import AppiumBy

from src.pages.base_page import BasePage

# Таймаут загрузки WebView/переходов между шагами флоу (медленные сети, SMS)
_LOGIN_FLOW_TIMEOUT = 30


class LoginPageLocators:
    """Локаторы экранов входа MTS ID (WebView SSO bottom sheet, 2.17.1+)."""

    # --- контейнер экрана (SSO-контент внутри bottom sheet) ---
    # id WebView (sdkSsoWebLoginForm) есть не во всех состояниях — при
    # переоткрытии bottom sheet WebView рендерится без resource-id. Надёжный
    # якорь — FrameLayout-контейнер SSO-контента (mts_id): он есть и в
    # bottom-sheet-версии, и в полноэкранной (после выхода из профиля).
    SCREEN_ROOT = (AppiumBy.ID, "ru.mts.mvats:id/mts_id")
    # Прогресс загрузки WebView — исчезает, когда форма отрисована
    LOADING_INDICATOR = (AppiumBy.ID, "ru.mts.mvats:id/sdkSsoProgressForm")
    # Сам bottom sheet — точка приложения жеста отмены входа (свайп вниз).
    # Есть только в версии «открыли с профиля»; после логаута SSO рисуется
    # полноэкранно без design_bottom_sheet — там отмена свайпом не нужна.
    BOTTOM_SHEET = (AppiumBy.ID, "ru.mts.mvats:id/design_bottom_sheet")

    # --- экран 1: «Рады видеть вас снова» (fast-track) ---
    WELCOME_BACK_TITLE = (AppiumBy.ANDROID_UIAUTOMATOR,
                          'new UiSelector().text("Рады видеть вас снова")')
    NEXT_BUTTON = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("ДАЛЕЕ")')
    LOGIN_WITH_OTHER_NUMBER = (AppiumBy.ANDROID_UIAUTOMATOR,
                               'new UiSelector().text("Войти с другим номером")')

    # --- экран 2: ввод номера телефона ---
    PHONE_TITLE_STARTS = (AppiumBy.ANDROID_UIAUTOMATOR,
                          'new UiSelector().textStartsWith("Войдите с номером")')
    PHONE_FIELD = (AppiumBy.ANDROID_UIAUTOMATOR,
                   'new UiSelector().resourceId("login")')
    CANT_LOGIN_LINK = (AppiumBy.ANDROID_UIAUTOMATOR,
                       'new UiSelector().text("Не могу войти")')

    # --- экран 3: OTP «Введите код из СМС» ---
    OTP_TITLE = (AppiumBy.ANDROID_UIAUTOMATOR,
                 'new UiSelector().text("Введите код из СМС")')
    OTP_FIELD = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("otp")')

    # --- признак успеха (авторизованный профиль) ---
    # После успешного входа bottom sheet закрывается и вкладка «Профиль»
    # показывает карточку пользователя с картинкой МТС ID.
    MTS_ID_AVATAR = (AppiumBy.ACCESSIBILITY_ID, "Изображение МТС ID")


class LoginPage(BasePage):
    """Экраны входа MTS ID: fast-track → ввод номера → OTP → успешный вход."""

    # --- ожидание экрана/загрузки ---
    @allure.step("Дождаться открытия экрана входа (bottom sheet с WebView)")
    def wait_opened(self, timeout: int = _LOGIN_FLOW_TIMEOUT) -> bool:
        """Ждёт появления WebView-контейнера SSO."""
        return self.driver.is_present(LoginPageLocators.SCREEN_ROOT, timeout=timeout)

    @allure.step("Дождаться загрузки формы (появился первый экран флоу)")
    def wait_form_loaded(self, timeout: int = _LOGIN_FLOW_TIMEOUT) -> bool:
        """Ждёт, пока WebView отрисует первый экран флоу входа.

        Ждём появления контента (заголовок fast-track/ввода номера/OTP),
        а не исчезновения прогресс-бара: sdkSsoProgressForm остаётся в
        a11y-дереве после загрузки (не скрывается), и ожидание по нему
        выгорало бы весь таймаут впустую.

        Экраны fast-track/phone/otp рисуются после прогрузки — без этого
        ожидания элемент шага может ещё не существовать в a11y-дереве.
        """
        loaded_locators = (
            LoginPageLocators.WELCOME_BACK_TITLE,
            LoginPageLocators.PHONE_TITLE_STARTS,
            LoginPageLocators.OTP_TITLE,
        )
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            for locator in loaded_locators:
                if self.driver.is_present(locator, timeout=0.2):
                    return True
            time.sleep(0.5)
        return False

    # --- экран 1: fast-track «Рады видеть вас снова» ---
    @allure.step("Проверить, что показан fast-track «Рады видеть вас снова»")
    def is_welcome_back_screen(self) -> bool:
        return self.is_displayed(LoginPageLocators.WELCOME_BACK_TITLE)

    @allure.step("Нажать «ДАЛЕЕ» (подтвердить вход по сохранённому номеру)")
    def tap_next(self) -> None:
        self.tap(LoginPageLocators.NEXT_BUTTON)

    @allure.step("Проверить видимость кнопки «Войти с другим номером»")
    def is_login_with_other_number_visible(self) -> bool:
        return self.is_displayed(LoginPageLocators.LOGIN_WITH_OTHER_NUMBER)

    @allure.step("Дойти до экрана ввода номера (fast-track опционален)")
    def open_phone_input_screen(self) -> None:
        """Приводит форму к экрану ввода номера телефона.

        Первый экран флоу зависит от состояния SDK: «Рады видеть вас снова»
        (fast-track, SDK помнит номер) или сразу «Войдите с номером телефона
        любого оператора». Поведение менялось между сборками — fast-track
        считаем опциональным: если он показан, уходим на экран ввода через
        «Войти с другим номером» (сохранённый номер может отличаться от
        тестового), иначе экран ввода уже открыт.
        """
        if self.is_welcome_back_screen():
            self.tap_login_with_other_number()

        if not self.is_phone_input_screen():
            raise RuntimeError(
                "Не открылся экран ввода номера: нет ни fast-track «Рады "
                "видеть вас снова», ни «Войдите с номером телефона»")

    @allure.step("Нажать «Войти с другим номером»")
    def tap_login_with_other_number(self) -> None:
        self.tap(LoginPageLocators.LOGIN_WITH_OTHER_NUMBER)

    # --- экран 2: ввод номера телефона ---
    @allure.step("Проверить, что показан экран ввода номера телефона")
    def is_phone_input_screen(self) -> bool:
        return self.is_displayed(LoginPageLocators.PHONE_TITLE_STARTS)

    @allure.step("Ввести номер телефона {msisdn}")
    def type_phone(self, msisdn: str) -> None:
        """Вводит MSISDN в поле номера (поле принимает «сырые» цифры, +7 уже на экране)."""
        self.driver.tap_element(
            self.driver.wait_visible(LoginPageLocators.PHONE_FIELD, self.timeout))
        self.driver.type_text(LoginPageLocators.PHONE_FIELD, msisdn,
                              clear=True, timeout=self.timeout)
        # SDK перерисовывает экран (маска +7 …) после ввода — даём stability
        time.sleep(0.5)

    @allure.step("Нажать «ДАЛЕЕ» (отправить номер)")
    def submit_phone(self) -> None:
        # Кнопка активируется после валидации номера SDK — ждём полным
        # таймаутом флоу (BasePage.tap ждёт ctx.timeout, здесь нужно больше).
        self.driver.tap(LoginPageLocators.NEXT_BUTTON,
                        timeout=_LOGIN_FLOW_TIMEOUT)

    # --- экран 3: OTP ---
    @allure.step("Проверить, что показан экран «Введите код из СМС»")
    def is_otp_screen(self) -> bool:
        return self.is_displayed(LoginPageLocators.OTP_TITLE, _LOGIN_FLOW_TIMEOUT)

    @allure.step("Ввести код верификации")
    def type_otp(self, code: str) -> None:
        """Вводит OTP-код: вход выполняется автоматически после последней цифры."""
        field = self.driver.wait_visible(LoginPageLocators.OTP_FIELD,
                                         _LOGIN_FLOW_TIMEOUT)
        field.click()
        field.send_keys(code)

    @allure.step("Дождаться завершения входа (bottom sheet закрылся)")
    def wait_login_completed(self, timeout: int = _LOGIN_FLOW_TIMEOUT) -> bool:
        """Ждёт успешного входа: SSO bottom sheet закрылся, виден профиль.

        Признак успеха — аватар «Изображение МТС ID» на вкладке «Профиль»
        (появляется только у авторизованного пользователя).
        """
        return self.driver.is_present(LoginPageLocators.MTS_ID_AVATAR,
                                      timeout=timeout)

    @allure.step("Дождаться закрытия окна входа (SSO ушёл с экрана)")
    def wait_sheet_closed(self, timeout: int = _LOGIN_FLOW_TIMEOUT) -> bool:
        """Ждёт закрытия SSO-окна (контейнер mts_id уходит из разметки).

        В отличие от wait_login_completed (ждёт аватар на вкладке
        «Профиль») не привязан к конкретной вкладке: вход может быть
        запущен из другой вкладки (баннер на «Звонках»), и после входа
        приложение остаётся там, откуда открыли SSO.
        """
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if not self.driver.is_present(LoginPageLocators.SCREEN_ROOT,
                                          timeout=0.2):
                return True
            time.sleep(0.5)
        return False

    # --- отмена входа ---
    @allure.step("Отменить вход свайпом окна MTS ID вниз")
    def cancel_login_by_swipe_down(self, max_attempts: int = 5) -> None:
        """Отменяет ввод: свайп вниз за нижнюю кромку bottom sheet.

        МТС ID открыт в bottom sheet — стандартный жест отмены: тянем
        ручку (верх sheet) вниз до полного закрытия окна. Цель жеста —
        сам container design_bottom_sheet, не контент WebView внутри:
        тап по WebView центру открывал бы элементы формы вместо свайпа.
        После закрытия элемент пропадает из a11y-дерева — если жест не
        закрыл окно, перезапускаем свайп (до max_attempts).

        Жест выполняем от верхних 12% sheet'а к его нижней границе с
        перехлёстом (endY за экраном), иначе SDK распознаёт его как
        подтягивание контента, а не закрытие.
        """
        sheet = self.driver.wait_visible(LoginPageLocators.BOTTOM_SHEET,
                                         self.timeout)
        screen = self.driver.raw.get_window_size()
        screen_h = screen["height"]

        for attempt in range(max_attempts):
            if not self.driver.is_present(LoginPageLocators.BOTTOM_SHEET,
                                          timeout=0.5):
                return  # окно закрылось предыдущим свайпом
            bounds = sheet.get_attribute("bounds")
            m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
            x1, y1, x2, y2 = (int(g) for g in m.groups())
            start_y = y1 + max(1, int((y2 - y1) * 0.12))
            # тянем от верхней кромки sheet'а до низа экрана с перехлёстом
            self.driver.raw.execute_script("mobile: dragGesture", {
                "startX": (x1 + x2) // 2, "startY": start_y,
                "endX": (x1 + x2) // 2, "endY": screen_h + 50,
            })
            time.sleep(1.5)
        # Последняя проверка: окно могло закрыться сразу после exit-проверки
        if self.driver.is_present(LoginPageLocators.BOTTOM_SHEET, timeout=1):
            raise RuntimeError(
                "Bottom sheet MTS ID не закрылся свайпом вниз — вход не отменён")

    # --- сквозной сценарий ---
    @allure.step("Пройти флоу входа: номер телефона {msisdn} и код из СМС")
    def pass_login_flow(self, msisdn: str, code: str) -> None:
        """Флоу входа через уже открытую форму: fast-track → номер → OTP.

        Без ожиданий открытия/загрузки (ждите wait_opened/wait_form_loaded
        до вызова) и без проверки финального успеха. Это позволяет запускать
        вход с любой вкладки: SSO закрывается само, а приложение остаётся
        там, откуда вход был начат (не на вкладке «Профиль»), — признак
        успеха проверяет вызывающий код (wait_login_completed либо
        собственные проверки авторизованного состояния).

        Fast-track «Рады видеть вас снова» появляется, когда SDK уже
        сохранял номер: сохранённый номер может отличаться от тестового,
        поэтому уходим на экран ввода через «Войти с другим номером».
        """
        self.open_phone_input_screen()

        self.type_phone(msisdn)
        self.submit_phone()

        if not self.is_otp_screen():
            raise RuntimeError(
                "После «ДАЛЕЕ» не открылся экран «Введите код из СМС»")
        self.type_otp(code)

    @allure.step("Авторизоваться по номеру {msisdn} и коду из СМС")
    def login_with_credentials(self, msisdn: str, code: str) -> None:
        """Сквозной вход: открыть форму → флоу (pass_login_flow) → готово.

        Признак успеха — аватар на вкладке «Профиль»: вход с этой заготовки
        всегда завершается на вкладке «Профиль» (кнопка входа неавторизован-
        ного экрана профиля). Для входа, запущенного с другой вкладки
        (баннер «Звонков», точки входа диктофона), вызывайте
        pass_login_flow напрямую — приложение после входа остаётся на
        исходной вкладке.
        """
        if not self.wait_opened():
            raise RuntimeError(
                "Экран входа MTS ID не открылся: WebView SSO (sdkSsoWebLoginForm) "
                "не найден в разметке")
        self.wait_form_loaded()

        self.pass_login_flow(msisdn, code)

        if not self.wait_login_completed():
            raise RuntimeError(
                "Вход не завершился: аватар «Изображение МТС ID» не появился — "
                "проверьте MSISDN/VERIFICATION_CODE (код мог устареть)")
