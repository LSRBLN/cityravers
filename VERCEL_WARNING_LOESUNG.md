# ⚠️ Vercel Warning beheben - Builds Configuration

## ⚠️ Warnung

```
WARN! Due to `builds` existing in your configuration file, the Build and Development Settings defined in your Project Settings will not apply.
```

---

## 🔍 Problem

**Ursache:** Die Root `vercel.json` (für Backend) enthält `builds`, was die Frontend-Einstellungen überschreibt.

**Es gibt zwei `vercel.json` Dateien:**
1. **Root:** `/vercel.json` - Für Backend (Python/Serverless)
2. **Frontend:** `/frontend/vercel.json` - Für Frontend (Vite)

**Problem:** Vercel verwendet die Root `vercel.json` und ignoriert die Frontend-Einstellungen.

---

## ✅ Lösung: Root vercel.json ignorieren

### Schritt 1: .vercelignore aktualisieren

**Ich habe `.vercelignore` bereits aktualisiert:**
- Root `vercel.json` wird jetzt ignoriert
- Frontend verwendet `frontend/vercel.json`

### Schritt 2: Root Directory prüfen

**Vercel Dashboard:**
1. Frontend-Projekt → Settings → General
2. **Root Directory:** Sollte `frontend` sein
3. Falls nicht: Setze auf `frontend` und speichere

### Schritt 3: Redeploy

**Vercel Dashboard:**
- Deployments → Neuestes Deployment → Redeploy

**Oder Vercel CLI:**
```bash
cd frontend
vercel --prod
```

---

## 📋 Was wurde geändert?

### `.vercelignore` aktualisiert:

**Vorher:**
```
*.json  (ignoriert alle JSON-Dateien)
```

**Nachher:**
```
vercel.json  (ignoriert nur Root vercel.json)
```

**Jetzt:**
- ✅ Root `vercel.json` wird ignoriert (für Frontend-Projekt)
- ✅ `frontend/vercel.json` wird verwendet
- ✅ Frontend-Einstellungen werden angewendet

---

## ✅ Alternative: Root Directory setzen

**Falls die Warnung weiterhin besteht:**

**Vercel Dashboard:**
1. Frontend-Projekt → Settings → General
2. **Root Directory:** Setze auf `frontend`
3. **Save**
4. **Redeploy**

**Dann verwendet Vercel automatisch `frontend/vercel.json` statt Root `vercel.json`.**

---

## 🎯 Zusammenfassung

**Problem:** Root `vercel.json` (Backend) überschreibt Frontend-Einstellungen

**Lösung:**
1. ✅ `.vercelignore` aktualisiert (Root `vercel.json` wird ignoriert)
2. ✅ Root Directory auf `frontend` prüfen/setzen
3. ✅ Redeploy

**Nach Redeploy sollte die Warnung verschwinden!**

---

## 📝 Checkliste

- [x] `.vercelignore` aktualisiert
- [ ] Root Directory auf `frontend` gesetzt (Vercel Dashboard)
- [ ] Redeploy durchgeführt
- [ ] Warnung verschwunden?

---

## 🔗 Nützliche Links

- **Vercel Dashboard:** https://vercel.com/dashboard
- **Vercel Docs:** https://vercel.com/docs/projects/configuration

