# 🧪 Quick Test - Browser Console

## 📋 Führe diese Tests direkt im Browser aus

**Öffne:** `https://tele-sandy.vercel.app`

**F12 → Console Tab**

---

## Test 1: Variable prüfen

**Tippe in Console:**
```javascript
console.log('VITE_API_BASE_URL:', import.meta.env.VITE_API_BASE_URL)
```

**Erwartetes Ergebnis:**
```
VITE_API_BASE_URL: https://cityraver.up.railway.app/api
```

**Falls `undefined`:**
- Variable nicht gesetzt oder Frontend nicht neu deployed

**Falls leer (`""`):**
- Variable ist leer

**Falls ohne `/api`:**
- Variable falsch gesetzt

---

## Test 2: API_BASE prüfen

**Tippe in Console:**
```javascript
// API_BASE aus config importieren
const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api'
console.log('API_BASE:', API_BASE)
```

**Erwartetes Ergebnis:**
```
API_BASE: https://cityraver.up.railway.app/api
```

**Falls `/api`:**
- Variable nicht gesetzt (Fallback)

**Falls falsche URL:**
- Variable falsch gesetzt

---

## Test 3: Request URL testen

**Tippe in Console:**
```javascript
const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api'
const loginUrl = `${API_BASE}/auth/login`
console.log('Login URL:', loginUrl)
```

**Erwartetes Ergebnis:**
```
Login URL: https://cityraver.up.railway.app/api/auth/login
```

**Falls falsch:**
- Variable nicht gesetzt oder falsch

---

## Test 4: Direkter Request testen

**Tippe in Console:**
```javascript
const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api'
fetch(`${API_BASE}/auth/login`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'test', password: 'test' })
})
.then(r => r.json())
.then(data => console.log('Response:', data))
.catch(err => console.error('Error:', err))
```

**Erwartetes Ergebnis:**
- ✅ Status: 401 (Ungültige Credentials - OK, Endpoint funktioniert)
- ✅ Response: `{detail: "Ungültige Anmeldedaten"}`

**Falls 404:**
- Endpoint nicht gefunden → Variable falsch oder nicht gesetzt

**Falls CORS Error:**
- CORS-Problem → `ALLOWED_ORIGINS` prüfen

---

## Test 5: Network Tab prüfen

1. **Network Tab** (DevTools)
2. **Login versuchen**
3. **Suche nach:** `login` Request
4. **Klicke auf Request**

**Request URL sollte sein:**
```
https://cityraver.up.railway.app/api/auth/login
```

**Status Code:**
- ✅ 200 = Erfolg
- ✅ 401 = Ungültige Credentials (OK, Endpoint funktioniert)
- ❌ 404 = Endpoint nicht gefunden

**Response:**
- Klicke auf "Response" Tab
- Was zeigt es?

---

## 📋 Bitte sende mir:

**Kopiere die Ergebnisse aller 5 Tests hierher:**

1. **Test 1:** `VITE_API_BASE_URL = ???`
2. **Test 2:** `API_BASE = ???`
3. **Test 3:** `Login URL = ???`
4. **Test 4:** `Response = ???` oder `Error = ???`
5. **Test 5:** `Request URL = ???`, `Status Code = ???`, `Response = ???`

---

## 🔧 Mögliche Lösungen basierend auf Ergebnissen

### Falls Test 1 zeigt `undefined`:

**Problem:** Variable nicht gesetzt oder Frontend nicht neu deployed

**Lösung:**
1. Vercel → Settings → Environment Variables
2. Prüfe `VITE_API_BASE_URL`
3. Falls nicht vorhanden: Hinzufügen
4. Falls vorhanden: Prüfe Value
5. Frontend neu deployen (Redeploy)
6. Browser: Hard Refresh (`Ctrl+Shift+R`)

### Falls Test 1 zeigt falsche URL:

**Problem:** Variable falsch gesetzt

**Lösung:**
1. Vercel → Settings → Environment Variables
2. `VITE_API_BASE_URL` korrigieren zu: `https://cityraver.up.railway.app/api`
3. Save
4. Frontend neu deployen (Redeploy)
5. Browser: Hard Refresh

### Falls Test 4 zeigt 404:

**Problem:** Endpoint nicht gefunden

**Lösung:**
1. Prüfe Backend: `https://cityraver.up.railway.app/docs`
2. Prüfe ob `POST /api/auth/login` existiert
3. Prüfe `ALLOWED_ORIGINS` in Railway

### Falls Test 4 zeigt CORS Error:

**Problem:** CORS-Problem

**Lösung:**
1. Railway → "tele" Service → Variables
2. Prüfe `ALLOWED_ORIGINS`
3. Sollte enthalten: `https://tele-sandy.vercel.app`
4. Backend neu starten (Redeploy)

