# 🔧 Railway "tele" Service - Konfiguration

## ⚠️ Status

**Service "tele":**
- Status: "Edited" mit "1 Change"
- Watch Paths: `/api/**` und `/frontend/**` (FALSCH für Backend!)

---

## ❌ Problem: Watch Paths sind falsch

**Aktuell (FALSCH):**
- `/api/**`
- `/frontend/**`

**Das sind Frontend-Pfade, nicht Backend!**

### Backend sollte überwachen:
- Python-Dateien: `*.py`
- Requirements: `requirements.txt`
- Config: `railway.json`, `Procfile`

---

## ✅ Lösung: Watch Paths korrigieren

### Option 1: Watch Paths entfernen (Empfohlen)

**Für Backend:**
- Watch Paths sind optional
- Railway deployed automatisch bei Git-Push
- Watch Paths nur nötig für selektive Deployments

**Lösung:**
1. Entferne die Watch Paths:
   - Klicke auf das X bei `/api/**`
   - Klicke auf das X bei `/frontend/**`
2. Oder: Lasse sie leer

### Option 2: Korrekte Watch Paths setzen

**Falls du Watch Paths behalten willst:**

**Für Backend (Python):**
```
*.py
requirements.txt
railway.json
Procfile
```

**Oder spezifischer:**
```
/api.py
/account_manager.py
/database.py
/requirements.txt
/railway.json
```

---

## 🔧 Build-Command prüfen

**Backend braucht KEINEN Build-Command!**

1. **Klicke auf "+ Build Command"** (falls noch nicht gesetzt)
2. **Lasse es LEER** (oder entferne es)
3. **Backend ist Python - kein Build nötig!**

---

## ✅ Start-Command prüfen

**Backend braucht Start-Command:**

1. **Settings → Deploy**
2. **Start Command:** Sollte sein:
   ```
   uvicorn api:app --host 0.0.0.0 --port $PORT
   ```
3. Falls nicht gesetzt, hinzufügen

---

## 🚀 Änderungen anwenden

**Wichtig:** Du siehst "1 Change" - die Änderungen müssen deployed werden!

1. **Klicke auf "Apply 1 change"** (oben links, lila Button)
2. **Oder:** Klicke auf "Deploy ↑+Enter"
3. **Warte bis Deployment fertig ist**

---

## 📋 Korrekte Konfiguration für Backend

### Watch Paths:
```
(LEER - nicht nötig)
```
Oder:
```
*.py
requirements.txt
```

### Build Command:
```
(LEER - nicht nötig für Python)
```

### Start Command:
```
uvicorn api:app --host 0.0.0.0 --port $PORT
```

### Root Directory:
```
(LEER - Root-Verzeichnis)
```

---

## ✅ Checkliste

- [ ] Watch Paths entfernt oder korrigiert
- [ ] Build Command entfernt (LEER)
- [ ] Start Command gesetzt: `uvicorn api:app --host 0.0.0.0 --port $PORT`
- [ ] Änderungen angewendet ("Apply 1 change")
- [ ] Deployment erfolgreich
- [ ] Backend erreichbar: `https://cityraver.up.railway.app/docs`

---

## 🎯 Schnell-Fix

### Schritt 1: Watch Paths entfernen
1. Klicke auf X bei `/api/**`
2. Klicke auf X bei `/frontend/**`

### Schritt 2: Build Command prüfen
1. Prüfe ob Build Command gesetzt ist
2. Falls ja, entferne es (LEER lassen)

### Schritt 3: Start Command prüfen
1. Settings → Deploy
2. Start Command: `uvicorn api:app --host 0.0.0.0 --port $PORT`

### Schritt 4: Änderungen anwenden
1. Klicke auf "Apply 1 change"
2. Warte auf Deployment

---

## 📝 Zusammenfassung

**Problem:**
- Watch Paths sind für Frontend, nicht Backend
- Build Command sollte nicht gesetzt sein

**Lösung:**
1. ✅ Watch Paths entfernen oder korrigieren
2. ✅ Build Command entfernen (LEER)
3. ✅ Start Command prüfen
4. ✅ Änderungen anwenden

**Backend braucht keine Watch Paths für Frontend-Pfade!**

