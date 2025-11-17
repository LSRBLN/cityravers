# ✅ Backend URLs - Korrekte Endpoints

## ⚠️ 404 auf `/` ist NORMAL!

**Was du siehst:**
```
{"detail":"Not Found"}
```

**Das ist korrekt!** Das Backend hat keine Root-Route (`/`). Alle Endpoints beginnen mit `/api/`.

---

## ✅ Korrekte Backend-URLs

### API-Dokumentation (Swagger UI):
```
https://cityraver.up.railway.app/docs
```
**Interaktive API-Dokumentation** - Hier kannst du alle Endpoints testen!

### Alternative Dokumentation (ReDoc):
```
https://cityraver.up.railway.app/redoc
```

---

## 📋 Verfügbare API-Endpoints

### Authentifizierung:
```
https://cityraver.up.railway.app/api/auth/login
https://cityraver.up.railway.app/api/auth/register
https://cityraver.up.railway.app/api/auth/me
```

### Accounts:
```
https://cityraver.up.railway.app/api/accounts
https://cityraver.up.railway.app/api/accounts/{id}
```

### Gruppen:
```
https://cityraver.up.railway.app/api/groups
```

### Geplante Nachrichten:
```
https://cityraver.up.railway.app/api/scheduled-messages
```

**Vollständige Liste:** Siehe `/docs` Endpoint

---

## 🧪 Backend testen

### Option 1: API-Dokumentation (Empfohlen)

1. **Öffne:** https://cityraver.up.railway.app/docs
2. **Interaktive Swagger-UI** öffnet sich
3. **Teste Endpoints direkt im Browser:**
   - Klicke auf einen Endpoint (z.B. `POST /api/auth/login`)
   - Klicke auf "Try it out"
   - Fülle die Felder aus
   - Klicke auf "Execute"

### Option 2: Direkt im Browser

**Login-Endpoint testen:**
```
https://cityraver.up.railway.app/api/auth/login
```

**Accounts auflisten:**
```
https://cityraver.up.railway.app/api/accounts
```

### Option 3: Mit curl

```bash
# API-Dokumentation
curl https://cityraver.up.railway.app/docs

# Login testen
curl -X POST https://cityraver.up.railway.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

---

## ✅ Status-Check

### Backend läuft:
- ✅ URL erreichbar: `https://cityraver.up.railway.app`
- ✅ 404 auf `/` ist normal (keine Root-Route)
- ✅ API-Dokumentation verfügbar: `/docs`
- ✅ API-Endpoints funktionieren: `/api/*`

---

## 🎯 Schnellstart

### 1. API-Dokumentation öffnen
```
https://cityraver.up.railway.app/docs
```

### 2. Endpoint testen
- Wähle einen Endpoint (z.B. `GET /api/accounts`)
- Klicke auf "Try it out"
- Klicke auf "Execute"
- Siehst du die Antwort? ✅ Backend funktioniert!

---

## 📝 Zusammenfassung

**404 auf `/`:** ✅ Normal (keine Root-Route)

**Korrekte URLs:**
- ✅ `/docs` - API-Dokumentation
- ✅ `/api/*` - Alle API-Endpoints

**Backend funktioniert!** Öffne einfach `/docs` um alle Endpoints zu sehen.

---

## 🔗 Nützliche Links

- **API-Dokumentation:** https://cityraver.up.railway.app/docs
- **Backend-URL:** https://cityraver.up.railway.app
- **Frontend-URL:** https://frontend-6xd5khhkc-jans-projects-10df1634.vercel.app

