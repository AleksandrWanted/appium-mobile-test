# Запуск тестов

Пошаговое руководство по запуску автотестов на Android (эмулятор и реальное устройство).
Проект: **Appium + Python + pytest**. Приложение для дымового теста — «МТС Optimus»
(`resources/app/mts-optimus.apk`, пакет `ru.mts.mvats`).

---

## 1. Содержимое

- [Предварительные требования](#2-предварительные-требования)
- [Установка зависимостей](#3-установка-зависимостей)
- [Запуск Appium-сервера](#4-запуск-appium-сервера)
- [Подготовка устройства](#5-подготовка-устройства)
- [Конфигурация (APP_CONFIG)](#6-конфигурация-app_config)
- [Запуск тестов](#7-запуск-тестов)
- [Маркеры и фильтрация](#8-маркеры-и-фильтрация)
- [Отчёт Allure](#9-отчёт-allure)
- [Решение проблем](#10-решение-проблем)
- [Запуск в Docker](#11-запуск-в-docker)

---

## 2. Предварительные требования

| Компонент | Версия / примечание |
|---|---|
| Python | ≥ 3.10 (проверено на 3.14) |
| Poetry | ≥ 2.0 |
| Node.js | для Appium |
| Appium | 2.x (`npm install -g appium`) |
| UiAutomator2 driver | `appium driver install uiautomator2` |
| Android SDK | `adb`, `emulator`, `aapt2` в `PATH` |
| JDK | 17+ |

Проверить Appium и драйверы:

```bash
appium --version
appium driver list
```

---

## 3. Установка зависимостей

```bash
# Установить Poetry (macOS)
brew install poetry

# Установить зависимости проекта (создаст .venv)
poetry install
```

Все команды ниже — либо внутри `poetry shell`, либо с префиксом `poetry run`, либо
напрямую через `.venv/bin/python3` / `.venv/bin/pytest`.

---

## 4. Запуск Appium-сервера

В отдельном терминале:

```bash
poetry run appium        # поднимается на http://127.0.0.1:4723
```

Проверить, что отвечает:

```bash
curl -s http://127.0.0.1:4723/status | jq .
```

---

## 5. Подготовка устройства

### 5.1. Эмулятор

```bash
# Список доступных AVD
emulator -list-avds

# Запустить эмулятор (имя из конфига — Pixel_10)
emulator -avd Pixel_10 -no-snapshot-load &

# Дождаться полной загрузки
adb wait-for-device shell 'while [[ -z $(getprop sys.boot_completed) ]]; do sleep 1; done; echo boot ok'
adb devices
```

В `config/android.local.emul.yaml` указано `device_name: Pixel_10`. Имя AVD должно с ним совпадать.

### 5.2. Реальное устройство

1. Включить **Developer Options** и **USB debugging** на телефоне
   (`Settings → About phone → tap Build number 7×` → `System → Developer options`).
2. Подключить кабелем. На телефоне подтвердить диалог **«Разрешить отладку USB»**.
3. Проверить:

```bash
adb devices
# должно быть:
# R5CT21KZN7E    device
```

Если видно `unauthorized` — ответь «Разрешить» в диалоге на телефоне
(или `adb kill-server && adb start-server`).

---

## 6. Конфигурация (APP_CONFIG)

Конфиг — это YAML-файл в `config/`. Имя файла **без расширения** передаётся через
переменную окружения `APP_CONFIG` (или `.env`).

| `APP_CONFIG` | Файл | Назначение |
|---|---|---|
| `android.local.emul` | `config/android.local.emul.yaml` | Локальный эмулятор Pixel_10 |
| `android.local.real` | `config/android.local.real.yaml` | Реальное устройство (UDID `R5CT21KZN7E`) |
| `ios.local` | `config/ios.local.yaml` | iOS-симулятор (требуется macOS + Xcode) |

### Пример конфига реального устройства

```yaml
platform: android
automation_name: UiAutomator2
app: "resources/app/mts-optimus.apk"
platform_version: "15"
device_name: R5CT21KZN7E
udid: R5CT21KZN7E          # гарантирует, что Appium выберет телефон, а не эмулятор
remote_url: http://127.0.0.1:4723
no_reset: true
full_reset: false
new_command_timeout: 300
handle_permissions: false   # включать только если приложение реально показывает permission-диалоги
```

### Смена конфига

```bash
# Через переменную окружения (одноразово)
APP_CONFIG=android.local.real poetry run pytest tests/smoke/test_app_launch.py -v

# Через .env (постоянно)
echo 'APP_CONFIG=android.local.real' > .env
```

### Поле `handle_permissions`

- `false` (по умолчанию) — системные permission-диалоги **не** закрываются.
  Используй для приложений, которые не показывают диалоги при старте (МТС Optimus).
  Без этого флага тест проходил за **9 с** вместо ~56 с.
- `true` — `PermissionsHandler.grant_permissions()` закроет диалоги «Разрешить/Allow».
  Включай **только** для приложений, реально их показывающих.

---

## 7. Запуск тестов

> Appium-сервер должен быть запущен, устройство — подключено и видно в `adb devices`.

### Дымовой тест (запуск приложения)

```bash
# На эмуляторе
APP_CONFIG=android.local.emul poetry run pytest tests/smoke/test_app_launch.py -v

# На реальном устройстве
APP_CONFIG=android.local.real poetry run pytest tests/smoke/test_app_launch.py -v
```

Ожидаемый результат: `1 passed in ~9s`. Тест:
1. Проверяет активность Appium-сессии.
2. Best-effort ждёт прохождения сплэша (`SplashActivity` → другая активность, до 20 с).
3. Запрашивает состояние приложения через `mobile: queryAppState`.
4. Assert: процесс жив (`state ∈ {2,3,4}`).

### Все тесты

```bash
APP_CONFIG=android.local.real poetry run pytest -v
```

### Один тест по имени

```bash
APP_CONFIG=android.local.real poetry run pytest tests/smoke/test_app_launch.py::test_app_is_running -v
```

### Параллельно (pytest-xdist)

```bash
APP_CONFIG=android.local.real poetry run pytest -n auto
```

> ⚠ Фикстура `driver` — `scope="session"`. Для полноценной параллельной работы на
> одном хосте переведи её в `scope="function"` или поднимай отдельный `udid`/порт
> Appium на каждый воркер.

### С перезапуском упавших (pytest-rerunfailures)

```bash
APP_CONFIG=android.local.real poetry run pytest --reruns 2
```

### Без Allure (быстрый прогон)

```bash
APP_CONFIG=android.local.real poetry run pytest tests/smoke/ -v -p no:allure
```

### С выводом логов Appium в консоль (отладка)

```bash
APP_CONFIG=android.local.real poetry run pytest tests/smoke/test_app_launch.py -v \
  --log-cli-level=INFO
```

---

## 8. Маркеры и фильтрация

Зарегистрированные маркеры (`pyproject.toml`): `android`, `ios`, `smoke`.

```bash
# Только дымовые
poetry run pytest -m smoke -v

# Только Android
poetry run pytest -m android -v

# Smoke + Android (пересечение)
poetry run pytest -m "smoke and android" -v
```

### Текущие тесты

| Файл | Тест | Маркеры |
|---|---|---|
| `tests/smoke/test_app_launch.py` | `test_app_is_running` | `android`, `smoke` |
| `tests/login/test_login.py` | `test_login_success`, `test_login_invalid_credentials` | `android` |
| `tests/home/test_home.py` | `test_home_title_displayed` | `android` |

> `test_login_*` и `test_home_*` написаны под условный пример приложения и могут
> требовать актуальных локаторов/данных. Дымовой тест `test_app_is_running` —
> полностью рабочий для МТС Optimus.

---

## 9. Отчёт Allure

Результаты складываются в `reports/allure-results/` (`addopts` в `pyproject.toml`).

```bash
# Поднять локальный сервер отчётов
poetry run allure serve reports/allure-results

# Или сгенерировать статичный HTML
allure generate reports/allure-results -o reports/allure-report --clean
open reports/allure-report/index.html
```

В отчёте:
- шаги `@allure.step` из Page Object и бизнес-шаги из тестов;
- вложения: `session_current_package`, `splash_wait_result`, `app_state`;
- скриншот падения (автоматически в хуке `pytest_runtest_makereport`).

---

## 10. Решение проблем

| Симптом | Причина / решение |
|---|---|
| `The application at '...' does not exist or is not accessible` | В пути к APK есть пробелы/скобки. Переименуй файл (текущий: `mts-optimus.apk`) и проверь `app:` в конфиге. |
| `device unauthorized` | Подтверди диалог USB-отладки на телефоне; `adb kill-server && adb start_server`. |
| Appium создаёт сессию на эмуляторе вместо телефона | В конфиге реального устройства должен быть `udid: R5CT21KZN7E`. |
| Тест идёт ~50–60 с вместо ~9 с | В конфиге стоит `handle_permissions: true`, а приложение не показывает диалогов. Поставь `false`. |
| На эмуляторе сплэш закрывается, UI не выходит в фон | Норма: МТС Optimus использует Google Play Integrity, который не проходит на эмуляторе. Тест проверяет «процесс жив» через `queryAppState`. На реальном устройстве Integrity проходит — UI виден полностью. |
| `Potentially insecure feature 'adb_shell' has not been enabled` | Проект не использует `mobile: shell`. Если встретил — это где-то лишний вызов; используй `mobile: queryAppState` / `mobile: terminateApp` вместо `adb shell`. |
| Сессия падает по таймауту простоя | Подними `new_command_timeout` в конфиге (по умолчанию 300 с). |
| `aapt2: command not found` | Установи build-tools и добавь в `PATH`, либо используй `aapt` из `platform-tools`. |

### Логи Appium

```bash
# Запустить Appium с подробным логом в файл
poetry run appium --log reports/appium.log --log-level debug
tail -f reports/appium.log
```

### Логи устройства (logcat)

```bash
adb logcat -d | grep -i "ru.mts.mvats\|integrity\|AndroidRuntime"
```

---

## 11. Запуск в Docker

Самодостаточный Android-контейнер (эмулятор + Appium + pytest внутри). См. `Dockerfile`
и `README.md`.

```bash
# Сборка
docker build -t mobile-appium-android:latest .

# Без KVM (медленнее, но работает везде)
docker run --rm -v "$PWD/reports:/project/reports" mobile-appium-android:latest

# С KVM-ускорением (Linux)
docker run --rm --device /dev/kvm -v "$PWD/reports:/project/reports" mobile-appium-android:latest
```

Внутри контейнера `scripts/ci-android-entrypoint.sh` поднимает эмулятор → Appium →
`pytest -m android -n auto --reruns 2` и прокидывает результаты в `reports/`.
