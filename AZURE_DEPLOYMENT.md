# 🚀 Azure Static Web Apps Deployment

## Übersicht

Azure Static Web Apps ist die beste Option für React/Vite Frontend-Deployments auf Azure.

---

## 📋 Voraussetzungen

- ✅ Azure Account (kostenlos erstellbar: https://azure.microsoft.com/free)
- ✅ GitHub Repository (bereits vorhanden: `phnxvision-pixel/tele`)
- ✅ Backend-URL: `https://cityraver.up.railway.app`

---

## 🎯 Option 1: Azure Portal (Empfohlen - 5 Minuten)

### Schritt 1: Azure Static Web App erstellen

1. **Gehe zu:** https://portal.azure.com
2. **"Create a resource"** → Suche nach **"Static Web App"**
3. **"Create"** klicken

### Schritt 2: Grundkonfiguration

**Basics:**
- **Subscription:** Wähle dein Azure-Abonnement
- **Resource Group:** Erstelle neue oder wähle bestehende
- **Name:** z.B. `telegram-bot-frontend`
- **Plan type:** Free (für Start)
- **Region:** Wähle nächstgelegene Region (z.B. `West Europe`)

**Deployment details:**
- **Source:** GitHub
- **GitHub Account:** Mit GitHub verbinden (falls noch nicht)
- **Organization:** `phnxvision-pixel`
- **Repository:** `tele`
- **Branch:** `main`

**Build details:**
- **Build Presets:** Custom
- **App location:** `frontend`
- **Api location:** (leer lassen)
- **Output location:** `dist`

### Schritt 3: Environment Variables setzen

Nach dem Erstellen:

1. **Static Web App** öffnen
2. **Configuration** → **Application settings**
3. **"Add"** klicken
4. **Name:** `VITE_API_BASE_URL`
5. **Value:** `https://cityraver.up.railway.app`
6. **"OK"** → **"Save"**

### Schritt 4: Deployment

- Azure startet automatisch den ersten Build
- Warte auf Deployment (ca. 2-3 Minuten)
- **Fertig!** Deine URL: `https://[name].azurestaticapps.net`

---

## 🎯 Option 2: Azure CLI (Für Entwickler)

### Schritt 1: Azure CLI installieren

```bash
# macOS
brew install azure-cli

# Oder: https://docs.microsoft.com/cli/azure/install-azure-cli
```

### Schritt 2: Login & Setup

```bash
# Login
az login

# Subscription setzen
az account set --subscription "[deine-subscription-id]"

# Resource Group erstellen (falls nicht vorhanden)
az group create \
  --name telegram-bot-rg \
  --location westeurope
```

### Schritt 3: Static Web App erstellen

```bash
cd frontend

# Static Web App erstellen
az staticwebapp create \
  --name telegram-bot-frontend \
  --resource-group telegram-bot-rg \
  --location westeurope \
  --sku Free \
  --app-location "frontend" \
  --output-location "dist" \
  --branch main \
  --repo-url https://github.com/phnxvision-pixel/tele \
  --login-with-github
```

### Schritt 4: Environment Variable setzen

```bash
az staticwebapp appsettings set \
  --name telegram-bot-frontend \
  --resource-group telegram-bot-rg \
  --setting-names VITE_API_BASE_URL=https://cityraver.up.railway.app
```

---

## 🎯 Option 3: GitHub Actions (Automatisch)

Azure erstellt automatisch einen GitHub Actions Workflow:

**Datei:** `.github/workflows/azure-static-web-apps-[name].yml`

Dieser wird automatisch erstellt und konfiguriert. Du musst nichts tun!

---

## 🔧 Konfigurationsdateien

### `staticwebapp.config.json` (bereits erstellt)

Diese Datei ist bereits im `frontend/` Verzeichnis und konfiguriert:
- SPA-Routing (alle Routes → index.html)
- 404-Handling
- Custom Routes

### Build-Konfiguration

Azure erkennt automatisch:
- **Build command:** `npm run build` (aus `package.json`)
- **Output:** `dist` (aus Vite-Konfiguration)
- **Node version:** Automatisch (empfohlen: 18+)

---

## 🔗 URLs nach Deployment

**Frontend (Azure):**
```
https://[dein-name].azurestaticapps.net
```

**Backend (Railway):**
```
https://cityraver.up.railway.app
```

**API-Dokumentation:**
```
https://cityraver.up.railway.app/docs
```

---

## ✅ Checkliste

- [ ] Azure Account erstellt
- [ ] Static Web App erstellt (Portal oder CLI)
- [ ] GitHub Repository verbunden
- [ ] Build-Einstellungen konfiguriert:
  - [ ] App location: `frontend`
  - [ ] Output location: `dist`
- [ ] Environment Variable gesetzt: `VITE_API_BASE_URL`
- [ ] Erster Deployment erfolgreich
- [ ] Frontend-URL getestet
- [ ] Login funktioniert

---

## 🐛 Troubleshooting

### Problem: Build schlägt fehl

**Lösung:**
- Prüfe GitHub Actions Logs
- Stelle sicher, dass `app-location: frontend` korrekt ist
- Prüfe ob `package.json` im `frontend/` Verzeichnis existiert
- Prüfe Node-Version (sollte 18+ sein)

### Problem: 404 auf Routes

**Lösung:**
- Prüfe ob `staticwebapp.config.json` im `frontend/` Verzeichnis ist
- Stelle sicher, dass `navigationFallback` konfiguriert ist
- Prüfe Azure Portal → Configuration → Routes

### Problem: API-Calls gehen zu `/api` statt Railway

**Lösung:**
- Prüfe ob `VITE_API_BASE_URL` in Azure Application Settings gesetzt ist
- Stelle sicher, dass nach dem Setzen ein neuer Build gestartet wurde
- Prüfe Browser-Console (F12) für die tatsächlich verwendete URL

### Problem: CORS-Fehler

**Lösung:**
- Stelle sicher, dass Railway die Azure-Domain erlaubt
- In Railway Environment Variables:
  ```
  ALLOWED_ORIGINS=https://[dein-name].azurestaticapps.net,https://*.azurestaticapps.net
  ```

---

## 🔄 Continuous Deployment

Azure Static Web Apps unterstützt automatisches Deployment:

- **Automatisch:** Bei jedem Push zu `main` Branch
- **Preview:** Bei Pull Requests (automatische Preview-URLs)
- **Manuell:** Über Azure Portal → "Redeploy"

---

## 💰 Kosten

**Free Tier:**
- ✅ 100 GB Bandbreite/Monat
- ✅ Unbegrenzte Builds
- ✅ Custom Domains
- ✅ SSL-Zertifikate
- ✅ Preview-Deployments

**Für Produktion ausreichend!**

---

## 🎯 Custom Domain hinzufügen

1. **Azure Portal** → Deine Static Web App
2. **Custom domains** → **"Add"**
3. **Domain eingeben** (z.B. `app.deine-domain.com`)
4. **DNS-Einstellungen befolgen**
5. **SSL-Zertifikat** wird automatisch erstellt

---

## 📞 Hilfe & Ressourcen

- **Azure Static Web Apps Docs:** https://docs.microsoft.com/azure/static-web-apps
- **Azure Portal:** https://portal.azure.com
- **GitHub Actions Logs:** Repository → Actions Tab
- **Backend API Docs:** https://cityraver.up.railway.app/docs

---

## 🚀 Schnellstart (Zusammenfassung)

1. **Azure Portal** → Static Web App erstellen
2. **GitHub verbinden** → Repository auswählen
3. **Build-Einstellungen:**
   - App location: `frontend`
   - Output location: `dist`
4. **Environment Variable:** `VITE_API_BASE_URL=https://cityraver.up.railway.app`
5. **Deploy!** → Warte 2-3 Minuten
6. **Fertig!** → Teste deine URL

---

## 🎉 Vorteile von Azure Static Web Apps

- ✅ **Kostenlos** (Free Tier)
- ✅ **Automatisches Deployment** (GitHub Integration)
- ✅ **Preview-Deployments** (bei Pull Requests)
- ✅ **Custom Domains** (kostenlos)
- ✅ **SSL-Zertifikate** (automatisch)
- ✅ **CDN** (schnelle Ladezeiten)
- ✅ **Einfache Konfiguration**

