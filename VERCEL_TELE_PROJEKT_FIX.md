# 🔧 Vercel "tele" Projekt - Root Directory Problem

## 🔍 Problem

**Aktuell:**
- Es gibt nur **ein Projekt "tele"** auf Vercel
- Root Directory ist auf **`frontend`** gesetzt
- Das Projekt versucht Frontend zu deployen, aber es ist wahrscheinlich für Backend gedacht

---

## ✅ Lösung: Zwei Optionen

### Option 1: "tele" Projekt für Frontend verwenden (Empfohlen)

**Falls "tele" das Frontend-Projekt sein soll:**

#### Schritt 1: Root Directory prüfen

1. **Vercel Dashboard → "tele" Projekt**
2. **Settings → General**
3. **Root Directory:** Sollte `frontend` sein ✅

#### Schritt 2: Build Settings prüfen

**Settings → Build and Development Settings:**

- **Framework Preset:** `Vite` ✅
- **Build Command:** `npm run build` ✅
- **Output Directory:** `dist` ✅
- **Install Command:** `npm install` ✅

#### Schritt 3: Environment Variables

**Settings → Environment Variables:**

Füge hinzu (falls nicht vorhanden):
```
VITE_API_BASE_URL=https://cityraver.up.railway.app
```

#### Schritt 4: Redeploy

1. **Deployments → Redeploy**

**Dann sollte "tele" das Frontend deployen!**

---

### Option 2: Neues Frontend-Projekt erstellen

**Falls "tele" das Backend-Projekt bleiben soll:**

#### Schritt 1: "tele" Projekt Root Directory entfernen

1. **Vercel Dashboard → "tele" Projekt**
2. **Settings → General**
3. **Root Directory:** LEER lassen (oder entfernen)
4. **Save**

**Dann ist "tele" wieder Backend-Projekt (falls auf Vercel deployed werden soll)**

#### Schritt 2: Neues Frontend-Projekt erstellen

1. **Vercel Dashboard → "Add New..." → "Project"**
2. **Repository:** `phnxvision-pixel/tele`
3. **Project Name:** `frontend` (oder `tele-frontend`)
4. **Root Directory:** `frontend` ✅
5. **Framework Preset:** `Vite`
6. **Deploy**

**Dann hast du:**
- **"tele"** → Backend (falls auf Vercel)
- **"frontend"** → Frontend ✅

---

## 🎯 Empfehlung: Option 1

**Da Backend bereits auf Railway läuft:**

**"tele" Projekt sollte Frontend deployen:**

1. ✅ Root Directory = `frontend` (bereits gesetzt)
2. ✅ Build Settings prüfen und korrigieren
3. ✅ Environment Variables setzen
4. ✅ Redeploy

**Vorteile:**
- ✅ Kein neues Projekt nötig
- ✅ Einfacher zu verwalten
- ✅ Backend bleibt auf Railway

---

## 🔧 Schnell-Fix für "tele" Projekt

### Schritt 1: Build Settings prüfen

**Vercel Dashboard → "tele" Projekt:**

1. **Settings → Build and Development Settings**
2. **Build Command:** `npm run build` (explizit setzen)
3. **Install Command:** `npm install` (prüfen)
4. **Output Directory:** `dist`
5. **Framework Preset:** `Vite`
6. **Save**

### Schritt 2: Environment Variables

1. **Settings → Environment Variables**
2. Füge hinzu:
   ```
   VITE_API_BASE_URL=https://cityraver.up.railway.app
   ```
3. **Save**

### Schritt 3: Redeploy

1. **Deployments → Redeploy**

---

## 📋 Checkliste

### "tele" Projekt (als Frontend):
- [ ] Root Directory = `frontend` ✅ (bereits gesetzt)
- [ ] Build Command = `npm run build`
- [ ] Install Command = `npm install`
- [ ] Output Directory = `dist`
- [ ] Framework Preset = `Vite`
- [ ] `VITE_API_BASE_URL` Environment Variable gesetzt
- [ ] Settings gespeichert
- [ ] Redeploy erfolgreich

---

## ✅ Nach dem Fix

**"tele" Projekt sollte:**
- ✅ Frontend erfolgreich deployen
- ✅ `npm install` erfolgreich
- ✅ `npm run build` erfolgreich
- ✅ Frontend-URL funktioniert

**Backend:**
- ✅ Läuft weiterhin auf Railway
- ✅ URL: `https://cityraver.up.railway.app`

---

## 🎯 Zusammenfassung

**Aktuell:**
- "tele" Projekt hat Root Directory = `frontend` ✅
- Aber Build Settings müssen korrekt sein

**Lösung:**
- Build Settings prüfen und korrigieren
- Environment Variables setzen
- Redeploy

**Dann funktioniert "tele" als Frontend-Projekt!**

