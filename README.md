# Mobile Appium Project

Типовой проект автоматизации мобильного тестирования на **Appium + Python + pytest**.

## Структура

```
config/          — YAML-конфиги окружений (android.local.emul, android.local.real, ios.local)
docs/            — RUN.md: подробное руководство по запуску тестов
src/driver/      — фабрика драйвера, обёртка с ожиданиями и скриншотами
src/pages/       — Page Object Pattern (BasePage, LoginPage, HomePage)
src/utils/       — хелперы и обработка системных диалогов (permissions.py)
tests/           — только тесты; conftest.py с фикстурами driver/test_data
resources/app/   — сборки приложений (mts-optimus.apk)
resources/data/  — тестовые данные (users.json)
reports/         — результаты запусков (allure, скриншоты)
scripts/         — entrypoint для Docker (ci-android-entrypoint.sh)
```

> 📖 **Подробное пошаговое руководство по запуску** (эмулятор, реальное устройство,
> маркеры, Allure, решение проблем) — в [`docs/RUN.md`](docs/RUN.md). Ниже — краткая выжимка.

## Требования

1. Appium-сервер: `npm install -g appium` (Appium 2.x)
2. Драйверы: `appium driver install uiautomator2` (Android), `appium driver install xcuitest` (iOS)
3. Эмулятор/устройство запущено, `adb devices` видит устройство
4. Сборка приложения в `resources/app/` — сейчас `mts-optimus.apk` (МТС Optimus, `ru.mts.mvats`)
5. `aapt2` / `aapt` для инспекции APK (имя пакета, launchable activity)

## Управление зависимостями

Проект использует **Poetry** (≥ 2.0). Все зависимости зафиксированы в `poetry.lock`.

```bash
# Установка Poetry (macOS, через Homebrew)
brew install poetry

# Установить зависимости проекта (создаст .venv)
poetry install

# Войти в виртуальное окружение
poetry shell
```

> Все команды ниже выполняются либо внутри `poetry shell`, либо через префикс `poetry run`.

## Запуск Appium

```bash
poetry run appium   # в отдельном терминале, поднимается на http://127.0.0.1:4723
```

## Запуск тестов

Конфиг выбирается переменной окружения `APP_CONFIG` (имя файла из `config/` без `.yaml`).
Доступные конфиги: `android.local.emul` (эмулятор Pixel_10), `android.local.real`
(реальное устройство, UDID `R5CT21KZN7E`), `ios.local` (симулятор).

```bash
# Дымовой тест на эмуляторе
APP_CONFIG=android.local.emul poetry run pytest tests/smoke/test_app_launch.py -v

# Дымовой тест на реальном устройстве
APP_CONFIG=android.local.real poetry run pytest tests/smoke/test_app_launch.py -v

# Все тесты
APP_CONFIG=android.local.real poetry run pytest -v

# Параллельно (pytest-xdist) — см. примечание про scope=driver ниже
APP_CONFIG=android.local.real poetry run pytest -n auto

# С перезапуском упавших (pytest-rerunfailures)
poetry run pytest --reruns 2

# Только дымовые
poetry run pytest -m smoke

# Отчёт allure
poetry run allure serve reports/allure-results
```

## Отчётность (Allure)

- Каждый шаг Page Object обёрнут в `@allure.step` — клики, ввод текста, проверки видны в отчёте.
- Тесты размечены `@allure.epic` / `@allure.feature` для группировки по модулям.
- Бизнес-шаги в тестах — через явные `with allure.step(...)`.
- Скриншот падения автоматически крепится к отчёту в хуке `pytest_runtest_makereport`.

## Обработка системных диалогов

`src/utils/permissions.py` — `PermissionsHandler` закрывает всплывающие permission-диалоги:

- нативные alert — через `driver.switch_to.alert`;
- кнопки «Разрешить»/«Allow» — по тексту через UiAutomator + accessibility id;
- мультиязычность (RU/EN);
- `grant_permissions()` — цикл для идущих подряд диалогов (камера → геолокация → уведомления);
- `dismiss_apk_installer()` — системный установщик APK (Install/Установить/Done/Готово).

Вызывается автоматически в фикстуре `driver` после старта приложения — **но только если в конфиге `handle_permissions: true`**. По умолчанию флаг `False`: для приложений, которые не показывают диалогов при старте (МТС Optimus), это экономит ~50 с на каждом запуске (поиск несуществующих кнопок «Разрешить»).

### Закрытие приложения после теста

Автоматическая фикстура `_close_app_after_test` (autouse) после каждого теста вызывает
`mobile: terminateApp` по `appPackage` из capabilities драйвера — каждый тест стартует
с чистого состояния приложения. Если сессия уже умерла — тихо пропускает.

### Ограничение эмулятора (Play Integrity)

МТС Optimus — release-сборка с Google Play Integrity. На эмуляторе `requestIntegrityToken`
заваливается, splash-активность закрывается без краша, и UI не выходит в фон. Поэтому
дымовой тест `test_app_is_running`:

- best-effort ждёт прохождения сплэша (`SplashActivity` → другая активность, до 20 с, не падает при таймауте);
- твёрдо проверяет только «процесс жив» через `mobile: queryAppState` (`state ∈ {2,3,4}`).

