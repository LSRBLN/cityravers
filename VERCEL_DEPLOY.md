# Vercel Deployment Guide

## Voraussetzungen

1. **Vercel Account** - Erstelle einen Account auf [vercel.com](https://vercel.com)
2. **Vercel CLI** (optional) - Für lokales Deployment
3. **Git Repository** - Code muss in einem Git-Repository sein

## Deployment-Schritte

### 1. Vercel CLI installieren (optional)

```bash
npm install -g vercel
```

### 2. Environment Variables in Vercel setzen

In den Vercel-Einstellungen (Project Settings → Environment Variables) hinzufügen:

#### Erforderliche Variablen:

```
DATABASE_URL=postgresql://user:password@host:port/database
JWT_SECRET_KEY=dein-sehr-langer-geheimer-schluessel
ENCRYPTION_KEY=dein-encryption-key-fuer-sensible-daten
```

#### Optional (falls verwendet):

```
TELEGRAM_API_ID=deine-telegram-api-id
TELEGRAM_API_HASH=deine-telegram-api-hash
FIVESIM_API_KEY=dein-5sim-api-key
SMS_ACTIVATE_API_KEY=dein-sms-activate-api-key
SMS_MANAGER_API_KEY=dein-sms-manager-api-key
GETSMSCODE_API_KEY=dein-getsmscode-api-key
```

### 3. Deployment-Methoden

#### Option A: Vercel Dashboard (Empfohlen)

1. Gehe zu [vercel.com](https://vercel.com)
2. Klicke auf **"Add New Project"**
3. Verbinde dein Git-Repository (GitHub, GitLab, Bitbucket)
4. Wähle das Repository aus
5. **Framework Preset:** Wähle "Other" oder lasse es automatisch erkennen
6. **Root Directory:** Lasse leer (oder `./` wenn nötig)
7. **Build Command:** Lasse leer (nicht benötigt für Python)
8. **Output Directory:** Lasse leer
9. **Install Command:** Lasse leer
10. Klicke auf **"Deploy"**

#### Option B: Vercel CLI

```bash
# Vercel CLI installieren (falls noch nicht installiert)
npm install -g vercel

# Login (öffnet Browser für Authentifizierung)
vercel login

# Im Projekt-Root navigieren
cd /Users/rebelldesign/Documents/telegram-bot

# Erste Deployment (Preview)
# Folgt den Prompts:
# - Set up and deploy? Yes
# - Which scope? Wähle deinen Account/Team
# - Link to existing project? No (für neues Projekt)
# - Project name? telegram-bot-api (oder dein Name)
# - Directory? ./
# - Override settings? No
vercel

# Für Produktion (nach erfolgreichem Preview)
vercel --prod

# Environment Variables über CLI setzen
vercel env add DATABASE_URL production
vercel env add JWT_SECRET_KEY production
vercel env add ENCRYPTION_KEY production

# Alle Environment Variables anzeigen
vercel env ls

# Deployment-Status prüfen
vercel ls

# Logs anzeigen
vercel logs
```

### 4. Konfiguration

Die `vercel.json` Datei ist bereits konfiguriert:
- **Entrypoint:** `api/index.py`
- **Python Version:** 3.11
- **Routes:** Alle Requests werden an die FastAPI-App weitergeleitet

### 5. Nach dem Deployment

1. **Prüfe die Deployment-URL:**
   - Vercel gibt dir eine URL wie: `https://dein-projekt.vercel.app`
   - Diese URL ist deine API-Base-URL

2. **Aktualisiere Frontend Environment Variable:**
   - In Netlify: Setze `VITE_API_BASE_URL` auf deine Vercel-URL
   - Beispiel: `VITE_API_BASE_URL=https://dein-projekt.vercel.app`

3. **Teste die API:**
   ```bash
   curl https://dein-projekt.vercel.app/api/health
   ```

## Wichtige Dateien

- `api/index.py` - Vercel Serverless Entrypoint
- `vercel.json` - Vercel-Konfiguration
- `requirements.txt` - Python-Dependencies

## Vercel-spezifische Anpassungen

### Serverless-Funktionen

Vercel verwendet Serverless-Funktionen. Beachte:

1. **Stateless:** Jede Request ist isoliert
2. **Cold Starts:** Erste Request kann langsamer sein
3. **Timeout:** Standard-Timeout ist 10 Sekunden (kann erhöht werden)
4. **Memory:** Standard ist 1GB (kann erhöht werden)

### Datenbank

Vercel unterstützt keine persistenten Dateisysteme. Verwende:

- **PostgreSQL:** Externe Datenbank (z.B. Supabase, Neon, Railway)
- **Session-Dateien:** Müssen in externem Storage sein (z.B. S3, Cloudflare R2)

### Session-Dateien

Telegram Session-Dateien müssen in externem Storage gespeichert werden:

1. **Option A: S3-kompatibler Storage**
   - AWS S3
   - Cloudflare R2
   - DigitalOcean Spaces

2. **Option B: Datenbank**
   - Session-Dateien als BLOB in PostgreSQL speichern

## Troubleshooting

### Problem: "No fastapi entrypoint found"

**Lösung:**
- Stelle sicher, dass `api/index.py` existiert
- Prüfe ob `vercel.json` korrekt konfiguriert ist
- Prüfe ob die App-Variable in `api/index.py` exportiert wird

### Problem: Import-Fehler

**Lösung:**
- Stelle sicher, dass alle Dependencies in `requirements.txt` sind
- Prüfe ob der Python-Pfad in `api/index.py` korrekt ist

### Problem: Timeout-Fehler

**Lösung:**
- Erhöhe Timeout in Vercel-Projekt-Einstellungen
- Optimiere langsame Endpoints
- Verwende Background-Jobs für lange Operationen

### Problem: CORS-Fehler

**Lösung:**
- Stelle sicher, dass die Frontend-URL in CORS-Origins erlaubt ist
- Prüfe `api.py` CORS-Konfiguration

## Beispiel-Konfiguration

### vercel.json (bereits erstellt)
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

### Environment Variables in Vercel
```
DATABASE_URL=postgresql://user:pass@host:5432/db
JWT_SECRET_KEY=super-secret-key-min-32-chars
ENCRYPTION_KEY=fernet-key-base64-encoded
```

## Nächste Schritte

1. ✅ Code zu GitHub pushen
2. ✅ Vercel-Projekt erstellen
3. ✅ Environment Variables setzen
4. ✅ Deployment starten
5. ✅ API-URL in Frontend-Netlify-Environment-Variable setzen
6. ✅ Testen

## Support

- [Vercel Python Documentation](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python)
- [Vercel FastAPI Guide](https://vercel.com/guides/deploying-fastapi-with-vercel)

