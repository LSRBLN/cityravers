# 🚨 CORS-Fehler: Vercel Frontend → Railway Backend

## ❌ Fehler

```
Access to XMLHttpRequest at 'https://cityraver.up.railway.app/auth/login' 
from origin 'https://tele-ah2426k66-phnxvisioins-projects.vercel.app' 
has been blocked by CORS policy: 
No 'Access-Control-Allow-Origin' header is present
```

**Problem:** Das Backend auf Railway erlaubt die Vercel-Domain nicht.

---

## ✅ Lösung: ALLOWED_ORIGINS in Railway setzen

### Schritt 1: Railway Dashboard öffnen

1. Gehe zu: https://railway.app/dashboard
2. Öffne dein **Projekt**
3. Öffne den **Backend-Service** (nicht Postgres!)

**WICHTIG:** Es muss der **Backend-Service** sein, nicht die Datenbank!

### Schritt 2: Environment Variables öffnen

1. Klicke auf **Settings** (oben rechts im Service)
2. Klicke auf **Variables** (links im Menü)

### Schritt 3: ALLOWED_ORIGINS hinzufügen

**Falls bereits vorhanden:**
1. Klicke auf `ALLOWED_ORIGINS`
2. Füge die Vercel-Domain hinzu

**Falls nicht vorhanden:**
1. Klicke auf **"New Variable"**
2. **Key:** `ALLOWED_ORIGINS`
3. **Value:** 
```
https://tele-ah2426k66-phnxvisioins-projects.vercel.app,https://tele-sandy.vercel.app,https://tele-*.vercel.app,http://localhost:3000,http://localhost:5173
```

**WICHTIG:**
- ✅ Komma-getrennt (keine Leerzeichen!)
- ✅ Mit `https://` (nicht `http://`)
- ✅ Wildcard `*` für alle Vercel-Preview-URLs
- ✅ Localhost für lokale Entwicklung

**Beispiel:**
```
https://tele-sandy.vercel.app,https://tele-*.vercel.app,http://localhost:3000,http://localhost:5173
```

4. **Save**

### Schritt 4: Backend Service neu starten

**WICHTIG:** Nach dem Setzen der Variable muss der Service neu gestartet werden!

1. Gehe zurück zum **Backend-Service**
2. Klicke auf **...** (drei Punkte) oben rechts
3. Klicke auf **"Restart"**
4. Warte bis Service wieder läuft

---

## 🔍 Prüfen ob es funktioniert

### Schritt 1: Backend-Logs prüfen

1. **Railway Dashboard → Backend-Service**
2. Klicke auf **"Logs"** Tab
3. Suche nach:
   - `✅ Datenbank-Migration erfolgreich`
   - `INFO:     Uvicorn running`
   - Keine CORS-Fehler

### Schritt 2: Frontend testen

1. Öffne: `https://tele-sandy.vercel.app`
2. Öffne Browser DevTools (F12)
3. Gehe zu **Network** Tab
4. Versuche Login
5. Prüfe Request:

**Sollte zeigen:**
- **URL:** `https://cityraver.up.railway.app/api/auth/login` ✅
- **Status:** 200 oder 401 (nicht CORS-Fehler)
- **Response Headers:** `Access-Control-Allow-Origin: https://tele-ah2426k66-phnxvisioins-projects.vercel.app`

---

## 📋 Checkliste

### Railway Backend-Service:
- [ ] Richtiger Service geöffnet? (Backend, nicht Postgres!)
- [ ] `ALLOWED_ORIGINS` Environment Variable gesetzt
- [ ] Enthält: `https://tele-*.vercel.app` (Wildcard für alle Vercel-URLs)
- [ ] Enthält: `https://tele-sandy.vercel.app` (Haupt-Domain)
- [ ] Enthält: `http://localhost:3000` (für lokale Entwicklung)
- [ ] Variable gespeichert
- [ ] Backend Service neu gestartet

### Test:
- [ ] Frontend öffnen
- [ ] Login versuchen
- [ ] Browser Console prüfen (keine CORS-Fehler)
- [ ] Network Tab prüfen (Request erfolgreich)

---

## 🎯 Warum Wildcard `*`?

**Vercel erstellt verschiedene URLs:**
- `https://tele-sandy.vercel.app` (Haupt-Domain)
- `https://tele-ah2426k66-phnxvisioins-projects.vercel.app` (Deployment-URL)
- `https://tele-xyz123-...vercel.app` (andere Deployment-URLs)

**Mit Wildcard:**
```
https://tele-*.vercel.app
```
✅ Erlaubt alle Vercel-Preview-URLs automatisch

**Ohne Wildcard:**
```
https://tele-sandy.vercel.app,https://tele-ah2426k66-phnxvisioins-projects.vercel.app
```
❌ Muss jede URL einzeln hinzufügen

---

## 🔧 Alternative: Alle Vercel-URLs erlauben

**Falls Wildcard nicht funktioniert:**

**Value:**
```
https://tele-sandy.vercel.app,https://tele-ah2426k66-phnxvisioins-projects.vercel.app,https://*.vercel.app,http://localhost:3000,http://localhost:5173
```

**Oder für alle Vercel-Projekte:**
```
https://*.vercel.app,http://localhost:3000,http://localhost:5173
```

---

## ✅ Nach dem Fix

**Backend sollte:**
- ✅ CORS-Header senden
- ✅ Vercel-Domain erlauben
- ✅ Login-Requests akzeptieren

**Frontend sollte:**
- ✅ Keine CORS-Fehler mehr
- ✅ Login funktioniert
- ✅ API-Calls erfolgreich

---

## 🎯 Zusammenfassung

**Problem:**
- CORS-Fehler beim Login
- Backend erlaubt Vercel-Domain nicht

**Lösung:**
1. ✅ `ALLOWED_ORIGINS` in Railway Backend-Service setzen
2. ✅ Vercel-Domain hinzufügen (mit Wildcard)
3. ✅ Backend Service neu starten

**Nach dem Fix:**
- ✅ Login funktioniert
- ✅ Keine CORS-Fehler mehr

