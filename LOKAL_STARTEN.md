# 🚀 App lokal starten

## 📋 Voraussetzungen

- ✅ Python 3.11+ installiert
- ✅ Node.js 18+ installiert
- ✅ npm installiert

---

## 🔧 Schritt 1: Environment-Variablen einrichten

### 1.1 .env Datei erstellen

```bash
# Im Root-Verzeichnis
cp env.example .env
```

### 1.2 .env Datei bearbeiten

Öffne `.env` und setze die erforderlichen Werte:

```bash
# JWT Secret Key (min. 32 Zeichen)
# Generiere mit: python3 generate_secrets.py
JWT_SECRET_KEY=dein-jwt-secret-key-min-32-zeichen

# Encryption Key (Fernet Key, base64)
# Generiere mit: python3 generate_secrets.py
ENCRYPTION_KEY=dein-encryption-key-base64-encoded

# Telegram API Credentials
# Erhalte von https://my.telegram.org/apps
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890

# Datenbank (SQLite für lokale Entwicklung)
DATABASE_URL=sqlite:///./telegram_bot.db
```

**Secrets generieren:**
```bash
python3 generate_secrets.py
```

---

## 🐍 Schritt 2: Backend starten

### Option A: Mit Start-Skript (Empfohlen)

```bash
# Skript ausführbar machen
chmod +x start_backend.sh

# Backend starten
./start_backend.sh
```

### Option B: Manuell

```bash
# Python Dependencies installieren (nur beim ersten Mal)
pip install -r requirements.txt

# Backend starten
python3 -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### Option C: Mit Virtual Environment (Empfohlen)

```bash
# Virtual Environment erstellen
python3 -m venv venv

# Aktivieren (macOS/Linux)
source venv/bin/activate

# Oder (Windows)
# venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt

# Backend starten
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

**Backend läuft auf:** http://localhost:8000  
**API-Dokumentation:** http://localhost:8000/docs

---

## ⚛️ Schritt 3: Frontend starten

### Option A: Mit Start-Skript (Empfohlen)

```bash
# Skript ausführbar machen
chmod +x start_frontend.sh

# Frontend starten
./start_frontend.sh
```

### Option B: Manuell

```bash
# Ins Frontend-Verzeichnis wechseln
cd frontend

# Dependencies installieren (nur beim ersten Mal)
npm install

# Frontend starten
npm run dev
```

**Frontend läuft auf:** http://localhost:3000

---

## 🎯 Schritt 4: App öffnen

1. **Frontend öffnen:** http://localhost:3000
2. **API-Dokumentation:** http://localhost:8000/docs

---

## 🔄 Beide gleichzeitig starten (Terminal-Tabs)

### Terminal 1: Backend
```bash
cd /Users/rebelldesign/Documents/telegram-bot
./start_backend.sh
```

### Terminal 2: Frontend
```bash
cd /Users/rebelldesign/Documents/telegram-bot
./start_frontend.sh
```

---

## 🛠️ Troubleshooting

### Backend startet nicht

**Problem: Port bereits belegt**
```bash
# Prüfe ob Port 8000 belegt ist
lsof -i :8000

# Beende Prozess oder ändere Port
uvicorn api:app --host 0.0.0.0 --port 8001 --reload
```

**Problem: Module nicht gefunden**
```bash
# Dependencies neu installieren
pip install -r requirements.txt
```

**Problem: Datenbank-Fehler**
```bash
# Datenbank initialisieren
python3 -c "from database import init_db; init_db()"
```

### Frontend startet nicht

**Problem: Port bereits belegt**
```bash
# Prüfe ob Port 3000 belegt ist
lsof -i :3000

# Beende Prozess oder ändere Port in vite.config.js
```

**Problem: Module nicht gefunden**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Problem: API-Verbindung fehlgeschlagen**
- Prüfe ob Backend läuft: http://localhost:8000/docs
- Prüfe `.env` Datei im Frontend (falls vorhanden)
- Prüfe `frontend/src/config/api.js` - sollte auf `/api` zeigen

---

## 📝 Wichtige Hinweise

### Environment-Variablen

- **Backend:** Liest `.env` aus Root-Verzeichnis
- **Frontend:** Liest `VITE_*` Variablen aus `.env` (im Frontend-Verzeichnis)

### Datenbank

- **Lokal:** SQLite (`telegram_bot.db`)
- **Production:** PostgreSQL (Railway/Vercel)

### Hot Reload

- **Backend:** `--reload` Flag aktiviert Auto-Reload
- **Frontend:** Vite hat automatisch Hot Reload

---

## 🚀 Quick Start (Alles auf einmal)

```bash
# 1. Environment-Variablen
cp env.example .env
# Bearbeite .env und setze deine Werte

# 2. Backend (Terminal 1)
pip install -r requirements.txt
uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# 3. Frontend (Terminal 2)
cd frontend
npm install
npm run dev

# 4. Öffne Browser
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

---

## ✅ Checkliste

- [ ] Python 3.11+ installiert
- [ ] Node.js 18+ installiert
- [ ] `.env` Datei erstellt und konfiguriert
- [ ] Backend-Dependencies installiert (`pip install -r requirements.txt`)
- [ ] Frontend-Dependencies installiert (`cd frontend && npm install`)
- [ ] Backend läuft auf http://localhost:8000
- [ ] Frontend läuft auf http://localhost:3000
- [ ] API-Dokumentation erreichbar: http://localhost:8000/docs

---

## 🎉 Fertig!

Die App sollte jetzt lokal laufen:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

