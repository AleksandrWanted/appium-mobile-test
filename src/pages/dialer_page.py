"""Page Object номеронабирателя («Номер вызова») приложения МТС Optimus.

Локаторы сняты с разметки реального устройства (Samsung S21 FE, Android 15).
Номеронабиратель — Material bottom-sheet, открывается с экрана «Звонки» кликом
по FAB (CallsPageLocators.DIALER_BUTTON → pages.calls.open_dialer(), возвращает
DialerPage). Поверх экрана «Звонки» сохраняется нижнее меню с активной вкладкой
«Звонки»; закрывается шит системной кнопкой «Назад» (проверено) или тапом по
подложке touch_outside (кликабельна, стандартное поведение bottom-sheet).

Иерархия: design_bottom_sheet → rootContainer (handle) → content → contentCard
→ container: name (имя контакта, если номер распознан), phone (набираемый
номер), dailer (клавиатура — опечатка сохранена в resource-id приложения,
не исправлять!), call_button, delete_number. Клавиши — FrameLayout'ы
num_1..num_9, num_0 с дочерним TextView цифры; star (левая нижняя клавиша —
иконка без текста) и grid (правая, TextView «#») — клавиши нижнего ряда.

Важно: поле номера — TextView (не EditText), текст в него нельзя ввести через
send_keys; набор — только тапами по клавишам. При открытии поле уже содержит
плейсхолдер-маску «+7 (» ; набираемый номер форматируется маской
«+7 (XXX) XXX-XX-XX» (наблюдали «+7 (903) 384-11-»). Клавиши цифр и
delete_number помечены long-clickable (привычное «долгое нажатие»), поведение
долгих нажатий не проверялось. Кнопка вызова — зелёная FrameLayout с иконкой
трубки, без content-desc; нажатие начинает звонок — в тестах использовать с
осторожностью.
"""
from __future__ import annotations

import allure
from appium.webdriver.common.appiumby import AppiumBy

from src.pages.base_page import BasePage


class DialerPageLocators:
    """Локаторы номеронабирателя (МТС Optimus).

    Приоритет локаторов: id (resource-id) → текст (uiautomator).
    """

    # --- контейнер шита (Material bottom sheet) ---
    SCREEN_ROOT = (AppiumBy.ID, "ru.mts.mvats:id/design_bottom_sheet")

    # --- строка набора ---
    # Имя контакта, если набираемый номер есть в адресной книге; пустое при наборе.
    CONTACT_NAME = (AppiumBy.ID, "ru.mts.mvats:id/name")
    # TextView с маскированным номером; при открытии показывает «+7 (».
    PHONE_FIELD = (AppiumBy.ID, "ru.mts.mvats:id/phone")

    # --- клавиатура (опечатка в resource-id приложения: «dailer») ---
    KEYPAD = (AppiumBy.ID, "ru.mts.mvats:id/dailer")
    NUM_1 = (AppiumBy.ID, "ru.mts.mvats:id/num_1")
    NUM_2 = (AppiumBy.ID, "ru.mts.mvats:id/num_2")
    NUM_3 = (AppiumBy.ID, "ru.mts.mvats:id/num_3")
    NUM_4 = (AppiumBy.ID, "ru.mts.mvats:id/num_4")
    NUM_5 = (AppiumBy.ID, "ru.mts.mvats:id/num_5")
    NUM_6 = (AppiumBy.ID, "ru.mts.mvats:id/num_6")
    NUM_7 = (AppiumBy.ID, "ru.mts.mvats:id/num_7")
    NUM_8 = (AppiumBy.ID, "ru.mts.mvats:id/num_8")
    NUM_9 = (AppiumBy.ID, "ru.mts.mvats:id/num_9")
    NUM_0 = (AppiumBy.ID, "ru.mts.mvats:id/num_0")
    # Нижний ряд: левая клавиша — иконка без текста, правая — «#».
    KEY_STAR = (AppiumBy.ID, "ru.mts.mvats:id/star")
    KEY_HASH = (AppiumBy.ID, "ru.mts.mvats:id/grid")

    # --- действия ---
    # Зелёная кнопка трубки, без content-desc.
    CALL_BUTTON = (AppiumBy.ID, "ru.mts.mvats:id/call_button")
    # ImageButton справа от кнопки вызова: стирает последнюю цифру.
    DELETE_BUTTON = (AppiumBy.ID, "ru.mts.mvats:id/delete_number")


# Цифра → локатор клавиши (для type_number).
_DIGIT_KEYS: dict[str, tuple] = {
    "0": DialerPageLocators.NUM_0,
    "1": DialerPageLocators.NUM_1,
    "2": DialerPageLocators.NUM_2,
    "3": DialerPageLocators.NUM_3,
    "4": DialerPageLocators.NUM_4,
    "5": DialerPageLocators.NUM_5,
    "6": DialerPageLocators.NUM_6,
    "7": DialerPageLocators.NUM_7,
    "8": DialerPageLocators.NUM_8,
    "9": DialerPageLocators.NUM_9,
}


class DialerPage(BasePage):
    """Номеронабиратель приложения МТС Optimus.

    Открывается с экрана «Звонки»: pages.calls.open_dialer() (клик по FAB
    возвращает DialerPage). Закрытие — common.press_back(): шит схлопывается
    и возвращается экран «Звонки». Поле номера — только чтение: метод
    type_text не применим, ввод — press_digit/type_number.
    """

    # --- проверки состояния экрана ---
    @allure.step("Проверить, что номеронабиратель открыт")
    def is_loaded(self) -> bool:
        return self.is_displayed(DialerPageLocators.KEYPAD)

    # --- строка набора ---
    @allure.step("Получить имя контакта в поле имени")
    def get_contact_name(self) -> str:
        """Не пустое, только если набираемый номер есть в адресной книге."""
        return self.get_text(DialerPageLocators.CONTACT_NAME)

    @allure.step("Получить содержимое поля номера")
    def get_phone_number(self) -> str:
        """Маскированный номер; при пустом наборе — плейсхолдер «+7 (»."""
        return self.get_text(DialerPageLocators.PHONE_FIELD)

    # --- клавиатура ---
    @allure.step("Нажать цифру {digit}")
    def press_digit(self, digit: str | int) -> None:
        locator = _DIGIT_KEYS.get(str(digit))
        if locator is None:
            raise ValueError(f"Неизвестная цифра: {digit!r}")
        self.tap(locator)

    @allure.step("Набрать номер {number}")
    def type_number(self, number: str) -> None:
        """Последовательно нажать клавиши всех цифр номера (только «0»–«9»)."""
        for digit in number:
            self.press_digit(digit)

    @allure.step("Нажать клавишу #")
    def press_hash_key(self) -> None:
        self.tap(DialerPageLocators.KEY_HASH)

    @allure.step("Нажать левую клавишу нижнего ряда (star)")
    def press_star_key(self) -> None:
        self.tap(DialerPageLocators.KEY_STAR)

    # --- действия ---
    @allure.step("Стереть последнюю цифру")
    def delete_last_digit(self) -> None:
        self.tap(DialerPageLocators.DELETE_BUTTON)

    @allure.step("Проверить видимость кнопки стирания цифры")
    def is_delete_button_visible(self) -> bool:
        return self.is_displayed(DialerPageLocators.DELETE_BUTTON)

    @allure.step("Нажать кнопку вызова")
    def tap_call_button(self) -> None:
        """Начинает звонок на набираемый номер — осторожно в автотестах."""
        self.tap(DialerPageLocators.CALL_BUTTON)
