# ⚠️ Vercel Warning - Builds Configuration

## ⚠️ Warnung

```
WARN! Due to `builds` existing in your configuration file, the Build and Development Settings defined in your Project Settings will not apply.
```

---

## 🔍 Problem

**Ursache:** Die `vercel.json` im **Root-Verzeichnis** enthält `builds` (für Backend), was die Frontend-Einstellungen überschreibt.

**Es gibt zwei `vercel.json` Dateien:**
1. **Root:** `/vercel.json` - Für Backend (falls auf Vercel)
2. **Frontend:** `/frontend/vercel.json` - Für Frontend

**Problem:** Vercel verwendet die Root `vercel.json` und ignoriert die Frontend-Einstellungen.

---

## ✅ Lösung

### Option 1: Root vercel.json ignorieren (Empfohlen)

**Falls Frontend-Projekt auf Vercel:**

Die Root `vercel.json` ist für Backend (falls auf Vercel). Da Backend auf Railway läuft, kann sie ignoriert werden.

**Lösung:** `.vercelignore` erstellen oder aktualisieren:

```bash
# Ignoriere Root vercel.json für Frontend-Projekt
vercel.json
```

**Oder:** Frontend-Projekt sollte nur `frontend/vercel.json` verwenden.

### Option 2: Root vercel.json entfernen (falls Backend nicht auf Vercel)

**Falls Backend nur auf Railway läuft:**

Die Root `vercel.json` ist nicht nötig, da Backend auf Railway ist.

**Lösung:**
1. Verschiebe `vercel.json` nach `vercel.json.backup`
2. Oder: Lösche sie (falls Backend nicht auf Vercel)

### Option 3: Frontend-Projekt Root Directory setzen

**Vercel Dashboard:**
1. Frontend-Projekt → Settings → General
2. **Root Directory:** `frontend`
3. Dann verwendet Vercel `frontend/vercel.json` statt Root `vercel.json`

---

## 🔧 Schnell-Fix

### Schritt 1: Root Directory prüfen

**Vercel Dashboard → Frontend-Projekt:**
- Settings → General
- **Root Directory:** Sollte `frontend` sein

### Schritt 2: Falls Root Directory nicht gesetzt

1. **Settings → General**
2. **Root Directory:** Setze auf `frontend`
3. **Save**
4. **Redeploy**

### Schritt 3: Root vercel.json ignorieren

**Erstelle/aktualisiere `.vercelignore` im Root:**

```bash
# Ignoriere Root vercel.json für Frontend
vercel.json
api/
*.py
requirements.txt
```

**Oder:** Verschiebe Root `vercel.json` nach `vercel.json.backup`

---

## 📋 Aktuelle Konfiguration

### Root `vercel.json` (für Backend):
```json
{
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  ...
}
```

**Das ist für Backend, nicht Frontend!**

### Frontend `frontend/vercel.json` (für Frontend):
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  ...
}
```

**Das ist für Frontend!**

---

## ✅ Empfohlene Lösung

### Für Frontend-Projekt:

1. **Root Directory setzen:**
   - Vercel Dashboard → Frontend-Projekt
   - Settings → General → Root Directory: `frontend`

2. **Oder Root vercel.json ignorieren:**
   - Erstelle `.vercelignore` mit `vercel.json`

3. **Redeploy:**
   - Deployments → Redeploy

---

## 🎯 Zusammenfassung

**Problem:** Root `vercel.json` (Backend) überschreibt Frontend-Einstellungen

**Lösung:**
1. ✅ Root Directory auf `frontend` setzen
2. ✅ Oder Root `vercel.json` ignorieren
3. ✅ Redeploy

**Die Warnung verschwindet, wenn Vercel `frontend/vercel.json` verwendet statt Root `vercel.json`.**

---

## 📝 Checkliste

- [ ] Root Directory auf `frontend` gesetzt?
- [ ] Root `vercel.json` ignoriert oder entfernt?
- [ ] Frontend-Projekt verwendet `frontend/vercel.json`?
- [ ] Redeploy durchgeführt?
- [ ] Warnung verschwunden?

---

## 🔗 Nützliche Links

- **Vercel Docs:** https://vercel.com/docs/projects/configuration
- **Vercel Dashboard:** https://vercel.com/dashboard

