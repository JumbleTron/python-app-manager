"""Application directory layout and POSIX permissions."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from python_app_manager.infrastructure.command_runner import CommandRunner


class FilesystemService:
    """Tworzy strukturę katalogów aplikacji i ustawia jej ownership."""

    def create_layout(
        self,
        app_root: Path,
        *,
        app_user: str,
        app_group: str,
        deploy_user: str,
    ) -> None:
        """Utwórz katalogi aplikacji z bezpiecznymi prawami dostępu.

        :param app_root: Katalog główny aplikacji.
        :param app_user: Użytkownik uruchamiający usługę.
        :param app_group: Grupa aplikacji.
        :param deploy_user: Użytkownik zapisujący kod podczas deployu.
        :return: `None` po pomyślnym zakończeniu.
        :raises OSError: Gdy system nie pozwoli utworzyć lub zmienić plików.
        """
        app_dir = app_root / "app"
        uploads_dir = app_root / "shared" / "uploads"
        logs_dir = app_root / "shared" / "logs"
        venv_dir = app_root / ".venv"

        for directory in (app_dir, uploads_dir, logs_dir, venv_dir):
            directory.mkdir(parents=True, exist_ok=True)

        # Kod może zapisywać deploy user, ale proces aplikacji ma tylko odczyt.
        self._chown(app_dir, deploy_user, app_group)
        self._chmod(app_dir, 0o2750)
        for directory in (uploads_dir, logs_dir):
            self._chown(directory, app_user, app_group)
            self._chmod(directory, 0o2770)
        self._chown(venv_dir, deploy_user, app_group)
        self._chmod(venv_dir, 0o2750)
        self._chown(app_root, app_user, app_group)
        self._chmod(app_root, 0o2750)

    def remove_layout(self, app_root: Path) -> None:
        """Usuń katalog aplikacji.

        :param app_root: Dokładny katalog aplikacji do usunięcia.
        :return: `None` po usunięciu.
        :raises ValueError: Gdy ścieżka jest zbyt ogólna lub niebezpieczna.
        """
        if app_root in (Path("/"), Path("/var"), Path("/var/www")):
            raise ValueError("Refusing to remove a broad system directory")
        if app_root.exists():
            shutil.rmtree(app_root)

    def create_virtualenv(self, venv_path: Path) -> None:
        """Utwórz virtualenv wraz z pip.

        :param venv_path: Docelowa ścieżka `.venv`.
        :return: `None` po pomyślnym utworzeniu środowiska.
        :raises CommandExecutionError: Gdy moduł `venv` nie utworzy środowiska.
        """
        self._runner.run(["python3", "-m", "venv", "--upgrade-deps", str(venv_path)])

    @staticmethod
    def _chown(path: Path, user: str, group: str) -> None:
        import pwd
        import grp

        uid = pwd.getpwnam(user).pw_uid
        gid = grp.getgrnam(group).gr_gid
        os.chown(path, uid, gid)

    @staticmethod
    def _chmod(path: Path, mode: int) -> None:
        os.chmod(path, mode)
    def __init__(self, runner: CommandRunner | None = None) -> None:
        self._runner = runner or CommandRunner()
