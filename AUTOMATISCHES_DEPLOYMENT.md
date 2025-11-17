# 🚀 Automatisches Deployment Setup

## Übersicht

**Railway** und **Vercel** unterstützen automatische Deployments bei Git-Push. Es gibt zwei Methoden:

1. **Automatisch über GitHub Integration** (Empfohlen - Einfachste Methode)
2. **Manuell über GitHub Actions** (Für mehr Kontrolle)

---

## ✅ Option 1: Automatisches Deployment über GitHub Integration

### Railway (Backend)

Railway deployed **automatisch**, wenn:
- ✅ GitHub-Repo ist verbunden
- ✅ Push auf `main` Branch erfolgt

**Setup-Schritte:**

1. **Railway Dashboard öffnen**
   - Gehe zu [railway.app](https://railway.app)
   - Wähle dein Projekt

2. **GitHub Integration prüfen**
   - Settings → **Source**
   - Stelle sicher, dass dein GitHub-Repo verbunden ist
   - Branch: `main` (oder dein Standard-Branch)

3. **Automatisches Deployment aktivieren**
   - Settings → **Deployments**
   - **Auto Deploy**: ✅ Aktiviert
   - **Branch**: `main`

**Fertig!** Jeder Push auf `main` deployed automatisch.

---

### Vercel (Frontend/Backend)

Vercel deployed **automatisch**, wenn:
- ✅ GitHub-Repo ist verbunden
- ✅ Push auf `main` Branch erfolgt

**Setup-Schritte:**

1. **Vercel Dashboard öffnen**
   - Gehe zu [vercel.com](https://vercel.com)
   - Wähle dein Projekt

2. **GitHub Integration prüfen**
   - Settings → **Git**
   - Stelle sicher, dass dein GitHub-Repo verbunden ist
   - **Production Branch**: `main`

3. **Automatisches Deployment aktivieren**
   - Settings → **Git**
   - **Auto Deploy**: ✅ Aktiviert
   - **Production Branch**: `main`

**Fertig!** Jeder Push auf `main` deployed automatisch.

---

## 🔧 Option 2: GitHub Actions (Für mehr Kontrolle)

Falls du mehr Kontrolle über den Deployment-Prozess brauchst, kannst du GitHub Actions verwenden.

### Railway mit GitHub Actions

Erstelle `.github/workflows/railway-deploy.yml`:

```yaml
name: Deploy to Railway

on:
  push:
    branches: [main]
  workflow_dispatch: # Manuelles Auslösen möglich

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      
      - name: Setup Railway CLI
        run: |
          npm install -g @railway/cli
      
      - name: Deploy to Railway
        run: railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

**GitHub Secrets setzen:**
1. GitHub → Settings → Secrets → Actions
2. Füge hinzu: `RAILWAY_TOKEN`
3. Token holen: Railway Dashboard → Settings → Tokens → New Token

### Vercel mit GitHub Actions

Bereits vorhanden: `.github/workflows/vercel-deploy.yml`

**GitHub Secrets setzen:**
1. GitHub → Settings → Secrets → Actions
2. Füge hinzu:
   - `VERCEL_TOKEN` (Vercel Dashboard → Settings → Tokens)
   - `VERCEL_ORG_ID` (Vercel Dashboard → Settings → General)
   - `VERCEL_PROJECT_ID` (Vercel Dashboard → Settings → General)

---

## 📋 Deployment-Workflow

### Normaler Workflow (Automatisch)

```bash
# 1. Änderungen machen
git add .
git commit -m "Neue Features hinzugefügt"

# 2. Push auf main
git push origin main

# 3. Automatisches Deployment startet
# Railway/Vercel deployed automatisch
```

### Manuelles Deployment

**Railway:**
```bash
# Mit Railway CLI
railway up
```

**Vercel:**
```bash
# Mit Vercel CLI
vercel --prod
```

**Oder über Dashboard:**
- Railway: Dashboard → Deployments → Redeploy
- Vercel: Dashboard → Deployments → Redeploy

---

## 🔍 Deployment-Status prüfen

### Railway
1. Öffne [railway.app](https://railway.app)
2. Wähle dein Projekt
3. **Deployments** Tab zeigt alle Deployments
4. Grüner Status = Erfolgreich

### Vercel
1. Öffne [vercel.com](https://vercel.com)
2. Wähle dein Projekt
3. **Deployments** Tab zeigt alle Deployments
4. Grüner Status = Erfolgreich

---

## ⚠️ Wichtige Hinweise

### 1. Environment Variables
- **Railway**: Settings → Variables
- **Vercel**: Settings → Environment Variables
- Werden **nicht** automatisch aktualisiert bei Git-Push
- Muss manuell gesetzt werden

### 2. Datenbank-Migrationen
- Bei Schema-Änderungen: Migrationen manuell ausführen
- Railway: `railway run python migrate.py`
- Vercel: Über API-Endpunkt oder CLI

### 3. Session-Dateien
- Werden **nicht** in Git committed (`.gitignore`)
- Müssen persistent gespeichert werden (Railway Volumes oder Datenbank)

### 4. Build-Fehler
- Prüfe **Logs** in Railway/Vercel Dashboard
- Häufige Probleme:
  - Fehlende Dependencies (`requirements.txt`)
  - Falsche Environment Variables
  - Port-Konflikte

---

## 🚨 Troubleshooting

### Deployment schlägt fehl

**Railway:**
1. Prüfe Logs: Dashboard → Deployments → Logs
2. Prüfe Environment Variables
3. Prüfe `Procfile` oder Start-Command

**Vercel:**
1. Prüfe Logs: Dashboard → Deployments → Logs
2. Prüfe `vercel.json` Konfiguration
3. Prüfe Build-Logs

### Automatisches Deployment funktioniert nicht

1. **Prüfe GitHub Integration:**
   - Railway: Settings → Source
   - Vercel: Settings → Git

2. **Prüfe Branch:**
   - Stelle sicher, dass du auf `main` pushst
   - Oder ändere Production Branch in Settings

3. **Prüfe GitHub Permissions:**
   - Railway/Vercel braucht Zugriff auf dein Repo
   - GitHub → Settings → Applications → Authorized OAuth Apps

---

## 📝 Zusammenfassung

| Plattform | Automatisches Deployment | Setup |
|-----------|------------------------|-------|
| **Railway** | ✅ Ja (bei GitHub-Integration) | Settings → Source → Auto Deploy |
| **Vercel** | ✅ Ja (bei GitHub-Integration) | Settings → Git → Auto Deploy |
| **GitHub Actions** | ✅ Ja (mit Workflow) | `.github/workflows/*.yml` |

**Empfehlung:** Verwende GitHub Integration (Option 1) - einfachste Methode!

---

## 🎯 Quick Start

**Für automatisches Deployment:**

1. **Railway:**
   - Dashboard → Settings → Source
   - GitHub-Repo verbinden
   - Auto Deploy aktivieren

2. **Vercel:**
   - Dashboard → Settings → Git
   - GitHub-Repo verbinden
   - Auto Deploy aktivieren

3. **Testen:**
   ```bash
   git add .
   git commit -m "Test deployment"
   git push origin main
   ```
   
4. **Prüfen:**
   - Railway/Vercel Dashboard → Deployments
   - Status sollte "Success" sein

**Fertig!** 🎉

