# 🔍 Vercel 500 Error - Diagnose

## ⚠️ Problem

**Error:** `500: INTERNAL_SERVER_ERROR`  
**Code:** `FUNCTION_INVOCATION_FAILED`  
**ID:** `fra1::54bv2-1762982491665-4d8c05ab27ab`

---

## 🔍 Schritt 1: Welches Projekt hat den Fehler?

### Prüfe im Vercel Dashboard:

1. **Gehe zu:** https://vercel.com/dashboard
2. **Prüfe alle Projekte:**
   - **"frontend"** → Frontend-Projekt (sollte funktionieren)
   - **"tele"** oder ähnlich → Backend-Projekt (könnte fehlschlagen)

### Frontend-Deployments sind erfolgreich:
- ✅ `frontend-26h8m7t6r-jans-projects-10df1634.vercel.app` - Ready
- ✅ `frontend-ln6sdipib-jans-projects-10df1634.vercel.app` - Ready
- ✅ `frontend-rbvieqjxp-jans-projects-10df1634.vercel.app` - Ready

**Der 500-Fehler kommt wahrscheinlich von einem Backend-Projekt auf Vercel!**

---

## ⚠️ WICHTIG: Backend sollte auf Railway sein!

**Dein Backend läuft bereits erfolgreich auf Railway:**
```
https://cityraver.up.railway.app
```

**Falls du ein Backend auf Vercel hast:**
- ❌ Das sollte **NICHT** nötig sein!
- ✅ Backend läuft bereits auf Railway
- ✅ Frontend sollte Railway-Backend verwenden

---

## 🔧 Lösung: Backend auf Vercel deaktivieren

### Option 1: Backend-Projekt auf Vercel löschen

**Falls du ein Backend-Projekt auf Vercel hast:**
1. Vercel Dashboard → Backend-Projekt
2. Settings → Danger Zone → Delete Project
3. **Oder:** Einfach nicht verwenden

**Frontend sollte Railway-Backend verwenden:**
```
VITE_API_BASE_URL=https://cityraver.up.railway.app
```

### Option 2: Backend auf Vercel reparieren (falls nötig)

**Falls du das Backend auf Vercel behalten willst:**

1. **Environment Variables setzen:**
   - `DATABASE_URL` (PostgreSQL von Railway)
   - `JWT_SECRET_KEY`
   - `ENCRYPTION_KEY`
   - `TELEGRAM_API_ID`
   - `TELEGRAM_API_HASH`

2. **Logs prüfen:**
   - Deployments → Fehlgeschlagenes Deployment → Functions → View Function Logs

3. **Redeploy**

---

## ✅ Empfehlung: Backend auf Railway verwenden

**Warum?**
- ✅ Backend läuft bereits erfolgreich auf Railway
- ✅ Datenbank ist auf Railway
- ✅ Keine doppelten Deployments nötig
- ✅ Einfacher zu verwalten

**Frontend sollte Railway-Backend verwenden:**
```
VITE_API_BASE_URL=https://cityraver.up.railway.app
```

---

## 🔍 Schritt 2: Logs ansehen

### Vercel Dashboard:

1. **Gehe zu:** https://vercel.com/dashboard
2. **Finde das Projekt mit dem 500-Fehler:**
   - Prüfe alle Projekte
   - Suche nach fehlgeschlagenen Deployments (rotes X)
3. **Klicke auf das fehlgeschlagene Deployment**
4. **Klicke auf "Functions"** Tab
5. **Klicke auf "View Function Logs"**
6. **Kopiere die vollständige Fehlermeldung**

---

## 🎯 Schnell-Fix

### Falls Backend auf Vercel fehlschlägt:

**Option A: Backend-Projekt löschen (Empfohlen)**
- Backend läuft bereits auf Railway ✅
- Frontend verwendet Railway-Backend ✅
- Kein Backend auf Vercel nötig ✅

**Option B: Backend auf Vercel reparieren**
- Environment Variables setzen
- Logs prüfen
- Redeploy

---

## 📋 Checkliste

- [ ] Projekt identifiziert (welches hat den 500-Fehler?)
- [ ] Logs angesehen (vollständige Fehlermeldung)
- [ ] Backend auf Railway läuft? (`https://cityraver.up.railway.app/docs`)
- [ ] Frontend verwendet Railway-Backend? (`VITE_API_BASE_URL` gesetzt)
- [ ] Backend auf Vercel nötig? (sollte nicht nötig sein!)

---

## 🆘 Nächste Schritte

1. ✅ **Projekt identifizieren** (welches hat den Fehler?)
2. ✅ **Logs ansehen** (vollständige Fehlermeldung kopieren)
3. ✅ **Entscheiden:** Backend auf Vercel löschen oder reparieren?
4. ✅ **Empfehlung:** Backend auf Railway verwenden (läuft bereits!)

---

## 📞 Hilfe

- **Vercel Dashboard:** https://vercel.com/dashboard
- **Railway Dashboard:** https://railway.app
- **Backend API:** https://cityraver.up.railway.app/docs

