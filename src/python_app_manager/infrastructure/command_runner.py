"""Safe subprocess adapter used by system integration services."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from collections.abc import Sequence


@dataclass(frozen=True, slots=True)
class CommandResult:
    """Wynik procesu zewnętrznego."""

    returncode: int
    stdout: str
    stderr: str


class CommandExecutionError(RuntimeError):
    """Proces zewnętrzny zakończył się błędem."""


class CommandRunner:
    """Wykonuje polecenia bez używania powłoki systemowej."""

    def run(
        self,
        command: Sequence[str],
        *,
        input_text: str | None = None,
        check: bool = True,
    ) -> CommandResult:
        """Uruchom polecenie z kontrolowanym stdin/stdout/stderr.

        :param command: Argumenty procesu, pierwszy element to executable.
        :param input_text: Opcjonalna zawartość przekazywana przez stdin.
        :param check: Czy rzucić wyjątek przy niezerowym kodzie wyjścia.
        :return: Ustandaryzowany wynik procesu.
        :raises CommandExecutionError: Gdy `check=True` i proces zakończy się błędem.
        """
        completed = subprocess.run(
            list(command),
            input=input_text,
            text=True,
            capture_output=True,
            check=False,
        )
        result = CommandResult(completed.returncode, completed.stdout, completed.stderr)
        if check and result.returncode != 0:
            executable = command[0] if command else "<empty command>"
            raise CommandExecutionError(
                f"Command {executable!r} failed with exit code {result.returncode}: "
                f"{result.stderr.strip()}"
            )
        return result
