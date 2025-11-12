# Hetzner Server Setup - Berlin City Raver Marketing Tool

## 🚀 Schnellstart für Hetzner Server

### Voraussetzungen
- Hetzner Cloud Server oder Dedicated Server
- Ubuntu 22.04 LTS oder Debian 12 (empfohlen)
- Root-Zugriff via SSH

---

## 📋 Schritt 1: Server vorbereiten

### SSH-Verbindung
```bash
ssh root@deine-server-ip
```

### System aktualisieren
```bash
apt update && apt upgrade -y
```

### Basis-Pakete installieren
```bash
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
    htop
```

---

## 📋 Schritt 2: PostgreSQL einrichten

### Datenbank erstellen
```bash
# PostgreSQL User erstellen
sudo -u postgres psql << EOF
CREATE USER telegram_bot_user WITH PASSWORD 'SICHERES_PASSWORT_HIER';
CREATE DATABASE telegram_bot_db OWNER telegram_bot_user;
GRANT ALL PRIVILEGES ON DATABASE telegram_bot_db TO telegram_bot_user;
\q
EOF
```

### PostgreSQL konfigurieren (optional - für Remote-Zugriff)
```bash
# /etc/postgresql/15/main/postgresql.conf
# listen_addresses = 'localhost'  # Nur lokal (sicherer)

# /etc/postgresql/15/main/pg_hba.conf
# local all all peer
# host all all 127.0.0.1/32 md5
```

### PostgreSQL neu starten
```bash
systemctl restart postgresql
systemctl enable postgresql
```

---

## 📋 Schritt 3: Projekt deployen

### Projekt-Verzeichnis erstellen
```bash
mkdir -p /var/www
cd /var/www
```

### Projekt hochladen/kopieren
```bash
# Option 1: Git Clone (wenn Repository vorhanden)
git clone https://github.com/dein-repo/telegram-bot.git
cd telegram-bot

# Option 2: SCP vom lokalen Rechner
# Auf lokalem Rechner:
# scp -r telegram-bot root@deine-server-ip:/var/www/
```

### Python Virtual Environment
```bash
cd /var/www/telegram-bot
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Frontend bauen
```bash
cd frontend
npm install
npm run build
cd ..
```

---

## 📋 Schritt 4: Environment-Variablen

### .env Datei erstellen
```bash
cd /var/www/telegram-bot
nano .env
```

### Inhalt der .env Datei:
```env
# Telegram API
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash

# JWT Secret (WICHTIG: Starke, zufällige Zeichenkette!)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# PostgreSQL
DATABASE_URL=postgresql://telegram_bot_user:SICHERES_PASSWORT_HIER@localhost/telegram_bot_db

# 5sim.net
FIVESIM_API_KEY=your_5sim_api_key

# Domain (für CORS)
ALLOWED_ORIGINS=https://deine-domain.de,https://www.deine-domain.de
```

### JWT Secret generieren
```bash
# Generiere sicheres JWT Secret
openssl rand -hex 32
# Kopiere das Ergebnis in .env als JWT_SECRET_KEY
```

---

## 📋 Schritt 5: Datenbank initialisieren

```bash
cd /var/www/telegram-bot
source venv/bin/activate
python3 -c "from database import init_db; init_db(); print('✅ Datenbank initialisiert')"
```

---

## 📋 Schritt 6: Systemd Service erstellen

### Service-Datei erstellen
```bash
nano /etc/systemd/system/telegram-bot.service
```

### Inhalt:
```ini
[Unit]
Description=Berlin City Raver - Marketing Tool API
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/telegram-bot
Environment="PATH=/var/www/telegram-bot/venv/bin"
EnvironmentFile=/var/www/telegram-bot/.env
ExecStart=/var/www/telegram-bot/venv/bin/uvicorn api:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Service aktivieren
```bash
systemctl daemon-reload
systemctl enable telegram-bot
systemctl start telegram-bot
systemctl status telegram-bot
```

---

## 📋 Schritt 7: Nginx konfigurieren

### Nginx Config erstellen
```bash
nano /etc/nginx/sites-available/telegram-bot
```

### Inhalt:
```nginx
server {
    listen 80;
    server_name deine-domain.de www.deine-domain.de;

    # Frontend
    location / {
        root /var/www/telegram-bot/frontend/dist;
        try_files $uri $uri/ /index.html;
        index index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts für lange Requests
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # WebSocket Support (falls benötigt)
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Statische Dateien
    location /static {
        alias /var/www/telegram-bot/frontend/dist/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### Config aktivieren
```bash
ln -s /etc/nginx/sites-available/telegram-bot /etc/nginx/sites-enabled/
nginx -t  # Testen
systemctl restart nginx
```

---

## 📋 Schritt 8: SSL-Zertifikat (Let's Encrypt)

```bash
certbot --nginx -d deine-domain.de -d www.deine-domain.de
```

### Auto-Renewal prüfen
```bash
certbot renew --dry-run
```

---

## 📋 Schritt 9: Firewall konfigurieren

```bash
# UFW aktivieren
ufw default deny incoming
ufw default allow outgoing

