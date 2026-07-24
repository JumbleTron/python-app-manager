"""Secure random secret generation."""

from __future__ import annotations

import secrets


def generate_secret_key(length: int = 48) -> str:
    """Wygeneruj kryptograficznie bezpieczny klucz aplikacji.

    :param length: Minimalna liczba bajtów losowości przed kodowaniem URL-safe.
    :return: Klucz zawierający bezpieczne znaki ASCII.
    :raises ValueError: Gdy długość jest mniejsza niż 32 bajty.
    """
    if length < 32:
        raise ValueError("Secret key must contain at least 32 bytes of entropy")
    return secrets.token_urlsafe(length)


def generate_password(length: int = 32) -> str:
    """Wygeneruj losowe hasło przeznaczone np. dla użytkownika MySQL.

    :param length: Liczba bajtów losowości.
    :return: URL-safe hasło ASCII.
    :raises ValueError: Gdy długość jest mniejsza niż 16 bajtów.
    """
    if length < 16:
        raise ValueError("Password must contain at least 16 bytes of entropy")
    return secrets.token_urlsafe(length)
