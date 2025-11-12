#!/bin/bash
# Automatisches Setup-Script für Hetzner Server

set -e

echo "🚀 Hetzner Server Setup für Berlin City Raver Marketing Tool"
echo "============================================================"

# Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Prüfe ob Root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Bitte als root ausführen: sudo $0${NC}"
    exit 1
fi

# Variablen
DB_USER="telegram_bot_user"
DB_NAME="telegram_bot_db"
PROJECT_DIR="/var/www/telegram-bot"
SERVICE_NAME="telegram-bot"

echo -e "${YELLOW}📋 Schritt 1: System aktualisieren...${NC}"
apt update && apt upgrade -y

echo -e "${YELLOW}📦 Schritt 2: Basis-Pakete installieren...${NC}"
apt install -y \
    python3.10 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    nginx \
    postgresql \
    postgresql-contrib \
    certbot \
    python3-certbot-nginx \
    git \
    ufw \
    fail2ban \
    htop \
    curl \
    wget

echo -e "${YELLOW}🗄️  Schritt 3: PostgreSQL einrichten...${NC}"
# Generiere sicheres Passwort
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

# Erstelle PostgreSQL User und Datenbank
sudo -u postgres psql << EOF
CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';
CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
\q
EOF

echo -e "${GREEN}✅ PostgreSQL User: ${DB_USER}${NC}"
echo -e "${GREEN}✅ Datenbank: ${DB_NAME}${NC}"
echo -e "${YELLOW}⚠️  Passwort gespeichert in: ${PROJECT_DIR}/.db_password${NC}"
echo "${DB_PASSWORD}" > ${PROJECT_DIR}/.db_password 2>/dev/null || echo "${DB_PASSWORD}" > /root/.db_password
chmod 600 ${PROJECT_DIR}/.db_password 2>/dev/null || chmod 600 /root/.db_password

systemctl restart postgresql
systemctl enable postgresql

echo -e "${YELLOW}📁 Schritt 4: Projekt-Verzeichnis erstellen...${NC}"
mkdir -p ${PROJECT_DIR}
cd ${PROJECT_DIR}

echo -e "${YELLOW}🐍 Schritt 5: Python Virtual Environment...${NC}"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

echo -e "${YELLOW}📦 Schritt 6: Python Dependencies installieren...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo -e "${RED}⚠️  requirements.txt nicht gefunden. Bitte manuell installieren.${NC}"
fi

echo -e "${YELLOW}🌐 Schritt 7: Frontend Dependencies...${NC}"
if [ -d "frontend" ]; then
    cd frontend
    npm install
    npm run build
    cd ..
else
    echo -e "${RED}⚠️  frontend/ Verzeichnis nicht gefunden.${NC}"
fi

echo -e "${YELLOW}⚙️  Schritt 8: Environment-Variablen...${NC}"
if [ ! -f "${PROJECT_DIR}/.env" ]; then
    cat > ${PROJECT_DIR}/.env << EOF
# Telegram API
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash

# JWT Secret
JWT_SECRET_KEY=$(openssl rand -hex 32)

# PostgreSQL
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@localhost/${DB_NAME}

# 5sim.net
FIVESIM_API_KEY=your_5sim_api_key

# Domain (für CORS)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
EOF
    echo -e "${GREEN}✅ .env Datei erstellt${NC}"
    echo -e "${YELLOW}⚠️  Bitte .env Datei bearbeiten: nano ${PROJECT_DIR}/.env${NC}"
else
    echo -e "${YELLOW}⚠️  .env Datei existiert bereits${NC}"
fi

echo -e "${YELLOW}🗄️  Schritt 9: Datenbank initialisieren...${NC}"
if [ -f "database.py" ]; then
    source venv/bin/activate
    export DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@localhost/${DB_NAME}"
    python3 -c "from database import init_db; init_db(); print('✅ Datenbank initialisiert')" || echo -e "${RED}⚠️  Datenbank-Initialisierung fehlgeschlagen${NC}"
else
    echo -e "${RED}⚠️  database.py nicht gefunden${NC}"
fi

echo -e "${YELLOW}🔧 Schritt 10: Systemd Service erstellen...${NC}"
cat > /etc/systemd/system/${SERVICE_NAME}.service << EOF
[Unit]
Description=Berlin City Raver - Marketing Tool API
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=${PROJECT_DIR}
Environment="PATH=${PROJECT_DIR}/venv/bin"
EnvironmentFile=${PROJECT_DIR}/.env
ExecStart=${PROJECT_DIR}/venv/bin/uvicorn api:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ${SERVICE_NAME}

echo -e "${YELLOW}🌐 Schritt 11: Nginx konfigurieren...${NC}"
read -p "Domain eingeben (z.B. example.com): " DOMAIN

cat > /etc/nginx/sites-available/${SERVICE_NAME} << EOF
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};

    # Frontend
    location / {
        root ${PROJECT_DIR}/frontend/dist;
        try_files \$uri \$uri/ /index.html;
        index index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # WebSocket Support
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Statische Dateien
    location /static {
        alias ${PROJECT_DIR}/frontend/dist/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

ln -sf /etc/nginx/sites-available/${SERVICE_NAME} /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

echo -e "${YELLOW}🔒 Schritt 12: Firewall konfigurieren...${NC}"
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp

echo -e "${YELLOW}🛡️  Schritt 13: Fail2Ban konfigurieren...${NC}"
cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = 22
logpath = /var/log/auth.log
EOF

systemctl restart fail2ban
systemctl enable fail2ban

echo ""
echo -e "${GREEN}✅ Setup abgeschlossen!${NC}"
echo ""
echo -e "${YELLOW}📋 Nächste Schritte:${NC}"
echo "1. .env Datei bearbeiten: nano ${PROJECT_DIR}/.env"
echo "2. Domain DNS auf Server-IP zeigen lassen"
echo "3. SSL-Zertifikat installieren: certbot --nginx -d ${DOMAIN}"
echo "4. Service starten: systemctl start ${SERVICE_NAME}"
echo ""
echo -e "${YELLOW}📊 Wichtige Informationen:${NC}"
echo "PostgreSQL User: ${DB_USER}"
echo "Datenbank: ${DB_NAME}"
echo "Passwort gespeichert in: ${PROJECT_DIR}/.db_password"
echo "Service: systemctl status ${SERVICE_NAME}"
echo "Logs: journalctl -u ${SERVICE_NAME} -f"
echo ""

