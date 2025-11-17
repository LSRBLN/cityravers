# 🚨 Vercel Error: vite: command not found

## ❌ Fehler

```
sh: line 1: vite: command not found
Error: Command "vite build" exited with 127
```

**Problem:** Vercel versucht `vite build` direkt auszuführen, aber `vite` ist nicht installiert oder nicht im PATH.

---

## 🔍 Ursache

**Vercel führt aus:**
```bash
vite build  # ❌ Falsch! vite ist nicht im PATH
```

**Sollte sein:**
```bash
npm run build  # ✅ Richtig! Verwendet npm script
```

**Warum passiert das?**
1. Vercel erkennt Vite automatisch
2. Vercel versucht dann `vite build` direkt auszuführen
3. Aber `vite` ist in `devDependencies` und nicht global installiert
4. `npm install` muss zuerst erfolgreich sein

---

## ✅ Lösung 1: Build Command explizit setzen

### Vercel Dashboard:

1. **Settings → Build and Development Settings**
2. **Build Command:** Setze explizit auf:
   ```
   npm run build
   ```
3. **WICHTIG:** Aktiviere "Override" (falls vorhanden)
4. **Save**

### Prüfe auch:

**Install Command:**
```
npm install
```
✅ Sollte so sein

**Output Directory:**
```
dist
```
✅ Sollte so sein

---

## ✅ Lösung 2: Prüfe ob npm install erfolgreich war

**Vercel Build Logs prüfen:**

1. **Vercel Dashboard → Deployments**
2. Klicke auf fehlgeschlagenes Deployment
3. Klicke auf **Build Logs**
4. Suche nach:
   - `npm install`
   - Fehlermeldungen während Installation
   - `vite` wird installiert?

**Falls `npm install` fehlschlägt:**
- Prüfe ob `package.json` im richtigen Verzeichnis ist
- Prüfe ob Root Directory korrekt ist (`frontend`)

---

## ✅ Lösung 3: frontend/vercel.json prüfen

**Aktuelle `frontend/vercel.json`:**
```json
{
  "buildCommand": "npm run build",  // ✅ Korrekt!
  "outputDirectory": "dist",
  "framework": "vite"
}
```

**Problem:** Vercel ignoriert möglicherweise `buildCommand` aus `vercel.json`.

**Lösung:** Setze Build Command im Vercel Dashboard (siehe Lösung 1)

---

## ✅ Lösung 4: Root Directory prüfen

**Vercel Dashboard → Settings → General:**

**Root Directory:**
```
frontend
```
✅ **MUSS** auf `frontend` gesetzt sein!

**Falls nicht:**
1. Setze auf `frontend`
2. **Save**
3. **Redeploy**

---

## 🔧 Schnell-Fix (5 Minuten)

### Schritt 1: Vercel Dashboard

1. **Frontend-Projekt öffnen**
2. **Settings → Build and Development Settings**
3. **Build Command:** `npm run build` (explizit setzen)
4. **Install Command:** `npm install` (prüfen)
5. **Save**

### Schritt 2: Root Directory prüfen

1. **Settings → General**
2. **Root Directory:** `frontend` (muss gesetzt sein!)
3. **Save**

### Schritt 3: Redeploy

1. **Deployments → Neuestes Deployment**
2. **Redeploy**

---

## 📋 Checkliste

### Vercel Dashboard:
- [ ] Root Directory = `frontend`
- [ ] Build Command = `npm run build` (explizit gesetzt)
- [ ] Install Command = `npm install`
- [ ] Output Directory = `dist`
- [ ] Framework Preset = `Vite`
- [ ] Settings gespeichert

### Build Logs prüfen:
- [ ] `npm install` erfolgreich?
- [ ] `vite` wird installiert?
- [ ] `npm run build` wird ausgeführt? (nicht `vite build`)

---

## 🎯 Warum `npm run build` statt `vite build`?

**`vite build`:**
- ❌ Versucht `vite` direkt auszuführen
- ❌ `vite` muss im PATH sein
- ❌ Funktioniert nur wenn global installiert

**`npm run build`:**
- ✅ Verwendet npm script aus `package.json`
- ✅ Läuft `vite build` über `node_modules/.bin/vite`
- ✅ Funktioniert nach `npm install`

**`package.json`:**
```json
{
  "scripts": {
    "build": "vite build"  // ✅ Wird von npm ausgeführt
  }
}
```

---

## ✅ Nach dem Fix

**Vercel sollte zeigen:**
- ✅ `npm install` erfolgreich
- ✅ `npm run build` wird ausgeführt
- ✅ Build erfolgreich
- ✅ Deployment Ready