# SSH erlauben (WICHTIG: Vorher prüfen!)
ufw allow 22/tcp

# HTTP/HTTPS erlauben
ufw allow 80/tcp
ufw allow 443/tcp

# Firewall aktivieren
ufw enable
ufw status
```

---

## 📋 Schritt 10: Fail2Ban konfigurieren

### SSH-Schutz
```bash
nano /etc/fail2ban/jail.local
```

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = 22
logpath = /var/log/auth.log
```

```bash
systemctl restart fail2ban
systemctl enable fail2ban
```

---

## 📋 Schritt 11: Backup einrichten

### Backup-Script erstellen
```bash
nano /usr/local/bin/backup-telegram-bot.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/telegram-bot"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# PostgreSQL Backup
sudo -u postgres pg_dump telegram_bot_db > $BACKUP_DIR/db_$DATE.sql

# Projekt-Dateien
tar -czf $BACKUP_DIR/files_$DATE.tar.gz /var/www/telegram-bot

# Alte Backups löschen (älter als 7 Tage)
find $BACKUP_DIR -type f -mtime +7 -delete

echo "✅ Backup erstellt: $DATE"
```

### Ausführbar machen
```bash
chmod +x /usr/local/bin/backup-telegram-bot.sh
```

### Cron-Job (täglich um 2 Uhr)
```bash
crontab -e
# Füge hinzu:
0 2 * * * /usr/local/bin/backup-telegram-bot.sh
```

---

## 📋 Schritt 12: Monitoring

### Uptime-Monitoring (kostenlos)
- **UptimeRobot**: https://uptimerobot.com
- **StatusCake**: https://www.statuscake.com

### Logs ansehen
```bash
# Service Logs
journalctl -u telegram-bot -f

# Nginx Logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# PostgreSQL Logs
tail -f /var/log/postgresql/postgresql-15-main.log
```

---

## 🔧 Wartung & Updates

### Projekt aktualisieren
```bash
cd /var/www/telegram-bot
git pull  # oder manuell aktualisieren
source venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install && npm run build && cd ..
systemctl restart telegram-bot
```

### Datenbank-Backup manuell
```bash
sudo -u postgres pg_dump telegram_bot_db > backup_$(date +%Y%m%d).sql
```

### Datenbank wiederherstellen
```bash
sudo -u postgres psql telegram_bot_db < backup_20240101.sql
```

---

## 🐛 Troubleshooting

### Service startet nicht
```bash
systemctl status telegram-bot
journalctl -u telegram-bot -n 50
```

### Port bereits belegt
```bash
netstat -tulpn | grep 8000
# Prozess beenden oder Port ändern
```

### Datenbank-Verbindung fehlgeschlagen
```bash
# Testen:
sudo -u postgres psql -U telegram_bot_user -d telegram_bot_db
# Passwort prüfen in .env
```

### Nginx Fehler
```bash
nginx -t
tail -f /var/log/nginx/error.log
```

---

## 📊 Performance-Optimierung

### PostgreSQL Tuning
```bash
nano /etc/postgresql/15/main/postgresql.conf
```

Empfohlene Einstellungen für 2-4GB RAM:
```ini
shared_buffers = 512MB
effective_cache_size = 1536MB
maintenance_work_mem = 128MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 2621kB
min_wal_size = 1GB
max_wal_size = 4GB
```

```bash
systemctl restart postgresql
```

---

## ✅ Checkliste

- [ ] Server aktualisiert
- [ ] PostgreSQL installiert und konfiguriert
- [ ] Projekt deployt
- [ ] Environment-Variablen gesetzt
- [ ] Datenbank initialisiert
- [ ] Systemd Service erstellt und gestartet
- [ ] Nginx konfiguriert
- [ ] SSL-Zertifikat installiert
- [ ] Firewall konfiguriert
- [ ] Fail2Ban aktiviert
- [ ] Backup eingerichtet
- [ ] Monitoring konfiguriert

---

## 🎯 Nächste Schritte

1. Domain auf Hetzner Server zeigen (A-Record)
2. SSL-Zertifikat installieren
3. Frontend Login/Registrierung implementieren
4. Erste Tests durchführen
5. Monitoring einrichten

---

## 📞 Support

- **Hetzner Docs**: https://docs.hetzner.com
- **Hetzner Community**: https://community.hetzner.com

