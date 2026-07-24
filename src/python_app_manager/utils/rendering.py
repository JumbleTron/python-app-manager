"""Jinja2 template rendering and atomic file writes."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined


class TemplateRenderer:
    """Renderuje szablony Jinja2 z katalogu projektu."""

    def __init__(self, templates_dir: Path) -> None:
        self._environment = Environment(
            loader=FileSystemLoader(templates_dir),
            undefined=StrictUndefined,
            autoescape=False,
            keep_trailing_newline=True,
        )

    def render(self, template_name: str, **context: Any) -> str:
        """Wyrenderuj nazwany szablon.

        :param template_name: Nazwa pliku w katalogu szablonów.
        :param context: Dane dostępne w szablonie.
        :return: Wygenerowany tekst.
        :raises jinja2.UndefinedError: Gdy szablon odwołuje się do brakującej wartości.
        """
        return self._environment.get_template(template_name).render(**context)


def write_text_atomically(path: Path, content: str, mode: int) -> None:
    """Zapisz plik przez plik tymczasowy i atomową zmianę nazwy.

    :param path: Docelowa ścieżka.
    :param content: Treść pliku.
    :param mode: Tryb POSIX pliku.
    :return: `None` po pomyślnym zapisie.
    :raises OSError: Gdy zapis lub zmiana uprawnień się nie powiedzie.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary_name)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, "w", encoding="utf-8") as temporary_file:
            temporary_file.write(content)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        os.replace(temporary_path, path)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise
