from pathlib import Path

from python_app_manager.infrastructure.database import StateRepository


def test_repository_reserves_ports_and_does_not_store_secrets(tmp_path: Path) -> None:
    repository = StateRepository(tmp_path / "state.db")

    first = repository.claim_port(8000, 8001, checker=lambda _: True)
    second = repository.claim_port(8000, 8001, checker=lambda _: True)

    assert (first, second) == (8000, 8001)
    assert "password" not in (tmp_path / "state.db").read_bytes().decode("latin1", errors="ignore")
