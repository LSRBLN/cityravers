# ⚡ Vercel 500 Error - Schnell-Fix

## ⚠️ Problem

**Error:** `500: INTERNAL_SERVER_ERROR`  
**Code:** `FUNCTION_INVOCATION_FAILED`

---

## 🔍 Schritt 1: Logs ansehen (WICHTIG!)

### Vercel Dashboard:

1. **Gehe zu:** https://vercel.com/dashboard
2. **Öffne Projekt** (wahrscheinlich "tele" oder "frontend")
3. **Klicke auf "Deployments"**
4. **Klicke auf das fehlgeschlagene Deployment** (rotes X)
5. **Klicke auf "Functions"** Tab
6. **Klicke auf "View Function Logs"**

**Kopiere die vollständige Fehlermeldung!**

---

## 🔧 Häufige Ursachen & Lösungen

### 1. ❌ Backend auf Vercel (sollte auf Railway sein!)

**Problem:** Falls du ein Backend auf Vercel hast, das fehlschlägt

**Lösung:**
- Backend sollte auf **Railway** sein: `https://cityraver.up.railway.app`
- Falls Backend auf Vercel ist, prüfe Environment Variables:
  - `DATABASE_URL`
  - `JWT_SECRET_KEY`
  - `ENCRYPTION_KEY`

### 2. ❌ Frontend Environment Variable fehlt

**Problem:** `VITE_API_BASE_URL` nicht gesetzt oder nach Build gesetzt

**Lösung:**
1. Vercel Dashboard → Projekt → Settings → Environment Variables
2. Prüfe ob `VITE_API_BASE_URL` vorhanden ist:
   ```
   VITE_API_BASE_URL=https://cityraver.up.railway.app
   ```
3. Falls nicht, hinzufügen:
   - **Key:** `VITE_API_BASE_URL`
   - **Value:** `https://cityraver.up.railway.app`
   - **Environment:** Production, Preview, Development
4. **WICHTIG:** Redeploy nach Änderung!

### 3. ❌ Build-Fehler

**Problem:** Frontend-Build schlägt fehl

**Lösung:**
1. Vercel Dashboard → Deployments → Build Logs
2. Prüfe auf Fehler:
   - `npm install` Fehler?
   - `npm run build` Fehler?
   - Module nicht gefunden?

---

## 🚀 Schnell-Fix (Schritt-für-Schritt)

### Schritt 1: Logs ansehen
**Vercel Dashboard:**
- Deployments → Fehlgeschlagenes Deployment → Functions → View Function Logs
- **Kopiere die Fehlermeldung!**

### Schritt 2: Environment Variable prüfen
**Vercel Dashboard:**
- Settings → Environment Variables
- Prüfe: `VITE_API_BASE_URL=https://cityraver.up.railway.app`
- Falls fehlt: Hinzufügen

### Schritt 3: Redeploy
**Vercel Dashboard:**
- Deployments → Neuestes Deployment → Redeploy

**Oder Vercel CLI:**
```bash
cd frontend
vercel --prod
```

### Schritt 4: Testen
Öffne Frontend-URL und prüfe ob Fehler behoben ist.

---

## 🐛 Welches Projekt hat den Fehler?

### Prüfe welches Projekt:

**Vercel Dashboard:**
1. Alle Projekte ansehen
2. Prüfe welches Projekt den 500-Fehler hat:
   - **"frontend"** → Frontend-Problem
   - **"tele"** oder Backend-Projekt → Backend-Problem

### Falls Backend auf Vercel:
- Backend sollte auf **Railway** sein!
- Falls auf Vercel: Prüfe Environment Variables (siehe oben)

### Falls Frontend:
- Prüfe `VITE_API_BASE_URL`
- Prüfe Build-Logs

---

## ✅ Checkliste

- [ ] Logs angesehen (vollständige Fehlermeldung kopiert)
- [ ] Projekt identifiziert (Frontend oder Backend?)
- [ ] Environment Variables geprüft
- [ ] `VITE_API_BASE_URL` gesetzt (falls Frontend)
- [ ] `DATABASE_URL` gesetzt (falls Backend auf Vercel)
- [ ] Redeploy durchgeführt
- [ ] Frontend/Backend getestet

---

## 📋 Nächste Schritte

1. ✅ **Logs ansehen** (siehe oben)
2. ✅ **Fehlermeldung identifizieren**
3. ✅ **Environment Variables prüfen**
4. ✅ **Redeploy**
5. ✅ **Testen**

---

## 🆘 Falls weiterhin Fehler

**Teile die vollständige Fehlermeldung aus den Logs!**

**Vercel Dashboard:**
- Deployments → Fehlgeschlagenes Deployment → Functions → View Function Logs
- Kopiere die komplette Fehlermeldung

---

## 📞 Hilfe

- **Vercel Dashboard:** https://vercel.com/dashboard
- **Vercel Docs:** https://vercel.com/docs
- **Backend API:** https://cityraver.up.railway.app/docs

