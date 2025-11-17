# 🚨 Vercel: API URL korrigieren - FINALE LÖSUNG

## ❌ Problem

**Fehler:**
```
cityraver.up.railway.app/auth/login:1 Failed to load resource: 404
cityraver.up.railway.app/auth/register:1 Failed to load resource: 404
```

**Ursache:**
- `VITE_API_BASE_URL` ist in Vercel gesetzt
- Aber **OHNE `/api` am Ende**
- Request geht zu: `https://cityraver.up.railway.app/auth/login` ❌
- Sollte sein: `https://cityraver.up.railway.app/api/auth/login` ✅

---

## ✅ Lösung: VITE_API_BASE_URL korrigieren

### Schritt 1: Vercel Dashboard öffnen

1. Gehe zu: https://vercel.com/dashboard
2. Öffne das **"tele"** Projekt
3. Klicke auf **Settings**

### Schritt 2: Environment Variables öffnen

1. **Settings → Environment Variables**
2. Suche nach `VITE_API_BASE_URL`

### Schritt 3: Variable korrigieren

**Falls vorhanden:**
1. Klicke auf `VITE_API_BASE_URL`
2. **Aktueller Value (wahrscheinlich):**
   ```
   https://cityraver.up.railway.app
   ```
3. **Korrigierter Value (MUSS sein):**
   ```
   https://cityraver.up.railway.app/api
   ```
   - ✅ Mit `/api` am Ende!
   - ✅ Kein abschließender Slash nach `/api`

**Falls nicht vorhanden:**
1. Klicke auf **"Add New"**
2. Key: `VITE_API_BASE_URL`
3. Value: `https://cityraver.up.railway.app/api`
4. Environments: **Production**, **Preview**, **Development**
5. Save

### Schritt 4: Redeploy

**WICHTIG:** Nach Änderung der Variable muss das Frontend neu deployed werden!

**Option A: Automatisch (bei Git Push):**
```bash
git commit --allow-empty -m "Trigger Vercel redeploy for VITE_API_BASE_URL"
git push
```

**Option B: Manuell im Dashboard:**
1. **Deployments Tab**
2. Neuestes Deployment → **"..."** (drei Punkte)
3. **"Redeploy"**

---

## 🔍 Warum `/api` am Ende?

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

**Wenn `VITE_API_BASE_URL = https://cityraver.up.railway.app`:**
- Request: `https://cityraver.up.railway.app/auth/login` ❌ (404)

**Wenn `VITE_API_BASE_URL = https://cityraver.up.railway.app/api`:**
- Request: `https://cityraver.up.railway.app/api/auth/login` ✅ (200)

---

## 📋 Checkliste

### Vercel:
- [ ] `VITE_API_BASE_URL` Environment Variable vorhanden
- [ ] Value = `https://cityraver.up.railway.app/api` (mit `/api`!)
- [ ] Scopes: Production, Preview, Development
- [ ] Variable gespeichert
- [ ] Frontend neu deployed

### Test:
- [ ] Browser Console: `import.meta.env.VITE_API_BASE_URL` zeigt korrekte URL
- [ ] Network Tab: Request geht zu `/api/auth/login`
- [ ] Keine 404-Fehler mehr
- [ ] Login funktioniert

---

## 🎯 Nach dem Fix

**Requests sollten gehen zu:**
- ✅ `https://cityraver.up.railway.app/api/auth/login`
- ✅ `https://cityraver.up.railway.app/api/auth/register`
- ✅ `https://cityraver.up.railway.app/api/accounts`
- ✅ etc.

**Keine 404-Fehler mehr!** ✅

---

## 🔧 Schnell-Fix

1. **Vercel Dashboard → "tele" Projekt**
2. **Settings → Environment Variables**
3. **`VITE_API_BASE_URL` = `https://cityraver.up.railway.app/api`** (mit `/api`!)
4. **Save**
5. **Deployments → Redeploy**

**Dann sollte Login funktionieren!** ✅

