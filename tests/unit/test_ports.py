import pytest

from python_app_manager.domain.exceptions import PortUnavailableError
from python_app_manager.services.ports import find_free_port


def test_find_free_port_skips_reserved_and_busy_ports() -> None:
    busy = {8000, 8002}

    port = find_free_port(
        8000,
        8003,
        reserved_ports={8001},
        checker=lambda candidate: candidate not in busy,
    )

    assert port == 8003


def test_find_free_port_raises_when_range_is_exhausted() -> None:
    with pytest.raises(PortUnavailableError):
        find_free_port(8000, 8001, checker=lambda _: False)
