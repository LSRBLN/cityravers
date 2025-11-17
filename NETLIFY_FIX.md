# Netlify Build-Fehler - Fix

## Problem

```
npm error enoent This is related to npm not being able to find a file.
'/opt/build/repo/package.json'
Command failed: npm run start
```

**Ursache:**
- Netlify sucht `package.json` im Root-Verzeichnis
- Frontend ist im `frontend/` Unterverzeichnis
- Build-Command ist falsch: `npm run start` statt `npm run build`

## Lösung

### Option 1: netlify.toml im Root (Empfohlen)

Erstelle `netlify.toml` im **Root-Verzeichnis** (nicht in `frontend/`):

```toml
[build]
  base = "frontend"
  command = "cd frontend && npm install && npm run build"
  publish = "frontend/dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[build.environment]
  NODE_VERSION = "18"
```

### Option 2: Netlify Dashboard Einstellungen

Falls `netlify.toml` nicht funktioniert, setze manuell im Dashboard:

1. Gehe zu deiner Site in Netlify
2. **Site settings** → **Build & deploy**
3. **Build settings:**
   - **Base directory:** `frontend`
   - **Build command:** `npm run build`
   - **Publish directory:** `dist`

**Wichtig:** 
- Base directory muss `frontend` sein (nicht Root!)
- Build command muss `npm run build` sein (nicht `npm run start`!)

### Option 3: Netlify CLI

```bash
# Im Root-Verzeichnis
netlify.toml

# Oder manuell setzen
netlify env:set NETLIFY_BASE_DIR frontend
```

## Prüfen

### 1. Dateistruktur

```
telegram-bot/
├── netlify.toml          ← NEU: Im Root
├── frontend/
│   ├── package.json      ← Hier ist das Frontend
│   ├── netlify.toml      ← Kann bleiben (wird ignoriert wenn Root-Version existiert)
│   └── dist/             ← Build-Output
└── ...
```

### 2. Build-Command prüfen

**Falsch:**
```bash
npm run start  # ❌ Das ist für lokale Entwicklung
```

**Richtig:**
```bash
npm run build  # ✅ Das erstellt den Production-Build
```

### 3. package.json Scripts prüfen

In `frontend/package.json` sollte stehen:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }
}
```

**Wichtig:** `npm run start` existiert nicht standardmäßig in Vite-Projekten!

## Häufige Fehler

### Fehler: "package.json not found"

**Lösung:**
- Base directory auf `frontend` setzen
- Oder `netlify.toml` mit `base = "frontend"` erstellen

### Fehler: "npm run start failed"

**Lösung:**
- Build command auf `npm run build` ändern
- `npm run start` ist für lokale Entwicklung, nicht für Builds!

### Fehler: "dist directory not found"

**Lösung:**
- Publish directory auf `dist` setzen (nicht `frontend/dist` wenn base = "frontend")
- Oder `frontend/dist` wenn base = Root

## Nach dem Fix

1. **Trigger neuen Build:**
   - Netlify Dashboard → **Deploys** → **Trigger deploy** → **Deploy site**

2. **Prüfe Build-Logs:**
   - Stelle sicher, dass:
     - Base directory: `frontend` erkannt wird
     - Build command: `npm run build` ausgeführt wird
     - Publish directory: `dist` gefunden wird

3. **Teste die Site:**
   - Öffne deine Netlify-URL
   - Prüfe ob die App lädt

## Zusammenfassung

**Problem:**
- Netlify sucht `package.json` im Root
- Build-Command ist falsch (`npm run start`)

**Lösung:**
- ✅ `netlify.toml` im Root mit `base = "frontend"`
- ✅ Build command: `npm run build`
- ✅ Publish directory: `dist` (oder `frontend/dist` je nach base)

**Netlify Dashboard:**
- Base directory: `frontend`
- Build command: `npm run build`
- Publish directory: `dist`


