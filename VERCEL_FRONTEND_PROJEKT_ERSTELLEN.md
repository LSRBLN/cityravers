# 🚀 Vercel: Frontend-Projekt erstellen

## 🔍 Problem

**Aktuell:** Es gibt nur ein Projekt "tele" auf Vercel (für Backend).  
**Benötigt:** Ein separates Frontend-Projekt für das React/Vite Frontend.

---

## ✅ Lösung: Neues Frontend-Projekt erstellen

### Schritt 1: Neues Projekt hinzufügen

1. **Vercel Dashboard:** https://vercel.com/dashboard
2. Klicke auf **"Add New..."** Button (oben rechts)
3. Wähle **"Project"**

### Schritt 2: Repository auswählen

1. **Import Git Repository:**
   - Wähle: `phnxvision-pixel/tele` (dein Repository)
   - Oder: Suche nach deinem Repository

### Schritt 3: Projekt konfigurieren

**WICHTIG:** Diese Einstellungen sind kritisch!

**Project Name:**
```
frontend
```
(oder ein anderer Name wie "tele-frontend")

**Root Directory:**
```
frontend
```
✅ **SEHR WICHTIG!** Setze auf `frontend`

**Framework Preset:**
```
Vite
```
✅ Wähle "Vite" aus der Liste

**Build Command:**
```
npm run build
```
✅ Sollte automatisch erkannt werden

**Output Directory:**
```
dist
```
✅ Sollte automatisch erkannt werden

**Install Command:**
```
npm install
```
✅ Sollte automatisch erkannt werden

### Schritt 4: Environment Variables setzen

**Nach dem Erstellen des Projekts:**

1. Gehe zu **Settings → Environment Variables**
2. Füge hinzu:
   ```
   VITE_API_BASE_URL=https://cityraver.up.railway.app
   ```
3. Wähle **Production**, **Preview**, und **Development**
4. **Save**

### Schritt 5: Deploy

1. Klicke auf **"Deploy"**
2. Warte auf den Build
3. Prüfe Build Logs

---

## 🔧 Alternative: Bestehendes "tele" Projekt umkonfigurieren

**Falls du kein separates Frontend-Projekt willst:**

### Schritt 1: "tele" Projekt öffnen

1. Klicke auf das **"tele"** Projekt im Dashboard

### Schritt 2: Root Directory ändern

1. **Settings → General**
2. **Root Directory:** Setze auf `frontend`
3. **Save**

### Schritt 3: Build Settings anpassen

1. **Settings → Build and Development Settings**
2. **Framework Preset:** `Vite`
3. **Build Command:** `npm run build`
4. **Output Directory:** `dist`
5. **Save**

### Schritt 4: Environment Variables

1. **Settings → Environment Variables**
2. Füge hinzu: `VITE_API_BASE_URL=https://cityraver.up.railway.app`
3. **Save**

### Schritt 5: Redeploy

1. **Deployments → Redeploy**

---

## ⚠️ WICHTIG: Root vercel.json Problem

**Falls Root Directory auf `frontend` gesetzt ist:**

Vercel sollte automatisch `frontend/vercel.json` verwenden statt Root `vercel.json`.

**Falls nicht:**

1. Prüfe ob `.vercelignore` existiert
2. Stelle sicher, dass Root `vercel.json` ignoriert wird

---

## 📋 Checkliste

### Neues Frontend-Projekt:
- [ ] Projekt erstellt
- [ ] Root Directory = `frontend`
- [ ] Framework Preset = `Vite`
- [ ] Build Command = `npm run build`
- [ ] Output Directory = `dist`
- [ ] `VITE_API_BASE_URL` Environment Variable gesetzt
- [ ] Deploy erfolgreich

### Oder bestehendes Projekt:
- [ ] Root Directory auf `frontend` geändert
- [ ] Framework Preset = `Vite`
- [ ] Build Settings angepasst
- [ ] Environment Variables gesetzt
- [ ] Redeploy erfolgreich

---

## 🎯 Empfehlung

**Erstelle ein NEUES Frontend-Projekt!**

**Vorteile:**
- ✅ Klare Trennung: Backend ("tele") und Frontend ("frontend")
- ✅ Separate Deployments
- ✅ Einfacher zu verwalten
- ✅ Keine Konflikte mit Root `vercel.json`

**Nach dem Erstellen:**
- Backend bleibt auf Railway
- Frontend läuft auf Vercel
- Beide sind getrennt und funktionieren unabhängig

