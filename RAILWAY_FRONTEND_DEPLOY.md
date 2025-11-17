# 🚀 Frontend auf Railway deployen

## 📋 Voraussetzungen

- ✅ Backend läuft bereits auf Railway (`https://cityraver.up.railway.app`)
- ✅ Railway Account vorhanden
- ✅ Railway Token vorhanden (siehe `RAILWAY_TOKEN.md`)

---

## 🎯 Schritt-für-Schritt Anleitung

### Schritt 1: Railway Dashboard öffnen

1. Gehe zu [railway.app](https://railway.app)
2. Logge dich ein
3. Öffne dein Projekt (das mit dem Backend)

### Schritt 2: Neuen Service für Frontend erstellen

1. Klicke auf **"New"** (oben rechts)
2. Wähle **"GitHub Repo"**
3. Wähle dein Repository `telegram-bot`
4. Railway erstellt einen neuen Service

### Schritt 3: Service konfigurieren

1. Klicke auf den neuen Service
2. Gehe zu **Settings**
3. Setze folgende Werte:

#### Root Directory:
```
frontend
```

#### Build Command:
```
npm install && npm run build
```

#### Start Command:
```
npx serve -s dist -l $PORT
```

**Oder:** Railway erkennt automatisch `railway.json` im `frontend/` Ordner.

### Schritt 4: Environment Variables setzen

Gehe zu **Settings** → **Variables** → **New Variable**:

```bash
VITE_API_BASE_URL=https://cityraver.up.railway.app
```

**Wichtig:** Diese Variable wird beim Build verwendet!

### Schritt 5: Deployment starten

1. Railway startet automatisch das Deployment
2. Warte bis Build abgeschlossen ist
3. Prüfe Logs auf Fehler

---

## 🔧 Alternative: Railway CLI

### 1. Railway CLI installieren (falls noch nicht)

```bash
npm install -g @railway/cli
```

### 2. Mit Token einloggen

```bash
source .railway.env
railway login --token $RAILWAY_TOKEN
```

### 3. Projekt verlinken

```bash
cd /Users/rebelldesign/Documents/telegram-bot
railway link
```

### 4. Neuen Service erstellen

```bash
railway service create frontend
```

### 5. Root Directory setzen

```bash
railway service frontend
railway variables set RAILWAY_SERVICE_ROOT=frontend
```

### 6. Environment Variables setzen

```bash
railway variables set VITE_API_BASE_URL=https://cityraver.up.railway.app
```

### 7. Deployen

```bash
railway up --service frontend
```

---

## 📝 Konfigurationsdateien

### `frontend/railway.json` (bereits erstellt)

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "npx serve -s dist -l $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### `frontend/package.json` (aktualisiert)

- `serve` Dependency hinzugefügt
- `start` Script hinzugefügt

---

## ✅ Deployment-Checkliste

- [ ] Neuer Service in Railway erstellt
- [ ] Root Directory auf `frontend` gesetzt
- [ ] Build Command: `npm install && npm run build`
- [ ] Start Command: `npx serve -s dist -l $PORT`
- [ ] Environment Variable: `VITE_API_BASE_URL=https://cityraver.up.railway.app`
- [ ] Deployment erfolgreich
- [ ] Frontend-URL funktioniert
- [ ] API-Verbindung funktioniert

---

## 🔗 URLs nach Deployment

### Backend:
```
https://cityraver.up.railway.app
```

### Frontend:
```
https://dein-frontend-service.up.railway.app
```

Railway generiert automatisch eine URL für deinen Frontend-Service.

---

## 🧪 Frontend testen

### 1. Frontend-URL öffnen

Öffne die Railway-URL deines Frontend-Services im Browser.

### 2. Login testen

1. Versuche dich einzuloggen
2. Prüfe Browser-Konsole (F12) auf Fehler
3. Prüfe Network-Tab ob API-Calls funktionieren

### 3. API-Verbindung prüfen

API-Calls sollten gehen zu:
```
https://cityraver.up.railway.app/api/...
```

---

## 🔒 CORS konfigurieren

Falls CORS-Fehler auftreten:

1. Gehe zu deinem **Backend-Service** in Railway
2. Settings → Variables → New Variable:

```bash
ALLOWED_ORIGINS=https://dein-frontend-service.up.railway.app,http://localhost:3000
```

**Wichtig:** Ersetze `dein-frontend-service` mit deiner tatsächlichen Frontend-URL!

---

## 🐛 Troubleshooting

### Build fehlgeschlagen

**Problem:** `npm install` oder `npm run build` schlägt fehl

**Lösung:**
1. Prüfe Build-Logs in Railway
2. Prüfe ob `package.json` korrekt ist
3. Prüfe ob Node.js Version korrekt ist

### Frontend zeigt 404

**Problem:** Alle Routes zeigen 404

**Lösung:**
1. Prüfe ob `_redirects` Datei in `frontend/public/` vorhanden ist
2. Prüfe ob `serve -s` verwendet wird (Single-Page-App Modus)

### API-Calls fehlgeschlagen

**Problem:** Frontend kann Backend nicht erreichen

**Lösung:**
1. Prüfe ob `VITE_API_BASE_URL` beim Build gesetzt war
2. Prüfe Browser-Konsole auf CORS-Fehler
3. Prüfe ob `ALLOWED_ORIGINS` im Backend gesetzt ist

### Environment Variable nicht verwendet

**Problem:** `VITE_API_BASE_URL` wird nicht verwendet

**Lösung:**
1. **Wichtig:** Environment Variables müssen VOR dem Build gesetzt sein!
2. Rebuild nach Änderung der Environment Variables
3. Prüfe ob Variable mit `VITE_` beginnt (Vite-Requirement)

---

## 📊 Service-Struktur in Railway

```
Dein Projekt
├── Backend Service (cityraver)
│   └── https://cityraver.up.railway.app
├── Frontend Service
│   └── https://frontend-service.up.railway.app
└── PostgreSQL Database
    └── Automatisch verbunden
```

---

## 🚀 Schnellstart (Railway Dashboard)

1. **Railway Dashboard** → Dein Projekt
2. **New** → **GitHub Repo** → Repository wählen
3. **Settings** → **Root Directory:** `frontend`
4. **Settings** → **Variables** → `VITE_API_BASE_URL=https://cityraver.up.railway.app`
5. **Deploy** startet automatisch

---

## 📞 Support

- **Railway Dashboard:** https://railway.app
- **Railway Docs:** https://docs.railway.app
- **Backend API:** https://cityraver.up.railway.app/docs

---

## ✅ Nächste Schritte nach Deployment

1. ✅ Frontend-URL notieren
2. ✅ CORS konfigurieren (falls nötig)
3. ✅ Login testen
4. ✅ Alle Features testen
5. ✅ Custom Domain einrichten (optional)

