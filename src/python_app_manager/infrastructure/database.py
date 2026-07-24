"""SQLite metadata repository and atomic port reservations."""

from __future__ import annotations

import sqlite3
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from python_app_manager.domain.exceptions import (
    ApplicationManagerError,
    ApplicationNotFoundError,
    PortUnavailableError,
)
from python_app_manager.domain.models import ApplicationRecord


class ApplicationAlreadyExistsError(ApplicationManagerError):
    """Aplikacja o podanej nazwie jest już zarejestrowana."""


class StateRepository:
    """Przechowuje metadane aplikacji bez haseł i sekretów."""

    def __init__(self, database_path: Path) -> None:
        self._path = database_path
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._path, timeout=30)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS applications (
                    name TEXT PRIMARY KEY,
                    domain TEXT NOT NULL,
                    deploy_user TEXT NOT NULL,
                    app_user TEXT NOT NULL,
                    app_group TEXT NOT NULL,
                    port INTEGER NOT NULL UNIQUE,
                    path TEXT NOT NULL,
                    service_name TEXT NOT NULL UNIQUE,
                    mysql_database TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE TABLE IF NOT EXISTS port_reservations (port INTEGER PRIMARY KEY)"
            )

    def claim_port(
        self,
        start: int,
        end: int,
        *,
        checker: Callable[[int], bool],
    ) -> int:
        """Atomowo zarezerwuj pierwszy wolny port w SQLite.

        :param start: Początek zakresu.
        :param end: Koniec zakresu.
        :param checker: Dodatkowy test rzeczywistego nasłuchu systemowego.
        :return: Zarezerwowany port.
        :raises PortUnavailableError: Gdy zakres jest zajęty.
        """
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            used = {
                row[0]
                for row in connection.execute(
                    "SELECT port FROM applications UNION SELECT port FROM port_reservations"
                ).fetchall()
            }
            for port in range(start, end + 1):
                if port in used or not checker(port):
                    continue
                # Rezerwacja jest reprezentowana przez osobną transakcję wywołującego;
                # tymczasowo zajęty port zostanie zwolniony lub zamieniony na rekord.
                try:
                    connection.execute("INSERT INTO port_reservations(port) VALUES (?)", (port,))
                except sqlite3.IntegrityError:
                    continue
                connection.commit()
                return port
            connection.rollback()
        raise PortUnavailableError(f"No free port found in range {start}-{end}")

    def release_port(self, port: int) -> None:
        """Zwolnij tymczasową rezerwację portu."""
        with self._connect() as connection:
            connection.execute("DELETE FROM port_reservations WHERE port = ?", (port,))

    def register(self, record: ApplicationRecord) -> None:
        """Zapisz aplikację po pomyślnym provisioningu.

        :param record: Metadane aplikacji; nie powinny zawierać sekretów.
        :raises ApplicationAlreadyExistsError: Gdy nazwa lub usługa już istnieje.
        """
        now = datetime.now(UTC).isoformat()
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO applications
                    (name, domain, deploy_user, app_user, app_group, port, path,
                     service_name, mysql_database, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.name,
                        record.domain,
                        record.deploy_user,
                        record.app_user,
                        record.app_group,
                        record.port,
                        str(record.path),
                        record.service_name,
                        record.mysql_database,
                        now,
                        now,
                    ),
                )
                connection.execute(
                    "DELETE FROM port_reservations WHERE port = ?", (record.port,)
                )
        except sqlite3.IntegrityError as error:
            raise ApplicationAlreadyExistsError(record.name) from error

    def list_all(self) -> list[sqlite3.Row]:
        """Zwróć wszystkie aplikacje posortowane po nazwie."""
        with self._connect() as connection:
            return connection.execute("SELECT * FROM applications ORDER BY name").fetchall()

    def get(self, name: str) -> sqlite3.Row:
        """Pobierz aplikację po nazwie.

        :param name: Nazwa aplikacji.
        :return: Rekord SQLite.
        :raises ApplicationNotFoundError: Gdy aplikacja nie istnieje.
        """
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM applications WHERE name = ?", (name,)).fetchone()
        if row is None:
            raise ApplicationNotFoundError(name)
        return row

    def remove(self, name: str) -> None:
        """Usuń metadane aplikacji z rejestru."""
        with self._connect() as connection:
            connection.execute("DELETE FROM applications WHERE name = ?", (name,))
