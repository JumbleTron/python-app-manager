"""Health and status checks for managed applications."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from python_app_manager.infrastructure.command_runner import CommandRunner


@dataclass(frozen=True, slots=True)
class ApplicationHealth:
    """Wynik kontroli stanu aplikacji."""

    systemd: str
    nginx: str
    ssl: str
    free_space_gb: float
    last_deploy: str


class StatusService:
    """Zbiera informacje diagnostyczne bez zmiany stanu systemu."""

    def __init__(self, runner: CommandRunner | None = None) -> None:
        self._runner = runner or CommandRunner()

    def collect(self, service_name: str, app_path: Path, domain: str) -> ApplicationHealth:
        """Pobierz status systemd, nginx, SSL, dysku i ostatniego deployu.

        :param service_name: Nazwa unitu systemd.
        :param app_path: Katalog aplikacji.
        :param domain: Domena aplikacji.
        :return: Zestaw informacji diagnostycznych.
        """
        systemd_result = self._runner.run(["systemctl", "is-active", f"{service_name}.service"], check=False)
        nginx_result = self._runner.run(["nginx", "-t"], check=False)
        disk = shutil.disk_usage(app_path if app_path.exists() else Path("/"))
        deploy_marker = app_path / ".deploy-meta"
        last_deploy = str(deploy_marker.stat().st_mtime) if deploy_marker.exists() else "unknown"
        ssl_status = self._ssl_status(domain)
        return ApplicationHealth(
            systemd=systemd_result.stdout.strip() or "inactive",
            nginx="valid" if nginx_result.returncode == 0 else "invalid",
            ssl=ssl_status,
            free_space_gb=round(disk.free / 1024**3, 2),
            last_deploy=last_deploy,
        )

    def service_status(self, service_name: str) -> str:
        """Zwróć krótki status unitu systemd."""
        result = self._runner.run(["systemctl", "is-active", f"{service_name}.service"], check=False)
        return result.stdout.strip() or "inactive"

    def _ssl_status(self, domain: str) -> str:
        """Sprawdź, czy certyfikat certbot istnieje dla domeny."""
        certificate = Path("/etc/letsencrypt/live") / domain / "fullchain.pem"
        return "present" if certificate.exists() else "not-configured"
