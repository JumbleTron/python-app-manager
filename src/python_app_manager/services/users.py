"""System users and groups used to isolate applications."""

from __future__ import annotations

import grp
import pwd
from dataclasses import dataclass

from python_app_manager.infrastructure.command_runner import CommandRunner


@dataclass(frozen=True, slots=True)
class ApplicationIdentity:
    """Tożsamość systemowa aplikacji."""

    app_user: str
    app_group: str
    deploy_user: str


class UserService:
    """Tworzy izolowane konto aplikacji i nadaje dostęp użytkownikowi deploy."""

    def __init__(self, runner: CommandRunner | None = None) -> None:
        self._runner = runner or CommandRunner()

    def ensure_identity(self, identity: ApplicationIdentity) -> None:
        """Utwórz user/grupę aplikacji i dodaj deploy usera do grupy.

        :param identity: Nazwy usera, grupy i użytkownika deployującego.
        :return: `None` po pomyślnym zakończeniu.
        :raises CommandExecutionError: Gdy narzędzie systemowe odmówi operacji.
        """
        if not self._group_exists(identity.app_group):
            self._runner.run(["groupadd", "--system", identity.app_group])
        if not self._user_exists(identity.app_user):
            self._runner.run(
                [
                    "useradd",
                    "--system",
                    "--no-create-home",
                    "--shell",
                    "/usr/sbin/nologin",
                    "--gid",
                    identity.app_group,
                    identity.app_user,
                ]
            )
        self._runner.run(
            ["usermod", "--append", "--groups", identity.app_group, identity.deploy_user]
        )

    @staticmethod
    def _user_exists(username: str) -> bool:
        try:
            pwd.getpwnam(username)
        except KeyError:
            return False
        return True

    @staticmethod
    def _group_exists(groupname: str) -> bool:
        try:
            grp.getgrnam(groupname)
        except KeyError:
            return False
        return True
