"""Управление локальным Appium-сервером из фикстур pytest.

`ManagedAppiumServer.ensure_running()` проверяет доступность сервера и, если
тот не отвечает, поднимает собственный процесс `appium server`. Внешний сервер,
запущенный пользователем или CI, не помечается как управляемый и не трогается
при teardown.
"""
from __future__ import annotations

import logging
import shutil
import socket
import subprocess
import time
from pathlib import Path

import requests

log = logging.getLogger(__name__)

# Стандартный порт Appium; реальный берётся из remote_url конфига.
DEFAULT_PORT = 4723
# Сколько ждать готовности своего процесса.
STATUS_WAIT_TIMEOUT_S = 60
POLL_INTERVAL_S = 0.5

# Логи сервера, поднятого фикстурой; внешний сервер сюда не пишет.
LOG_DIR = Path("reports")


class AppiumServerError(RuntimeError):
    """Не удалось поднять локальный Appium-сервер."""


def is_appium_responsive(base_url: str, timeout: float = 2.0) -> bool:
    """True, если на {base_url}/status отвечает валидный сервер."""
    try:
        resp = requests.get(f"{base_url.rstrip('/')}/status", timeout=timeout)
    except requests.RequestException:
        return False
    return resp.ok


def _is_port_in_use(host: str, port: int) -> bool:
    """True, если TCP-порт чем-то занят (даже если это не Appium)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1.0)
        return sock.connect_ex((host, port)) == 0


def _wait_until_ready(base_url: str, timeout_s: float) -> bool:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if is_appium_responsive(base_url):
            return True
        time.sleep(POLL_INTERVAL_S)
    return False


class ManagedAppiumServer:
    """Локальный Appium-сервер, поднятый фикстурой и остановленный в teardown.

    Гарантии: (1) сервер отвечает при выдаче driver'а, (2) поднятый нами
    процесс остановлен после сессии; внешний сервер не трогается.
    """

    def __init__(
        self,
        address: str = "127.0.0.1",
        port: int = DEFAULT_PORT,
        session_override: bool = False,
        log_level: str = "info",
    ):
        self.address = address
        self.port = port
        self.session_override = session_override
        self.log_level = log_level
        self.process: subprocess.Popen | None = None
        self._log_path: Path | None = None

    @property
    def base_url(self) -> str:
        return f"http://{self.address}:{self.port}"

    @property
    def log_path(self) -> Path | None:
        return self._log_path

    def ensure_running(self) -> bool:
        """Удостовериться, что сервер отвечает. Возвращает True, если подняли сами."""
        if is_appium_responsive(self.base_url):
            log.info("Appium уже доступен на %s — используем внешний сервер", self.base_url)
            return False

        if not shutil.which("appium"):
            raise AppiumServerError(
                "Appium-сервер недоступен и бинарник `appium` не найден в PATH. "
                "Установите: npm install -g appium"
            )

        LOG_DIR.mkdir(parents=True, exist_ok=True)
        self._log_path = LOG_DIR / "appium_server.log"

        log.info("Appium недоступен на %s — запускаем собственный сервер", self.base_url)
        with self._log_path.open("ab") as log_file:
            log_file.write(
                f"--- автозапуск Appium фикстурой ({time.strftime('%Y-%m-%d %H:%M:%S')}) ---\n".encode()
            )
            argv = [
                "appium",
                "server",
                "--address",
                self.address,
                "--port",
                str(self.port),
                "--log",
                str(self._log_path),
                "--log-level",
                self.log_level,
            ]
            if self.session_override:
                argv.append("--session-override")
            self.process = subprocess.Popen(
                argv,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        if not _wait_until_ready(self.base_url, STATUS_WAIT_TIMEOUT_S):
            self.stop()
            hint = ""
            if _is_port_in_use(self.address, self.port):
                hint = (
                    f"\nПодсказка: порт {self.port} занят другим процессом — "
                    "проверьте `lsof -i :{port}`."
                )
            log_tail = ""
            if self._log_path.exists():
                log_tail = "\n".join(self._log_path.read_text(encoding="utf-8").splitlines()[-30:])
            raise AppiumServerError(
                f"Appium-сервер не поднялся за {STATUS_WAIT_TIMEOUT_S} c на {self.base_url}.\n"
                f"{hint}"
                f"Хвост лога: {log_tail}"
            )
            if self._log_path.exists():
                log_tail = "\n".join(self._log_path.read_text(encoding="utf-8").splitlines()[-30:])
            raise AppiumServerError(
                f"Appium-сервер не поднялся за {STATUS_WAIT_TIMEOUT_S} c на {self.base_url}.\n"
                f"Хвост лога: {log_tail}"
            )

        log.info("Appium поднят (pid=%s), лог: %s", self.process.pid, self._log_path)
        return True

    def stop(self) -> None:
        """Остановить поднятый нами процесс сервера (внешний не трогается)."""
        if self.process is None:
            return
        if self.process.poll() is None:
            log.info("Останавливаем поднятый нами Appium (pid=%s)", self.process.pid)
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        self.process = None
