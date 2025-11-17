# 🚨 Vercel Network Error beim Login - Fix

## ❌ Problem

**Fehler:** Network Error beim Login  
**Ursache:** `VITE_API_BASE_URL` ist nicht in Vercel gesetzt

**Was passiert:**
- Frontend versucht `/api/auth/login` (relativer Pfad)
- Das funktioniert nur, wenn Backend auf derselben Domain ist
- Backend ist aber auf Railway: `https://cityraver.up.railway.app`
- Frontend ist auf Vercel: `https://tele-sandy.vercel.app`
- → Request geht zu falscher Domain → Network Error

---

## ✅ Lösung: VITE_API_BASE_URL in Vercel setzen

### Schritt 1: Vercel Dashboard öffnen

1. Gehe zu: https://vercel.com/dashboard
2. Öffne das **"tele"** Projekt
3. Klicke auf **Settings**

### Schritt 2: Environment Variables hinzufügen

1. **Settings → Environment Variables**
2. Klicke auf **"Add New"**
3. Füge hinzu:

**Key:**
```
VITE_API_BASE_URL
```

**Value:**
```
https://cityraver.up.railway.app
```

**WICHTIG:**
- ✅ Muss mit `https://` beginnen
- ✅ Kein abschließender Slash (`/`)
- ✅ Keine Leerzeichen

**Scopes:**
- ✅ **Production** (für Live-Site)
- ✅ **Preview** (für Preview-Builds)
- ✅ **Development** (optional)

4. Klicke auf **"Save"**

### Schritt 3: Redeploy

**WICHTIG:** Nach dem Setzen der Environment Variable muss ein neuer Build gestartet werden!

1. Gehe zu **Deployments**
2. Klicke auf **...** (drei Punkte) beim neuesten Deployment
3. Klicke auf **"Redeploy"**
4. Oder: Klicke auf **"Redeploy"** Button (oben rechts)

**Warum Redeploy?**
- Environment Variables werden beim Build eingebettet
- Alte Builds haben die Variable nicht
- Neuer Build lädt die Variable

---

## 🔍 Prüfen ob Variable gesetzt ist

### Im Browser (nach Redeploy):

1. Öffne Frontend-URL: `https://tele-sandy.vercel.app`
2. Öffne Browser DevTools (F12)
3. Gehe zu **Console**
4. Tippe:
```javascript
console.log(import.meta.env.VITE_API_BASE_URL)
```

**Sollte zeigen:**
```
https://cityraver.up.railway.app
```

**Falls `undefined`:**
- Variable ist nicht gesetzt
- Oder: Build wurde nicht neu gestartet

---

## 🔧 CORS im Backend prüfen

**Falls Network Error weiterhin besteht:**

### Railway Dashboard:

1. Gehe zu: https://railway.app/dashboard
2. Öffne Backend Service
3. **Settings → Variables**
4. Prüfe `ALLOWED_ORIGINS`:

**Sollte enthalten:**
```
https://tele-sandy.vercel.app,https://tele-*.vercel.app,http://localhost:3000
```

**Falls nicht vorhanden:**
1. Klicke auf **"New Variable"**
2. **Key:** `ALLOWED_ORIGINS`
3. **Value:**
```
https://tele-sandy.vercel.app,https://tele-*.vercel.app,http://localhost:3000
```
4. **Save**
5. Backend Service **Restart**

---

## 📋 Checkliste

### Vercel:
- [ ] `VITE_API_BASE_URL` Environment Variable gesetzt
- [ ] Value = `https://cityraver.up.railway.app` (ohne Slash!)
- [ ] Scopes: Production, Preview, Development
- [ ] Variable gespeichert
- [ ] Redeploy gestartet

### Railway:
- [ ] `ALLOWED_ORIGINS` Environment Variable gesetzt
- [ ] Enthält: `https://tele-sandy.vercel.app`
- [ ] Backend Service neu gestartet

### Test:
- [ ] Frontend öffnen
- [ ] Browser Console prüfen: `import.meta.env.VITE_API_BASE_URL`
- [ ] Login versuchen
- [ ] Network Tab prüfen (F12 → Network)
- [ ] Request sollte zu `https://cityraver.up.railway.app/api/auth/login` gehen

---

## 🎯 Zusammenfassung

**Problem:**
- `VITE_API_BASE_URL` fehlt in Vercel
- Frontend verwendet `/api` (relativer Pfad)
- Request geht zu falscher Domain

**Lösung:**
1. ✅ `VITE_API_BASE_URL` in Vercel setzen
2. ✅ Redeploy
3. ✅ CORS im Backend prüfen

**Nach dem Fix:**
- ✅ Frontend verwendet `https://cityraver.up.railway.app`
- ✅ Login funktioniert
- ✅ Keine Network Errors mehr

---

## 🔍 Debug: Network Tab prüfen

**Nach dem Redeploy:**

1. Öffne Frontend: `https://tele-sandy.vercel.app`
2. Öffne Browser DevTools (F12)
3. Gehe zu **Network** Tab
4. Versuche Login
5. Prüfe Request:

**Sollte zeigen:**
- **URL:** `https://cityraver.up.railway.app/api/auth/login` ✅
- **Status:** 200 oder 401 (nicht Network Error)

**Falls immer noch Network Error:**
- Prüfe ob `VITE_API_BASE_URL` wirklich gesetzt ist
- Prüfe ob Redeploy erfolgreich war
- Prüfe Browser Console für Fehler

