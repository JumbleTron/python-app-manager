"""systemd unit installation and lifecycle operations."""

from __future__ import annotations

from pathlib import Path

from python_app_manager.infrastructure.command_runner import CommandRunner
from python_app_manager.utils.rendering import TemplateRenderer, write_text_atomically


class SystemdService:
    """Instaluje i aktywuje unit systemd dla aplikacji."""

    def __init__(self, runner: CommandRunner | None = None) -> None:
        self._runner = runner or CommandRunner()

    def install(
        self,
        *,
        unit_name: str,
        unit_directory: Path,
        renderer: TemplateRenderer,
        context: dict[str, object],
        enable: bool = True,
        start: bool = True,
    ) -> Path:
        """Zapisz unit, przeładuj systemd i opcjonalnie uruchom usługę.

        :param unit_name: Nazwa bez sufiksu `.service`.
        :param unit_directory: Katalog unitów systemd.
        :param renderer: Renderer szablonów.
        :param context: Dane szablonu.
        :param enable: Czy włączyć usługę przy starcie systemu.
        :param start: Czy uruchomić usługę natychmiast.
        :return: Ścieżka zapisanego unitu.
        :raises CommandExecutionError: Gdy systemd zwróci błąd.
        """
        unit_path = unit_directory / f"{unit_name}.service"
        content = renderer.render("systemd.service.j2", **context)
        write_text_atomically(unit_path, content, 0o644)
        self._runner.run(["systemctl", "daemon-reload"])
        if enable:
            self._runner.run(["systemctl", "enable", f"{unit_name}.service"])
        if start:
            self._runner.run(["systemctl", "start", f"{unit_name}.service"])
        return unit_path

    def remove(self, unit_name: str, unit_directory: Path) -> None:
        """Wyłącz, zatrzymaj i usuń unit aplikacji."""
        self._runner.run(["systemctl", "disable", "--now", f"{unit_name}.service"], check=False)
        (unit_directory / f"{unit_name}.service").unlink(missing_ok=True)
        self._runner.run(["systemctl", "daemon-reload"])
