"""Interactive prompts for sensitive values."""

from __future__ import annotations

from getpass import getpass


def prompt_mysql_password() -> str:
    """Pobierz i potwierdź hasło MySQL bez wyświetlania znaków.

    :return: Hasło wpisane przez operatora.
    :raises ValueError: Gdy hasła są puste lub różne.
    """
    password = getpass("MySQL application password: ")
    confirmation = getpass("Confirm MySQL application password: ")
    if not password:
        raise ValueError("MySQL password cannot be empty")
    if password != confirmation:
        raise ValueError("MySQL passwords do not match")
    return password
