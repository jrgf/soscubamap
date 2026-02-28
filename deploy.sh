#!/usr/bin/env bash
set -euo pipefail

APP_USER="soscuba"
APP_DIR="/home/${APP_USER}/soscubamap"
SERVICE_NAME="soscuba"
DOMAIN="mapa.soscuba.org"

if [[ $EUID -ne 0 ]]; then
  echo "Ejecuta como root: sudo ./deploy.sh"
  exit 1
fi

echo "[1/10] Paquetes base"
apt update && apt upgrade -y
apt install -y python3-venv python3-pip nginx postgresql postgresql-contrib git

if ! id -u "${APP_USER}" >/dev/null 2>&1; then
  echo "[2/10] Creando usuario ${APP_USER}"
  adduser --disabled-password --gecos "" "${APP_USER}"
  usermod -aG sudo "${APP_USER}"
fi

if [[ ! -d "${APP_DIR}" ]]; then
  echo "[3/10] Clona el repo en ${APP_DIR} antes de continuar"
  echo "Ejemplo: su - ${APP_USER} && git clone git@github.com:ORG/REPO.git ${APP_DIR}"
  exit 1
fi

cd "${APP_DIR}"

if [[ ! -d .venv ]]; then
  echo "[4/10] Creando venv"
  sudo -u "${APP_USER}" python3 -m venv .venv
fi

echo "[5/10] Instalando dependencias"
sudo -u "${APP_USER}" .venv/bin/pip install -r requirements.txt

if [[ ! -f .env ]]; then
  echo "[6/10] Falta .env en ${APP_DIR}. Crea el archivo primero."
  exit 1
fi

if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='soscubamap'" | grep -q 1; then
  echo "[7/10] Creando DB y usuario"
  sudo -u postgres psql <<'SQL'
CREATE DATABASE soscubamap;
CREATE USER soscuba WITH PASSWORD 'CHANGE_ME_DB_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE soscubamap TO soscuba;
SQL
fi

if [[ ! -f "/etc/systemd/system/${SERVICE_NAME}.service" ]]; then
  echo "[8/10] Creando systemd service"
  cat <<SERVICE >/etc/systemd/system/${SERVICE_NAME}.service
[Unit]
Description=SOS Cuba Map
After=network.target

[Service]
User=${APP_USER}
Group=www-data
WorkingDirectory=${APP_DIR}
Environment="PATH=${APP_DIR}/.venv/bin"
EnvironmentFile=${APP_DIR}/.env
ExecStart=${APP_DIR}/.venv/bin/gunicorn -w 2 -b 127.0.0.1:8000 run:app
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE
  systemctl daemon-reload
  systemctl enable ${SERVICE_NAME}
fi

systemctl restart ${SERVICE_NAME}

if [[ ! -f "/etc/nginx/sites-available/${SERVICE_NAME}" ]]; then
  echo "[9/10] Configurando Nginx"
  cat <<NGINX >/etc/nginx/sites-available/${SERVICE_NAME}
server {
    listen 80;
    server_name ${DOMAIN};

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX
  ln -s /etc/nginx/sites-available/${SERVICE_NAME} /etc/nginx/sites-enabled/${SERVICE_NAME}
  nginx -t
  systemctl reload nginx
fi

echo "[10/10] HTTPS (Let’s Encrypt)"
apt install -y certbot python3-certbot-nginx
certbot --nginx -d ${DOMAIN} || true

echo "Listo. Revisa logs con: journalctl -u ${SERVICE_NAME} -f"
