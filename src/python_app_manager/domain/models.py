"""Typed domain objects used by application-management workflows."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ApplicationSpec:
    """Opis aplikacji przekazany do procesu provisioningu.

    :param name: Bezpieczna nazwa aplikacji.
    :param domain: Nazwa domenowa używana przez reverse proxy.
    :param deploy_user: Wspólny użytkownik wykonujący deploy, domyślnie `gitlab`.
    :param app_user: Użytkownik systemowy aplikacji; domyślnie nazwa aplikacji.
    :param app_group: Grupa systemowa aplikacji; domyślnie nazwa aplikacji.
    :param with_mysql: Czy utworzyć zasoby MySQL.
    """

    name: str
    domain: str
    deploy_user: str = "gitlab"
    app_user: str | None = None
    app_group: str | None = None
    with_mysql: bool = False

    def resolved_app_user(self) -> str:
        """Zwróć użytkownika aplikacji, używając nazwy aplikacji jako domyślnej."""
        return self.app_user or self.name

    def resolved_app_group(self) -> str:
        """Zwróć grupę aplikacji, używając nazwy aplikacji jako domyślnej."""
        return self.app_group or self.name


@dataclass(frozen=True, slots=True)
class ApplicationRecord:
    """Trwały wpis aplikacji w rejestrze narzędzia."""

    name: str
    domain: str
    deploy_user: str
    app_user: str
    app_group: str
    port: int
    path: Path
    service_name: str
    mysql_database: str | None = None
