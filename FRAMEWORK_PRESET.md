# 🎯 Framework Preset - Vite

## ✅ Für dein Frontend

### Framework Preset:
```
Vite
```

**Oder:**
```
Other
```

---

## 📋 Framework Presets für verschiedene Plattformen

### Vercel

**Framework Preset:**
- ✅ **Vite** (wird automatisch erkannt)
- Oder: **Other**

**Vercel erkennt automatisch:**
- `vite.config.js` vorhanden
- `package.json` mit `vite` Dependency
- Setzt automatisch auf **Vite**

**Manuelle Einstellungen (falls nötig):**
- **Build Command:** `npm run build`
- **Output Directory:** `dist`
- **Install Command:** `npm install`

---

### Netlify

**Framework Preset:**
- ✅ **Vite** (wird automatisch erkannt)
- Oder: **Other**

**Netlify erkennt automatisch:**
- `vite.config.js` vorhanden
- `package.json` mit `vite` Dependency

**Manuelle Einstellungen:**
- **Base directory:** `frontend`
- **Build command:** `npm install && npm run build`
- **Publish directory:** `frontend/dist`

---

### Railway

**Framework Preset:**
- ✅ **NIXPACKS** (automatisch)
- Erkennt Node.js und baut automatisch

**Manuelle Einstellungen:**
- **Root Directory:** `frontend`
- **Build Command:** `npm install && npm run build`
- **Start Command:** `npx serve -s dist -l $PORT`

---

## 🎯 Zusammenfassung

### Vercel:
```
Framework Preset: Vite (automatisch erkannt)
```

### Netlify:
```
Framework Preset: Vite (automatisch erkannt)
```

### Railway:
```
Framework Preset: NIXPACKS (automatisch)
```

---

## ✅ Empfehlung

**Für alle Plattformen:**
- ✅ **Vite** wählen (oder automatisch erkennen lassen)
- ✅ Oder **Other** falls Vite nicht verfügbar

**Wichtig:** Die Build-Einstellungen sind wichtiger als das Preset!

---

## 📝 Build-Einstellungen (wichtig!)

### Vercel:
```
Build Command: npm run build
Output Directory: dist
```

### Netlify:
```
Build Command: npm install && npm run build
Publish Directory: frontend/dist
```

### Railway:
```
Build Command: npm install && npm run build
Start Command: npx serve -s dist -l $PORT
```

---

## 🔍 Prüfen ob Vite erkannt wird

**Vercel/Netlify erkennen automatisch:**
- ✅ `vite.config.js` vorhanden
- ✅ `package.json` mit `"vite"` Dependency
- ✅ `"build": "vite build"` in package.json scripts

**Falls nicht erkannt:**
- Wähle **"Other"** oder **"Static Site"**
- Setze Build-Einstellungen manuell

---

## 📞 Hilfe

- **Vite Docs:** https://vitejs.dev
- **Vercel Docs:** https://vercel.com/docs
- **Netlify Docs:** https://docs.netlify.com

