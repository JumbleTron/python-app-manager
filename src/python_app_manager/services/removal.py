"""Coordinated, explicit application removal."""

from __future__ import annotations

from pathlib import Path

from python_app_manager.infrastructure.database import StateRepository
from python_app_manager.services.filesystem import FilesystemService
from python_app_manager.services.mysql import MysqlService
from python_app_manager.services.nginx import NginxService
from python_app_manager.services.systemd import SystemdService


class RemovalService:
    """Usuwa zasoby aplikacji w kontrolowanej kolejności."""

    def __init__(
        self,
        repository: StateRepository,
        *,
        filesystem: FilesystemService | None = None,
        systemd: SystemdService | None = None,
        nginx: NginxService | None = None,
        mysql: MysqlService | None = None,
    ) -> None:
        self._repository = repository
        self._filesystem = filesystem or FilesystemService()
        self._systemd = systemd or SystemdService()
        self._nginx = nginx or NginxService()
        self._mysql = mysql or MysqlService()

    def remove(
        self,
        name: str,
        *,
        systemd_directory: Path,
        nginx_available: Path,
        nginx_enabled: Path,
        remove_database: bool = False,
    ) -> None:
        """Usuń usługę, nginx, katalog, rekord i opcjonalną bazę.

        :param name: Nazwa aplikacji.
        :param systemd_directory: Katalog unitów systemd.
        :param nginx_available: Katalog `sites-available`.
        :param nginx_enabled: Katalog `sites-enabled`.
        :param remove_database: Czy usunąć bazę i użytkownika MySQL.
        :return: `None` po pomyślnym zakończeniu.
        """
        record = self._repository.get(name)
        self._systemd.remove(record["service_name"], systemd_directory)
        self._nginx.remove(name, nginx_available, nginx_enabled)
        if remove_database and record["mysql_database"]:
            self._mysql.remove(record["mysql_database"], f"app_{name}")
        self._filesystem.remove_layout(Path(record["path"]))
        self._repository.remove(name)