На реальном устройстве Integrity проходит — сплэш сменяется `MainActivity`, UI виден полностью.

## CI (GitLab)

`.gitlab-ci.yml` — pipeline из трёх стадий `build → test → report`:

- `build:image` — собирает Docker-образ для Android (см. ниже) и пушит в GitLab Container Registry. Триггерится только при изменении `Dockerfile` / `pyproject.toml` / `poetry.lock` / entrypoint;
- `test:android` — тег `mobile-android`, бежит в собранном образе: эмулятор + Appium + `pytest -m android -n auto --reruns 2` поднимаются внутри контейнера (`scripts/ci-android-entrypoint.sh`);
- `test:ios` — тег `mobile-ios-mac`, нативный shell-executor на macOS (Docker для iOS не подходит): симулятор через `xcrun simctl`, `poetry install`, `pytest -m ios`;
- `allure:report` — сборка HTML-отчёта из артефактов обеих платформ;
- артефакты: `allure-results/` + `reports/screenshots/` + `reports/appium.log` + `reports/emulator.log`.

> BrowserStack и облачных провайдеров нет — только локальные эмуляторы/симуляторы.
> iOS-раннеру нужны предустановленные Xcode, Appium + `xcuitest`, Poetry.

## Docker (самодостаточный Android-контейнер)

`Dockerfile` собирает образ с Android SDK, headless-эмулятором (готовый AVD `ci_emulator`), Appium 2 + UiAutomator2 и Poetry-зависимостями. Эмулятор поднимается **внутри контейнера** — runner'у не нужен хост-эмулятор, только docker executor.

### Сборка образа

```bash
docker build -t mobile-appium-android:latest .
```

### Локальный запуск тестов в контейнере

```bash
# Без KVM (software-режим эмулятора — медленнее, но работает везде):
docker run --rm -v "$PWD/reports:/project/reports" mobile-appium-android:latest

# С KVM-ускорением (Linux, если /dev/kvm доступен) — заметно быстрее:
docker run --rm --device /dev/kvm -v "$PWD/reports:/project/reports" mobile-appium-android:latest
```

Ключ `-v .../reports` пробрасывает наружу результаты: `allure-results/`, скриншоты, `appium.log`, `emulator.log`.

### Запуск вручную (отладка)

```bash
docker run --rm -it --device /dev/kvm mobile-appium-android:latest bash
# внутри контейнера:
bash scripts/ci-android-entrypoint.sh   # полный прогон: эмулятор → Appium → pytest
```

### Что внутри entrypoint

`scripts/ci-android-entrypoint.sh` последовательно:
1. проверяет `/dev/kvm` → `-accel auto` (быстро) или `-no-accel` (software);
2. поднимает `emulator -avd ci_emulator -no-window -no-audio -no-snapshot -no-boot-anim`;
3. ждёт `sys.boot_completed` (до 90 × 2 с), при таймауте печатает хвост `emulator.log` и падает;
4. разблокирует экран (`keyevent 82`);
5. поднимает Appium на `:4723`, ждёт `/status`;
6. гонит `pytest -m android -n auto --reruns 2`;
7. гасит Appium и эмулятор, прокидывает код возврата.

### Нюансы

- **KVM критичен для скорости.** На Linux-runner'е пробросьте `/dev/kvm` (`devices = ["/dev/kvm"]` в config.toml GitLab-runner или `privileged: true`). Без него тесты идут в 5–10× медленнее.
- **ARM-хост** (Apple Silicon): замените `ANDROID_ABI=x86_64` → `arm64-v8a` в `Dockerfile`.
- Образ тяжёлый (~3–4 ГБ из-за системного образа Android) — собирайте редко (уже обеспечено `rules: changes`) и храните в Registry.
- **iOS в Docker не запускается** — XCUITest требует macOS + Xcode, доступа к симулятору из контейнера нет. iOS-тесты идут только на нативном Mac-runner.

## Особенности

- **Page Object Pattern** — тесты не трогают driver напрямую.
- **Explicit Waits** — никаких `sleep()`; только `WebDriverWait`.
- **Конфиг через pydantic** — валидация на старте, переключение окружения переменной `APP_CONFIG`.
- **`handle_permissions` флаг** — опциональное закрытие permission-диалогов (по умолчанию выключено ради скорости).
- **Автозакрытие приложения** после каждого теста (autouse-фикстура + `mobile: terminateApp`).
- **Скриншоты при падении** — автоматом через хук `pytest_runtest_makereport`.
- **Идемпотентность** — каждый тест сам поднимает своё состояние.
- **Cross-platform** — одни тесты, переключение через маркеры `-m android`/`-m ios` и конфиг.

## Текущие тесты

| Файл | Тест | Маркеры |
|---|---|---|
| `tests/smoke/test_app_launch.py` | `test_app_is_running` | `android`, `smoke` |
| `tests/login/test_login.py` | `test_login_success`, `test_login_invalid_credentials` | `android` |
| `tests/home/test_home.py` | `test_home_title_displayed` | `android` |

> `test_login_*` и `test_home_*` — условные примеры под шаблонное приложение и могут
> требовать актуальных локаторов/данных. Дымовой тест `test_app_is_running` полностью
> рабочий для МТС Optimus.
