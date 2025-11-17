# Railway Deployment Guide

## Voraussetzungen

1. **Railway Account** - Erstelle einen Account auf [railway.app](https://railway.app)
2. **Railway CLI** (optional) - Für lokales Deployment
3. **Git Repository** - Code muss in einem Git-Repository sein

## Start-Command

### Railway Start-Command

```bash
uvicorn api:app --host 0.0.0.0 --port $PORT
```

**Wichtig:**
- `--host 0.0.0.0` - Bindet an alle Interfaces (erforderlich für Railway)
- `--port $PORT` - Verwendet Railway's PORT Environment Variable
- Kein `--reload` in Production (nur für Entwicklung)

### Konfiguration

Railway erkennt automatisch:
- `Procfile` (falls vorhanden)
- `railway.json` (falls vorhanden)
- Oder manuell in Railway Dashboard setzen

## Deployment-Schritte

### Option 1: Railway Dashboard (Empfohlen)

1. Gehe zu [railway.app](https://railway.app)
2. Klicke auf **"New Project"**
3. Wähle **"Deploy from GitHub repo"**
4. Verbinde dein Repository
5. Railway erkennt automatisch Python und FastAPI

### Option 2: Railway CLI

```bash
# Installiere Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialisiere Projekt
railway init

# Deploy
railway up
```

## Environment Variables

Setze in Railway Dashboard (Settings → Variables):

### Erforderliche Variablen:

```
DATABASE_URL=postgresql://user:password@host:port/database
JWT_SECRET_KEY=dein-sehr-langer-geheimer-schluessel
ENCRYPTION_KEY=dein-encryption-key-fuer-sensible-daten
PORT=8000
```

**Hinweis:** `PORT` wird normalerweise automatisch von Railway gesetzt, aber kann manuell überschrieben werden.

### Optional (falls verwendet):

```
TELEGRAM_API_ID=deine-telegram-api-id
TELEGRAM_API_HASH=deine-telegram-api-hash
FIVESIM_API_KEY=dein-5sim-api-key
SMS_ACTIVATE_API_KEY=dein-sms-activate-api-key
SMS_MANAGER_API_KEY=dein-sms-manager-api-key
GETSMSCODE_API_KEY=dein-getsmscode-api-key
```

## Konfigurationsdateien

### 1. Procfile (Empfohlen)

Erstelle `Procfile` im Root-Verzeichnis:

```
web: uvicorn api:app --host 0.0.0.0 --port $PORT
```

### 2. railway.json (Optional)

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn api:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 3. Manuell in Railway Dashboard

1. Gehe zu deinem Projekt
2. Settings → Service
3. **Start Command:** `uvicorn api:app --host 0.0.0.0 --port $PORT`

## Datenbank (PostgreSQL)

Railway bietet integrierte PostgreSQL-Datenbanken:

1. Klicke auf **"New"** → **"Database"** → **"Add PostgreSQL"**
2. Railway erstellt automatisch `DATABASE_URL` Environment Variable
3. Keine manuelle Konfiguration nötig!

## Build-Konfiguration

Railway erkennt automatisch:
- `requirements.txt` - Python Dependencies
- Python Version (aus `runtime.txt` oder automatisch)

### Optional: runtime.txt

Erstelle `runtime.txt` für spezifische Python-Version:

```
python-3.11.0
```

## Lokale Entwicklung mit Railway

```bash
# Installiere Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link zu deinem Projekt
railway link

# Starte lokalen Dev-Server mit Railway Environment
railway run uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

## Vergleich: Railway vs. Vercel

| Aspekt | Railway | Vercel |
|--------|--------|--------|
| Start-Command | ✅ Erforderlich | ❌ Nicht nötig (Serverless) |
| Command | `uvicorn api:app --host 0.0.0.0 --port $PORT` | Automatisch |
| Datenbank | ✅ Integriert (PostgreSQL) | ❌ Extern nötig |
| Environment | Dashboard/CLI | Dashboard/CLI |
| Deployment | Automatisch bei Push | Automatisch bei Push |

## Troubleshooting

### "Port already in use"
- Stelle sicher, dass `$PORT` verwendet wird (nicht feste Port-Nummer)
- Railway setzt `PORT` automatisch

### "Module not found"
- Prüfe `requirements.txt`
- Prüfe ob alle Dependencies installiert sind

### "Database connection failed"
- Prüfe `DATABASE_URL` in Railway Variables
- Stelle sicher, dass PostgreSQL Service läuft

### "Start command not found"
- Prüfe `Procfile` oder `railway.json`
- Oder setze manuell in Railway Dashboard

## Start-Command Varianten

### Basis (Minimum)
```bash
uvicorn api:app --host 0.0.0.0 --port $PORT
```

### Mit Workers (für höhere Last)
```bash
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

**Hinweis:** Für Gunicorn muss `gunicorn` in `requirements.txt` sein.

### Mit Logging
```bash
uvicorn api:app --host 0.0.0.0 --port $PORT --log-level info
```

## App-URL finden

### Automatische Railway-URL

Nach dem Deployment erhältst du automatisch eine URL:

**Format:**
```
https://dein-service-name.up.railway.app
```

**Beispiel:**
```
https://telegram-bot-production.up.railway.app
```

### URL im Railway Dashboard finden

1. Gehe zu [railway.app](https://railway.app)
2. Öffne dein Projekt
3. Klicke auf deinen **Service** (z.B. "web")
4. Im **Settings** Tab findest du:
   - **Public Domain** - Deine Railway-URL
   - **Custom Domain** - Falls du eine eigene Domain hinzugefügt hast

### URL im Deployments-Tab

1. Gehe zu deinem Projekt
2. Klicke auf **Deployments**
3. Klicke auf das neueste Deployment
4. Die URL wird oben angezeigt

### Custom Domain einrichten

1. Gehe zu deinem Service → **Settings**
2. Scrolle zu **Networking**
3. Klicke auf **Generate Domain** (falls noch nicht geschehen)
4. Oder füge eine **Custom Domain** hinzu:
   - Klicke auf **"Add Custom Domain"**
   - Gib deine Domain ein (z.B. `api.deine-domain.de`)
   - Folge den DNS-Anweisungen

### URL-Struktur

```
https://[service-name].up.railway.app
```

**Beispiele:**
- `https://telegram-bot.up.railway.app`
- `https://api-production.up.railway.app`
- `https://backend-main.up.railway.app`

### API-Endpoints

Deine FastAPI-Endpoints sind dann erreichbar unter:

```
https://dein-service.up.railway.app/api/...
```

**Beispiele:**
- `https://telegram-bot.up.railway.app/api/auth/login`
- `https://telegram-bot.up.railway.app/api/accounts`
- `https://telegram-bot.up.railway.app/docs` (FastAPI Docs)

### URL über Railway CLI

```bash
# Zeige Service-URL
railway domain

# Oder
railway status
```

### Wichtig: HTTPS

- Railway URLs verwenden automatisch **HTTPS**
- Keine zusätzliche Konfiguration nötig
- SSL-Zertifikat wird automatisch bereitgestellt

## Zusammenfassung

**Railway Start-Command:**
```bash
uvicorn api:app --host 0.0.0.0 --port $PORT
```

**App-URL finden:**
1. Railway Dashboard → Projekt → Service → Settings → Public Domain
2. Oder: Deployments → Neuestes Deployment
3. Format: `https://[service-name].up.railway.app`

**Konfiguration:**
- ✅ `Procfile` erstellt
- ✅ `railway.json` erstellt (optional)
- ✅ Start-Command in Railway Dashboard setzen (falls nötig)

**Wichtig:**
- Verwende `$PORT` (nicht feste Port-Nummer)
- `--host 0.0.0.0` ist erforderlich
- Kein `--reload` in Production
- URL wird automatisch generiert nach Deployment

