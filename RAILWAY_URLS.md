# 🔗 Railway URLs und Endpoints

## ✅ Deployment erfolgreich!

Dein Backend läuft auf Railway. Der 404 auf `/` ist **normal** - die App hat keine Root-Route.

---

## 📍 Deine Railway URLs

### ✅ Backend-URL:
```
https://cityraver.up.railway.app
```

### Backend-URL finden:

1. **Railway Dashboard** → Dein Projekt → Service
2. Im **Settings** Tab findest du:
   - **Public Domain**: `https://cityraver.up.railway.app`
   - Oder: **Deployments** → Neuestes Deployment → URL oben

### Format:
```
https://[service-name].up.railway.app
```

---

## 🧪 Backend testen

### 1. API-Dokumentation (Swagger UI)
```
https://cityraver.up.railway.app/docs
```

**Interaktive API-Dokumentation** - Hier kannst du alle Endpoints testen!

### 2. Alternative API-Dokumentation (ReDoc)
```
https://cityraver.up.railway.app/redoc
```

### 3. Health Check (wenn vorhanden)
```
https://cityraver.up.railway.app/api/health
```

### 4. Login-Endpoint testen
```
POST https://cityraver.up.railway.app/api/auth/login
```

---

## 📋 Verfügbare API-Endpoints

### Authentifizierung
- `POST /api/auth/register` - Neuen Benutzer registrieren
- `POST /api/auth/login` - Einloggen
- `GET /api/auth/me` - Aktueller Benutzer

### Accounts
- `GET /api/accounts` - Alle Accounts auflisten
- `POST /api/accounts` - Neuen Account erstellen
- `GET /api/accounts/{id}` - Account-Details
- `POST /api/accounts/{id}/login` - Account einloggen
- `DELETE /api/accounts/{id}` - Account löschen

### Gruppen
- `GET /api/groups` - Alle Gruppen auflisten
- `POST /api/groups` - Neue Gruppe erstellen
- `DELETE /api/groups/{id}` - Gruppe löschen

### Geplante Nachrichten
- `GET /api/scheduled-messages` - Alle geplanten Nachrichten
- `POST /api/scheduled-messages` - Neue Nachricht planen
- `GET /api/scheduled-messages/{id}` - Nachricht-Details
- `PUT /api/scheduled-messages/{id}` - Nachricht aktualisieren
- `DELETE /api/scheduled-messages/{id}` - Nachricht löschen

### Admin (nur für Admins)
- `GET /api/admin/users` - Alle Benutzer
- `GET /api/admin/stats` - Statistiken
- `GET /api/admin/settings` - System-Einstellungen

**Vollständige Liste:** Siehe `/docs` Endpoint

---

## 🔧 Frontend konfigurieren

### 1. API-URL in Frontend setzen

**Option A: Environment Variable (empfohlen)**

Erstelle `frontend/.env.production`:
```bash
VITE_API_BASE_URL=https://cityraver.up.railway.app
```

✅ **Bereits erstellt:** `frontend/.env.production`

**Option B: In `frontend/src/config/api.js`**

```javascript
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'https://cityraver.up.railway.app';
```

### 2. CORS konfigurieren

In Railway Environment Variables:
```bash
ALLOWED_ORIGINS=https://dein-frontend-url.netlify.app,https://dein-frontend-url.vercel.app
```

Oder für lokale Entwicklung:
```bash
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## ✅ Deployment-Checkliste

- [x] Backend läuft (Port 8080)
- [x] Datenbank-Migration erfolgreich
- [x] Scheduler gestartet
- [ ] API-Dokumentation erreichbar (`/docs`)
- [ ] Frontend kann Backend erreichen
- [ ] Login funktioniert
- [ ] CORS konfiguriert

---

## 🐛 Troubleshooting

### 404 auf `/`
**Normal!** Die App hat keine Root-Route. Verwende `/api/*` oder `/docs`.

### CORS-Fehler
- Prüfe `ALLOWED_ORIGINS` in Railway Environment Variables
- Füge deine Frontend-URL hinzu

### "Connection refused"
- Prüfe ob Backend läuft (Railway Dashboard → Logs)
- Prüfe ob Port korrekt ist (Railway setzt automatisch `$PORT`)

### "Database connection failed"
- Prüfe `DATABASE_URL` in Railway Variables
- Prüfe ob PostgreSQL Service läuft

---

## 🎯 Nächste Schritte

1. **API-Dokumentation öffnen:** `https://dein-service.up.railway.app/docs`
2. **Frontend deployen** (Railway oder Netlify)
3. **API-URL in Frontend setzen**
4. **CORS konfigurieren**
5. **Login testen**

---

## 📞 Support

- **Railway Docs:** https://docs.railway.app
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **Railway Dashboard:** https://railway.app

