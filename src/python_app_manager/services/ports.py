"""Port allocation with injectable availability checks."""

from __future__ import annotations

import socket
from collections.abc import Callable, Iterable

from python_app_manager.domain.exceptions import PortUnavailableError
from python_app_manager.utils.validators import validate_port_range

PortChecker = Callable[[int], bool]


def is_port_available(port: int, host: str = "127.0.0.1") -> bool:
    """Sprawdź, czy można wykonać lokalny bind na porcie TCP.

    :param port: Numer portu.
    :param host: Adres interfejsu do sprawdzenia.
    :return: `True`, jeżeli bind jest możliwy.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
        except OSError:
            return False
        return True


def find_free_port(
    start: int,
    end: int,
    reserved_ports: Iterable[int] = (),
    checker: PortChecker = is_port_available,
) -> int:
    """Znajdź pierwszy dostępny port, pomijając zarezerwowane numery.

    :param start: Początek zakresu włącznie.
    :param end: Koniec zakresu włącznie.
    :param reserved_ports: Porty zajęte w rejestrze lub bieżącej transakcji.
    :param checker: Funkcja sprawdzająca dostępność portu.
    :return: Pierwszy wolny port.
    :raises ValueError: Gdy zakres jest niepoprawny.
    :raises PortUnavailableError: Gdy cały zakres jest zajęty.
    """
    validate_port_range(start, end)
    reserved = set(reserved_ports)
    for port in range(start, end + 1):
        if port not in reserved and checker(port):
            return port
    raise PortUnavailableError(f"No free port found in range {start}-{end}")
