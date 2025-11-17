# 🐛 Vercel 500 Error - FUNCTION_INVOCATION_FAILED

## ⚠️ Problem

**Error:** `500: INTERNAL_SERVER_ERROR`  
**Code:** `FUNCTION_INVOCATION_FAILED`  
**ID:** `fra1::54bv2-1762982491665-4d8c05ab27ab`

---

## 🔍 Mögliche Ursachen

### 1. **Environment Variable fehlt**
- `VITE_API_BASE_URL` nicht gesetzt
- Variable wurde nach Build gesetzt (muss vor Build sein!)

### 2. **Build-Fehler**
- Frontend-Build schlägt fehl
- Dependencies fehlen

### 3. **Serverless Function Fehler**
- Falls es ein Backend auf Vercel gibt (sollte auf Railway sein!)

---

## ✅ Lösung 1: Logs prüfen

### Vercel CLI:
```bash
cd frontend
vercel logs --follow
```

### Oder Vercel Dashboard:
1. Gehe zu: https://vercel.com/dashboard
2. Öffne Projekt "frontend" oder "tele"
3. Klicke auf **"Deployments"**
4. Klicke auf das fehlgeschlagene Deployment
5. Klicke auf **"Functions"** → **"View Function Logs"**

---

## ✅ Lösung 2: Environment Variables prüfen

### Prüfen ob Variable gesetzt ist:

**Vercel CLI:**
```bash
cd frontend
vercel env ls
```

**Oder Vercel Dashboard:**
1. Projekt → **Settings** → **Environment Variables**
2. Prüfe ob `VITE_API_BASE_URL` vorhanden ist:
   ```
   VITE_API_BASE_URL=https://cityraver.up.railway.app
   ```

### Falls nicht gesetzt, hinzufügen:

**Vercel CLI:**
```bash
cd frontend
vercel env add VITE_API_BASE_URL production
# Eingabe: https://cityraver.up.railway.app
```

**Oder Vercel Dashboard:**
1. Settings → Environment Variables → **Add New**
2. **Key:** `VITE_API_BASE_URL`
3. **Value:** `https://cityraver.up.railway.app`
4. **Environment:** Production, Preview, Development
5. **Save**

### WICHTIG: Redeploy nach Environment Variable!

```bash
cd frontend
vercel --prod
```

---

## ✅ Lösung 3: Build-Logs prüfen

### Vercel Dashboard:
1. Deployments → Fehlgeschlagenes Deployment
2. Klicke auf **"Build Logs"**
3. Prüfe auf Fehler:
   - `npm install` Fehler?
   - `npm run build` Fehler?
   - Module nicht gefunden?

---

## ✅ Lösung 4: Prüfen ob es ein Backend auf Vercel gibt

**Falls du ein Backend auf Vercel hast (sollte auf Railway sein!):**

### Backend sollte auf Railway sein:
```
https://cityraver.up.railway.app
```

**Falls Backend auf Vercel ist:**
- Prüfe Backend-Logs
- Prüfe Environment Variables (DATABASE_URL, JWT_SECRET_KEY, etc.)
- Siehe: `VERCEL_500_FIX_SUMMARY.md`

---

## 🔧 Schnell-Fix Checkliste

### 1. Environment Variable prüfen
- [ ] `VITE_API_BASE_URL` in Vercel gesetzt?
- [ ] Variable in Production, Preview UND Development?
- [ ] Wert korrekt: `https://cityraver.up.railway.app`

### 2. Redeploy
- [ ] Nach Environment Variable Änderung redeployed?
- [ ] Build erfolgreich?

### 3. Logs prüfen
- [ ] Vercel Logs angesehen?
- [ ] Fehlermeldung identifiziert?

### 4. Backend prüfen
- [ ] Backend läuft auf Railway? (`https://cityraver.up.railway.app/docs`)
- [ ] CORS konfiguriert? (`ALLOWED_ORIGINS` im Backend)

---

## 🚀 Schnell-Fix (Schritt-für-Schritt)

### Schritt 1: Logs ansehen
```bash
cd frontend
vercel logs --follow
```

**Oder Vercel Dashboard:**
- Deployments → Fehlgeschlagenes Deployment → Functions → View Function Logs

### Schritt 2: Environment Variable setzen (falls fehlt)
```bash
cd frontend
vercel env add VITE_API_BASE_URL production
# Eingabe: https://cityraver.up.railway.app
```

### Schritt 3: Redeploy
```bash
vercel --prod
```

### Schritt 4: Testen
Öffne Frontend-URL und prüfe ob Fehler behoben ist.

---

## 🐛 Häufige Fehler

### "Module not found"
**Ursache:** Dependency fehlt in `package.json`  
**Lösung:** Prüfe `package.json`, füge fehlende Dependency hinzu

### "Environment variable not set"
**Ursache:** `VITE_API_BASE_URL` fehlt oder wurde nach Build gesetzt  
**Lösung:** Variable setzen und redeployen

### "Function timeout"
**Ursache:** Funktion läuft zu lange  
**Lösung:** Prüfe ob es ein Backend-Problem ist (sollte auf Railway sein!)

---

## 📋 Debug-Informationen sammeln

### 1. Vercel Logs kopieren
```bash
vercel logs > vercel-logs.txt
```

### 2. Environment Variables prüfen
```bash
vercel env ls
```

### 3. Build-Logs prüfen
Vercel Dashboard → Deployments → Build Logs

---

## 🎯 Nächste Schritte

1. ✅ **Logs ansehen** (siehe oben)
2. ✅ **Environment Variable prüfen** (falls fehlt, setzen)
3. ✅ **Redeploy** (nach Environment Variable)
4. ✅ **Testen** (Frontend-URL öffnen)

---

## 📞 Hilfe

- **Vercel Dashboard:** https://vercel.com/dashboard
- **Vercel Docs:** https://vercel.com/docs
- **Backend API:** https://cityraver.up.railway.app/docs

---

## 🔗 Nützliche Dateien

- `VERCEL_500_FIX_SUMMARY.md` - Weitere Details zu 500-Fehlern
- `VERCEL_TROUBLESHOOTING.md` - Allgemeine Troubleshooting-Anleitung
- `NETWORK_ERROR_FIX.md` - Network Error beheben

