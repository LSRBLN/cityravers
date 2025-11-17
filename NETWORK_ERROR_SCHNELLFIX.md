# ⚡ Network Error - Schnell-Fix

## ✅ Status-Check

- ✅ Frontend lädt: `https://frontend-three-pi-61.vercel.app`
- ✅ `VITE_API_BASE_URL` ist gesetzt
- ✅ Backend erreichbar: `https://cityraver.up.railway.app`
- ⚠️ **Problem:** Frontend wurde nicht nach Environment Variable neu gebaut

---

## 🔧 Lösung: 2 Schritte

### Schritt 1: Frontend redeployen (WICHTIG!)

**Environment Variable wurde gesetzt, aber Frontend muss neu gebaut werden!**

**Vercel CLI:**
```bash
cd frontend
vercel --prod
```

**Oder Vercel Dashboard:**
1. Gehe zu: https://vercel.com/dashboard
2. Öffne Projekt "frontend"
3. Deployments → Neuestes Deployment
4. Klicke auf **"Redeploy"**

### Schritt 2: CORS im Backend setzen

**Railway Dashboard:**
1. Gehe zu deinem **Backend-Service** (cityraver)
2. Settings → Variables → New Variable:

```bash
ALLOWED_ORIGINS=https://frontend-three-pi-61.vercel.app,http://localhost:3000,http://localhost:5173
```

3. **Service neu starten:**
   - Settings → Restart Service

---

## ✅ Nach dem Fix

1. **Warte 1-2 Minuten** (Redeploy läuft)
2. **Öffne Frontend:** `https://frontend-three-pi-61.vercel.app`
3. **Prüfe Browser-Konsole (F12):**
   - Keine "Network Error" mehr
   - API-Calls gehen zu `https://cityraver.up.railway.app/api/...`
   - Keine CORS-Fehler

---

## 🎯 Zusammenfassung

**Problem:** Environment Variable wurde gesetzt, aber Frontend wurde nicht neu gebaut.

**Lösung:**
1. ✅ Frontend redeployen (`vercel --prod`)
2. ✅ CORS im Backend setzen (`ALLOWED_ORIGINS`)
3. ✅ Backend neu starten
4. ✅ Testen

**Fertig in 2 Minuten!**

