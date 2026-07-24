"""Interactive prompts for sensitive values."""

from __future__ import annotations

import os
from getpass import getpass


def prompt_mysql_password() -> str:
    """Pobierz i potwierdź hasło MySQL bez wyświetlania znaków.

    :return: Hasło wpisane przez operatora.
    :raises ValueError: Gdy hasła są puste lub różne.
    """
    automated_password = os.environ.get("CREATE_PYTHON_APP_MYSQL_PASSWORD")
    if automated_password is not None:
        if not automated_password:
            raise ValueError("CREATE_PYTHON_APP_MYSQL_PASSWORD cannot be empty")
        return automated_password

    password = getpass("MySQL application password: ")
    confirmation = getpass("Confirm MySQL application password: ")
    if not password:
        raise ValueError("MySQL password cannot be empty")
    if password != confirmation:
        raise ValueError("MySQL passwords do not match")
    return password
