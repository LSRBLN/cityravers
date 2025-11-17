# 🔧 Railway Backend-Service Fix

## ⚠️ Problem

Backend-Service "tele" ist fehlgeschlagen. Der Build-Command ist falsch!

**Aktuell (FALSCH):**
```
npm install && npm run build
```

**Das ist für Frontend, nicht für Backend!**

---

## ✅ Lösung: Start-Command statt Build-Command

### Backend braucht KEINEN Build-Command!

Das Backend ist Python/FastAPI - es braucht nur einen **Start-Command**.

---

## 🔧 Railway Settings korrigieren

### Schritt 1: Build-Command entfernen

**Railway Dashboard:**
1. Service "tele" → Settings → Build
2. **Custom Build Command:** LEER lassen (oder entfernen)
3. Speichern

### Schritt 2: Start-Command setzen

**Railway Dashboard:**
1. Service "tele" → Settings → Deploy
2. **Start Command:** Setze auf:
   ```
   uvicorn api:app --host 0.0.0.0 --port $PORT
   ```
3. Speichern

---

## 📋 Korrekte Konfiguration

### Backend-Service ("tele"):

**Build Command:**
```
(LEER - nicht nötig für Python)
```

**Start Command:**
```
uvicorn api:app --host 0.0.0.0 --port $PORT
```

**Root Directory:**
```
(LEER - Root-Verzeichnis)
```

---

## ✅ Alternative: railway.json verwenden

Die `railway.json` im Root-Verzeichnis sollte automatisch verwendet werden:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn api:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**Railway sollte das automatisch erkennen!**

---

## 🔍 Prüfen warum es fehlgeschlagen ist

### Railway Logs ansehen:

1. Service "tele" → Deployments
2. Klicke auf das fehlgeschlagene Deployment
3. Klicke auf "View Logs"
4. Prüfe die Fehlermeldung

**Wahrscheinliche Fehler:**
- Build-Command versucht `npm run build` (existiert nicht im Backend)
- Start-Command fehlt oder ist falsch

---

## 🚀 Schnell-Fix

### Option 1: Railway Dashboard

1. **Service "tele"** → **Settings** → **Deploy**
2. **Start Command:** `uvicorn api:app --host 0.0.0.0 --port $PORT`
3. **Settings** → **Build**
4. **Custom Build Command:** LEER lassen
5. **Speichern**
6. **Service neu starten** (Settings → Restart)

### Option 2: railway.json prüfen

Stelle sicher, dass `railway.json` im Root-Verzeichnis ist:
```bash
cat railway.json
```

Falls nicht vorhanden oder falsch, erstelle/aktualisiere es.

---

## ✅ Checkliste

- [ ] Build-Command entfernt (LEER)
- [ ] Start-Command gesetzt: `uvicorn api:app --host 0.0.0.0 --port $PORT`
- [ ] `railway.json` vorhanden und korrekt
- [ ] Service neu gestartet
- [ ] Deployment erfolgreich
- [ ] Backend erreichbar: `https://cityraver.up.railway.app/docs`

---

## 📝 Zusammenfassung

**Problem:** Build-Command `npm install && npm run build` ist für Frontend, nicht Backend!

**Lösung:**
1. ✅ Build-Command entfernen (LEER)
2. ✅ Start-Command setzen: `uvicorn api:app --host 0.0.0.0 --port $PORT`
3. ✅ Service neu starten

**Backend braucht KEINEN Build - nur Start-Command!**

