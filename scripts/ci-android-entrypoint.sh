#!/usr/bin/env bash
# Entry point самодостаточного Android-контейнера.
# Поднимает headless-эмулятор, Appium, прогоняет тесты — без хост-эмулятора.
set -euo pipefail

AVD_NAME="${AVD_NAME:-ci_emulator}"
ADB_PORT="${ADB_PORT:-5555}"
APPIUM_PORT="${APPIUM_PORT:-4723}"

# --- KVM: аппаратное ускорение (опционально) -------------------------------
# Если /dev/kvm доступен — эмулятор пойдёт с -accel auto (быстро).
# Если нет (обычный docker executor без вложенной виртуализации) —
# падаем на software-режим (-no-accel), он медленнее, но работает.
ACCEL_FLAG="-no-accel"
if [ -e /dev/kvm ] && [ -w /dev/kvm ]; then
    echo "==> KVM доступен — аппаратное ускорение включено."
    ACCEL_FLAG="-accel auto"
fi

# --- 1. Запуск headless-эмулятора ------------------------------------------
echo "==> Запуск эмулятора '${AVD_NAME}' (headless)..."
# no-window: без GUI; no-audio: без звука; no-snapshot: чистый старт каждый раз;
# no-boot-anim: пропускаем загрузочную анимацию.
emulator -avd "${AVD_NAME}" \
    -no-window -no-audio -no-snapshot -no-boot-anim \
    -port "${ADB_PORT}" ${ACCEL_FLAG} \
    > reports/emulator.log 2>&1 &
EMU_PID=$!

# --- 2. Ждём загрузки эмулятора --------------------------------------------
echo "==> Ожидание загрузки эмулятора..."
adb wait-for-device
BOOT_OK=0
for _ in $(seq 1 90); do
    if [ "$(adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" = "1" ]; then
        BOOT_OK=1
        echo "==> Эмулятор загрузился (PID ${EMU_PID})."
        break
    fi
    sleep 2
done
if [ "${BOOT_OK}" != "1" ]; then
    echo "!! Эмулятор не загрузился за отведённое время. Хвост emulator.log:"
    tail -n 40 reports/emulator.log || true
    kill "${EMU_PID}" 2>/dev/null || true
    exit 1
fi

# Скриншот-девайс иногда надо разблокировать перед тестами.
adb shell input keyevent 82 >/dev/null 2>&1 || true

# --- 3. Appium server ------------------------------------------------------
echo "==> Запуск Appium server на :${APPIUM_PORT}..."
appium --port "${APPIUM_PORT}" --log-timestamp --log-level info \
    > reports/appium.log 2>&1 &
APPIUM_PID=$!

APPIUM_OK=0
for _ in $(seq 1 30); do
    if curl -sf "http://localhost:${APPIUM_PORT}/status" >/dev/null; then
        APPIUM_OK=1
        echo "==> Appium готов."
        break
    fi
    sleep 1
done
if [ "${APPIUM_OK}" != "1" ]; then
    echo "!! Appium не поднялся. Хвост appium.log:"
    tail -n 40 reports/appium.log || true
    kill "${EMU_PID}" "${APPIUM_PID}" 2>/dev/null || true
    exit 1
fi

# --- 4. Тесты --------------------------------------------------------------
echo "==> Запуск тестов (APP_CONFIG=${APP_CONFIG:-android.local.emul})..."
TEST_RC=0
poetry run pytest -m android -n auto --reruns 2 || TEST_RC=$?

# --- 5. Уборка -------------------------------------------------------------
echo "==> Останавливаю Appium (PID ${APPIUM_PID}) и эмулятор (PID ${EMU_PID})..."
kill "${APPIUM_PID}" 2>/dev/null || true
adb -s "emulator-${ADB_PORT}" emu kill 2>/dev/null || true
kill "${EMU_PID}" 2>/dev/null || true

exit "${TEST_RC}"
