"""Application provisioning orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from python_app_manager.domain.models import ApplicationRecord, ApplicationSpec
from python_app_manager.infrastructure.database import StateRepository
from python_app_manager.infrastructure.command_runner import CommandRunner
from python_app_manager.services.filesystem import FilesystemService
from python_app_manager.services.mysql import MysqlApplicationResources, MysqlService
from python_app_manager.services.nginx import NginxService
from python_app_manager.services.ports import find_free_port, is_port_available
from python_app_manager.services.systemd import SystemdService
from python_app_manager.services.users import ApplicationIdentity, UserService
from python_app_manager.utils.rendering import TemplateRenderer, write_text_atomically
from python_app_manager.utils.secrets import generate_secret_key
from python_app_manager.utils.validators import validate_app_name, validate_domain


@dataclass(frozen=True, slots=True)
class ProvisionResult:
    """Podsumowanie utworzonej aplikacji."""

    name: str
    path: Path
    port: int
    domain: str
    service_name: str
    mysql: MysqlApplicationResources | None


class ApplicationService:
    """Koordynuje utworzenie kompletnego środowiska aplikacji."""

    def __init__(
        self,
        *,
        filesystem: FilesystemService | None = None,
        users: UserService | None = None,
        mysql: MysqlService | None = None,
        systemd: SystemdService | None = None,
        nginx: NginxService | None = None,
        runner: CommandRunner | None = None,
        repository: StateRepository | None = None,
    ) -> None:
        command_runner = runner or CommandRunner()
        self._filesystem = filesystem or FilesystemService(command_runner)
        self._users = users or UserService(command_runner)
        self._mysql = mysql or MysqlService(command_runner)
        self._systemd = systemd or SystemdService(command_runner)
        self._nginx = nginx or NginxService(command_runner)
        self._repository = repository

    def create(
        self,
        spec: ApplicationSpec,
        *,
        apps_root: Path,
        systemd_directory: Path,
        nginx_available: Path,
        nginx_enabled: Path,
        renderer: TemplateRenderer,
        port_start: int = 8000,
        port_end: int = 8999,
        reserved_ports: set[int] | None = None,
        mysql_password: str | None = None,
        start_service: bool = True,
        entrypoint: str = "app.py",
    ) -> ProvisionResult:
        """Utwórz aplikację i jej konfigurację systemową.

        :param spec: Dane aplikacji.
        :param apps_root: Główny katalog wszystkich aplikacji.
        :param systemd_directory: Katalog unitów systemd.
        :param nginx_available: Katalog aktywnych konfiguracji nginx.
        :param nginx_enabled: Katalog linków nginx.
        :param renderer: Renderer szablonów.
        :param port_start: Początek zakresu portów.
        :param port_end: Koniec zakresu portów.
        :param reserved_ports: Porty zajęte w rejestrze aplikacji.
        :param mysql_password: Hasło aplikacyjnego usera MySQL.
        :param start_service: Czy uruchomić unit po instalacji.
        :param entrypoint: Plik startowy aplikacji.
        :return: Podsumowanie utworzonej aplikacji.
        :raises ValueError: Przy niepoprawnych danych lub brakującym haśle MySQL.
        :raises OSError: Przy błędzie filesystemu.
        """
        name = validate_app_name(spec.name)
        domain = validate_domain(spec.domain)
        app_user = spec.resolved_app_user()
        app_group = spec.resolved_app_group()
        app_root = apps_root / name
        service_name = name
        if self._repository is not None:
            port = self._repository.claim_port(
                port_start,
                port_end,
                checker=is_port_available,
            )
        else:
            port = find_free_port(port_start, port_end, reserved_ports or set())
        identity = ApplicationIdentity(app_user, app_group, spec.deploy_user)
        try:
            self._users.ensure_identity(identity)
            self._filesystem.create_layout(
                app_root,
                app_user=app_user,
                app_group=app_group,
                deploy_user=spec.deploy_user,
            )
            self._filesystem.create_virtualenv(app_root / ".venv")

            mysql_resources: MysqlApplicationResources | None = None
            if spec.with_mysql:
                if mysql_password is None:
                    raise ValueError("mysql_password is required when with_mysql=True")
                mysql_resources = self._mysql.provision(name, mysql_password)

            context: dict[str, object] = {
            "app_name": name,
            "app_root": str(app_root),
            "venv_path": str(app_root / ".venv"),
            "app_user": app_user,
            "app_group": app_group,
            "deploy_user": spec.deploy_user,
            "domain": domain,
            "port": port,
            "entrypoint": entrypoint,
            "secret_key": generate_secret_key(),
            "mysql_database": mysql_resources.database if mysql_resources else None,
            "mysql_user": mysql_resources.username if mysql_resources else None,
            "mysql_password": mysql_password if mysql_resources else None,
            }
            env_content = renderer.render("env.j2", **context)
            env_path = app_root / ".env"
            write_text_atomically(env_path, env_content, 0o640)
            self._systemd.install(
                unit_name=service_name,
                unit_directory=systemd_directory,
                renderer=renderer,
                context=context,
                start=start_service,
            )
            self._nginx.install(
                site_name=name,
                available_directory=nginx_available,
                enabled_directory=nginx_enabled,
                renderer=renderer,
                context=context,
            )
            if self._repository is not None:
                self._repository.register(
                    ApplicationRecord(
                        name=name,
                        domain=domain,
                        deploy_user=spec.deploy_user,
                        app_user=app_user,
                        app_group=app_group,
                        port=port,
                        path=app_root,
                        service_name=service_name,
                        mysql_database=mysql_resources.database if mysql_resources else None,
                    )
                )
            return ProvisionResult(name, app_root, port, domain, service_name, mysql_resources)
        except Exception:
            if self._repository is not None:
                self._repository.release_port(port)
            raise
