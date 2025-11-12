# 🎵 Berlin City Raver - Marketing Tool

⚠️ **WICHTIGE WARNUNG:**
- Spam verstößt gegen die [Telegram Nutzungsbedingungen](https://telegram.org/tos)
- Kann zu **permanenten Account-Sperrungen** führen
- Nur für **legitime Zwecke** verwenden:
  - Eigene Chats/Gruppen
  - Test-Bots
  - Entwicklungszwecke
- **Verantwortungsvoller Umgang erforderlich**

## Features

✅ **Account-Verwaltung**: Mehrere Telegram-Accounts verwalten  
✅ **Gruppen-Verwaltung**: Automatisches Laden von Dialogen oder manuelles Hinzufügen  
✅ **Zeitplanung**: Nachrichten zu bestimmten Zeiten planen  
✅ **React Web-Interface**: Moderne, benutzerfreundliche Oberfläche  
✅ **Scheduler**: Automatische Ausführung geplanter Nachrichten  
✅ **Rate Limiting**: Eingebaute Schutzmechanismen gegen FloodWait  

## Installation

### Backend

```bash
# Python Dependencies installieren
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

## Start

### Backend starten

```bash
# Option 1: Direkt
python api.py

# Option 2: Mit uvicorn
uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# Option 3: Start-Skript
chmod +x start_backend.sh
./start_backend.sh
```

Backend läuft auf: http://localhost:8000

### Frontend starten

```bash
cd frontend
npm run dev

# Oder mit Start-Skript
chmod +x start_frontend.sh
./start_frontend.sh
```

Frontend läuft auf: http://localhost:3000

## Verwendung

### 1. Account hinzufügen

1. Öffne http://localhost:3000
2. Gehe zum Tab "Accounts"
3. Klicke auf "+ Neuer Account"
4. Fülle die Felder aus:
   - **Account-Name**: Beliebiger Name
   - **API ID**: Von https://my.telegram.org/apps
   - **API Hash**: Von https://my.telegram.org/apps
   - **Telefonnummer**: Deine Telegram-Nummer (+49...)
   - **Session-Name**: Eindeutiger Name (z.B. account1_session)
5. Nach dem Erstellen: Code von Telegram eingeben (ggf. 2FA-Passwort)

### 2. Gruppen hinzufügen

**Option A: Automatisch aus Dialogen**
1. Wähle einen verbundenen Account aus dem Dropdown
2. Dialoge werden geladen
3. Wähle gewünschte Gruppen aus

**Option B: Manuell**
1. Klicke auf "+ Manuell hinzufügen"
2. Fülle Chat-ID, Name und Typ aus

### 3. Nachrichten planen

1. Gehe zum Tab "Geplante Nachrichten"
2. Klicke auf "+ Neue geplante Nachricht"
3. Wähle:
   - **Account**: Verbundener Account
   - **Gruppe**: Zielgruppe
   - **Nachricht**: Text
   - **Geplant für**: Datum und Uhrzeit
   - **Wiederholungen**: Wie oft senden
   - **Delay**: Sekunden zwischen Nachrichten
   - **Batch-Größe**: Nachrichten pro Batch
   - **Batch-Delay**: Pause zwischen Batches

## API Endpoints

### Accounts
- `GET /api/accounts` - Liste aller Accounts
- `POST /api/accounts` - Neuen Account erstellen
- `POST /api/accounts/{id}/login` - Account einloggen
- `GET /api/accounts/{id}/dialogs` - Dialoge abrufen
- `DELETE /api/accounts/{id}` - Account löschen

### Gruppen
- `GET /api/groups` - Liste aller Gruppen
- `POST /api/groups` - Neue Gruppe erstellen
- `DELETE /api/groups/{id}` - Gruppe löschen

### Geplante Nachrichten
- `GET /api/scheduled-messages` - Liste aller geplanten Nachrichten
- `POST /api/scheduled-messages` - Neue geplante Nachricht erstellen
- `GET /api/scheduled-messages/{id}` - Details einer Nachricht
- `PUT /api/scheduled-messages/{id}` - Nachricht aktualisieren
- `DELETE /api/scheduled-messages/{id}` - Nachricht abbrechen

### Test
- `POST /api/send-test` - Sofortige Testnachricht senden

## Datenbank

Die SQLite-Datenbank `telegram_bot.db` wird automatisch erstellt. Enthält:
- **accounts**: Gespeicherte Telegram-Accounts
- **groups**: Gespeicherte Gruppen/Chats
- **scheduled_messages**: Geplante Nachrichten mit Status

## Rate Limiting

Eingebaute Schutzmechanismen:
- **Delay zwischen Nachrichten**: Standard 1 Sekunde (konfigurierbar)
- **Batch-Größe**: Standard 10 Nachrichten
- **Batch-Delay**: Standard 5 Sekunden zwischen Batches
- **Automatische FloodWait-Behandlung**: Pausiert bei Telegram-Limits

## Sicherheitshinweise

1. **Niedrige Rate Limits verwenden** (mindestens 1-2 Sekunden Delay)
2. **Kleine Batch-Größen** (max. 10-20 Nachrichten)
3. **Nur eigene Chats/Gruppen** verwenden
4. **Testen mit kleinen Mengen** vor größeren Versendungen
5. **Account kann gesperrt werden** bei Missbrauch

## Technische Details

- **Backend**: FastAPI (asynchron)
- **Frontend**: React + Vite
- **Datenbank**: SQLite mit SQLAlchemy
- **Scheduler**: APScheduler für zeitgesteuerte Aufgaben
- **Telegram**: Telethon (asynchrone Telegram Client Library)
- **Session-Management**: Automatische Speicherung der Login-Sessions

## Projektstruktur

```
telegram-bot/
├── api.py                 # FastAPI Backend
├── account_manager.py     # Account-Verwaltung
├── scheduler_service.py   # Scheduler für geplante Nachrichten
├── database.py            # Datenbank-Modelle
├── spam_tool.py          # CLI-Tool (Legacy)
├── requirements.txt      # Python Dependencies
├── frontend/             # React Frontend
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── AccountManager.jsx
│   │   │   ├── GroupManager.jsx
│   │   │   └── ScheduledMessages.jsx
│   │   └── ...
│   └── package.json
└── telegram_bot.db       # SQLite Datenbank (wird erstellt)
```

## Lizenz

Nur für legale und ethische Zwecke. Der Autor übernimmt keine Verantwortung für Missbrauch.

