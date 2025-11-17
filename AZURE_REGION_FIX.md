# 🔧 Azure Region Policy Fehler - Lösung

## ❌ Fehler

```
InvalidTemplateDeployment
Resource 'telegram-bot-frontend' was disallowed by Azure: 
This policy maintains a set of best available regions where your subscription 
can deploy resources.
```

**Ursache:** Die ausgewählte Region ist durch eine Azure-Policy blockiert.

---

## ✅ Lösung: Erlaubte Region verwenden

### Schritt 1: Erlaubte Regionen finden

**Option A: Azure Portal**
1. **Azure Portal** → **Subscriptions** → Dein Abonnement
2. **Policies** → Prüfe welche Regionen erlaubt sind
3. Oder: **Resource groups** → **Create** → Prüfe verfügbare Regionen

**Option B: Azure CLI**
```bash
az account list-locations --query "[].{Name:name, DisplayName:displayName}" -o table
```

**Option C: Häufig erlaubte Regionen**
- `eastus` (East US)
- `westus2` (West US 2)
- `westeurope` (West Europe) - **oft blockiert**
- `northeurope` (North Europe)
- `southeastasia` (Southeast Asia)

---

## 🚀 Static Web App mit erlaubter Region erstellen

### Option 1: Azure Portal

1. **"Create a resource"** → **"Static Web App"**
2. **Basics:**
   - **Region:** Wähle eine **erlaubte Region** (z.B. `East US` statt `West Europe`)
   - **Name:** `telegram-bot-frontend`
   - **Plan type:** Free

3. **Deployment details:**
   - **Source:** GitHub
   - **Repository:** `LSRBLN/cityravers`
   - **Branch:** `main`

4. **Build details:**
   - **App location:** `frontend`
   - **Output location:** `dist`

5. **"Review + create"** → **"Create"**

### Option 2: Azure CLI

```bash
# Erlaubte Region finden (z.B. eastus)
az staticwebapp create \
  --name telegram-bot-frontend \
  --resource-group telegram-bot-rg \
  --location eastus \
  --sku Free \
  --app-location "frontend" \
  --output-location "dist" \
  --branch main \
  --repo-url https://github.com/LSRBLN/cityravers \
  --login-with-github
```

---

## 📋 Empfohlene Regionen (meist erlaubt)

### US-Regionen:
- ✅ **eastus** (East US) - **Empfohlen**
- ✅ **westus2** (West US 2)
- ✅ **centralus** (Central US)

### Europa (oft blockiert):
- ⚠️ **westeurope** (West Europe) - **Oft blockiert**
- ✅ **northeurope** (North Europe) - **Oft erlaubt**

### Asien:
- ✅ **southeastasia** (Southeast Asia)
- ✅ **eastasia** (East Asia)

---

## 🔍 Region-Status prüfen

### Vor dem Erstellen testen:

```bash
# Resource Group in erlaubter Region erstellen (Test)
az group create \
  --name test-rg \
  --location eastus

# Wenn erfolgreich → Region ist erlaubt
# Wenn Fehler → Andere Region probieren
```

---

## 🎯 Schnellste Lösung

**Empfehlung:** Verwende **`eastus` (East US)**

1. **Azure Portal** → Static Web App erstellen
2. **Region:** `East US` (nicht West Europe!)
3. Rest wie gewohnt konfigurieren
4. **"Create"** → Sollte funktionieren

---

## 🔄 Region nachträglich ändern

**Wichtig:** Die Region einer Static Web App kann **nicht** nachträglich geändert werden!

**Lösung:**
1. Static Web App löschen
2. Neue Static Web App in erlaubter Region erstellen
3. Gleiche Konfiguration verwenden

---

## 📝 Checkliste

- [ ] Erlaubte Region identifiziert
- [ ] Static Web App in erlaubter Region erstellen
- [ ] Region: `eastus` oder andere erlaubte Region
- [ ] Deployment erfolgreich

---

## 🐛 Troubleshooting

### Problem: Alle Regionen blockiert

**Lösung:**
- Kontaktiere Azure Support
- Oder: Prüfe ob dein Abonnement Region-Beschränkungen hat
- Oder: Upgrade auf höheres Abonnement

### Problem: Region nicht verfügbar

**Lösung:**
- Warte einige Minuten
- Oder: Verwende alternative Region

---

## 🔗 Links

- **Azure Regions:** https://azure.microsoft.com/global-infrastructure/geographies/
- **Azure Portal:** https://portal.azure.com
- **Static Web Apps Docs:** https://docs.microsoft.com/azure/static-web-apps

---

## ✅ Zusammenfassung

**Problem:** Region durch Policy blockiert
**Lösung:** Erlaubte Region verwenden (z.B. `eastus`)
**Nächster Schritt:** Static Web App in erlaubter Region neu erstellen

