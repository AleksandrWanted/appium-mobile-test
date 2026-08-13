# Полностью самодостаточный образ для Android-тестов:
# Android SDK + системный образ + готовый AVD (headless-эмулятор) + Appium + Python.
#
# Внутри поднимается эмулятор через emulator -no-window -no-audio,
# поэтому runner'у не нужен хост-эмулятор — только Docker (DinD или docker executor).
FROM ghcr.io/android-actions/android-sdk:latest

# Версии инструментов — зафиксированы для воспроизводимости.
# Appium 3.6.0 + UiAutomator2 3.10.0 соответствуют локальному окружению проекта.
# ABI x86_64 быстрее всего в эмуляторе на CI-машинерии (KVM/HVF при наличии).
ENV ANDROID_API_LEVEL=34
ENV ANDROID_BUILD_TOOLS=34.0.0
ENV ANDROID_ABI=x86_64
ENV AVD_NAME=ci_emulator
ENV APPIUM_VERSION=3.6.0
ENV UIAUTOMATOR2_VERSION=3.10.0
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV POETRY_NO_INTERACTION=1

# cmdline-tools (avdmanager) не на PATH в базовом образе — добавляем явно.
ENV PATH=/root/cmdline-tools/latest/bin:$PATH

# --- Системные зависимости -------------------------------------------------
# Графические библиотеки нужны emulator'у даже в headless-режиме (-no-window).
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl ca-certificates gnupg \
        nodejs npm \
        openjdk-17-jre-headless \
        libgl1 libx11-6 libxcomposite1 libxcursor1 libxdamage1 \
        libxrandr2 libasound2 libatk1.0-0 libatk-bridge2.0-0 \
        libpango-1.0-0 libcairo2 libnss3 libnspr4 libgbm1 \
    && rm -rf /var/lib/apt/lists/*

# --- Python + Poetry -------------------------------------------------------
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# --- Appium server + драйвер UiAutomator2 ---------------------------------
RUN npm install -g appium@${APPIUM_VERSION} \
    && appium driver install uiautomator2@${UIAUTOMATOR2_VERSION}

# --- Системный образ + AVD для headless-эмулятора --------------------------
# sdkmanager/adb/emulator уже на PATH из базового образа; avdmanager добавлен выше
# через PATH (cmdline-tools/latest/bin). cmdline-tools ставим, если вдруг отсутствует.
RUN yes | sdkmanager --licenses >/dev/null 2>&1 \
    && sdkmanager \
        "system-images;android-${ANDROID_API_LEVEL};google_apis;${ANDROID_ABI}" \
        "cmdline-tools;latest" \
        "platform-tools" "emulator" \
        "platforms;android-${ANDROID_API_LEVEL}" \
        "build-tools;${ANDROID_BUILD_TOOLS}"

RUN echo "no" | avdmanager create avd \
        --name "${AVD_NAME}" \
        --package "system-images;android-${ANDROID_API_LEVEL};google_apis;${ANDROID_ABI}" \
        --force

# --- Рабочая директория ----------------------------------------------------
WORKDIR /project

# Сначала только манифесты зависимостей — кешируем слой установки.
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --without dev

# Дальше — исходники тестов (меняются чаще, слой дешевле).
COPY . .

RUN mkdir -p reports/allure-results reports/screenshots
# В контейнере бежит эмулятор, поэтому конфиг эмулятора (android.local.emul).
# ВАЖНО: файла android.local.yaml в проекте нет — был устаревший дефолт,
# приводивший к FileNotFoundError на старте pytest.
ENV APP_CONFIG=android.local.emul

EXPOSE 4723

# Эмулятор + Appium стартуют в entrypoint. См. scripts/ci-android-entrypoint.sh.
CMD ["bash", "scripts/ci-android-entrypoint.sh"]
