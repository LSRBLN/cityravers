# 🔧 Azure Static Web Apps GitHub Actions Workflow

## ✅ Workflow-Datei erstellt

**Datei:** `.github/workflows/azure-static-web-apps.yml`

## 🔧 Korrekturen

### 1. Output Location korrigiert
- **Vorher:** `output_location: "build"`
- **Jetzt:** `output_location: "dist"` ✅
- **Grund:** Vite baut standardmäßig nach `dist`, nicht `build`

### 2. Secret-Name vereinfacht
- **Vorher:** `AZURE_STATIC_WEB_APPS_API_TOKEN_<GENERATED_HOSTNAME>`
- **Jetzt:** `AZURE_STATIC_WEB_APPS_API_TOKEN` ✅
- **Grund:** Azure generiert den Secret-Namen automatisch

## 📋 Workflow-Konfiguration

```yaml
app_location: "./frontend"     # ✅ Korrekt
api_location: ""                # ✅ Kein Backend-API
output_location: "dist"         # ✅ Vite Build-Output
```

## 🔑 Secrets einrichten

### Schritt 1: Azure Static Web App erstellen

1. **Azure Portal:** https://portal.azure.com
2. **Static Web App erstellen** (siehe `AZURE_DEPLOYMENT.md`)
3. **GitHub Repository verbinden**

### Schritt 2: Deployment Token kopieren

Nach dem Erstellen der Static Web App:

1. **Azure Portal** → Deine Static Web App
2. **"Manage deployment token"** klicken
3. **Token kopieren**

### Schritt 3: Secret zu GitHub hinzufügen

1. **GitHub Repository:** https://github.com/LSRBLN/cityravers
2. **Settings** → **Secrets and variables** → **Actions**
3. **"New repository secret"** klicken
4. **Name:** `AZURE_STATIC_WEB_APPS_API_TOKEN`
5. **Value:** Token aus Azure einfügen
6. **"Add secret"** klicken

## ✅ Workflow testen

### Automatisch:
- **Push zu `main`** → Workflow startet automatisch
- **Pull Request** → Preview-Deployment

### Manuell:
1. **GitHub Repository** → **Actions** Tab
2. **"Azure Static Web Apps CI/CD"** auswählen
3. **"Run workflow"** klicken

## 🐛 Troubleshooting

### Problem: "Secret not found"

**Lösung:**
- Prüfe ob Secret `AZURE_STATIC_WEB_APPS_API_TOKEN` in GitHub existiert
- Stelle sicher, dass der Name exakt übereinstimmt

### Problem: "Build failed - dist not found"

**Lösung:**
- Prüfe ob `output_location: "dist"` korrekt ist
- Prüfe ob `npm run build` erfolgreich ist
- Prüfe Build-Logs in GitHub Actions

### Problem: "Deployment failed"

**Lösung:**
- Prüfe Azure Static Web App Status
- Prüfe ob Token noch gültig ist
- Prüfe Azure Portal → Deployment Logs

## 📝 Workflow-Details

### Trigger:
- ✅ Push zu `main` Branch
- ✅ Pull Requests (öffnen, synchronisieren, wiedereröffnen)
- ✅ Pull Request schließen (cleanup)

### Jobs:
1. **build_and_deploy_job:** Baut und deployed die App
2. **close_pull_request_job:** Räumt Preview-Deployments auf

### Steps:
1. **Checkout:** Code aus Repository holen
2. **Build & Deploy:** Vite Build + Azure Deployment
3. **Close PR:** Cleanup bei geschlossenen PRs

## 🔗 Links

- **GitHub Actions:** Repository → Actions Tab
- **Azure Portal:** https://portal.azure.com
- **Workflow-Datei:** `.github/workflows/azure-static-web-apps.yml`

## ✅ Checkliste

- [x] Workflow-Datei erstellt
- [x] Output Location korrigiert (`dist`)
- [ ] Azure Static Web App erstellt
- [ ] Deployment Token kopiert
- [ ] Secret zu GitHub hinzugefügt
- [ ] Workflow getestet (Push zu main)
- [ ] Deployment erfolgreich

## 🚀 Nächste Schritte

1. **Azure Static Web App erstellen** (siehe `AZURE_DEPLOYMENT.md`)
2. **Deployment Token kopieren**
3. **Secret zu GitHub hinzufügen**
4. **Code pushen** → Workflow startet automatisch
5. **Deployment prüfen** in Azure Portal

