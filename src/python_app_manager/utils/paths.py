"""Runtime paths for source and PyInstaller builds."""

from __future__ import annotations

import sys
from pathlib import Path


def templates_directory() -> Path:
    """Zwróć katalog szablonów dla checkoutu oraz binarki PyInstaller.

    :return: Istniejąca ścieżka katalogu z szablonami.
    :raises FileNotFoundError: Gdy szablony nie zostały dołączone do artefaktu.
    """
    if getattr(sys, "frozen", False):
        bundle_root = Path(sys._MEIPASS)  # type: ignore[attr-defined]
        directory = bundle_root / "templates"
    else:
        directory = Path(__file__).resolve().parents[3] / "templates"
    if not directory.is_dir():
        raise FileNotFoundError(f"Templates directory does not exist: {directory}")
    return directory
