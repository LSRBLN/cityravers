# ✅ Vercel: VITE_API_BASE_URL setzen - Schritt für Schritt

## 📋 Was du siehst

**Vercel zeigt Dokumentation über System-Umgebungsvariablen:**
- `VERCEL=1` (automatisch von Vercel)
- `VERCEL_URL` (automatisch von Vercel)
- etc.

**Das ist NICHT relevant für unser Problem!** ❌

Wir brauchen eine **benutzerdefinierte Variable**, nicht eine System-Variable.

---

## ✅ Lösung: Benutzerdefinierte Variable setzen

### Schritt 1: Vercel Dashboard öffnen

1. Gehe zu: https://vercel.com/dashboard
2. Öffne das **"tele"** Projekt
3. Klicke auf **Settings**

### Schritt 2: Environment Variables öffnen

1. **Settings → Environment Variables** (linke Sidebar)
2. Du siehst eine Liste von Variablen (oder "No environment variables")

### Schritt 3: Variable hinzufügen/korrigieren

**Falls `VITE_API_BASE_URL` NICHT vorhanden ist:**

1. Klicke auf **"Add New"** (oben rechts)
2. **Key:** `VITE_API_BASE_URL`
3. **Value:** `https://cityraver.up.railway.app/api`
   - ✅ Mit `https://` am Anfang
   - ✅ Mit `/api` am Ende
   - ✅ Kein abschließender Slash nach `/api`
4. **Environments:** Wähle alle aus:
   - ✅ **Production** (für Live-Site)
   - ✅ **Preview** (für Preview-Builds)
   - ✅ **Development** (optional, für lokale Entwicklung)
5. Klicke auf **"Save"**

**Falls `VITE_API_BASE_URL` bereits vorhanden ist:**

1. Klicke auf `VITE_API_BASE_URL` in der Liste
2. Prüfe den **Value**
3. **Sollte sein:** `https://cityraver.up.railway.app/api`
4. **Falls falsch:** Korrigiere und **Save**

### Schritt 4: System-Umgebungsvariablen (optional)

**"Automatically expose System Environment Variables" Checkbox:**
- ✅ **NICHT nötig** für unser Problem
- ✅ Kann aktiviert bleiben (schadet nicht)
- ✅ Oder deaktiviert lassen (funktioniert auch)

**Wichtig:** Diese Einstellung betrifft nur Vercel-System-Variablen (`VERCEL`, `VERCEL_URL`, etc.), nicht unsere benutzerdefinierte Variable!

---

## 🔍 Unterschied: System vs. Benutzerdefinierte Variablen

### System-Umgebungsvariablen (von Vercel):
- ✅ Automatisch von Vercel gesetzt
- ✅ Beispiele: `VERCEL=1`, `VERCEL_URL`, `VERCEL_ENV`
- ✅ Nicht relevant für unser Problem

### Benutzerdefinierte Variablen (von uns):
- ✅ Wir müssen sie manuell setzen
- ✅ Beispiel: `VITE_API_BASE_URL`
- ✅ **Das ist was wir brauchen!**

---

## 📋 Checkliste

### Vercel Dashboard:
- [ ] Settings → Environment Variables geöffnet
- [ ] `VITE_API_BASE_URL` vorhanden
- [ ] Value = `https://cityraver.up.railway.app/api` (mit `/api`!)
- [ ] Environments: Production, Preview, Development
- [ ] Variable gespeichert

### Nach dem Setzen:
- [ ] Frontend neu deployed (automatisch oder manuell)
- [ ] Browser Console: `import.meta.env.VITE_API_BASE_URL` zeigt korrekte URL
- [ ] Network Tab: Request geht zu `/api/auth/login`
- [ ] Keine 404-Fehler mehr

---

## 🎯 Zusammenfassung

**Was du siehst:**
- Vercel-Dokumentation über System-Umgebungsvariablen
- Das ist nicht relevant für unser Problem

**Was wir brauchen:**
- ✅ Benutzerdefinierte Variable: `VITE_API_BASE_URL`
- ✅ Value: `https://cityraver.up.railway.app/api`
- ✅ In Vercel Dashboard → Settings → Environment Variables setzen

**System-Umgebungsvariablen:**
- ✅ Nicht relevant
- ✅ "Automatically expose" kann aktiviert/deaktiviert bleiben

---

## 🔧 Schnell-Fix

1. **Vercel Dashboard → "tele" Projekt**
2. **Settings → Environment Variables**
3. **"Add New"** (falls nicht vorhanden)
4. **Key:** `VITE_API_BASE_URL`
5. **Value:** `https://cityraver.up.railway.app/api`
6. **Environments:** Production, Preview, Development
7. **Save**
8. **Redeploy** (automatisch oder manuell)

**Dann sollte Login funktionieren!** ✅

