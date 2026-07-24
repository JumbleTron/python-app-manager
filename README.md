# create-python-app

CLI do przygotowywania aplikacji Python na Ubuntu 24.04 LTS. Narzędzie tworzy izolowane
środowisko aplikacji, użytkownika i grupę systemową, virtualenv, konfigurację systemd,
reverse proxy nginx oraz — opcjonalnie — bazę i użytkownika MySQL.

## Wymagania

Na serwerze wymagane są:

- Ubuntu 24.04 LTS;
- Python 3.12 lub nowszy;
- `python3-venv`;
- nginx;
- opcjonalnie `mysql-server`;
- istniejący użytkownik `gitlab`;
- uprawnienia root do tworzenia userów, usług i konfiguracji systemowych.

Przykładowa instalacja zależności:

```bash
sudo apt update
sudo apt install python3 python3-venv nginx mysql-server
```

Użytkownik deployujący musi istnieć przed uruchomieniem narzędzia:

```bash
id gitlab
```

## Instalacja narzędzia

Instalacja w osobnym virtualenv, odpowiednia dla serwera produkcyjnego:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install .
sudo install -m 0755 .venv/bin/create-python-app /usr/local/bin/create-python-app
```

W środowisku developerskim można zainstalować również testy i narzędzia jakości kodu:

```bash
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/pytest
```

Większość komend provisioningowych wymaga uruchomienia jako root, ponieważ modyfikuje
`/etc`, `/var/www`, systemd, nginx i konta systemowe.

## Tworzenie aplikacji

Podstawowe użycie:

```bash
sudo create-python-app create \
    --name raporty \
    --domain raporty.example.pl
```

Z MySQL:

```bash
sudo create-python-app create \
    --name raporty \
    --domain raporty.example.pl \
    --with-mysql
```

Przy opcji `--with-mysql` narzędzie dwukrotnie poprosi o hasło aplikacyjnego użytkownika
MySQL. Hasło nie jest przekazywane jako argument procesu, nie trafia do logów ani do
rejestru SQLite. Administracyjne połączenie z MySQL korzysta z lokalnego socketu systemowego.

Dostępne opcje:

```text
--name TEXT             Nazwa aplikacji
--domain TEXT           Domena aplikacji
--deploy-user TEXT      Użytkownik deployujący; domyślnie gitlab
--with-mysql            Utwórz bazę i użytkownika MySQL
--start-service         Uruchom usługę po instalacji
```

Po utworzeniu aplikacji powstaje:

```text
/var/www/apps/raporty/
├── app/
├── shared/
│   ├── uploads/
│   └── logs/
├── .venv/
└── .env
```

Usługa systemd oczekuje pliku startowego:

```text
/var/www/apps/raporty/app/app.py
```

Domyślnie proces działa jako `raporty:raporty`, nasłuchuje na pierwszym wolnym porcie od
8000 i jest wystawiany przez nginx pod wskazaną domeną.

## Użytkownicy i uprawnienia

Każda aplikacja ma własnego usera i grupę:

```text
gitlab              użytkownik wykonujący deploy
raporty             użytkownik procesu aplikacji
raporty             grupa aplikacji
raporty.service     User=raporty, Group=raporty
```

`gitlab` jest dodawany do grupy aplikacji. Kod aplikacji może być aktualizowany przez
deploy, ale proces aplikacji nie działa jako `gitlab`. Plik `.env` ma ograniczone prawa i
zawiera sekret aplikacji oraz ewentualne dane MySQL.

Po dodaniu `gitlab` do nowej grupy należy rozpocząć nową sesję użytkownika, aby odświeżyć
członkostwo grupowe.

## Zarządzanie aplikacjami

Lista aplikacji:

```bash
sudo create-python-app list
```

Szczegółowy status:

```bash
sudo create-python-app status raporty
```

Status pokazuje stan systemd, poprawność konfiguracji nginx, obecność certyfikatu SSL,
wolne miejsce oraz znacznik ostatniego deployu `.deploy-meta`, jeśli istnieje.

Usuwanie aplikacji zawsze wymaga potwierdzenia:

```bash
sudo create-python-app remove raporty
```

Usunięcie razem z bazą i użytkownikiem MySQL:

```bash
sudo create-python-app remove raporty --with-database
```

Flaga `--yes` pomija interaktywne potwierdzenie i powinna być używana wyłącznie w
kontrolowanych automatyzacjach:

```bash
sudo create-python-app remove raporty --with-database --yes
```

## Deploy przez GitLab

Typowy deploy powinien aktualizować kod w katalogu `app/`, instalować zależności do
virtualenv i przeładowywać usługę:

```bash
gitlab-runner exec shell deploy
cd /var/www/apps/raporty/app
/var/www/apps/raporty/.venv/bin/pip install -r requirements.txt
sudo systemctl restart raporty.service
```

W praktycznej konfiguracji GitLab Runner powinien mieć ograniczone uprawnienia tylko do
konkretnej aplikacji. Nie należy nadawać mu pełnego `sudo` bez ograniczenia do konkretnych
poleceń systemctl.

## Rejestr i blokady

Metadane aplikacji są przechowywane w:

```text
/var/lib/create-python-app/state.db
```

Rejestr zawiera nazwę, domenę, usera, grupę, port, ścieżkę i nazwę usługi. Nie zawiera
sekretów ani haseł MySQL.

Operacje zmieniające system korzystają z blokady:

```text
/var/lock/create-python-app.lock
```

Dzięki temu dwa równoległe procesy nie wybiorą tego samego portu.

## Architektura

```text
src/python_app_manager/
├── cli.py                  CLI Typer
├── domain/                 modele i wyjątki
├── services/               przypadki użycia systemd/nginx/MySQL/filesystem
├── infrastructure/         subprocess, SQLite i blokady
├── templates/              szablony Jinja2
└── utils/                  walidacja, sekrety, logowanie i prompty
```

Szablony znajdują się w katalogu `templates/`:

- `systemd.service.j2`;
- `nginx.conf.j2`;
- `env.j2`.

## Rozwój projektu

Uruchomienie testów:

```bash
.venv/bin/pytest
```

Kontrola jakości:

```bash
.venv/bin/ruff check .
.venv/bin/mypy src
```

Planowane rozszerzenia obejmują backup/restore, Let's Encrypt, PostgreSQL, Redis, cron,
Docker Compose, PHP, Node.js oraz integrację z GitLab Deploy.

## Troubleshooting

Sprawdzenie usługi:

```bash
sudo systemctl status raporty.service
sudo journalctl -u raporty.service -n 100 --no-pager
```

Sprawdzenie nginx:

```bash
sudo nginx -t
sudo systemctl status nginx
```

Jeżeli aplikacja nie startuje, sprawdź przede wszystkim istnienie `app/app.py`, prawa
usera `raporty`, zawartość `.env`, port w konfiguracji oraz logi systemd.

## Status projektu

Projekt jest rozwijany iteracyjnie. Aktualnie dostępne są: tworzenie aplikacji, izolacja
user/grupa, virtualenv, MySQL, systemd, nginx, SQLite, rezerwacja portów, `list`, `status`
i `remove`.
