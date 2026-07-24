"""Provisioning of isolated MySQL databases and users."""

from __future__ import annotations

import re
from dataclasses import dataclass

from python_app_manager.infrastructure.command_runner import CommandRunner

_MYSQL_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_]{1,62}$")


@dataclass(frozen=True, slots=True)
class MysqlApplicationResources:
    """Nazwy zasobów MySQL utworzonych dla aplikacji."""

    database: str
    username: str


class MysqlService:
    """Tworzy osobną bazę i użytkownika MySQL dla jednej aplikacji."""

    def __init__(self, runner: CommandRunner | None = None) -> None:
        self._runner = runner or CommandRunner()

    def provision(
        self,
        app_name: str,
        password: str,
        *,
        database_prefix: str = "app",
    ) -> MysqlApplicationResources:
        """Utwórz bazę, użytkownika i uprawnienia MySQL.

        :param app_name: Bezpieczna nazwa aplikacji.
        :param password: Hasło aplikacyjnego użytkownika MySQL; nie jest logowane.
        :param database_prefix: Prefiks nazw baz i użytkowników.
        :return: Nazwy utworzonych zasobów.
        :raises ValueError: Gdy identyfikator nie jest bezpieczny.
        :raises CommandExecutionError: Gdy klient MySQL zwróci błąd.
        """
        database = self._identifier(f"{database_prefix}_{app_name}")
        username = self._identifier(f"{database_prefix}_{app_name}")
        sql = "\n".join(
            [
                f"CREATE DATABASE IF NOT EXISTS `{database}`;",
                f"CREATE USER IF NOT EXISTS '{username}'@'localhost' IDENTIFIED BY '{_escape_sql(password)}';",
                f"ALTER USER '{username}'@'localhost' IDENTIFIED BY '{_escape_sql(password)}';",
                f"GRANT ALL PRIVILEGES ON `{database}`.* TO '{username}'@'localhost';",
                "FLUSH PRIVILEGES;",
            ]
        )
        self._runner.run(["mysql", "--protocol=socket", "--batch", "--skip-column-names"], input_text=sql)
        return MysqlApplicationResources(database=database, username=username)

    def remove(self, database: str, username: str) -> None:
        """Usuń bazę i użytkownika MySQL aplikacji.

        :param database: Nazwa bazy.
        :param username: Nazwa użytkownika.
        :return: `None` po pomyślnym zakończeniu.
        :raises ValueError: Gdy identyfikatory są niebezpieczne.
        :raises CommandExecutionError: Gdy MySQL zwróci błąd.
        """
        safe_database = self._identifier(database)
        safe_username = self._identifier(username)
        sql = "\n".join(
            [
                f"DROP DATABASE IF EXISTS `{safe_database}`;",
                f"DROP USER IF EXISTS '{safe_username}'@'localhost';",
                "FLUSH PRIVILEGES;",
            ]
        )
        self._runner.run(
            ["mysql", "--protocol=socket", "--batch", "--skip-column-names"],
            input_text=sql,
        )

    @staticmethod
    def _identifier(value: str) -> str:
        if not _MYSQL_IDENTIFIER.fullmatch(value):
            raise ValueError(f"Unsafe MySQL identifier: {value!r}")
        return value


def _escape_sql(value: str) -> str:
    """Escape SQL string literal without exposing it to shell parsing."""
    return value.replace("\\", "\\\\").replace("'", "\\'")
