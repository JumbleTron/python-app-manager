# Security Policy

## Zgłaszanie problemów

Nie publikuj podatności ani sekretów w publicznym issue. Zgłoś problem prywatnie przez
GitHub Security Advisories albo kontakt bezpieczeństwa skonfigurowany dla repozytorium.

W zgłoszeniu podaj wersję, system operacyjny, kroki odtworzenia i potencjalny wpływ.
Nie dołączaj haseł, kluczy SSH, plików `.env` ani danych produkcyjnych.

## Zakres bezpieczeństwa

Projekt wykonuje operacje uprzywilejowane i powinien być uruchamiany wyłącznie z zaufanego
źródła. Przed użyciem produkcyjnym należy przejrzeć konfigurację `sudo`, systemd, nginx,
uprawnienia użytkownika `gitlab` i zawartość szablonów.
