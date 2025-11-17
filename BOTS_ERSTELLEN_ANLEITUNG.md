# Anleitung: 10 Bots erstellen

## Voraussetzungen

1. **User-Account vorhanden**: Du benötigst mindestens einen verbundenen User-Account (nicht Bot), der mit @BotFather kommunizieren kann
2. **Account verbunden**: Der User-Account muss in der Datenbank vorhanden und verbunden sein

## Bot-Erstellung

### Schritt 1: Script ausführen

```bash
python create_10_bots.py
```

Das Script:
- Findet automatisch den ersten verfügbaren User-Account
- Verbindet ihn falls nötig
- Erstellt 10 Bots über BotFather
- Speichert die Bots in der Datenbank
- Verbindet alle Bots automatisch

### Schritt 2: Bots in Gruppen hinzufügen

Nach der Erstellung kannst du die Bots in Gruppen hinzufügen:

**Option A: Über die API**

```python
# Beispiel: Bot zu Gruppe hinzufügen
POST /api/groups/{group_id}/add-bot
{
    "bot_id": 123
}
```

**Option B: Manuell über Telegram**

1. Öffne die Gruppe in Telegram
2. Gehe zu Gruppen-Einstellungen → Mitglieder hinzufügen
3. Suche nach dem Bot-Username (z.B. `@group_bot_1_...`)
4. Füge den Bot hinzu

**Option C: Über einen Admin-Account**

Wenn du einen Admin-Account hast, kannst du die Bots programmatisch hinzufügen:

```python
# Verwende account_manager.check_bot_can_be_added() und dann invite
```

## Bot-Verwaltung

### Bots anzeigen

Alle erstellten Bots werden in der Account-Liste angezeigt (Typ: "bot").

### Bot-Informationen

Jeder Bot hat:
- **ID**: Datenbank-ID
- **Name**: Anzeigename
- **Username**: Telegram-Username (z.B. `@group_bot_1_...`)
- **Token**: Bot-Token (wird verschlüsselt gespeichert)

### Mit Bots posten

Nachdem die Bots zu Gruppen hinzugefügt wurden, kannst du sie verwenden:

1. **Geplante Nachrichten**: Erstelle eine geplante Nachricht und wähle einen Bot-Account
2. **Direkt posten**: Verwende die API-Endpunkte zum Senden von Nachrichten

## Wichtige Hinweise

⚠️ **Rate Limiting**: 
- Das Script wartet 3 Sekunden zwischen Bot-Erstellungen
- Bei Fehlern wird 5 Sekunden gewartet
- Telegram kann bei zu vielen Anfragen temporär sperren

⚠️ **BotFather Limits**:
- Telegram erlaubt eine begrenzte Anzahl von Bots pro Account
- Falls das Limit erreicht wird, musst du einen anderen User-Account verwenden

⚠️ **Bot-Namen**:
- Bot-Usernames müssen mit "bot" enden
- Das Script fügt automatisch "bot" hinzu falls nötig
- Usernames müssen eindeutig sein (Timestamp wird hinzugefügt)

## Fehlerbehebung

### "Kein User-Account gefunden"
- Erstelle zuerst einen User-Account über die API oder das Frontend
- Stelle sicher, dass der Account-Typ "user" ist (nicht "bot")

### "Account nicht verbunden"
- Verbinde den Account manuell über die API oder das Frontend
- Falls Code erforderlich ist, führe den Login-Prozess durch

### "Bot-Token nicht erhalten"
- Prüfe ob der User-Account mit BotFather kommunizieren kann
- Stelle sicher, dass der Account nicht gesperrt ist
- Versuche es später erneut (Rate Limiting)

### "FloodWait Error"
- Telegram hat temporär gesperrt
- Warte die angegebene Zeit ab
- Führe das Script später erneut aus

## Beispiel-Ausgabe

```
🤖 Erstelle 10 Bots über BotFather...

✅ User-Account gefunden: Mein Account (ID: 1)
✅ Account Mein Account ist verbunden

🤖 Erstelle 10 Bots über BotFather...
============================================================

[1/10] Erstelle Bot: Group Bot 1 (@group_bot_1_1234567890bot)
  ✅ Bot erstellt! Token: 1234567890:ABCdefGHI...
  ✅ Bot verbunden: @group_bot_1_1234567890bot
  ⏳ Warte 3s vor nächstem Bot...

...

============================================================
📊 ZUSAMMENFASSUNG
============================================================
✅ Erfolgreich erstellt: 10/10
❌ Fehlgeschlagen: 0/10

✅ Erfolgreich erstellte Bots:
  • Group Bot 1 (ID: 2, @group_bot_1_1234567890bot)
  • Group Bot 2 (ID: 3, @group_bot_2_1234567890bot)
  ...

✅ Fertig!
```

