from python_app_manager.infrastructure.command_runner import CommandResult
from python_app_manager.services.mysql import MysqlService


class FakeRunner:
    def __init__(self) -> None:
        self.command: list[str] | None = None
        self.input_text: str | None = None

    def run(self, command: list[str], *, input_text: str | None = None) -> CommandResult:
        self.command = command
        self.input_text = input_text
        return CommandResult(0, "", "")


def test_mysql_password_is_sent_via_stdin_and_not_command_arguments() -> None:
    runner = FakeRunner()
    service = MysqlService(runner)  # type: ignore[arg-type]

    resources = service.provision("raporty", "secret'\\password")

    assert resources.database == "app_raporty"
    assert runner.command == ["mysql", "--protocol=socket", "--batch", "--skip-column-names"]
    assert "secret\\'\\\\password" in (runner.input_text or "")
