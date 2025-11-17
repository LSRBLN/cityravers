# GitHub Actions Workflow - Manuelle Einrichtung

## Problem

Der Personal Access Token hat keine `workflow` Berechtigung, daher kann die Workflow-Datei nicht direkt gepusht werden.

## Lösung: Workflow manuell erstellen

### Option 1: Über GitHub Web-Interface (Empfohlen)

1. Gehe zu deinem Repository: `https://github.com/phnxvision-pixel/tele`
2. Klicke auf **"Add file"** → **"Create new file"**
3. Pfad eingeben: `.github/workflows/vercel-deploy.yml`
4. Kopiere den folgenden Inhalt:

```yaml
name: Deploy to Vercel

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
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install Vercel CLI
        run: npm install -g vercel@latest
      
      - name: Pull Vercel Environment Information
        id: vercel-pull
        run: |
          vercel pull --yes --environment=production --token=${{ secrets.VERCEL_TOKEN }}
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
      
      - name: Build Project Artifacts
        run: vercel build --prod --token=${{ secrets.VERCEL_TOKEN }}
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
      
      - name: Deploy Project Artifacts to Vercel
        run: vercel deploy --prebuilt --prod --token=${{ secrets.VERCEL_TOKEN }}
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
```

5. Klicke auf **"Commit new file"**

### Option 2: Personal Access Token aktualisieren

1. Gehe zu [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. Erstelle neuen Token oder bearbeite existierenden
3. Aktiviere **`workflow`** Scope
4. Token speichern
5. Git neu konfigurieren:
   ```bash
   git remote set-url origin https://dein-token@github.com/phnxvision-pixel/tele.git
   ```
6. Dann pushen:
   ```bash
   git push
   ```

## Prüfen ob es funktioniert

1. Gehe zu: `https://github.com/phnxvision-pixel/tele/actions`
2. Du solltest den Workflow "Deploy to Vercel" sehen
3. Klicke auf **"Run workflow"** für manuellen Test

## Workflow-Informationen

- **Trigger:** Automatisch bei Push auf `main` Branch
- **Manuell:** Über Actions Tab → "Run workflow"
- **Verwendet Secrets:**
  - `VERCEL_TOKEN`
  - `VERCEL_ORG_ID` = `team_9M9pQcpCWQMBdN6ATT1gOpB3`
  - `VERCEL_PROJECT_ID` = `prj_MtCpxq0zVIs9AxzJAYdHUATj6vDR`

