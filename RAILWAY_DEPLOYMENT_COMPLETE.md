# ✅ Railway Deployment erfolgreich!

## 🎉 Backend läuft auf:

```
https://cityraver.up.railway.app
```

---

## 🔗 Wichtige URLs

### API-Dokumentation (Swagger UI)
```
https://cityraver.up.railway.app/docs
```
**Interaktive API-Dokumentation** - Teste alle Endpoints direkt im Browser!

### Alternative Dokumentation (ReDoc)
```
https://cityraver.up.railway.app/redoc
```

### API-Endpoints
Alle Endpoints beginnen mit `/api/`:
- `https://cityraver.up.railway.app/api/auth/login`
- `https://cityraver.up.railway.app/api/accounts`
- `https://cityraver.up.railway.app/api/groups`
- etc.

---

## 🔧 Frontend konfigurieren

### Option 1: Environment Variable für Production Build

**Für Netlify/Vercel/Railway Frontend:**

Setze in den Environment Variables:
```bash
VITE_API_BASE_URL=https://cityraver.up.railway.app
```

### Option 2: Lokale Entwicklung

Erstelle `frontend/.env.local`:
```bash
VITE_API_BASE_URL=http://localhost:8000
```

**Hinweis:** `.env` Dateien sind in `.gitignore` - werden nicht committed.

---

## 🔒 CORS konfigurieren

Falls dein Frontend auf einer anderen Domain läuft (z.B. Netlify), musst du CORS in Railway konfigurieren:

### Railway Environment Variables hinzufügen:

1. Railway Dashboard → Dein Projekt → Settings → Variables
2. Neue Variable hinzufügen:

```bash
ALLOWED_ORIGINS=https://dein-frontend.netlify.app,https://dein-frontend.vercel.app
```

**Beispiel:**
```bash
ALLOWED_ORIGINS=https://cityraver-frontend.netlify.app,http://localhost:3000,http://localhost:5173
```

**Wichtig:** Trenne mehrere URLs mit Komma (keine Leerzeichen!)

---

## ✅ Deployment-Status

- [x] Backend läuft auf Railway
- [x] Datenbank-Migration erfolgreich
- [x] Scheduler gestartet
- [ ] Frontend deployed (Netlify/Vercel/Railway)
- [ ] CORS konfiguriert (falls Frontend auf anderer Domain)
- [ ] API-URL in Frontend gesetzt
- [ ] Login getestet

---

## 🧪 Backend testen

### 1. API-Dokumentation öffnen
```
https://cityraver.up.railway.app/docs
```

### 2. Login testen
```bash
curl -X POST https://cityraver.up.railway.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

### 3. Accounts auflisten (mit Token)
```bash
curl https://cityraver.up.railway.app/api/accounts \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📋 Verfügbare Endpoints

### Authentifizierung
- `POST /api/auth/register` - Registrierung
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Aktueller Benutzer

### Accounts
- `GET /api/accounts` - Alle Accounts
- `POST /api/accounts` - Neuen Account erstellen
- `GET /api/accounts/{id}` - Account-Details
- `POST /api/accounts/{id}/login` - Account einloggen
- `DELETE /api/accounts/{id}` - Account löschen

### Gruppen
- `GET /api/groups` - Alle Gruppen
- `POST /api/groups` - Neue Gruppe erstellen
- `DELETE /api/groups/{id}` - Gruppe löschen

### Geplante Nachrichten
- `GET /api/scheduled-messages` - Alle geplanten Nachrichten
- `POST /api/scheduled-messages` - Neue Nachricht planen
- `PUT /api/scheduled-messages/{id}` - Nachricht aktualisieren
- `DELETE /api/scheduled-messages/{id}` - Nachricht löschen

**Vollständige Liste:** Siehe `/docs` Endpoint

---

## 🚀 Nächste Schritte

### 1. Frontend deployen

**Option A: Netlify**
1. Gehe zu [netlify.com](https://netlify.com)
2. Importiere dein Repository
3. Setze:
   - **Base directory:** `frontend`
   - **Build command:** `npm run build`
   - **Publish directory:** `frontend/dist`
4. Environment Variable setzen:
   - `VITE_API_BASE_URL=https://cityraver.up.railway.app`

**Option B: Vercel**
1. Gehe zu [vercel.com](https://vercel.com)
2. Importiere dein Repository
3. Setze:
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
4. Environment Variable setzen:
   - `VITE_API_BASE_URL=https://cityraver.up.railway.app`

**Option C: Railway (separater Service)**
1. Railway Dashboard → New → GitHub Repo
2. Wähle Repository
3. Setze:
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
4. Environment Variable setzen:
   - `VITE_API_BASE_URL=https://cityraver.up.railway.app`

### 2. CORS konfigurieren

Nachdem Frontend deployed ist, füge die Frontend-URL zu `ALLOWED_ORIGINS` hinzu:

```bash
ALLOWED_ORIGINS=https://dein-frontend-url.netlify.app,http://localhost:3000
```

### 3. Testen

1. Öffne Frontend-URL
2. Versuche dich einzuloggen
3. Prüfe Browser-Konsole auf Fehler
4. Prüfe Network-Tab ob API-Calls funktionieren

---

## 🐛 Troubleshooting

### CORS-Fehler
**Problem:** `Access-Control-Allow-Origin` Fehler im Browser

**Lösung:**
1. Prüfe `ALLOWED_ORIGINS` in Railway Environment Variables
2. Füge deine Frontend-URL hinzu (exakt, mit `https://`)
3. Trenne mehrere URLs mit Komma
4. Railway Service neu starten

### API-Calls gehen zu `/api` statt Railway-URL
**Problem:** Frontend verwendet relative Pfade

**Lösung:**
1. Prüfe ob `VITE_API_BASE_URL` in Frontend Environment Variables gesetzt ist
2. Prüfe ob Variable beim Build verfügbar war
3. Rebuild Frontend nach Änderung der Environment Variables

### 404 auf API-Endpoints
**Problem:** Endpoints nicht erreichbar

**Lösung:**
1. Prüfe ob Backend läuft (Railway Dashboard → Logs)
2. Prüfe ob URL korrekt ist: `https://cityraver.up.railway.app/api/...`
3. Teste `/docs` Endpoint (sollte funktionieren)

---

## 📞 Support

- **Railway Dashboard:** https://railway.app
- **API-Dokumentation:** https://cityraver.up.railway.app/docs
- **Railway Docs:** https://docs.railway.app

---

## ✅ Checkliste

- [x] Backend läuft auf Railway
- [x] API-Dokumentation erreichbar (`/docs`)
- [ ] Frontend deployed
- [ ] `VITE_API_BASE_URL` in Frontend gesetzt
- [ ] `ALLOWED_ORIGINS` in Railway gesetzt
- [ ] Login funktioniert
- [ ] API-Calls funktionieren

