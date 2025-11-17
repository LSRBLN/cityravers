# 🚨 CORS-Fehler: Falsche API-URL

## ❌ Problem

**Fehler:**
```
POST https://cityraver.up.railway.app/auth/login
```

**Sollte sein:**
```
POST https://cityraver.up.railway.app/api/auth/login
```

**Ursache:** `VITE_API_BASE_URL` ist falsch gesetzt oder fehlt das `/api` Suffix.

---

## 🔍 Analyse

**Frontend verwendet:**
```javascript
API_BASE = import.meta.env.VITE_API_BASE_URL || '/api'
// Dann: `${API_BASE}/auth/login`
```

**Wenn `VITE_API_BASE_URL=https://cityraver.up.railway.app`:**
- `${API_BASE}/auth/login` = `https://cityraver.up.railway.app/auth/login` ❌

**Korrekt wäre:**
- `VITE_API_BASE_URL=https://cityraver.up.railway.app/api` ✅
- Dann: `${API_BASE}/auth/login` = `https://cityraver.up.railway.app/api/auth/login` ✅

---

## ✅ Lösung: VITE_API_BASE_URL korrigieren

### Schritt 1: Vercel Dashboard

1. Gehe zu: https://vercel.com/dashboard
2. Öffne das **"tele"** Projekt
3. **Settings → Environment Variables**

### Schritt 2: VITE_API_BASE_URL prüfen/korrigieren

**Aktueller Wert (wahrscheinlich):**
```
https://cityraver.up.railway.app
```

**Korrigierter Wert:**
```
https://cityraver.up.railway.app/api
```

**WICHTIG:**
- ✅ Muss `/api` am Ende haben!
- ✅ Mit `https://`
- ✅ Kein abschließender Slash nach `/api`

### Schritt 3: Variable aktualisieren

1. Klicke auf `VITE_API_BASE_URL`
2. Ändere Value zu: `https://cityraver.up.railway.app/api`
3. **Save**

### Schritt 4: Redeploy

**WICHTIG:** Nach Änderung der Environment Variable muss ein neuer Build gestartet werden!

1. **Deployments → Neuestes Deployment**
2. **Redeploy**

---

## 🔍 Alternative: Backend-Endpunkte prüfen

**Falls Backend-Endpunkte OHNE `/api` sind:**

Dann sollte `VITE_API_BASE_URL` sein:
```
https://cityraver.up.railway.app
```

**Aber:** Prüfe zuerst, ob Backend-Endpunkte `/api` haben!

### Backend-Endpunkte prüfen:

1. Öffne: `https://cityraver.up.railway.app/docs`
2. Suche nach `/auth/login` Endpoint
3. Prüfe ob es `/api/auth/login` oder `/auth/login` ist

**Falls `/api/auth/login`:**
- ✅ `VITE_API_BASE_URL=https://cityraver.up.railway.app/api`

**Falls `/auth/login`:**
- ✅ `VITE_API_BASE_URL=https://cityraver.up.railway.app`

---

## 📋 Checkliste

### Vercel:
- [ ] `VITE_API_BASE_URL` gesetzt
- [ ] Value = `https://cityraver.up.railway.app/api` (mit `/api`!)
- [ ] Variable gespeichert
- [ ] Redeploy gestartet

### Railway:
- [ ] `ALLOWED_ORIGINS` gesetzt (für CORS)
- [ ] Enthält: `https://tele-*.vercel.app`
- [ ] Backend Service neu gestartet

### Test:
- [ ] Browser Console: `console.log(import.meta.env.VITE_API_BASE_URL)`
- [ ] Sollte zeigen: `https://cityraver.up.railway.app/api`
- [ ] Network Tab: Request sollte zu `/api/auth/login` gehen
- [ ] Keine CORS-Fehler mehr

---

## 🎯 Zusammenfassung

**Problem:**
- API-URL fehlt `/api` Suffix
- Request geht zu falschem Endpoint

**Lösung:**
1. ✅ `VITE_API_BASE_URL` auf `https://cityraver.up.railway.app/api` setzen
2. ✅ Redeploy
3. ✅ `ALLOWED_ORIGINS` in Railway setzen (für CORS)

**Nach dem Fix:**
- ✅ Request geht zu `/api/auth/login` ✅
- ✅ CORS funktioniert ✅
- ✅ Login funktioniert ✅

