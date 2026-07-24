"""Process-wide file locks for mutating CLI operations."""

from __future__ import annotations

import fcntl
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def exclusive_lock(path: Path) -> Iterator[None]:
    """Uzyskaj wyłączną blokadę plikową na czas operacji.

    :param path: Plik blokady.
    :yield: Kontrolę po uzyskaniu blokady.
    :raises OSError: Gdy plik blokady nie może zostać otwarty lub zablokowany.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
