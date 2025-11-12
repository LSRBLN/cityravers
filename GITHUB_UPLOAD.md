# GitHub Upload - Anleitung

## Status
✅ Git Repository initialisiert
✅ Alle Dateien committed
✅ Remote konfiguriert: `https://github.com/phnxvision-pixel/tele.git`
✅ Branch: `main`

## Authentifizierung

GitHub unterstützt keine Passwort-Authentifizierung mehr. Du musst einen **Personal Access Token (PAT)** verwenden.

### Option 1: Personal Access Token erstellen (Empfohlen)

1. Gehe zu: https://github.com/settings/tokens
2. Klicke auf "Generate new token" → "Generate new token (classic)"
3. Name: z.B. "tele-bot-upload"
4. Scopes: Wähle `repo` (alle Repository-Berechtigungen)
5. Klicke "Generate token"
6. **Kopiere den Token** (wird nur einmal angezeigt!)

### Upload mit Token

```bash
cd /Users/rebelldesign/Documents/telegram-bot

# Remote mit Token setzen (USERNAME = phnxvision, TOKEN = dein kopierter Token)
git remote set-url origin https://phnxvision:DEIN_TOKEN_HIER@github.com/phnxvision-pixel/tele.git

# Pushen
git push -u origin main
```

### Option 2: GitHub CLI (falls installiert)

```bash
gh auth login
git push -u origin main
```

### Option 3: SSH (falls SSH-Key bei GitHub hinterlegt)

```bash
# SSH-Key zu GitHub hinzufügen (falls noch nicht geschehen)
# Dann:
git remote set-url origin git@github.com:phnxvision-pixel/tele.git
git push -u origin main
```

## Wichtige Hinweise

- `.gitignore` ist konfiguriert und schließt sensible Dateien aus:
  - `.env` (Umgebungsvariablen)
  - `*.db` (Datenbanken)
  - `*.session` (Telegram Sessions)
  - `venv/` (Python Virtual Environment)
  - `backups/` (Backups)

- **NICHT hochgeladen werden:**
  - `telegram_bot.db` (Datenbank)
  - `.env` (API-Keys, Secrets)
  - `*.session` (Telegram Sessions)
  - `backend.log` (Logs)

## Nach dem Upload

1. Repository auf GitHub prüfen: https://github.com/phnxvision-pixel/tele
2. `.env.example` als Vorlage für andere Entwickler
3. `README.md` aktualisieren mit Setup-Anleitung

