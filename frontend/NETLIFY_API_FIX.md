# Netlify 404 API-Fehler - Fix

## Problem

```
POST https://6914d5cd08772a2330d2aaf5--cityravers.netlify.app/api/auth/login 404 (Not Found)
```

**Ursache:**
- Frontend versucht API auf Netlify-Domain zu erreichen
- Backend ist aber auf Vercel/Railway
- `VITE_API_BASE_URL` ist nicht gesetzt oder falsch

## Lösung

### 1. Environment Variable in Netlify setzen

1. Gehe zu deiner Netlify Site
2. **Site settings** → **Environment variables**
3. Füge hinzu:
   - **Key:** `VITE_API_BASE_URL`
   - **Value:** Deine Backend-URL (z.B. `https://telegram-bot.up.railway.app` oder Vercel-URL)
   - **Scopes:** ✅ Production, ✅ Deploy previews

**Wichtig:**
- Muss mit `https://` beginnen
- Kein abschließender Slash (`/`)
- Beispiel: `https://telegram-bot.up.railway.app`

### 2. Neuen Build triggern

Nach dem Setzen der Variable:
1. **Deploys** → **Trigger deploy** → **Deploy site**
2. Oder: Push neuen Commit zu GitHub

### 3. Prüfen ob Variable gesetzt ist

Im Build-Log sollte erscheinen:
```
VITE_API_BASE_URL=https://deine-api-url.com
```

## Backend-URLs

### Railway
```
https://[service-name].up.railway.app
```

### Vercel
```
https://[project-name].vercel.app
```

## API-Konfiguration

Die App verwendet `frontend/src/config/api.js`:

```javascript
export const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api'
```

**Fallback:**
- Wenn `VITE_API_BASE_URL` nicht gesetzt: `/api` (relativer Pfad)
- Das funktioniert nur, wenn Backend auf derselben Domain ist

## CORS-Konfiguration im Backend

Stelle sicher, dass dein Backend die Netlify-Domain erlaubt:

```python
# In api.py
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5173,https://cityravers.netlify.app"
).split(",")
```

Oder setze in Railway/Vercel:
```
ALLOWED_ORIGINS=https://cityravers.netlify.app,https://*.netlify.app
```

## Testen

1. Öffne deine Netlify-Site
2. Öffne Browser DevTools (F12)
3. Network Tab
4. Versuche Login
5. Prüfe ob Request zu korrekter Backend-URL geht

**Erwartet:**
```
POST https://deine-backend-url.com/api/auth/login
```

**Falsch:**
```
POST https://cityravers.netlify.app/api/auth/login
```

## Zusammenfassung

**Problem:** API-URL ist falsch (404 auf Netlify-Domain)

**Lösung:**
1. ✅ `VITE_API_BASE_URL` in Netlify Environment Variables setzen
2. ✅ Backend-URL eintragen (Railway oder Vercel)
3. ✅ CORS im Backend für Netlify-Domain erlauben
4. ✅ Neuen Build triggern


