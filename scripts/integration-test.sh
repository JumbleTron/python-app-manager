#!/usr/bin/env bash
set -euo pipefail

until systemctl is-system-running >/dev/null 2>&1; do
    sleep 1
done

systemctl start mysql nginx
install -o root -g root -m 0755 /dist/create-python-app /usr/local/bin/create-python-app

export CREATE_PYTHON_APP_MYSQL_PASSWORD='integration_test_password_123'
create-python-app create \
    --name raporty \
    --domain raporty.example.test \
    --with-mysql \
    --no-start-service

cp /workspace/tests/fixtures/integration_app.py /var/www/apps/raporty/app/app.py
chown gitlab:raporty /var/www/apps/raporty/app/app.py
chmod 0750 /var/www/apps/raporty/app/app.py

systemctl start raporty.service
test "$(systemctl is-active raporty.service)" = "active"
nginx -t

response=""
for attempt in $(seq 1 10); do
    response="$(curl --silent --header 'Host: raporty.example.test' http://127.0.0.1/)"
    if [ "$response" = "python-app-manager integration test" ]; then
        break
    fi
    sleep 1
done
if [ "$response" != "python-app-manager integration test" ]; then
    systemctl status raporty.service --no-pager || true
    journalctl -u raporty.service -n 50 --no-pager || true
    ss -lntp || true
    printf 'unexpected HTTP response: %s\n' "$response" >&2
    exit 1
fi

mysql --batch --skip-column-names \
    -e "SELECT User FROM mysql.user WHERE User = 'app_raporty'" \
    | grep -qx 'app_raporty'

echo "integration provisioning: OK"
