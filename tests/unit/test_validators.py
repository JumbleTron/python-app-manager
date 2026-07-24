import pytest

from python_app_manager.domain.exceptions import InvalidApplicationNameError, InvalidDomainError
from python_app_manager.utils.validators import (
    validate_app_name,
    validate_domain,
    validate_port_range,
)


@pytest.mark.parametrize("name", ["raporty", "app-01", "a1"])
def test_valid_app_names(name: str) -> None:
    assert validate_app_name(name) == name


@pytest.mark.parametrize("name", ["Raporty", "-app", "app_name", "a"])
def test_invalid_app_names(name: str) -> None:
    with pytest.raises(InvalidApplicationNameError):
        validate_app_name(name)


def test_valid_domain_is_normalized() -> None:
    assert validate_domain("Raporty.Example.PL.") == "raporty.example.pl"


@pytest.mark.parametrize("domain", ["localhost", "https://example.pl", "a..example.pl"])
def test_invalid_domains(domain: str) -> None:
    with pytest.raises(InvalidDomainError):
        validate_domain(domain)


def test_valid_port_range() -> None:
    assert validate_port_range(8000, 8002) == (8000, 8002)
