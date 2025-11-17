# 🚀 Deployment-Anleitung: Telegram-Bot hochladen

## 📋 Übersicht der verfügbaren Optionen

| Plattform | Schwierigkeit | Kosten | Backend | Frontend | Datenbank | Empfehlung |
|-----------|---------------|--------|---------|----------|-----------|------------|
| **Railway** | ⭐ Einfach | $5-20/Monat | ✅ | ✅ | ✅ Inklusive | ⭐⭐⭐⭐⭐ |
| **Vercel** | ⭐⭐ Mittel | $0-20/Monat | ✅ Serverless | ✅ | ❌ Extern nötig | ⭐⭐⭐ |
| **Netlify** | ⭐⭐ Mittel | $0-19/Monat | ❌ | ✅ | ❌ Extern nötig | ⭐⭐ |
| **Eigener Server** | ⭐⭐⭐ Komplex | €0-30/Monat | ✅ | ✅ | ✅ | ⭐⭐⭐⭐⭐ |

---

## 🎯 Option 1: Railway (EMPFOHLEN - Einfachste Option)

### ✅ Vorteile
- All-in-One: Backend + Frontend + Datenbank
- Automatisches Deployment bei Git-Push
- PostgreSQL inklusive
- Einfache Konfiguration
- Bereits vorbereitet (`Procfile`, `railway.json`)

### 📝 Schritt-für-Schritt Anleitung

