# 🔧 Network Error beheben - Frontend ↔ Backend

## ⚠️ Problem

Frontend lädt, aber zeigt "Network Error" - die Verbindung zum Backend funktioniert nicht.

---

## 🔍 Ursachen

1. **`VITE_API_BASE_URL` nicht gesetzt** (am wahrscheinlichsten)
2. **CORS-Problem** im Backend
3. **Backend nicht erreichbar**

---

## ✅ Lösung 1: Environment Variable prüfen und setzen

### Prüfen ob Variable gesetzt ist:

```bash
cd frontend
vercel env ls
```

### Falls nicht gesetzt, hinzufügen:

```bash
cd frontend
vercel env add VITE_API_BASE_URL production
# Eingabe: https://cityraver.up.railway.app
```

### Dann redeploy:

```bash
vercel --prod
```

**Wichtig:** Environment Variables müssen VOR dem Build gesetzt sein!

---

## ✅ Lösung 2: CORS im Backend konfigurieren

### Railway Dashboard:

1. Gehe zu deinem **Backend-Service** (cityraver)
2. Settings → Variables → New Variable:

```bash
ALLOWED_ORIGINS=https://frontend-three-pi-61.vercel.app,http://localhost:3000,http://localhost:5173
```

**Wichtig:** Ersetze `frontend-three-pi-61.vercel.app` mit deiner tatsächlichen Frontend-URL!

### Service neu starten:

Nach dem Setzen der Variable:
- Railway Dashboard → Service → Settings → Restart Service

---

## ✅ Lösung 3: Backend erreichbar prüfen

### Teste Backend:

Öffne im Browser:
```
https://cityraver.up.railway.app/docs
```

**Falls das nicht lädt:** Backend-Problem (siehe Railway Logs)

---

## 🔧 Schritt-für-Schritt Fix

### Schritt 1: Environment Variable setzen

**Vercel Dashboard:**
1. Gehe zu: https://vercel.com/dashboard
2. Öffne Projekt "frontend"
3. Settings → Environment Variables
4. Klicke auf "Add New"
5. Setze:
   - **Key:** `VITE_API_BASE_URL`
   - **Value:** `https://cityraver.up.railway.app`
   - **Environment:** Production, Preview, Development
6. Speichere

**Oder Vercel CLI:**
```bash
cd frontend
vercel env add VITE_API_BASE_URL production
# Eingabe: https://cityraver.up.railway.app
```

### Schritt 2: Redeploy Frontend

**Vercel Dashboard:**
- Deployments → Neuestes Deployment → Redeploy

**Oder Vercel CLI:**
```bash
cd frontend
vercel --prod
```

### Schritt 3: CORS im Backend setzen

**Railway Dashboard:**
1. Backend-Service → Settings → Variables
2. New Variable:
   ```
   ALLOWED_ORIGINS=https://frontend-three-pi-61.vercel.app,http://localhost:3000
   ```
3. Service neu starten

### Schritt 4: Testen

1. Öffne Frontend: `https://frontend-three-pi-61.vercel.app`
2. Öffne Browser-Konsole (F12)
3. Prüfe Network-Tab:
   - API-Calls sollten zu `https://cityraver.up.railway.app/api/...` gehen
   - Keine CORS-Fehler

---

## 🐛 Troubleshooting

### "Network Error" bleibt bestehen

**Prüfe Browser-Konsole (F12):**
- **Console Tab:** Welche Fehler?
- **Network Tab:** Welche Requests schlagen fehl?

### CORS-Fehler im Browser

**Problem:** `Access-Control-Allow-Origin` Fehler

**Lösung:**
1. Prüfe ob `ALLOWED_ORIGINS` im Backend gesetzt ist
2. Füge Frontend-URL hinzu (exakt, mit `https://`)
3. Backend-Service neu starten

### API-Calls gehen zu `/api` statt Railway-URL

**Problem:** `VITE_API_BASE_URL` nicht verwendet

**Lösung:**
1. Prüfe ob Variable beim Build gesetzt war
2. **Wichtig:** Redeploy nach Änderung der Environment Variable
3. Prüfe ob Variable in Production, Preview UND Development gesetzt ist

### Backend nicht erreichbar

**Problem:** `https://cityraver.up.railway.app/docs` lädt nicht

**Lösung:**
1. Prüfe Railway Logs (Backend-Service → Logs)
2. Prüfe ob Backend-Service läuft (grüner Status)
3. Prüfe Environment Variables im Backend

---

## ✅ Checkliste

- [ ] `VITE_API_BASE_URL` in Vercel gesetzt
- [ ] Frontend redeployed nach Environment Variable
- [ ] `ALLOWED_ORIGINS` im Backend gesetzt
- [ ] Backend-Service neu gestartet
- [ ] Backend erreichbar (`/docs` funktioniert)
- [ ] Browser-Konsole prüft (keine CORS-Fehler)
- [ ] Network-Tab prüft (API-Calls funktionieren)

---

## 🎯 Schnell-Fix (Alle Schritte)

### 1. Environment Variable setzen (Vercel)
```bash
cd frontend
vercel env add VITE_API_BASE_URL production
# Eingabe: https://cityraver.up.railway.app
vercel --prod
```

### 2. CORS setzen (Railway)
Railway Dashboard → Backend Service → Settings → Variables:
```
ALLOWED_ORIGINS=https://frontend-three-pi-61.vercel.app,http://localhost:3000
```

### 3. Backend neu starten
Railway Dashboard → Backend Service → Settings → Restart

### 4. Testen
Öffne Frontend und prüfe Browser-Konsole

---

## 📞 Hilfe

- **Vercel Dashboard:** https://vercel.com/dashboard
- **Railway Dashboard:** https://railway.app
- **Backend API:** https://cityraver.up.railway.app/docs

