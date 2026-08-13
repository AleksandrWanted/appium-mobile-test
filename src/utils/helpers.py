"""Утилиты: генерация тестовых данных."""
from __future__ import annotations

import random
import string


def random_string(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=length))


def random_email() -> str:
    return f"user_{random_string(6)}@test.example"
