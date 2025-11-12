# Vercel Access Token - Anleitung

## Wo findest du deinen Vercel Access Token?

### Methode 1: Über Vercel Dashboard

1. Gehe zu [vercel.com/account/tokens](https://vercel.com/account/tokens)
2. Klicke auf **"Create Token"**
3. Gib einen Namen ein (z.B. "Telegram Bot API")
4. Wähle **Scope:**
   - ✅ **Full Account** (für alle Projekte)
   - Oder **Specific Projects** (nur für bestimmte Projekte)
5. Klicke auf **"Create Token"**
6. **⚠️ WICHTIG:** Kopiere den Token sofort - er wird nur einmal angezeigt!

### Methode 2: Über Vercel CLI

```bash
# Token erstellen
vercel tokens create "Telegram Bot API"

# Alle Tokens anzeigen
vercel tokens ls

# Token löschen
vercel tokens rm <token-id>
```

## Wo verwendest du den Access Token?

### 1. Environment Variables (für CI/CD)

#### GitHub Actions

Erstelle `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Vercel

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
```

**GitHub Secrets setzen:**
1. Gehe zu Repository → Settings → Secrets and variables → Actions
2. Klicke auf **"New repository secret"**
3. Füge hinzu:
   - `VERCEL_TOKEN` = dein Access Token
   - `VERCEL_ORG_ID` = findest du in `.vercel/project.json` oder Vercel Dashboard
   - `VERCEL_PROJECT_ID` = findest du in `.vercel/project.json` oder Vercel Dashboard

#### GitLab CI/CD

Erstelle `.gitlab-ci.yml`:

```yaml
deploy:
  stage: deploy
  image: node:18
  before_script:
    - npm install -g vercel
  script:
    - vercel --token $VERCEL_TOKEN --prod
  only:
    - main
```

**GitLab Variables setzen:**
1. Gehe zu Repository → Settings → CI/CD → Variables
2. Füge hinzu: `VERCEL_TOKEN` = dein Access Token

### 2. Lokale Verwendung (ohne Login)

```bash
# Token als Environment Variable setzen
export VERCEL_TOKEN=dein-token-hier

# Oder in .env Datei
echo "VERCEL_TOKEN=dein-token-hier" >> .env

# Dann verwenden
vercel --token $VERCEL_TOKEN
```

### 3. In Scripts

Erstelle `deploy.sh`:

```bash
#!/bin/bash
export VERCEL_TOKEN="dein-token-hier"
vercel --token $VERCEL_TOKEN --prod
```

### 4. Für andere Tools/APIs

Viele Tools benötigen den Vercel Token für API-Zugriff:

```bash
# Beispiel: Vercel API verwenden
curl -H "Authorization: Bearer $VERCEL_TOKEN" \
  https://api.vercel.com/v9/projects
```

## Sicherheit

### ✅ DO's

- ✅ Token in Environment Variables speichern
- ✅ Token in CI/CD Secrets speichern
- ✅ Token mit minimalen Berechtigungen erstellen
- ✅ Token regelmäßig rotieren
- ✅ Token in `.gitignore` aufnehmen (falls in .env)

### ❌ DON'Ts

- ❌ Token niemals in Code committen
- ❌ Token nicht in öffentlichen Repositories teilen
- ❌ Token nicht in Logs ausgeben
- ❌ Token nicht in Client-seitigem Code verwenden

## Token-Informationen abrufen

### Projekt-Informationen

```bash
# Projekt-ID und Org-ID finden
cat .vercel/project.json

# Oder über Vercel CLI
vercel inspect
```

### Token-Informationen

```bash
# Alle Tokens anzeigen
vercel tokens ls

# Token-Details
vercel tokens inspect <token-id>
```

## Beispiel: GitHub Actions Workflow

Erstelle `.github/workflows/vercel-deploy.yml`:

```yaml
name: Deploy to Vercel

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install Vercel CLI
        run: npm install -g vercel@latest
      
      - name: Deploy to Vercel
        run: vercel --prod --token ${{ secrets.VERCEL_TOKEN }}
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
```

## Troubleshooting

### Problem: "Invalid token"

**Lösung:**
- Prüfe ob Token korrekt kopiert wurde (keine Leerzeichen)
- Prüfe ob Token nicht abgelaufen ist
- Erstelle neuen Token

### Problem: "Insufficient permissions"

**Lösung:**
- Prüfe Token-Scope (muss "Full Account" oder Projekt-spezifisch sein)
- Prüfe ob du Zugriff auf das Projekt hast

### Problem: Token funktioniert nicht in CI/CD

**Lösung:**
- Stelle sicher, dass Token als Secret gesetzt ist
- Prüfe ob Variable-Name korrekt ist (`VERCEL_TOKEN`)
- Prüfe ob Token nicht abgelaufen ist

## Nützliche Links

- [Vercel Tokens Dashboard](https://vercel.com/account/tokens)
- [Vercel CLI Documentation](https://vercel.com/docs/cli)
- [Vercel API Documentation](https://vercel.com/docs/rest-api)

