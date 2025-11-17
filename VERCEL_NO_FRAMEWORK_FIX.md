# ⚠️ Vercel "No framework detected" - Fix

## ⚠️ Problem

**Vercel zeigt:** "No framework detected"

**Das bedeutet:** Vercel erkennt das Framework (Vite) nicht automatisch.

---

## 🔍 Mögliche Ursachen

### 1. **Falsches Projekt**
- Du siehst das **Backend-Projekt "tele"** statt Frontend-Projekt
- Backend hat kein Framework (Python/FastAPI)

### 2. **Root Directory nicht gesetzt**
- Frontend-Projekt verwendet Root-Verzeichnis statt `frontend/`
- `frontend/vercel.json` wird nicht erkannt

### 3. **vercel.json nicht erkannt**
- `frontend/vercel.json` wird nicht verwendet
- Root `vercel.json` wird verwendet (für Backend)

---

## ✅ Lösung

### Schritt 1: Prüfe welches Projekt

**Vercel Dashboard:**
- **Projekt "tele":** Backend-Projekt (Python) - "No framework" ist normal
- **Projekt "frontend":** Frontend-Projekt (Vite) - sollte Framework erkennen

### Schritt 2: Frontend-Projekt prüfen

**Falls du im Frontend-Projekt bist:**

1. **Settings → General:**
   - **Root Directory:** Sollte `frontend` sein
   - Falls nicht: Setze auf `frontend` und speichere

2. **Settings → Build and Deployment:**
   - **Framework Preset:** Sollte `Vite` sein
   - Falls nicht: Setze auf `Vite`

3. **Redeploy:**
   - Deployments → Redeploy

### Schritt 3: Root Directory setzen (wichtig!)

**Vercel Dashboard → Frontend-Projekt:**
1. Settings → General
2. **Root Directory:** Setze auf `frontend`
3. **Save**
4. **Redeploy**

**Dann verwendet Vercel:**
- ✅ `frontend/vercel.json`
- ✅ `frontend/package.json`
- ✅ Erkennt Vite automatisch

---

## 📋 Korrekte Konfiguration

### Frontend-Projekt:

**Root Directory:**
```
frontend
```

**Framework Preset:**
```
Vite
```

**Build Command:**
```
npm run build
```

**Output Directory:**
```
dist
```

**vercel.json:**
- Verwendet `frontend/vercel.json` (nicht Root)

---

## 🎯 Schnell-Fix

### Falls Frontend-Projekt:

1. **Vercel Dashboard → Frontend-Projekt**
2. **Settings → General**
3. **Root Directory:** `frontend`
4. **Save**
5. **Settings → Build and Deployment**
6. **Framework Preset:** `Vite`
7. **Save**
8. **Deployments → Redeploy**

### Falls Backend-Projekt ("tele"):

**"No framework detected" ist normal!**
- Backend ist Python/FastAPI
- Braucht kein Framework-Preset
- Verwendet `vercel.json` mit `@vercel/python`

---

## ✅ Checkliste

### Frontend-Projekt:
- [ ] Root Directory auf `frontend` gesetzt
- [ ] Framework Preset auf `Vite` gesetzt
- [ ] `frontend/vercel.json` vorhanden
- [ ] Redeploy durchgeführt
- [ ] Framework erkannt?

### Backend-Projekt ("tele"):
- [x] "No framework detected" ist normal ✅
- [ ] `vercel.json` mit `@vercel/python` vorhanden
- [ ] Environment Variables gesetzt

---

## 🔍 Welches Projekt siehst du?

**Prüfe die URL:**
- `vercel.com/.../tele/...` → Backend-Projekt (Python)
- `vercel.com/.../frontend/...` → Frontend-Projekt (Vite)

**Backend-Projekt:**
- "No framework detected" ist **normal**
- Python braucht kein Framework-Preset

**Frontend-Projekt:**
- Sollte Vite erkennen
- Root Directory muss `frontend` sein

---

## 📝 Zusammenfassung

**Falls Frontend-Projekt:**
1. ✅ Root Directory auf `frontend` setzen
2. ✅ Framework Preset auf `Vite` setzen
3. ✅ Redeploy

**Falls Backend-Projekt:**
- ✅ "No framework detected" ist normal (Python)

**Welches Projekt siehst du in der URL?**