#### 1. Railway Account erstellen
1. Gehe zu [railway.app](https://railway.app)
2. Klicke auf **"Start a New Project"**
3. Melde dich mit GitHub an

#### 2. Projekt verbinden
1. Klicke auf **"Deploy from GitHub repo"**
2. Wähle dein Repository `telegram-bot`
3. Railway erkennt automatisch Python und FastAPI

#### 3. PostgreSQL Datenbank hinzufügen
1. Klicke auf **"New"** → **"Database"** → **"Add PostgreSQL"**
2. Railway erstellt automatisch `DATABASE_URL` Environment Variable

#### 4. Environment Variables setzen
Gehe zu **Settings** → **Variables** und füge hinzu:

```bash
# Datenbank (wird automatisch von Railway gesetzt, aber prüfen!)
DATABASE_URL=postgresql://user:password@host:port/database

# JWT & Verschlüsselung
JWT_SECRET_KEY=dein-sehr-langer-geheimer-schluessel-min-32-zeichen
ENCRYPTION_KEY=dein-encryption-key-fuer-sensible-daten-min-32-zeichen

# Telegram API (von https://my.telegram.org/apps)
TELEGRAM_API_ID=deine-telegram-api-id
TELEGRAM_API_HASH=deine-telegram-api-hash

# Optional: SMS Provider
FIVESIM_API_KEY=dein-5sim-api-key
SMS_ACTIVATE_API_KEY=dein-sms-activate-api-key
SMS_MANAGER_API_KEY=dein-sms-manager-api-key
GETSMSCODE_API_KEY=dein-getsmscode-api-key
```

#### 5. Start-Command prüfen
Railway verwendet automatisch die `Procfile`:
```
web: uvicorn api:app --host 0.0.0.0 --port $PORT
```

**Falls nicht automatisch erkannt:**
1. Gehe zu **Settings** → **Service**
2. Setze **Start Command**: `uvicorn api:app --host 0.0.0.0 --port $PORT`

#### 6. Frontend deployen (separater Service)
1. Klicke auf **"New"** → **"GitHub Repo"**
2. Wähle das gleiche Repository
3. Railway erkennt automatisch Node.js
4. Setze **Root Directory**: `frontend`
5. Setze **Build Command**: `npm run build`
6. Setze **Start Command**: (leer lassen - statische Dateien)

#### 7. Deployment prüfen
- Backend URL: `https://dein-service.up.railway.app`
- Frontend URL: `https://dein-frontend-service.up.railway.app`
- API Docs: `https://dein-service.up.railway.app/docs`

### 🔧 Wichtige Anpassungen für Railway

**1. Datenbank-Migration auf PostgreSQL**
```bash
# Lokal testen:
python migrate_to_postgresql.py
```

**2. Session-Dateien**
- Session-Dateien müssen persistent gespeichert werden
- Railway bietet **Volumes** für persistente Daten
- Oder: Session-Dateien in Datenbank speichern (empfohlen)

---

## 🎯 Option 2: Vercel (Serverless)

### ✅ Vorteile
- Kostenloser Tier verfügbar
- Automatisches Deployment
- Edge-Network (schnell)
- Bereits vorbereitet (`vercel.json`, `api/index.py`)

### ⚠️ Nachteile
- Serverless (keine persistenten Dateien)
- Externe Datenbank nötig
- Session-Dateien müssen in Datenbank gespeichert werden

### 📝 Schritt-für-Schritt Anleitung

#### 1. Vercel Account erstellen
1. Gehe zu [vercel.com](https://vercel.com)
2. Melde dich mit GitHub an

#### 2. Projekt importieren
1. Klicke auf **"Add New"** → **"Project"**
2. Wähle dein Repository `telegram-bot`
3. Vercel erkennt automatisch die `vercel.json`

#### 3. Environment Variables setzen
Gehe zu **Settings** → **Environment Variables**:

```bash
DATABASE_URL=postgresql://user:password@host:port/database
JWT_SECRET_KEY=dein-secret-key
ENCRYPTION_KEY=dein-encryption-key
TELEGRAM_API_ID=deine-api-id
TELEGRAM_API_HASH=deine-api-hash
```

#### 4. Externe Datenbank einrichten
**Option A: Supabase (kostenlos)**
1. Gehe zu [supabase.com](https://supabase.com)
2. Erstelle neues Projekt
3. Kopiere `DATABASE_URL` aus Settings

**Option B: Railway PostgreSQL**
1. Erstelle Railway PostgreSQL Service
2. Kopiere `DATABASE_URL`

#### 5. Frontend deployen
1. Erstelle neues Vercel-Projekt
2. Setze **Root Directory**: `frontend`
3. Setze **Build Command**: `npm run build`
4. Setze **Output Directory**: `dist`

#### 6. Deployment prüfen
- Backend: `https://dein-projekt.vercel.app`
- Frontend: `https://dein-frontend.vercel.app`

### 🔧 Wichtige Anpassungen für Vercel

**1. Session-Dateien in Datenbank speichern**
```python
# Session-Dateien müssen als BLOB in Datenbank gespeichert werden
# Oder: Externes Storage (S3, Cloudflare R2)
```

**2. File-Uploads**
- Verwende externes Storage (S3, R2)
- Oder: Base64 in Datenbank

---

## 🎯 Option 3: Netlify (Nur Frontend)

### ⚠️ Einschränkung
- Netlify ist primär für statische Frontends
- Backend muss separat gehostet werden (Railway, Vercel, etc.)

### 📝 Schritt-für-Schritt Anleitung

#### 1. Netlify Account erstellen
1. Gehe zu [netlify.com](https://netlify.com)
2. Melde dich mit GitHub an

#### 2. Frontend deployen
1. Klicke auf **"Add new site"** → **"Import an existing project"**
2. Wähle dein Repository
3. Setze:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/dist`

#### 3. Environment Variables
Gehe zu **Site settings** → **Environment variables**:

```bash
VITE_API_URL=https://dein-backend-url.com
```

#### 4. Redirects konfigurieren
Die `frontend/public/_redirects` Datei ist bereits vorhanden:
```
/*    /index.html   200
```

#### 5. Backend separat hosten
- Verwende Railway oder Vercel für Backend
- Setze `VITE_API_URL` in Netlify auf Backend-URL

---

## 🎯 Option 4: Eigener Linux-Server (Maximale Kontrolle)

### ✅ Vorteile
- Volle Kontrolle
- Keine monatlichen Kosten (außer Server)
- Alle Daten lokal
- Keine Limits

### 📝 Schritt-für-Schritt Anleitung

#### 1. Server vorbereiten
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.10 python3-pip python3-venv nodejs npm nginx postgresql postgresql-contrib git
```

#### 2. Projekt klonen
```bash
cd /var/www
git clone <dein-repo-url> telegram-bot
cd telegram-bot
```

#### 3. Backend einrichten
```bash
# Virtual Environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Datenbank-Migration
python migrate_to_postgresql.py
```

#### 4. Frontend bauen
```bash
cd frontend
npm install
npm run build
cd ..
```

#### 5. Systemd Service erstellen
```bash
sudo nano /etc/systemd/system/telegram-bot.service
```

Inhalt:
```ini
[Unit]
Description=Telegram Bot API
After=network.target postgresql.service

[Service]
User=www-data
WorkingDirectory=/var/www/telegram-bot
Environment="PATH=/var/www/telegram-bot/venv/bin"
Environment="DATABASE_URL=postgresql://user:password@localhost/telegram_bot_db"
Environment="JWT_SECRET_KEY=dein-secret-key"
Environment="ENCRYPTION_KEY=dein-encryption-key"
ExecStart=/var/www/telegram-bot/venv/bin/uvicorn api:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Aktivieren:
```bash
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

#### 6. Nginx konfigurieren
```bash
sudo nano /etc/nginx/sites-available/telegram-bot
```

Inhalt:
```nginx
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
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Aktivieren:
```bash
sudo ln -s /etc/nginx/sites-available/telegram-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 7. SSL-Zertifikat (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d deine-domain.de
```

---

## 🔐 Environment Variables Checkliste

### Erforderlich für alle Plattformen:
```bash
DATABASE_URL=postgresql://...
JWT_SECRET_KEY=min-32-zeichen-langer-geheimer-schluessel
ENCRYPTION_KEY=min-32-zeichen-langer-encryption-key
```

### Erforderlich für Telegram:
```bash
TELEGRAM_API_ID=deine-api-id
TELEGRAM_API_HASH=deine-api-hash
```

### Optional (SMS Provider):
```bash
FIVESIM_API_KEY=...
SMS_ACTIVATE_API_KEY=...
SMS_MANAGER_API_KEY=...
GETSMSCODE_API_KEY=...
```

---

## 📊 Vergleich: Welche Option wählen?

### Für schnellen Start:
**→ Railway** (Option 1)
- Einfachste Einrichtung
- All-in-One
- Automatisches Deployment

### Für kostenlosen Start:
**→ Vercel** (Option 2)
- Kostenloser Tier
- Serverless
- Externe Datenbank nötig

### Für maximale Kontrolle:
**→ Eigener Server** (Option 4)
- Volle Kontrolle
- Keine Limits
- Selbst-Wartung erforderlich

### Für nur Frontend:
**→ Netlify** (Option 3)
- Einfach für statische Sites
- Backend separat nötig

---

## ✅ Deployment-Checkliste

### Vor dem Deployment:
- [ ] `requirements.txt` aktualisiert
- [ ] `package.json` aktualisiert
- [ ] Environment Variables dokumentiert
- [ ] Datenbank-Migration getestet
- [ ] `.env.example` erstellt
- [ ] `.gitignore` prüft (keine Secrets!)

### Nach dem Deployment:
- [ ] Backend-URL funktioniert (`/docs` aufrufbar)
- [ ] Frontend-URL funktioniert
- [ ] API-Verbindung Frontend → Backend
- [ ] Datenbank-Verbindung funktioniert
- [ ] Login funktioniert
- [ ] Session-Dateien werden gespeichert

---

## 🐛 Troubleshooting

### Backend startet nicht
- Prüfe Start-Command (muss `$PORT` verwenden)
- Prüfe Logs in Railway/Vercel Dashboard
- Prüfe Environment Variables

### Datenbank-Verbindung fehlgeschlagen
- Prüfe `DATABASE_URL` Format
- Prüfe ob Datenbank läuft (Railway: Service Status)
- Prüfe Firewall-Regeln

### Frontend kann Backend nicht erreichen
- Prüfe `VITE_API_URL` in Frontend
- Prüfe CORS-Einstellungen im Backend
- Prüfe Nginx/Proxy-Konfiguration

### Session-Dateien verschwinden
- Railway/Vercel: Session-Dateien müssen in Datenbank gespeichert werden
- Eigener Server: Prüfe Dateiberechtigungen

---

## 📚 Weitere Ressourcen

- **Railway Docs**: https://docs.railway.app
- **Vercel Docs**: https://vercel.com/docs
- **Netlify Docs**: https://docs.netlify.com
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/

---

## 🎯 Empfehlung für dein Projekt

**Für schnellen Start:**
1. **Railway** für Backend + Datenbank
2. **Railway** für Frontend (separater Service)
3. Oder: **Netlify** für Frontend, **Railway** für Backend

**Für Produktion:**
1. **Eigener Server** (Hetzner, DigitalOcean)
2. PostgreSQL Datenbank
3. Nginx als Reverse Proxy
4. SSL-Zertifikat (Let's Encrypt)

---

**Nächste Schritte:**
1. Wähle eine Option aus
2. Folge der Schritt-für-Schritt Anleitung
3. Teste das Deployment lokal
4. Deploye auf die gewählte Plattform

