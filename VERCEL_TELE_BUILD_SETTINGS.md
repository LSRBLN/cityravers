# 🔧 Vercel "tele" Projekt - Build Settings korrigieren

## ✅ Aktueller Status

**"tele" Projekt:**
- ✅ Root Directory = `frontend` (korrekt!)
- ❌ Build Settings müssen geprüft werden

---

## 🔧 Lösung: Build Settings im "tele" Projekt prüfen

### Schritt 1: Vercel Dashboard öffnen

1. Gehe zu: https://vercel.com/dashboard
2. Öffne das **"tele"** Projekt
3. Klicke auf **Settings**

### Schritt 2: Build and Development Settings prüfen

**Settings → Build and Development Settings:**

#### Install Command:
```
npm install
```
✅ **MUSS** so sein (explizit setzen, falls nicht)

#### Build Command:
```
npm run build
```
✅ **MUSS** so sein (explizit setzen, falls nicht)

#### Output Directory:
```
dist
```
✅ **MUSS** so sein (explizit setzen, falls nicht)

#### Framework Preset:
```
Vite
```
✅ **MUSS** so sein (aus Dropdown wählen)

### Schritt 3: Environment Variables prüfen

**Settings → Environment Variables:**

**Muss vorhanden sein:**
```
VITE_API_BASE_URL=https://cityraver.up.railway.app
```

**Falls nicht vorhanden:**
1. Klicke auf **"Add New"**
2. **Key:** `VITE_API_BASE_URL`
3. **Value:** `https://cityraver.up.railway.app`
4. Wähle: **Production**, **Preview**, **Development**
5. **Save**

### Schritt 4: Settings speichern

1. **WICHTIG:** Klicke auf **"Save"** (unten rechts)
2. Warte bis "Saved" erscheint

### Schritt 5: Redeploy

1. Gehe zu **Deployments**
2. Klicke auf **...** (drei Punkte) beim neuesten Deployment
3. Klicke auf **"Redeploy"**
4. Oder: Klicke auf **"Redeploy"** Button (oben rechts)

---

## 🔍 Warum der Fehler auftritt

**Vercel sucht nach:**
```
/vercel/path0/frontend/package.json
```

**Das bedeutet:**
- Root Directory ist auf `frontend` gesetzt ✅
- Aber Vercel klont das Repository und sucht dann nach `frontend/package.json` im geklonten Repo
- **Problem:** Wenn Root Directory = `frontend` ist, sollte Vercel nach `/vercel/path0/package.json` suchen (weil `frontend/` das Root wird)

**Mögliche Ursachen:**
1. Build Settings sind nicht korrekt
2. Vercel verwendet nicht die korrekten Commands
3. `npm install` schlägt fehl, bevor `package.json` gefunden wird

---

## ✅ Korrekte Konfiguration

### "tele" Projekt Settings:

**General:**
- Root Directory: `frontend` ✅

**Build and Development Settings:**
- Framework Preset: `Vite` ✅
- Build Command: `npm run build` ✅
- Install Command: `npm install` ✅
- Output Directory: `dist` ✅
- Development Command: `vite` (optional)

**Environment Variables:**
- `VITE_API_BASE_URL=https://cityraver.up.railway.app` ✅

---

## 📋 Checkliste

### Vercel Dashboard → "tele" Projekt:
- [ ] Root Directory = `frontend` ✅ (bereits gesetzt)
- [ ] Framework Preset = `Vite`
- [ ] Build Command = `npm run build` (explizit gesetzt)
- [ ] Install Command = `npm install` (explizit gesetzt)
- [ ] Output Directory = `dist` (explizit gesetzt)
- [ ] `VITE_API_BASE_URL` Environment Variable gesetzt
- [ ] Settings gespeichert
- [ ] Redeploy gestartet

---

## 🎯 Nach dem Fix

**Vercel sollte zeigen:**
- ✅ `npm install` erfolgreich
- ✅ `package.json` gefunden
- ✅ `npm run build` erfolgreich
- ✅ Build erfolgreich
- ✅ Deployment Ready

**Teste:**
- Öffne Frontend-URL (von "tele" Projekt)
- Prüfe Browser-Konsole (F12)
- Versuche Login

---

## 🔧 Falls es weiterhin nicht funktioniert

### Option 1: Root Directory temporär entfernen

**Test:**
1. **Settings → General**
2. **Root Directory:** LEER lassen
3. **Build Command:** `cd frontend && npm install && npm run build`
4. **Output Directory:** `frontend/dist`
5. **Save & Redeploy**

### Option 2: Neues Frontend-Projekt erstellen

**Falls "tele" Projekt weiterhin Probleme hat:**

1. **Vercel Dashboard → "Add New..." → "Project"**
2. **Repository:** `phnxvision-pixel/tele`
3. **Project Name:** `frontend`
4. **Root Directory:** `frontend`
5. **Framework Preset:** `Vite`
6. **Deploy**

---

## ✅ Zusammenfassung

**"tele" Projekt ist bereits korrekt konfiguriert:**
- ✅ Root Directory = `frontend`

**Was noch zu tun ist:**
- ✅ Build Settings explizit setzen
- ✅ Environment Variables prüfen
- ✅ Redeploy

**Dann sollte alles funktionieren!**

