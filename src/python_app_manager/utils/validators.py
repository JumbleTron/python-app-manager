"""Pure input validators used before changing system state."""

from __future__ import annotations

import re

from python_app_manager.domain.exceptions import (
    InvalidApplicationNameError,
    InvalidDomainError,
)

_APP_NAME = re.compile(r"^[a-z][a-z0-9-]{1,62}$")
_DOMAIN_LABEL = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")


def validate_app_name(name: str) -> str:
    """Zweryfikuj i zwróć nazwę bezpieczną do użycia w ścieżkach i unitach.

    :param name: Nazwa aplikacji.
    :return: Oryginalna nazwa po walidacji.
    :raises InvalidApplicationNameError: Gdy nazwa jest niepoprawna.
    """
    if not _APP_NAME.fullmatch(name):
        raise InvalidApplicationNameError(
            "Application name must start with a lowercase letter and contain only "
            "lowercase letters, digits and hyphens"
        )
    return name


def validate_domain(domain: str) -> str:
    """Zweryfikuj składnię domeny bez wykonywania zapytania DNS.

    :param domain: FQDN bez protokołu i ścieżki.
    :return: Oryginalna domena po walidacji.
    :raises InvalidDomainError: Gdy domena jest niepoprawna.
    """
    normalized = domain.rstrip(".").lower()
    labels = normalized.split(".")
    if len(labels) < 2 or len(normalized) > 253 or any(
        not _DOMAIN_LABEL.fullmatch(label) for label in labels
    ):
        raise InvalidDomainError("Domain must be a valid fully-qualified domain name")
    return normalized


def validate_port_range(start: int, end: int) -> tuple[int, int]:
    """Zweryfikuj zakres portów TCP.

    :param start: Początek zakresu włącznie.
    :param end: Koniec zakresu włącznie.
    :return: Zweryfikowana para `(start, end)`.
    :raises ValueError: Gdy zakres wykracza poza porty TCP lub jest odwrócony.
    """
    if not (1 <= start <= end <= 65535):
        raise ValueError("Port range must be between 1 and 65535")
    return start, end
