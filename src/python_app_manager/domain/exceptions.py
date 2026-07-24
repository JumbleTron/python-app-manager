"""Exceptions with stable meanings for CLI and service layers."""


class ApplicationManagerError(Exception):
    """Bazowy wyjątek aplikacji."""


class ValidationError(ApplicationManagerError):
    """Dane wejściowe nie spełniają wymagań."""


class InvalidApplicationNameError(ValidationError):
    """Nazwa aplikacji zawiera niedozwolone znaki."""


class InvalidDomainError(ValidationError):
    """Domena ma niepoprawny format."""


class PortUnavailableError(ApplicationManagerError):
    """Nie znaleziono wolnego portu w skonfigurowanym zakresie."""


class ApplicationNotFoundError(ApplicationManagerError):
    """Nie znaleziono aplikacji w rejestrze."""
