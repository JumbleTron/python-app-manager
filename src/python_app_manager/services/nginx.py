"""nginx virtual-host management."""

from __future__ import annotations

from pathlib import Path

from python_app_manager.infrastructure.command_runner import CommandRunner
from python_app_manager.utils.rendering import TemplateRenderer, write_text_atomically


class NginxService:
    """Instaluje konfigurację reverse proxy i bezpiecznie przeładowuje nginx."""

    def __init__(self, runner: CommandRunner | None = None) -> None:
        self._runner = runner or CommandRunner()

    def install(
        self,
        *,
        site_name: str,
        available_directory: Path,
        enabled_directory: Path,
        renderer: TemplateRenderer,
        context: dict[str, object],
    ) -> Path:
        """Zapisz, aktywuj i zweryfikuj konfigurację nginx.

        :param site_name: Nazwa pliku site bez sufiksu `.conf`.
        :param available_directory: Katalog `sites-available`.
        :param enabled_directory: Katalog `sites-enabled`.
        :param renderer: Renderer szablonów.
        :param context: Dane szablonu.
        :return: Ścieżka konfiguracji w `sites-available`.
        :raises CommandExecutionError: Gdy test konfiguracji nginx się nie powiedzie.
        """
        site_path = available_directory / f"{site_name}.conf"
        content = renderer.render("nginx.conf.j2", **context)
        write_text_atomically(site_path, content, 0o644)
        link_path = enabled_directory / site_path.name
        link_path.parent.mkdir(parents=True, exist_ok=True)
        link_path.unlink(missing_ok=True)
        link_path.symlink_to(site_path)
        self._runner.run(["nginx", "-t"])
        self._runner.run(["systemctl", "reload", "nginx"])
        return site_path

    def remove(self, site_name: str, available_directory: Path, enabled_directory: Path) -> None:
        """Usuń konfigurację site i przeładuj nginx."""
        (enabled_directory / f"{site_name}.conf").unlink(missing_ok=True)
        (available_directory / f"{site_name}.conf").unlink(missing_ok=True)
        self._runner.run(["nginx", "-t"], check=False)
        self._runner.run(["systemctl", "reload", "nginx"], check=False)
