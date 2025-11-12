# Hosting-Anleitung: Berlin City Raver - Marketing Tool

## 📋 Anforderungen

**Backend:**
- Python 3.10+
- FastAPI (uvicorn)
- SQLite (aktuell) oder PostgreSQL (empfohlen für Produktion)
- ~500MB RAM (minimal)
- ~2GB Festplatte

**Frontend:**
- Node.js 18+
- React + Vite
- Nginx/Apache für statische Dateien

**Datenbank:**
- SQLite (Entwicklung) oder PostgreSQL (Produktion)
- ~100MB-1GB je nach Nutzeranzahl

## 🖥️ Hosting-Optionen

### Option 1: Eigenen Linux-Server nutzen (Empfohlen wenn vorhanden)

**Vorteile:**
- ✅ Volle Kontrolle
- ✅ Keine monatlichen Kosten (außer Server)
- ✅ Keine Limits
- ✅ Alle Daten lokal

**Nachteile:**
- ⚠️ Selbst-Wartung erforderlich
- ⚠️ Backup selbst verwalten
- ⚠️ Sicherheit selbst konfigurieren

**Setup:**
- Nginx als Reverse Proxy
- Systemd für Service-Management
- PostgreSQL für Datenbank
- SSL-Zertifikat (Let's Encrypt)

---

### Option 2: VPS (Virtual Private Server)

#### **DigitalOcean** ⭐ Empfohlen
- **Preis**: $6-12/Monat
- **Specs**: 1-2GB RAM, 1 vCPU, 25GB SSD
- **Vorteile**: Einfach, gute Docs, SSD, gute Performance
- **URL**: https://www.digitalocean.com

#### **Hetzner Cloud**
- **Preis**: €4-8/Monat
- **Specs**: 2GB RAM, 1 vCPU, 20GB SSD
- **Vorteile**: Günstig, deutsche Server, gute Performance
- **URL**: https://www.hetzner.com/cloud

#### **Linode (Akamai)**
- **Preis**: $5-12/Monat
- **Specs**: 1-2GB RAM, 1 vCPU, 25GB SSD
- **Vorteile**: Zuverlässig, gute Performance
- **URL**: https://www.linode.com

#### **Vultr**
- **Preis**: $6-12/Monat
- **Specs**: 1-2GB RAM, 1 vCPU, 25GB SSD
- **Vorteile**: Viele Standorte, gute Performance
- **URL**: https://www.vultr.com

#### **Contabo**
- **Preis**: €4-8/Monat
- **Specs**: 4GB RAM, 2 vCPU, 50GB SSD
- **Vorteile**: Sehr günstig, viel RAM
- **URL**: https://www.contabo.com

---

### Option 3: Managed Hosting (Backend + Datenbank getrennt)

#### **Railway** ⭐ Einfachste Option
- **Preis**: $5-20/Monat
- **Features**: Automatisches Deployment, PostgreSQL inklusive
- **Vorteile**: Sehr einfach, GitHub-Integration
- **URL**: https://railway.app

#### **Render**
- **Preis**: $7-25/Monat
- **Features**: Automatisches Deployment, PostgreSQL verfügbar
- **Vorteile**: Einfach, kostenloser Tier verfügbar
- **URL**: https://render.com

#### **Fly.io**
- **Preis**: $5-15/Monat
- **Features**: Globales Edge-Network, PostgreSQL
- **Vorteile**: Schnell, gute Performance
- **URL**: https://fly.io

#### **Heroku** (teurer)
- **Preis**: $7-25/Monat
- **Features**: Managed PostgreSQL, einfach
- **Vorteile**: Sehr einfach, aber teurer
- **URL**: https://www.heroku.com

---

### Option 4: Cloud-Provider (Skalierbar)

#### **AWS (Amazon Web Services)**
- **Preis**: Pay-as-you-go (~$10-50/Monat)
- **Services**: EC2, RDS (PostgreSQL), S3
- **Vorteile**: Sehr skalierbar, viele Services
- **Nachteile**: Komplex, teuer bei hohem Traffic
- **URL**: https://aws.amazon.com

#### **Google Cloud Platform**
- **Preis**: Pay-as-you-go (~$10-50/Monat)
- **Services**: Compute Engine, Cloud SQL
- **Vorteile**: Gute Performance, viele Services
- **URL**: https://cloud.google.com

#### **Microsoft Azure**
- **Preis**: Pay-as-you-go (~$10-50/Monat)
- **Services**: Virtual Machines, Azure Database
- **Vorteile**: Enterprise-Features
- **URL**: https://azure.microsoft.com

---

### Option 5: Datenbank-Hosting (getrennt)

#### **Supabase** ⭐ Empfohlen für PostgreSQL
- **Preis**: Kostenlos bis $25/Monat
- **Features**: PostgreSQL, Auth, Storage
- **Vorteile**: Kostenloser Tier, einfach
- **URL**: https://supabase.com

#### **PlanetScale** (MySQL)
- **Preis**: Kostenlos bis $29/Monat
- **Features**: MySQL-kompatibel, skalierbar
- **Vorteile**: Serverless, automatische Skalierung
- **URL**: https://planetscale.com

#### **Neon** (PostgreSQL)
- **Preis**: Kostenlos bis $19/Monat
- **Features**: Serverless PostgreSQL
- **Vorteile**: Sehr günstig, gute Performance
- **URL**: https://neon.tech

---

## 🎯 Empfehlung

### Für Start/Small Scale:
1. **Eigener Linux-Server** (wenn vorhanden) + PostgreSQL
2. **DigitalOcean/Hetzner VPS** ($6-8/Monat) + PostgreSQL
3. **Railway** ($5/Monat) - All-in-One

### Für Produktion/Scale:
1. **Eigener Linux-Server** + PostgreSQL + Nginx
2. **AWS/GCP** + RDS/Cloud SQL
3. **Hetzner Dedicated Server** (€30-50/Monat)

---

## 🚀 Setup auf eigenem Linux-Server

### 1. System-Voraussetzungen
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.10 python3-pip python3-venv nodejs npm nginx postgresql postgresql-contrib

# PostgreSQL einrichten
sudo -u postgres createuser -P telegram_bot_user
sudo -u postgres createdb -O telegram_bot_user telegram_bot_db
```

### 2. Projekt deployen
```bash
# Projekt klonen/kopieren
cd /var/www
git clone <your-repo> telegram-bot
cd telegram-bot

# Python Virtual Environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend bauen
cd frontend
npm install
npm run build
cd ..
```

### 3. Datenbank auf PostgreSQL umstellen
```python
# database.py anpassen:
# Statt: sqlite:///telegram_bot.db
# Verwende: postgresql://user:password@localhost/telegram_bot_db
```

### 4. Systemd Service erstellen
```bash
# /etc/systemd/system/telegram-bot.service
[Unit]
Description=Telegram Bot API
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/telegram-bot
Environment="PATH=/var/www/telegram-bot/venv/bin"
ExecStart=/var/www/telegram-bot/venv/bin/uvicorn api:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### 5. Nginx konfigurieren
```nginx
# /etc/nginx/sites-available/telegram-bot
server {
    listen 80;
    server_name deine-domain.de;

    # Frontend
    location / {
        root /var/www/telegram-bot/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 6. SSL-Zertifikat (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d deine-domain.de
```

---

## 💰 Kostenvergleich

| Anbieter | Preis/Monat | RAM | CPU | Datenbank | Empfehlung |
|----------|-------------|-----|-----|-----------|------------|
| **Eigener Server** | €0-30 | - | - | PostgreSQL | ⭐⭐⭐⭐⭐ |
| **Hetzner Cloud** | €4-8 | 2GB | 1 vCPU | PostgreSQL | ⭐⭐⭐⭐⭐ |
| **DigitalOcean** | $6-12 | 1-2GB | 1 vCPU | PostgreSQL | ⭐⭐⭐⭐ |
| **Railway** | $5-20 | - | - | Inklusive | ⭐⭐⭐⭐ |
| **Render** | $7-25 | - | - | Inklusive | ⭐⭐⭐ |
| **Supabase** | $0-25 | - | - | PostgreSQL | ⭐⭐⭐⭐ |

---

## 🔒 Sicherheit

1. **Firewall konfigurieren** (UFW)
2. **SSL-Zertifikat** (Let's Encrypt)
3. **Backups** (täglich)
4. **Environment Variables** für Secrets
5. **Rate Limiting** im Nginx
6. **Fail2Ban** für SSH-Schutz

---

## 📊 Monitoring

- **Uptime**: UptimeRobot (kostenlos)
- **Logs**: journalctl für Systemd
- **Performance**: htop, nginx status
- **Backups**: Automatische PostgreSQL-Dumps

---

## 🎯 Nächste Schritte

1. **Datenbank-Migration**: SQLite → PostgreSQL
2. **Deployment-Script** erstellen
3. **Environment-Variablen** konfigurieren
4. **Backup-Strategie** implementieren
5. **Monitoring** einrichten

