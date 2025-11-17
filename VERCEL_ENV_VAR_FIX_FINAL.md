# 🚨 Vercel: Network Error vs 404 - Finale Lösung

## ❌ Problem

**URL 1:** Network Error (CORS oder Backend nicht erreichbar)  
**URL 2:** 404 Not Found (falsche API-URL)

**Ursache:** `VITE_API_BASE_URL` ist nicht in Vercel gesetzt oder falsch konfiguriert.

---

## ✅ Lösung: VITE_API_BASE_URL in Vercel setzen

### Schritt 1: Vercel Dashboard öffnen

1. Gehe zu: https://vercel.com/dashboard
2. Öffne das **"tele"** Projekt
3. Klicke auf **Settings**

### Schritt 2: Environment Variables prüfen

1. **Settings → Environment Variables**
2. Suche nach `VITE_API_BASE_URL`

**Falls NICHT vorhanden:**
- Klicke auf **"Add New"**
- Weiter zu Schritt 3

**Falls vorhanden:**
- Klicke auf `VITE_API_BASE_URL`
- Prüfe den Value
- Weiter zu Schritt 3

### Schritt 3: Variable setzen/korrigieren

**Key:**
```
VITE_API_BASE_URL
```

**Value:**
```
https://cityraver.up.railway.app/api
```

**WICHTIG:**
- ✅ Muss mit `https://` beginnen
- ✅ Muss `/api` am Ende haben
- ✅ Kein abschließender Slash nach `/api`

**Environments:**
- ✅ **Production** (für Live-Site)
- ✅ **Preview** (für Preview-Builds)
- ✅ **Development** (optional, für lokale Entwicklung)

### Schritt 4: Save

1. Klicke auf **"Save"** (unten rechts)
2. Warte bis "Saved" erscheint

### Schritt 5: Redeploy ALLE Deployments

**WICHTIG:** Nach dem Setzen der Variable müssen ALLE Deployments neu gebaut werden!

**Option A: Automatisch (bei Git Push):**
```bash
# Mache eine kleine Änderung und pushe
git commit --allow-empty -m "Trigger Vercel redeploy"
git push
```

**Option B: Manuell im Dashboard:**

1. **Deployments** Tab
2. Für **jedes Deployment:**
   - Klicke auf **"..."** (drei Punkte)
   - Klicke auf **"Redeploy"**

**Oder:** Warte auf automatisches Deployment bei nächstem Git Push

---

## 🔍 Prüfen ob Variable gesetzt ist

### Im Browser (nach Redeploy):

1. Öffne Frontend-URL: `https://tele-sandy.vercel.app`
2. Öffne Browser DevTools (F12)
3. Gehe zu **Console** Tab
4. Tippe:
```javascript
console.log(import.meta.env.VITE_API_BASE_URL)
```

**Sollte zeigen:**
```
https://cityraver.up.railway.app/api
```

**Falls `undefined`:**
- Variable ist nicht gesetzt
- Oder: Build wurde nicht neu gestartet
- Oder: Variable ist für falsches Environment gesetzt

---

## 🔧 Warum beide URLs unterschiedliche Fehler?

**Deployment-URL (`tele-xdp3o5kwg-...`):**
- Möglicherweise älteres Deployment
- Variable wurde nicht beim Build eingebettet
- → Network Error (versucht `/api` relativ)

**Production-Domain (`tele-sandy.vercel.app`):**
- Neueres Deployment
- Variable wurde beim Build eingebettet, aber falsch
- → 404 (geht zu `/auth/login` statt `/api/auth/login`)

**Lösung:** Beide Deployments müssen mit korrekter Variable neu gebaut werden!

---

## 📋 Checkliste

### Vercel:
- [ ] `VITE_API_BASE_URL` Environment Variable vorhanden
- [ ] Value = `https://cityraver.up.railway.app/api` (mit `/api`!)
- [ ] Scopes: Production, Preview, Development
- [ ] Variable gespeichert
- [ ] Alle Deployments neu deployed

### Test:
- [ ] Browser Console: `import.meta.env.VITE_API_BASE_URL` zeigt korrekte URL
- [ ] Network Tab: Request geht zu `/api/auth/login`
- [ ] Beide URLs funktionieren gleich
- [ ] Keine 404-Fehler mehr
- [ ] Keine Network Errors mehr

---

## 🎯 Nach dem Fix

**Beide URLs sollten:**
- ✅ Gleiche Environment Variables verwenden
- ✅ Zu `/api/auth/login` gehen
- ✅ Keine Fehler mehr zeigen
- ✅ Login funktioniert

**Verwende:**
- `https://tele-sandy.vercel.app` für normale Nutzung ✅

---

## 🔧 Schnell-Fix

1. **Vercel Dashboard → "tele" Projekt**
2. **Settings → Environment Variables**
3. **`VITE_API_BASE_URL` = `https://cityraver.up.railway.app/api`**
4. **Save**
5. **Deployments → Redeploy** (alle)

**Dann sollten beide URLs funktionieren!**

