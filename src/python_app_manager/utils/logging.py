"""Consistent, coloured logging for interactive CLI usage."""

from __future__ import annotations

import logging
import sys

_RESET = "\033[0m"
_COLORS = {
    logging.INFO: "\033[36m",  # cyan
    logging.WARNING: "\033[33m",  # yellow
    logging.ERROR: "\033[31m",  # red
    logging.CRITICAL: "\033[31;1m",
    25: "\033[32m",  # SUCCESS
}

SUCCESS_LEVEL = 25
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")


class ColorFormatter(logging.Formatter):
    """Formatter dodający kolor do poziomu logowania na terminalu."""

    def format(self, record: logging.LogRecord) -> str:
        """Sformatuj rekord, kolorując poziom logowania.

        :param record: Rekord biblioteki `logging`.
        :return: Tekst gotowy do wyświetlenia.
        """
        level = record.levelno
        label = record.levelname
        color = _COLORS.get(level, "")
        message = super().format(record)
        if not sys.stderr.isatty():
            return message
        return f"{color}{label:<7}{_RESET} {message}"


def get_logger(name: str = "create-python-app") -> logging.Logger:
    """Zwróć skonfigurowany logger CLI.

    :param name: Nazwa loggera.
    :return: Logger zapisujący na stderr.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(ColorFormatter("%(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


def log_success(logger: logging.Logger, message: str, *args: object) -> None:
    """Zapisz komunikat na poziomie `SUCCESS`.

    :param logger: Docelowy logger.
    :param message: Komunikat z opcjonalnymi placeholderami logging.
    :param args: Argumenty formatowania komunikatu.
    """
    logger.log(SUCCESS_LEVEL, message, *args)
