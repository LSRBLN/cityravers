# 🚨 404-Fehler: Request geht zu falscher URL

## ❌ Problem

**Fehler:**
```
Failed to load resource: 404 (login, line 0)
Failed to load resource: 404 (register, line 0)
```

**Ursache:**
- Request geht zu: `/login` und `/register` ❌
- Sollte gehen zu: `/api/auth/login` und `/api/auth/register` ✅

**Das bedeutet:**
- `VITE_API_BASE_URL` ist nicht gesetzt
- Oder: Frontend wurde nicht neu deployed nach dem Setzen

---

## ✅ Lösung: VITE_API_BASE_URL in Vercel setzen

### Schritt 1: Vercel Dashboard öffnen

1. **Gehe zu:** https://vercel.com/dashboard
2. **Öffne das "tele" Projekt**
3. **Settings → Environment Variables**

### Schritt 2: Variable prüfen/hinzufügen

**Falls NICHT vorhanden:**

1. **Klicke auf "Add New"**
2. **Key:** `VITE_API_BASE_URL`
3. **Value:** `https://cityraver.up.railway.app/api`
   - ✅ Mit `https://` am Anfang
   - ✅ Mit `/api` am Ende
   - ✅ Kein abschließender Slash nach `/api`
4. **Environments:** Wähle alle aus:
   - ✅ **Production**
   - ✅ **Preview**
   - ✅ **Development**
5. **Klicke auf "Save"**

**Falls bereits vorhanden:**

1. **Klicke auf `VITE_API_BASE_URL`**
2. **Prüfe Value**
3. **Sollte sein:** `https://cityraver.up.railway.app/api`
4. **Falls falsch:** Korrigiere und **Save**

### Schritt 3: Frontend neu deployed

**WICHTIG:** Nach dem Setzen der Variable muss das Frontend neu deployed werden!

**Option A: Automatisch (bei Git Push):**
```bash
git commit --allow-empty -m "Trigger Vercel redeploy for VITE_API_BASE_URL"
git push
```

**Option B: Manuell im Dashboard:**

1. **Vercel Dashboard → "tele" Projekt**
2. **Deployments Tab**
3. **Neuestes Deployment → "..." (drei Punkte)**
4. **"Redeploy"**

**Warte bis Deployment fertig ist!**

---

## 🔍 Warum passiert das?

**Frontend Code (`frontend/src/config/api.js`):**
```javascript
export const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api'
```

**Verwendung (`frontend/src/contexts/AuthContext.jsx`):**
```javascript
const response = await axios.post(`${API_BASE}/auth/login`, {
  username,
  password
})
```

**Wenn `VITE_API_BASE_URL` nicht gesetzt ist:**
- `API_BASE` = `/api` (relativer Pfad)
- Request: `https://tele-sandy.vercel.app/api/auth/login` ✅ (sollte funktionieren)

**Aber wenn Variable falsch gesetzt ist:**
- `VITE_API_BASE_URL` = `https://cityraver.up.railway.app` (ohne `/api`)
- `API_BASE` = `https://cityraver.up.railway.app`
- Request: `https://cityraver.up.railway.app/auth/login` ❌ (404)

**Oder wenn Variable leer/undefined:**
- `VITE_API_BASE_URL` = `undefined`
- `API_BASE` = `/api` (Fallback)
- Request: `https://tele-sandy.vercel.app/api/auth/login` ✅ (sollte funktionieren)

**Aber der Fehler zeigt `/login` statt `/api/auth/login`:**
- Das bedeutet: `API_BASE` ist leer oder `undefined`
- Request: `https://tele-sandy.vercel.app/login` ❌ (404)

**Mögliche Ursachen:**
1. Variable nicht gesetzt
2. Variable leer/undefined
3. Frontend nicht neu deployed nach dem Setzen
4. Build-Prozess verwendet alte Variable

---

## 🔧 Browser Console prüfen

### Schritt 1: Console öffnen

1. **Frontend öffnen:** `https://tele-sandy.vercel.app`
2. **F12** (DevTools)
3. **Console Tab**

### Schritt 2: API_BASE prüfen

**Tippe in Console:**
```javascript
console.log(import.meta.env.VITE_API_BASE_URL)
```

**Sollte zeigen:**
```
https://cityraver.up.railway.app/api
```

**Falls `undefined`:**
- Variable nicht gesetzt
- Oder: Frontend nicht neu deployed

**Falls leer (`""`):**
- Variable ist leer
- Korrigiere in Vercel

### Schritt 3: Network Tab prüfen

1. **Network Tab** (DevTools)
2. **Login versuchen**
3. **Suche nach:** `login` Request

**Request URL sollte sein:**
```
https://cityraver.up.railway.app/api/auth/login
```

**Falls falsch:**
- `https://tele-sandy.vercel.app/login` → Variable nicht gesetzt
- `https://cityraver.up.railway.app/auth/login` → Variable ohne `/api`

---

## 📋 Checkliste

### Vercel:
- [ ] `VITE_API_BASE_URL` vorhanden
- [ ] Value = `https://cityraver.up.railway.app/api` (mit `/api`!)
- [ ] Environments: Production, Preview, Development
- [ ] Variable gespeichert
- [ ] Frontend neu deployed (nach Änderung)

### Browser:
- [ ] Cache geleert (Hard Refresh: `Ctrl+Shift+R`)
- [ ] Console: `import.meta.env.VITE_API_BASE_URL` zeigt korrekte URL
- [ ] Network Tab: Request geht zu `/api/auth/login`
- [ ] Keine 404-Fehler mehr

---

## 🎯 Schnell-Fix

1. **Vercel Dashboard → "tele" Projekt**
2. **Settings → Environment Variables**
3. **`VITE_API_BASE_URL` = `https://cityraver.up.railway.app/api`** (mit `/api`!)
4. **Save**
5. **Deployments → Redeploy** (warten bis fertig!)
6. **Browser: Hard Refresh** (`Ctrl+Shift+R`)
7. **Test: Login versuchen**

**Dann sollte Login funktionieren!** ✅

---

## 🔍 Debugging

**Falls es immer noch nicht funktioniert:**

1. **Prüfe Network Tab:**
   - Welche URL wird tatsächlich aufgerufen?
   - Status Code?
   - Response?

2. **Prüfe Console:**
   - `import.meta.env.VITE_API_BASE_URL` Wert?
   - Fehlermeldungen?

3. **Prüfe Vercel Deployment:**
   - Wurde Frontend nach Variable-Änderung neu deployed?
   - Build Logs: Wird Variable verwendet?

4. **Prüfe Railway Backend:**
   - `https://cityraver.up.railway.app/docs` funktioniert?
   - Endpoints sichtbar?

