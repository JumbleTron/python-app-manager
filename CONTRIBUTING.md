# Contributing

Dziękujemy za zainteresowanie projektem `python-app-manager`.

## Zasady

- każda zmiana powinna rozwiązywać jeden jasno opisany problem;
- nie dodawaj sekretów, haseł ani danych produkcyjnych do repozytorium;
- integracje z systemem muszą być testowalne przez wstrzykiwane adaptery;
- publiczne funkcje muszą mieć typy, docstring oraz testy tam, gdzie jest to praktyczne;
- zmiany destrukcyjne wymagają jawnej obsługi potwierdzenia.

## Lokalny setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/pytest
.venv/bin/ruff check .
```

## Pull request

Pull request powinien zawierać opis problemu, zakres zmiany, testy oraz informację o
wpływie na bezpieczeństwo i kompatybilność z Ubuntu 24.04.
