"""Command-line entry point."""

from __future__ import annotations

from pathlib import Path

import typer

from python_app_manager import __version__
from python_app_manager.domain.models import ApplicationSpec
from python_app_manager.infrastructure.command_runner import CommandRunner
from python_app_manager.infrastructure.database import StateRepository
from python_app_manager.infrastructure.locks import exclusive_lock
from python_app_manager.services.application import ApplicationService
from python_app_manager.services.removal import RemovalService
from python_app_manager.services.status import StatusService
from python_app_manager.utils.paths import templates_directory
from python_app_manager.utils.prompts import prompt_mysql_password
from python_app_manager.utils.rendering import TemplateRenderer

app = typer.Typer(
    name="create-python-app",
    help="Zarządzanie aplikacjami Python na Ubuntu.",
    no_args_is_help=True,
)


@app.callback()
def main_callback(
    version: bool = typer.Option(False, "--version", help="Pokaż wersję narzędzia."),
) -> None:
    """Punkt wejścia do narzędzia create-python-app."""
    if version:
        typer.echo(__version__)


@app.command("create")
def create_application(
    name: str = typer.Option(..., help="Nazwa aplikacji."),
    domain: str = typer.Option(..., help="Domena aplikacji."),
    deploy_user: str = typer.Option("gitlab", help="Użytkownik wykonujący deploy."),
    with_mysql: bool = typer.Option(False, help="Utwórz bazę i użytkownika MySQL."),
    start_service: bool = typer.Option(True, help="Uruchom usługę po instalacji."),
) -> None:
    """Utwórz aplikację Python wraz z konfiguracją systemową."""
    mysql_password = prompt_mysql_password() if with_mysql else None
    renderer = TemplateRenderer(templates_directory())
    repository = StateRepository(Path("/var/lib/create-python-app/state.db"))
    with exclusive_lock(Path("/var/lock/create-python-app.lock")):
        result = ApplicationService(repository=repository).create(
            ApplicationSpec(name=name, domain=domain, deploy_user=deploy_user, with_mysql=with_mysql),
            apps_root=Path("/var/www/apps"),
            systemd_directory=Path("/etc/systemd/system"),
            nginx_available=Path("/etc/nginx/sites-available"),
            nginx_enabled=Path("/etc/nginx/sites-enabled"),
            renderer=renderer,
            mysql_password=mysql_password,
            start_service=start_service,
        )
    typer.echo(f"Created {result.name}: {result.path} port={result.port} domain={result.domain}")


@app.command("list")
def list_applications() -> None:
    """Pokaż aplikacje zapisane w rejestrze."""
    repository = StateRepository(Path("/var/lib/create-python-app/state.db"))
    rows = repository.list_all()
    if not rows:
        typer.echo("No applications registered.")
        return
    typer.echo("NAME\tPORT\tDOMAIN\tAPP USER\tSTATUS")
    for row in rows:
        status = StatusService(CommandRunner()).service_status(row["service_name"])
        typer.echo(f"{row['name']}\t{row['port']}\t{row['domain']}\t{row['app_user']}\t{status}")


@app.command("status")
def application_status(
    name: str = typer.Argument(..., help="Nazwa aplikacji."),
) -> None:
    """Pokaż szczegółowy status aplikacji."""
    repository = StateRepository(Path("/var/lib/create-python-app/state.db"))
    row = repository.get(name)
    health = StatusService().collect(row["service_name"], Path(row["path"]), row["domain"])
    typer.echo(f"Application: {row['name']}")
    typer.echo(f"systemd: {health.systemd}")
    typer.echo(f"nginx: {health.nginx}")
    typer.echo(f"ssl: {health.ssl}")
    typer.echo(f"free space: {health.free_space_gb} GB")
    typer.echo(f"last deploy: {health.last_deploy}")


@app.command("remove")
def remove_application(
    name: str = typer.Argument(..., help="Nazwa aplikacji."),
    remove_database: bool = typer.Option(False, "--with-database", help="Usuń bazę MySQL."),
    yes: bool = typer.Option(False, "--yes", help="Potwierdź usunięcie bez promptu."),
) -> None:
    """Usuń aplikację po jawnym potwierdzeniu operatora."""
    if not yes and not typer.confirm(f"Remove application '{name}' and its files?", default=False):
        typer.echo("Cancelled.")
        raise typer.Abort()
    repository = StateRepository(Path("/var/lib/create-python-app/state.db"))
    with exclusive_lock(Path("/var/lock/create-python-app.lock")):
        RemovalService(repository).remove(
            name,
            systemd_directory=Path("/etc/systemd/system"),
            nginx_available=Path("/etc/nginx/sites-available"),
            nginx_enabled=Path("/etc/nginx/sites-enabled"),
            remove_database=remove_database,
        )
    typer.echo(f"Removed {name}.")


def main() -> None:
    """Uruchom aplikację CLI."""
    app()


if __name__ == "__main__":
    main()
