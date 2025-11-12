# Netlify Deployment Guide

## Voraussetzungen

1. **Netlify Account** - Erstelle einen Account auf [netlify.com](https://www.netlify.com)
2. **Git Repository** - Code muss in einem Git-Repository sein (GitHub, GitLab, Bitbucket)
3. **Backend API** - Das Backend muss separat gehostet werden (z.B. auf einem VPS, Heroku, Railway, etc.)

## Deployment-Schritte

### 1. Environment Variables in Netlify setzen

In den Netlify-Einstellungen (Site settings → Environment variables) hinzufügen:

```
VITE_API_BASE_URL=https://deine-api-domain.com
```

**Wichtig:** Ersetze `https://deine-api-domain.com` mit der tatsächlichen URL deines Backend-APIs.

### 2. Build-Einstellungen

Netlify erkennt automatisch die `netlify.toml` Datei:
- **Build command:** `npm run build`
- **Publish directory:** `dist`
- **Node version:** 18

### 3. Deployment-Methoden

#### Option A: GitHub Integration (Empfohlen)

1. Push Code zu GitHub
2. In Netlify: "New site from Git"
3. GitHub Repository auswählen
4. Build-Einstellungen werden automatisch aus `netlify.toml` geladen
5. Environment Variables setzen (siehe Schritt 1)
6. "Deploy site" klicken

#### Option B: Netlify CLI

```bash
# Netlify CLI installieren
npm install -g netlify-cli

# Login
netlify login

# Im frontend-Verzeichnis
cd frontend

# Deployment
netlify deploy --prod
```

#### Option C: Drag & Drop

1. Im `frontend` Verzeichnis: `npm run build`
2. Den `dist` Ordner zu Netlify Drag & Drop ziehen

### 4. CORS-Konfiguration im Backend

Stelle sicher, dass dein Backend die Netlify-Domain erlaubt:

```python
# In api.py
origins = [
    "http://localhost:3000",
    "https://deine-netlify-domain.netlify.app",
    "https://deine-custom-domain.com"
]
```

### 5. Custom Domain (Optional)

1. In Netlify: Site settings → Domain management
2. "Add custom domain" klicken
3. Domain eingeben und DNS-Einstellungen befolgen

## Wichtige Dateien

- `netlify.toml` - Netlify-Konfiguration
- `public/_redirects` - SPA-Routing (alle Routes → index.html)
- `.env.example` - Beispiel für Environment Variables

## Troubleshooting

### Problem: API-Calls schlagen fehl

**Lösung:** 
- Prüfe `VITE_API_BASE_URL` in Netlify Environment Variables
- Stelle sicher, dass das Backend CORS für die Netlify-Domain erlaubt
- Prüfe Browser-Console für Fehler

### Problem: 404 bei direkten Routes

**Lösung:**
- Die `_redirects` Datei sollte im `public/` Ordner sein
- Nach Build sollte sie im `dist/` Ordner sein

### Problem: Build schlägt fehl

**Lösung:**
- Prüfe Node-Version (sollte 18 sein)
- Prüfe ob alle Dependencies installiert sind
- Lokal testen: `npm run build`

## Nach dem Deployment

1. Teste alle Funktionen
2. Prüfe Browser-Console auf Fehler
3. Teste Login/Logout
4. Teste API-Verbindung

