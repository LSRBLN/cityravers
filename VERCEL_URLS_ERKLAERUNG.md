# 🔗 Vercel URLs - Warum 2 verschiedene Adressen?

## 📋 Die zwei URL-Typen

### 1. Deployment-URL (temporär, für jeden Build)
```
tele-xdp3o5kwg-phnxvisioins-projects.vercel.app
```

**Eigenschaften:**
- ✅ Wird für **jeden neuen Build** erstellt
- ✅ Eindeutig für jedes Deployment
- ✅ Bleibt bestehen (wird nicht gelöscht)
- ✅ Nützlich für: Testing, Preview, Rollback

**Beispiel:**
- Build #1: `tele-abc123-...vercel.app`
- Build #2: `tele-xyz789-...vercel.app`
- Build #3: `tele-xdp3o5kwg-...vercel.app` (aktuell)

### 2. Production-Domain (permanent, Haupt-URL)
```
tele-sandy.vercel.app
```

**Eigenschaften:**
- ✅ **Immer gleich** (bleibt konstant)
- ✅ Zeigt auf **neuestes Production-Deployment**
- ✅ Automatisch aktualisiert bei neuem Deployment
- ✅ Nützlich für: Haupt-URL, Bookmarks, Links

---

## 🎯 Wie funktioniert das?

**Bei jedem neuen Deployment:**

1. **Vercel erstellt neue Deployment-URL:**
   - `tele-xyz123-...vercel.app` (eindeutig für diesen Build)

2. **Production-Domain zeigt auf neues Deployment:**
   - `tele-sandy.vercel.app` → zeigt jetzt auf neues Deployment

3. **Alte Deployment-URLs bleiben bestehen:**
   - Alte Builds sind weiterhin erreichbar
   - Nützlich für Rollback oder Vergleich

---

## ✅ Welche URL solltest du verwenden?

### Für normale Nutzer:
```
https://tele-sandy.vercel.app
```
✅ **Diese URL verwenden!**
- Bleibt immer gleich
- Zeigt immer neuestes Deployment
- Einfach zu merken

### Für Testing/Development:
```
https://tele-xdp3o5kwg-phnxvisioins-projects.vercel.app
```
✅ **Diese URL für spezifisches Deployment**
- Teste bestimmten Build
- Vergleiche verschiedene Builds
- Preview vor Production

---

## 🔧 Custom Domain (optional)

**Falls du eine eigene Domain willst:**

1. **Vercel Dashboard → "tele" Projekt**
2. **Settings → Domains**
3. Füge deine Domain hinzu (z.B. `telegram-tool.com`)
4. Konfiguriere DNS-Einträge

**Dann hast du:**
- ✅ `tele-sandy.vercel.app` (Vercel-Domain)
- ✅ `telegram-tool.com` (Custom Domain)
- ✅ Beide zeigen auf dasselbe Deployment

---

## 📋 Zusammenfassung

**Warum 2 URLs?**

1. **Deployment-URL:**
   - Eindeutig für jeden Build
   - Für Testing/Preview
   - Bleibt bestehen

2. **Production-Domain:**
   - Immer gleich
   - Zeigt auf neuestes Deployment
   - Für normale Nutzer

**Beide funktionieren gleich!**
- ✅ Beide zeigen auf dasselbe Frontend
- ✅ Beide verwenden dieselben Environment Variables
- ✅ Beide kommunizieren mit Railway-Backend

**Verwende:**
- `tele-sandy.vercel.app` für normale Nutzung ✅

---

## 🎯 Für dein Setup

**Frontend-URLs:**
- Haupt-URL: `https://tele-sandy.vercel.app` ✅
- Deployment-URL: `https://tele-xdp3o5kwg-...vercel.app` (für Testing)

**Backend-URL:**
- `https://cityraver.up.railway.app` ✅

**Environment Variable:**
- `VITE_API_BASE_URL=https://cityraver.up.railway.app/api` ✅

**Beide Frontend-URLs funktionieren gleich!**

