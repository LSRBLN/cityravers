# 📚 Funktions-Dokumentation

**Stand:** $(date)

Vollständige Übersicht aller Funktionen im Telegram Marketing Tool.

---

## 📋 Inhaltsverzeichnis

1. [API Endpoints (api.py)](#api-endpoints-apipy)
2. [Account Manager (account_manager.py)](#account-manager-account_managerpy)
3. [Bot Manager (bot_manager.py)](#bot-manager-bot_managerpy)
4. [Authentifizierung (auth.py)](#authentifizierung-authpy)
5. [Scheduler Service (scheduler_service.py)](#scheduler-service-scheduler_servicepy)
6. [Warming Service (warming_service.py)](#warming-service-warming_servicepy)
7. [Datenbank (database.py)](#datenbank-databasepy)
8. [Phone Providers (phone_providers.py)](#phone-providers-phone_providerspy)
9. [Message Storage (message_storage.py)](#message-storage-message_storagepy)

---

## 🔌 API Endpoints (api.py)

### Event Handlers

#### `startup_event()`
**Typ:** Event Handler  
**Beschreibung:** Wird beim Start des Backends ausgeführt.  
**Funktion:**
- Führt Datenbank-Migrationen aus
- Startet Scheduler-Service
- Lädt ausstehende Nachrichten
- Startet Account-Warming für aktive Accounts

**Wann wird es aufgerufen:** Automatisch beim Backend-Start

---

#### `shutdown_event()`
**Typ:** Event Handler  
**Beschreibung:** Wird beim Herunterfahren des Backends ausgeführt.  
**Funktion:**
- Trennt alle Telegram-Verbindungen
- Stoppt alle Warming-Aktivitäten
- Beendet Scheduler-Service

**Wann wird es aufgerufen:** Automatisch beim Backend-Shutdown

---

### Account Endpoints

#### `POST /api/accounts` - `create_account()`
**Beschreibung:** Erstellt einen neuen Telegram-Account (User oder Bot).  
**Funktion:**
- Prüft Account-Limit des Benutzers
- Erstellt Account in Datenbank
- Für User-Accounts: Fordert Login-Code an
- Für Bot-Accounts: Verbindet Bot direkt
- Unterstützt Proxy-Zuweisung

**Parameter:**
- `name`: Account-Name
- `account_type`: "user" oder "bot"
- `api_id`, `api_hash`: Telegram API Credentials (optional)
- `bot_token`: Bot-Token (für Bots)
- `phone_number`: Telefonnummer (für User)
- `session_name`: Session-Name (für User)
- `proxy_id`: Optional Proxy-ID

**Rückgabe:** Account-ID und Verbindungsstatus

---

#### `POST /api/accounts/{account_id}/request-code` - `request_code()`
**Beschreibung:** Fordert einen Login-Code für einen Account an.  
**Funktion:**
- Prüft ob Account existiert
- Prüft ob Telefonnummer vorhanden
- Sendet Code-Anfrage an Telegram
- Code wird per Telegram/Telefon gesendet

**Parameter:**
- `account_id`: Account-ID

**Rückgabe:** Status "code_required" oder "connected"

---

#### `POST /api/accounts/{account_id}/login` - `login_account()`
**Beschreibung:** Loggt einen Account mit Code oder 2FA-Passwort ein.  
**Funktion:**
- Validiert Code oder Passwort
- Verbindet Account mit Telegram
- Speichert Session-Datei
- Aktualisiert Account-Status

**Parameter:**
- `account_id`: Account-ID
- `code`: Telegram-Verifizierungscode (optional)
- `password`: 2FA-Passwort (optional)

**Rückgabe:** Verbindungsstatus und Account-Info

---

#### `GET /api/accounts` - `list_accounts()`
**Beschreibung:** Listet alle Accounts des aktuellen Benutzers.  
**Funktion:**
- Filtert Accounts nach Benutzer-ID
- Lädt Account-Informationen
- Zeigt Verbindungsstatus
- Zeigt Proxy-Informationen

**Rückgabe:** Liste von Accounts mit Details

---

#### `GET /api/accounts/{account_id}` - `get_account()`
**Beschreibung:** Gibt Details eines spezifischen Accounts zurück.  
**Funktion:**
- Lädt Account aus Datenbank
- Prüft Zugriffsrechte
- Lädt zusätzliche Informationen (Proxy, Statistiken)

**Parameter:**
- `account_id`: Account-ID

**Rückgabe:** Account-Details

---

#### `DELETE /api/accounts/{account_id}` - `delete_account()`
**Beschreibung:** Löscht einen Account.  
**Funktion:**
- Prüft Zugriffsrechte
- Trennt Telegram-Verbindung
- Löscht Account aus Datenbank
- Löscht zugehörige Session-Dateien

**Parameter:**
- `account_id`: Account-ID

**Rückgabe:** Erfolgsstatus

---

#### `GET /api/accounts/{account_id}/dialogs` - `get_dialogs()`
**Beschreibung:** Ruft alle Dialoge (Chats/Gruppen) eines Accounts ab.  
**Funktion:**
- Verbindet mit Telegram
- Lädt alle Dialoge
- Kategorisiert nach Typ (User, Gruppe, Kanal)
- Gibt Metadaten zurück

**Parameter:**
- `account_id`: Account-ID

**Rückgabe:** Liste von Dialogen

---

### Upload Endpoints

#### `POST /api/upload/session` - `upload_session()`
**Beschreibung:** Lädt eine Telegram Session-Datei hoch.  
**Funktion:**
- Validiert Dateiformat (.session)
- Speichert Datei im Upload-Verzeichnis
- Gibt Dateipfad zurück

**Parameter:**
- `file`: Session-Datei (.session)

**Rückgabe:** Dateipfad

---

#### `POST /api/upload/tdata` - `upload_tdata()`
**Beschreibung:** Lädt tdata-Ordner hoch (Telegram Desktop Daten).  
**Funktion:**
- Akzeptiert mehrere Dateien
- Erstellt tdata-Ordner
- Speichert alle Dateien
- Gibt Ordnerpfad zurück

**Parameter:**
- `files`: Mehrere Dateien aus tdata-Ordner

**Rückgabe:** tdata-Pfad und Dateiliste

---

#### `POST /api/accounts/from-session` - `create_account_from_session()`
**Beschreibung:** Erstellt einen Account aus einer hochgeladenen Session-Datei.  
**Funktion:**
- Extrahiert API Credentials aus Session
- Erstellt Account in Datenbank
- Versucht automatische Verbindung
- Gibt Verbindungsstatus zurück

**Parameter:**
- `name`: Account-Name
- `session_file_path`: Pfad zur Session-Datei
- `api_id`, `api_hash`: Optional (werden extrahiert)

**Rückgabe:** Account-ID und Verbindungsstatus

---

### Gruppen Endpoints

#### `POST /api/groups` - `create_group()`
**Beschreibung:** Erstellt eine neue Gruppe in der Datenbank.  
**Funktion:**
- Prüft Gruppen-Limit
- Erstellt Gruppe in Datenbank
- Validiert Chat-ID oder Name
- Speichert Gruppendetails

**Parameter:**
- `name`: Gruppenname
- `chat_id`: Telegram Chat-ID (optional)
- `chat_type`: Typ (group, channel, private)
- `username`: Username (optional)

**Rückgabe:** Gruppen-ID

---

#### `GET /api/groups` - `list_groups()`
**Beschreibung:** Listet alle Gruppen des aktuellen Benutzers.  
**Funktion:**
- Filtert nach Benutzer-ID
- Lädt Gruppendetails
- Zeigt Metadaten (Mitgliederzahl, Typ)

**Rückgabe:** Liste von Gruppen

---

#### `DELETE /api/groups/{group_id}` - `delete_group()`
**Beschreibung:** Löscht eine Gruppe.  
**Funktion:**
- Prüft Zugriffsrechte
- Löscht Gruppe aus Datenbank

**Parameter:**
- `group_id`: Gruppen-ID

**Rückgabe:** Erfolgsstatus

---

#### `POST /api/groups/search-by-name` - `search_groups_by_name()`
**Beschreibung:** Sucht Gruppen nach Namen und fügt sie hinzu.  
**Funktion:**
- Verwendet Telegram-Account zum Suchen
- Findet Gruppen nach Name/Username
- Erstellt Gruppen in Datenbank
- Gibt gefundene Gruppen zurück

**Parameter:**
- `account_id`: Account-ID für Suche
- `group_names`: Liste von Gruppennamen

**Rückgabe:** Liste von gefundenen Gruppen

---

#### `POST /api/groups/bulk` - `bulk_create_groups()`
**Beschreibung:** Erstellt mehrere Gruppen auf einmal.  
**Funktion:**
- Ruft `search_groups_by_name()` für mehrere Namen auf
- Erstellt alle gefundenen Gruppen
- Gibt Erfolgs-/Fehlerstatistiken zurück

**Parameter:**
- `account_id`: Account-ID
- `group_names`: Liste von Gruppennamen

**Rückgabe:** Liste von erstellten Gruppen

---

### Bulk Operations

#### `POST /api/accounts/bulk-bots` - `bulk_create_bots()`
**Beschreibung:** Erstellt mehrere Bot-Accounts auf einmal.  
**Funktion:**
- Parst Bot-Liste (Name:Token Format)
- Erstellt jeden Bot in Datenbank
- Verbindet alle Bots
- Gibt Erfolgs-/Fehlerstatistiken zurück

**Parameter:**
- `bots`: Liste von Bot-Daten [{"name": "...", "bot_token": "..."}]

**Rückgabe:** Erfolgs-/Fehlerstatistiken

---

### Authentifizierung

#### `POST /api/auth/register` - `register_user()`
**Beschreibung:** Registriert einen neuen Benutzer.  
**Funktion:**
- Validiert Email und Username
- Erstellt Passwort-Hash
- Erstellt User in Datenbank
- Erstellt automatisches Free Trial (7 Tage)
- Gibt JWT Token zurück

**Parameter:**
- `email`: E-Mail-Adresse
- `username`: Benutzername
- `password`: Passwort

**Rückgabe:** JWT Token und User-Info

---

#### `POST /api/auth/login` - `login_user()`
**Beschreibung:** Loggt einen Benutzer ein.  
**Funktion:**
- Validiert Email/Username und Passwort
- Erstellt JWT Token
- Aktualisiert last_login
- Gibt Token und User-Info zurück

**Parameter:**
- `username`: Email oder Username
- `password`: Passwort

**Rückgabe:** JWT Token und User-Info

---

#### `GET /api/auth/me` - `get_current_user_info()`
**Beschreibung:** Gibt Informationen über den aktuellen Benutzer zurück.  
**Funktion:**
- Lädt User aus JWT Token
- Lädt Abonnement-Informationen
- Gibt User-Details zurück

**Rückgabe:** User-Info und Abonnement-Status

---

### Phone Number Purchase

#### `POST /api/phone/buy-number` - `buy_phone_number()`
**Beschreibung:** Kauft eine Telefonnummer über SMS-Provider.  
**Funktion:**
- Wählt Provider (5sim, SMS-Activate, etc.)
- Kauft Telefonnummer
- Wartet auf SMS-Code (Polling)
- Speichert Nummer in Datenbank
- Erstellt automatisch Telegram-Account (optional)

**Parameter:**
- `provider`: Provider-Name
- `country`: Ländercode
- `service`: Service-Name (telegram)
- `operator`: Mobilfunkbetreiber (optional)

**Rückgabe:** Telefonnummer und SMS-Code

---

### Subscriptions

#### `GET /api/subscriptions/plans` - `get_subscription_plans()`
**Beschreibung:** Gibt verfügbare Abonnement-Pakete zurück.  
**Funktion:**
- Definiert Paket-Typen (free_trial, basic, pro, enterprise)
- Gibt Features pro Paket zurück
- Gibt Preise zurück

**Rückgabe:** Liste von Paketen mit Features

---

#### `POST /api/subscriptions/purchase` - `purchase_subscription()`
**Beschreibung:** Kauft ein Abonnement-Paket.  
**Funktion:**
- Validiert Paket-Typ
- Erstellt/aktualisiert Abonnement
- Setzt Ablaufdatum
- Aktualisiert Limits

**Parameter:**
- `plan_type`: Paket-Typ
- `duration_days`: Laufzeit in Tagen

**Rückgabe:** Abonnement-Details

---

### Scheduled Messages

#### `POST /api/scheduled-messages` - `create_scheduled_message()`
**Beschreibung:** Erstellt eine geplante Nachricht.  
**Funktion:**
- Validiert Account und Gruppen
- Erstellt geplante Nachricht in Datenbank
- Plant Nachricht im Scheduler
- Unterstützt Multi-Gruppen

**Parameter:**
- `account_id`: Account-ID
- `group_ids`: Liste von Gruppen-IDs
- `message`: Nachrichtentext
- `scheduled_time`: Geplante Zeit
- `delay`: Delay zwischen Nachrichten
- `batch_size`: Nachrichten pro Batch
- `repeat_count`: Wiederholungen

**Rückgabe:** Nachrichten-ID

---

#### `GET /api/scheduled-messages` - `list_scheduled_messages()`
**Beschreibung:** Listet alle geplanten Nachrichten.  
**Funktion:**
- Filtert nach Benutzer
- Lädt Nachrichtendetails
- Zeigt Status (pending, running, completed, failed)

**Rückgabe:** Liste von geplanten Nachrichten

---

#### `GET /api/scheduled-messages/{message_id}` - `get_scheduled_message()`
**Beschreibung:** Gibt Details einer geplanten Nachricht zurück.  
**Funktion:**
- Lädt Nachricht aus Datenbank
- Prüft Zugriffsrechte
- Gibt vollständige Details zurück

**Parameter:**
- `message_id`: Nachrichten-ID

**Rückgabe:** Nachrichtendetails

---

#### `PUT /api/scheduled-messages/{message_id}` - `update_scheduled_message()`
**Beschreibung:** Aktualisiert eine geplante Nachricht.  
**Funktion:**
- Lädt Nachricht aus Datenbank
- Aktualisiert Felder
- Re-plant Nachricht im Scheduler (falls Zeit geändert)

**Parameter:**
- `message_id`: Nachrichten-ID
- `message`: Neuer Text (optional)
- `scheduled_time`: Neue Zeit (optional)
- Weitere Parameter optional

**Rückgabe:** Aktualisierte Nachricht

---

#### `DELETE /api/scheduled-messages/{message_id}` - `cancel_scheduled_message()`
**Beschreibung:** Bricht eine geplante Nachricht ab.  
**Funktion:**
- Entfernt Nachricht aus Scheduler
- Setzt Status auf "cancelled"
- Speichert in Datenbank

**Parameter:**
- `message_id`: Nachrichten-ID

**Rückgabe:** Erfolgsstatus

---

### Test & Send

#### `POST /api/send-test` - `send_test_message()`
**Beschreibung:** Sendet eine Testnachricht sofort.  
**Funktion:**
- Validiert Account und Gruppe
- Sendet Nachricht sofort
- Speichert in Sent-Messages
- Aktualisiert Statistiken

**Parameter:**
- `account_id`: Account-ID
- `group_id`: Gruppen-ID
- `message`: Nachrichtentext

**Rückgabe:** Erfolgsstatus

---

### Scraping

#### `POST /api/scrape/group-members` - `scrape_group_members()`
**Beschreibung:** Scrapt Mitglieder aus einer Gruppe.  
**Funktion:**
- Verbindet mit Telegram
- Lädt Gruppenmitglieder
- Speichert User-Informationen
- Gibt Liste zurück

**Parameter:**
- `account_id`: Account-ID
- `group_entity`: Gruppen-ID oder Username
- `limit`: Maximale Anzahl (Standard: 10000)

**Rückgabe:** Liste von gescrapten Usern

---

#### `GET /api/scraped-users` - `list_scraped_users()`
**Beschreibung:** Listet alle gescrapten User.  
**Funktion:**
- Filtert nach aktiven Usern
- Lädt User-Details
- Zeigt Quell-Gruppe

**Rückgabe:** Liste von gescrapten Usern

---

### Invites

#### `POST /api/invite/users` - `invite_users_to_group()`
**Beschreibung:** Lädt User zu einer Gruppe ein.  
**Funktion:**
- Prüft ob Account Admin ist
- Lädt User zur Gruppe ein
- Rate Limiting zwischen Einladungen
- Gibt Erfolgs-/Fehlerstatistiken zurück

**Parameter:**
- `account_id`: Account-ID (muss Admin sein)
- `group_entity`: Gruppen-ID oder Username
- `user_ids`: Liste von User-IDs oder Usernames
- `delay`: Delay zwischen Einladungen

**Rückgabe:** Erfolgs-/Fehlerstatistiken

---

#### `POST /api/invite/from-scraped` - `invite_from_scraped()`
**Beschreibung:** Lädt gescrapte User zu einer Gruppe ein.  
**Funktion:**
- Lädt gescrapte User aus Datenbank
- Lädt sie zur Gruppe ein
- Rate Limiting
- Gibt Statistiken zurück

**Parameter:**
- `account_id`: Account-ID
- `group_entity`: Gruppen-ID oder Username
- `limit`: Maximale Anzahl
- `delay`: Delay zwischen Einladungen

**Rückgabe:** Erfolgs-/Fehlerstatistiken

---

#### `POST /api/accounts/add-to-groups` - `add_account_to_groups()`
**Beschreibung:** Fügt einen Account zu mehreren Gruppen hinzu.  
**Funktion:**
- Verbindet Account mit Telegram
- Fügt Account zu Gruppen hinzu
- Rate Limiting zwischen Gruppen
- Gibt Statistiken zurück

**Parameter:**
- `account_id`: Account-ID
- `group_entities`: Liste von Gruppen-IDs oder Usernames
- `delay`: Delay zwischen Gruppen

**Rückgabe:** Erfolgs-/Fehlerstatistiken

---

### Messages

#### `POST /api/messages/get-group-messages` - `get_group_messages()`
**Beschreibung:** Ruft Nachrichten aus einer Gruppe ab.  
**Funktion:**
- Verbindet mit Telegram
- Lädt Nachrichten aus Gruppe
- Gibt Metadaten zurück (ID, Text, Datum, etc.)

**Parameter:**
- `account_id`: Account-ID
- `group_entity`: Gruppen-ID oder Username
- `limit`: Maximale Anzahl (Standard: 100)

**Rückgabe:** Liste von Nachrichten

---

#### `POST /api/messages/forward` - `forward_message()`
**Beschreibung:** Leitet Nachrichten weiter.  
**Funktion:**
- Lädt Nachrichten aus Quell-Gruppe
- Leitet sie an Ziel-Gruppen weiter
- Rate Limiting
- Gibt Statistiken zurück

**Parameter:**
- `account_id`: Account-ID
- `source_group`: Quell-Gruppe
- `message_ids`: Liste von Message-IDs
- `target_groups`: Liste von Ziel-Gruppen
- `delay`: Delay zwischen Weiterleitungen

**Rückgabe:** Erfolgs-/Fehlerstatistiken

---

### Warming

#### `POST /api/warming/config` - `create_warming_config()`
**Beschreibung:** Erstellt oder aktualisiert Warming-Konfiguration.  
**Funktion:**
- Erstellt Warming-Konfiguration für Account
- Setzt Aktivitäts-Limits
- Setzt Zeitplanung
- Aktiviert Warming

**Parameter:**
- `account_id`: Account-ID
- `is_active`: Aktivierungsstatus
- `read_messages_per_day`: Nachrichten lesen pro Tag
- `scroll_dialogs_per_day`: Dialoge scrollen pro Tag
- `reactions_per_day`: Reaktionen pro Tag
- `start_time`, `end_time`: Zeitfenster
- `min_delay`, `max_delay`: Delay-Bereich

**Rückgabe:** Warming-Konfiguration

---

#### `GET /api/warming/config/{account_id}` - `get_warming_config()`
**Beschreibung:** Gibt Warming-Konfiguration zurück.  
**Funktion:**
- Lädt Konfiguration aus Datenbank
- Gibt alle Einstellungen zurück

**Parameter:**
- `account_id`: Account-ID

**Rückgabe:** Warming-Konfiguration

---

#### `PUT /api/warming/config/{account_id}` - `update_warming_config()`
**Beschreibung:** Aktualisiert Warming-Konfiguration.  
**Funktion:**
- Lädt bestehende Konfiguration
- Aktualisiert Felder
- Speichert Änderungen

**Parameter:**
- `account_id`: Account-ID
- Alle Warming-Parameter (optional)

**Rückgabe:** Aktualisierte Konfiguration

---

#### `GET /api/warming/activities/{account_id}` - `get_warming_activities()`
**Beschreibung:** Gibt Warming-Aktivitäten zurück.  
**Funktion:**
- Lädt Aktivitäts-Log aus Datenbank
- Filtert nach Account
- Gibt chronologische Liste zurück

**Parameter:**
- `account_id`: Account-ID

**Rückgabe:** Liste von Aktivitäten

---

#### `GET /api/warming/stats` - `get_all_warming_stats()`
**Beschreibung:** Gibt Statistiken aller Warming-Konfigurationen zurück.  
**Funktion:**
- Lädt alle aktiven Warmings
- Berechnet Statistiken
- Gibt Übersicht zurück

**Rückgabe:** Liste von Warming-Statistiken

---

### Message Templates

#### `POST /api/message-templates` - `create_message_template()`
**Beschreibung:** Erstellt eine Nachrichtenvorlage.  
**Funktion:**
- Erstellt Vorlage in Datenbank
- Speichert Nachrichtentext
- Setzt Kategorie und Tags

**Parameter:**
- `name`: Vorlagenname
- `message`: Nachrichtentext
- `category`: Kategorie (optional)
- `tags`: Tags (optional)

**Rückgabe:** Vorlagen-ID

---

#### `GET /api/message-templates` - `list_message_templates()`
**Beschreibung:** Listet alle Nachrichtenvorlagen.  
**Funktion:**
- Lädt Vorlagen aus Datenbank
- Filtert nach aktiven Vorlagen
- Gibt Liste zurück

**Rückgabe:** Liste von Vorlagen

---

#### `GET /api/message-templates/{template_id}` - `get_message_template()`
**Beschreibung:** Gibt eine Vorlage zurück.  
**Funktion:**
- Lädt Vorlage aus Datenbank
- Gibt Details zurück

**Parameter:**
- `template_id`: Vorlagen-ID

**Rückgabe:** Vorlagendetails

---

#### `PUT /api/message-templates/{template_id}` - `update_message_template()`
**Beschreibung:** Aktualisiert eine Vorlage.  
**Funktion:**
- Lädt Vorlage aus Datenbank
- Aktualisiert Felder
- Speichert Änderungen

**Parameter:**
- `template_id`: Vorlagen-ID
- Alle Felder optional

**Rückgabe:** Aktualisierte Vorlage

---

#### `DELETE /api/message-templates/{template_id}` - `delete_message_template()`
**Beschreibung:** Löscht eine Vorlage.  
**Funktion:**
- Lädt Vorlage aus Datenbank
- Löscht aus Datenbank

**Parameter:**
- `template_id`: Vorlagen-ID

**Rückgabe:** Erfolgsstatus

---

### Statistics

#### `GET /api/sent-messages` - `list_sent_messages()`
**Beschreibung:** Listet gesendete Nachrichten.  
**Funktion:**
- Filtert nach Benutzer
- Lädt Nachrichten-Historie
- Zeigt Erfolgs-/Fehlerstatus

**Rückgabe:** Liste von gesendeten Nachrichten

---

#### `GET /api/accounts/{account_id}/statistics` - `get_account_statistics_endpoint()`
**Beschreibung:** Gibt Statistiken für einen Account zurück.  
**Funktion:**
- Lädt Account-Statistiken
- Berechnet Gesamtstatistiken
- Gibt Übersicht zurück

**Parameter:**
- `account_id`: Account-ID

**Rückgabe:** Account-Statistiken

---

### Proxies

#### `POST /api/proxies` - `create_proxy()`
**Beschreibung:** Erstellt einen neuen Proxy.  
**Funktion:**
- Verschlüsselt Passwörter
- Erstellt Proxy in Datenbank
- Speichert Konfiguration

**Parameter:**
- `name`: Proxy-Name
- `proxy_type`: Typ (socks5, http, https, mtproto)
- `host`: Host-Adresse
- `port`: Port
- `username`, `password`: Credentials (optional)
- `secret`: Secret (für MTProto)

**Rückgabe:** Proxy-ID

---

#### `GET /api/proxies` - `list_proxies()`
**Beschreibung:** Listet alle Proxies.  
**Funktion:**
- Lädt Proxies aus Datenbank
- Entschlüsselt Passwörter für Anzeige
- Filtert nach aktiven Proxies

**Rückgabe:** Liste von Proxies

---

#### `GET /api/proxies/{proxy_id}` - `get_proxy()`
**Beschreibung:** Gibt einen Proxy zurück.  
**Funktion:**
- Lädt Proxy aus Datenbank
- Entschlüsselt Passwörter
- Gibt Details zurück

**Parameter:**
- `proxy_id`: Proxy-ID

**Rückgabe:** Proxy-Details

---

#### `PUT /api/proxies/{proxy_id}` - `update_proxy()`
**Beschreibung:** Aktualisiert einen Proxy.  
**Funktion:**
- Lädt Proxy aus Datenbank
- Aktualisiert Felder
- Verschlüsselt neue Passwörter
- Speichert Änderungen

**Parameter:**
- `proxy_id`: Proxy-ID
- Alle Felder optional

**Rückgabe:** Aktualisierter Proxy

---

#### `DELETE /api/proxies/{proxy_id}` - `delete_proxy()`
**Beschreibung:** Löscht einen Proxy.  
**Funktion:**
- Lädt Proxy aus Datenbank
- Löscht aus Datenbank

**Parameter:**
- `proxy_id`: Proxy-ID

**Rückgabe:** Erfolgsstatus

---

#### `POST /api/proxies/bulk` - `bulk_create_proxies()`
**Beschreibung:** Erstellt mehrere Proxies auf einmal.  
**Funktion:**
- Parst Proxy-Liste
- Erstellt jeden Proxy
- Verschlüsselt Passwörter
- Gibt Statistiken zurück

**Parameter:**
- `proxies`: Liste von Proxy-Daten

**Rückgabe:** Erfolgs-/Fehlerstatistiken

---

#### `POST /api/proxies/{proxy_id}/test` - `test_proxy()`
**Beschreibung:** Testet einen Proxy.  
**Funktion:**
- Verbindet mit Proxy
- Testet Verbindung
- Gibt Ergebnis zurück

**Parameter:**
- `proxy_id`: Proxy-ID

**Rückgabe:** Test-Ergebnis

---

#### `POST /api/accounts/{account_id}/assign-proxy` - `assign_proxy_to_account()`
**Beschreibung:** Weist einem Account einen Proxy zu.  
**Funktion:**
- Lädt Account und Proxy
- Weist Proxy zu
- Speichert Änderung

**Parameter:**
- `account_id`: Account-ID
- `proxy_id`: Proxy-ID (oder null zum Entfernen)

**Rückgabe:** Erfolgsstatus

---

## 👤 Account Manager (account_manager.py)

### `AccountManager` Klasse

#### `add_account()`
**Beschreibung:** Fügt einen Telegram-Account hinzu und verbindet.  
**Funktion:**
- Erstellt TelegramClient
- Konfiguriert Proxy (falls vorhanden)
- Prüft ob bereits autorisiert
- Sendet Code-Anfrage (falls nötig)
- Loggt mit Code/Passwort ein
- Speichert Account-Info

**Parameter:**
- `account_id`: Datenbank-ID
- `api_id`, `api_hash`: API Credentials
- `session_name`: Session-Name
- `phone_number`: Telefonnummer
- `code`: Verifizierungscode
- `password`: 2FA-Passwort
- `session_file_path`: Pfad zur Session-Datei
- `proxy_config`: Proxy-Konfiguration

**Rückgabe:** Status-Dict (connected, code_required, password_required, error)

---

#### `remove_account()`
**Beschreibung:** Entfernt einen Account.  
**Funktion:**
- Trennt Telegram-Verbindung
- Entfernt aus internem Cache

**Parameter:**
- `account_id`: Account-ID

---

#### `get_account_info()`
**Beschreibung:** Gibt Account-Informationen zurück.  
**Funktion:**
- Lädt Info aus Cache
- Gibt User-Details zurück

**Parameter:**
- `account_id`: Account-ID

**Rückgabe:** Account-Info-Dict

---

#### `list_accounts()`
**Beschreibung:** Listet alle verbundenen Accounts.  
**Funktion:**
- Gibt alle Account-Infos zurück

**Rückgabe:** Liste von Account-Infos

---

#### `send_message()`
**Beschreibung:** Sendet eine Nachricht über einen Account.  
**Funktion:**
- Validiert Account-Verbindung
- Sendet Nachricht an Entity
- Behandelt FloodWait-Fehler
- Gibt Ergebnis zurück

**Parameter:**
- `account_id`: Account-ID
- `entity`: Chat-ID, Username oder Telefonnummer
- `message`: Nachrichtentext
- `delay`: Verzögerung nach dem Senden

**Rückgabe:** Erfolgsstatus oder Fehler

---

#### `get_dialogs()`
**Beschreibung:** Ruft alle Dialoge eines Accounts ab.  
**Funktion:**
- Verbindet mit Telegram
- Lädt alle Dialoge
- Kategorisiert nach Typ
- Gibt Liste zurück

**Parameter:**
- `account_id`: Account-ID

**Rückgabe:** Liste von Dialogen

---

#### `send_to_multiple_groups()`
**Beschreibung:** Sendet eine Nachricht an mehrere Gruppen.  
**Funktion:**
- Iteriert über Gruppen
- Sendet Nachricht an jede Gruppe
- Rate Limiting zwischen Gruppen
- Gibt Statistiken zurück

**Parameter:**
- `account_id`: Account-ID
- `group_ids`: Liste von Chat-IDs
- `message`: Nachrichtentext
- `delay`: Delay zwischen Nachrichten
- `group_delay`: Delay zwischen Gruppen

**Rückgabe:** Erfolgs-/Fehlerstatistiken

---

#### `scrape_group_members()`
**Beschreibung:** Scrapt Mitglieder aus einer Gruppe.  
**Funktion:**
- Verbindet mit Telegram
- Lädt Gruppenmitglieder
- Filtert Bots
- Speichert User-Informationen
- Rate Limiting

**Parameter:**
- `account_id`: Account-ID
- `group_entity`: Gruppen-ID oder Username
- `limit`: Maximale Anzahl

**Rückgabe:** Liste von User-Informationen

---

#### `invite_users_to_group()`
**Beschreibung:** Lädt User zu einer Gruppe ein.  
**Funktion:**
- Prüft Admin-Rechte
- Lädt User zur Gruppe ein
- Rate Limiting
- Behandelt Privacy-Fehler

**Parameter:**
- `account_id`: Account-ID
- `group_entity`: Gruppen-ID oder Username
- `user_ids`: Liste von User-IDs
- `delay`: Delay zwischen Einladungen

**Rückgabe:** Erfolgs-/Fehlerstatistiken

---

#### `add_account_to_groups()`
**Beschreibung:** Fügt einen Account zu mehreren Gruppen hinzu.  
**Funktion:**
- Prüft ob bereits Mitglied
- Fügt Account zu Gruppen hinzu
- Rate Limiting

**Parameter:**
- `account_id`: Account-ID
- `group_entities`: Liste von Gruppen
- `delay`: Delay zwischen Gruppen

**Rückgabe:** Erfolgs-/Fehlerstatistiken

---

#### `forward_message()`
**Beschreibung:** Leitet Nachrichten weiter.  
**Funktion:**
- Lädt Nachrichten aus Quell-Gruppe
- Leitet an Ziel-Gruppen weiter
- Rate Limiting

**Parameter:**
- `account_id`: Account-ID
- `source_group`: Quell-Gruppe
- `message_ids`: Liste von Message-IDs
- `target_groups`: Liste von Ziel-Gruppen
- `delay`: Delay zwischen Weiterleitungen

**Rückgabe:** Erfolgs-/Fehlerstatistiken

---

#### `get_group_messages()`
**Beschreibung:** Ruft Nachrichten aus einer Gruppe ab.  
**Funktion:**
- Verbindet mit Telegram
- Lädt Nachrichten
- Gibt Metadaten zurück

**Parameter:**
- `account_id`: Account-ID
- `group_entity`: Gruppen-ID oder Username
- `limit`: Maximale Anzahl

**Rückgabe:** Liste von Nachrichten

---

#### `warm_account_read_messages()`
**Beschreibung:** Liest Nachrichten (für Account-Warming).  
**Funktion:**
- Simuliert Lesen durch Pausen
- Liest Nachrichten ohne zu markieren

**Parameter:**
- `account_id`: Account-ID
- `group_entity`: Gruppen-ID oder Username
- `limit`: Anzahl zu lesender Nachrichten

**Rückgabe:** Erfolgsstatus

---

#### `warm_account_scroll_dialogs()`
**Beschreibung:** Scrollt durch Dialoge (für Account-Warming).  
**Funktion:**
- Simuliert Chat-Öffnen
- Scrollt durch Dialoge

**Parameter:**
- `account_id`: Account-ID
- `limit`: Anzahl Dialoge

**Rückgabe:** Erfolgsstatus

---

#### `warm_account_send_reaction()`
**Beschreibung:** Sendet eine Reaktion (für Account-Warming).  
**Funktion:**
- Sendet Reaktion auf Nachricht
- Behandelt FloodWait

**Parameter:**
- `account_id`: Account-ID
- `group_entity`: Gruppen-ID oder Username
- `message_id`: Message-ID
- `reaction`: Reaktions-Emoji

**Rückgabe:** Erfolgsstatus

---

#### `warm_account_send_small_message()`
**Beschreibung:** Sendet eine kleine Nachricht (für Account-Warming).  
**Funktion:**
- Sendet kurze Nachricht
- Behandelt FloodWait

**Parameter:**
- `account_id`: Account-ID
- `group_entity`: Gruppen-ID oder Username
- `message`: Nachrichtentext

**Rückgabe:** Erfolgsstatus

---

#### `check_group_exists()`
**Beschreibung:** Prüft ob eine Gruppe existiert.  
**Funktion:**
- Verbindet mit Telegram
- Prüft Gruppen-Existenz
- Gibt Informationen zurück

**Parameter:**
- `account_id`: Account-ID
- `group_entity`: Gruppen-ID oder Username

**Rückgabe:** Gruppen-Info oder Fehler

---

#### `check_bot_can_be_added()`
**Beschreibung:** Prüft ob ein Bot zu einer Gruppe hinzugefügt werden kann.  
**Funktion:**
- Prüft Gruppen-Existenz
- Prüft Admin-Rechte
- Prüft Bot-Existenz
- Prüft ob Bot bereits in Gruppe

**Parameter:**
- `account_id`: Account-ID
- `group_entity`: Gruppen-ID oder Username
- `bot_username`: Bot-Username (optional)
- `bot_id`: Bot-ID (optional)

**Rückgabe:** Prüf-Ergebnisse

---

#### `create_bot_via_botfather()`
**Beschreibung:** Erstellt einen Bot über BotFather.  
**Funktion:**
- Sendet /newbot Befehl
- Sendet Bot-Namen
- Sendet Bot-Username
- Extrahiert Bot-Token aus Antwort
- Gibt Token zurück

**Parameter:**
- `account_id`: Account-ID
- `bot_name`: Bot-Name
- `bot_username`: Bot-Username
- `timeout`: Timeout für Antworten

**Rückgabe:** Bot-Token und Info

---

#### `disconnect_all()`
**Beschreibung:** Trennt alle Verbindungen.  
**Funktion:**
- Trennt alle Accounts
- Leert Cache

---

## 🤖 Bot Manager (bot_manager.py)

### `BotManager` Klasse

#### `add_bot()`
**Beschreibung:** Fügt einen Bot hinzu und verbindet.  
**Funktion:**
- Erstellt Bot-Instanz
- Verbindet mit Telegram Bot API
- Speichert Bot-Info
- Gibt Verbindungsstatus zurück

**Parameter:**
- `bot_id`: Datenbank-ID
- `bot_token`: Bot-Token

**Rückgabe:** Status-Dict

---

#### `remove_bot()`
**Beschreibung:** Entfernt einen Bot.  
**Funktion:**
- Trennt Bot-Verbindung
- Entfernt aus Cache

**Parameter:**
- `bot_id`: Bot-ID

---

#### `get_bot_info()`
**Beschreibung:** Gibt Bot-Informationen zurück.  
**Funktion:**
- Lädt Info aus Cache
- Gibt Bot-Details zurück

**Parameter:**
- `bot_id`: Bot-ID

**Rückgabe:** Bot-Info-Dict

---

#### `list_bots()`
**Beschreibung:** Listet alle verbundenen Bots.  
**Funktion:**
- Gibt alle Bot-Infos zurück

**Rückgabe:** Liste von Bot-Infos

---

#### `disconnect_all()`
**Beschreibung:** Trennt alle Bot-Verbindungen.  
**Funktion:**
- Trennt alle Bots
- Leert Cache

---

## 🔐 Authentifizierung (auth.py)

### `verify_password()`
**Beschreibung:** Verifiziert ein Passwort gegen einen Hash.  
**Funktion:**
- Verwendet bcrypt zum Vergleich
- Konvertiert Strings zu Bytes
- Gibt True/False zurück

**Parameter:**
- `plain_password`: Klartext-Passwort
- `hashed_password`: Gehashtes Passwort

**Rückgabe:** True wenn Passwort korrekt

---

### `get_password_hash()`
**Beschreibung:** Erstellt einen Passwort-Hash.  
**Funktion:**
- Verwendet bcrypt
- Generiert Salt
- Gibt Hash zurück

**Parameter:**
- `password`: Klartext-Passwort

**Rückgabe:** Gehashtes Passwort

---

### `create_access_token()`
**Beschreibung:** Erstellt ein JWT Token.  
**Funktion:**
- Erstellt Token mit User-ID
- Setzt Ablaufzeit
- Verschlüsselt mit Secret Key

**Parameter:**
- `data`: Token-Daten (User-ID)
- `expires_delta`: Ablaufzeit (optional)

**Rückgabe:** JWT Token

---

### `get_db()`
**Beschreibung:** Dependency für Datenbank-Session.  
**Funktion:**
- Erstellt Session
- Gibt Session zurück
- Schließt Session automatisch

**Rückgabe:** Datenbank-Session

---

### `get_current_user()`
**Beschreibung:** Gibt aktuellen Benutzer aus JWT Token zurück.  
**Funktion:**
- Dekodiert JWT Token
- Lädt User aus Datenbank
- Gibt User zurück

**Parameter:**
- `token`: JWT Token (automatisch aus Header)
- `db`: Datenbank-Session

**Rückgabe:** User-Objekt

---

### `get_current_active_user()`
**Beschreibung:** Prüft ob Benutzer aktiv ist.  
**Funktion:**
- Prüft `is_active` Flag
- Wirft Fehler wenn inaktiv

**Parameter:**
- `current_user`: User aus `get_current_user()`

**Rückgabe:** Aktiver User

---

### `get_current_admin()`
**Beschreibung:** Prüft ob Benutzer Admin ist.  
**Funktion:**
- Prüft `is_admin` Flag
- Wirft Fehler wenn kein Admin

**Parameter:**
- `current_user`: User aus `get_current_active_user()`

**Rückgabe:** Admin-User

---

### `check_subscription()`
**Beschreibung:** Prüft ob Benutzer aktives Abonnement hat.  
**Funktion:**
- Prüft Abonnement-Existenz
- Prüft Abonnement-Status
- Prüft Feature-Verfügbarkeit (optional)

**Parameter:**
- `user`: User-Objekt
- `feature`: Feature-Name (optional)

**Rückgabe:** True wenn Abonnement aktiv

---

### `check_account_limit()`
**Beschreibung:** Prüft ob Benutzer noch Accounts erstellen kann.  
**Funktion:**
- Prüft aktuelle Account-Anzahl
- Vergleicht mit Abonnement-Limit
- Berücksichtigt Free Trial (2 Accounts)

**Parameter:**
- `user`: User-Objekt
- `current_count`: Aktuelle Account-Anzahl

**Rückgabe:** True wenn Limit nicht erreicht

---

### `check_group_limit()`
**Beschreibung:** Prüft ob Benutzer noch Gruppen erstellen kann.  
**Funktion:**
- Prüft aktuelle Gruppen-Anzahl
- Vergleicht mit Abonnement-Limit
- Berücksichtigt Free Trial (5 Gruppen)

**Parameter:**
- `user`: User-Objekt
- `current_count`: Aktuelle Gruppen-Anzahl

**Rückgabe:** True wenn Limit nicht erreicht

---

## ⏰ Scheduler Service (scheduler_service.py)

### `SchedulerService` Klasse

#### `schedule_message()`
**Beschreibung:** Plant eine Nachricht.  
**Funktion:**
- Erstellt Job im Scheduler
- Setzt Ausführungszeit
- Speichert Job-ID

**Parameter:**
- `scheduled_msg`: ScheduledMessage-Objekt

---

#### `_execute_scheduled_message()`
**Beschreibung:** Führt eine geplante Nachricht aus.  
**Funktion:**
- Lädt Nachricht aus Datenbank
- Sendet an alle Gruppen
- Wiederholt nach `repeat_count`
- Batch-Verarbeitung
- Rate Limiting
- Aktualisiert Status

**Parameter:**
- `message_id`: Nachrichten-ID

---

#### `cancel_message()`
**Beschreibung:** Bricht eine geplante Nachricht ab.  
**Funktion:**
- Entfernt Job aus Scheduler
- Setzt Status auf "cancelled"

**Parameter:**
- `message_id`: Nachrichten-ID

---

#### `load_pending_messages()`
**Beschreibung:** Lädt ausstehende Nachrichten beim Start.  
**Funktion:**
- Lädt alle pending/completed Nachrichten
- Plant sie neu im Scheduler

---

#### `start()`
**Beschreibung:** Startet Scheduler.  
**Funktion:**
- Startet APScheduler
- Aktiviert Job-Verarbeitung

---

#### `shutdown()`
**Beschreibung:** Beendet Scheduler.  
**Funktion:**
- Stoppt alle Jobs
- Beendet Scheduler

---

## 🔥 Warming Service (warming_service.py)

### `WarmingService` Klasse

#### `start_warming()`
**Beschreibung:** Startet Account-Warming.  
**Funktion:**
- Erstellt Warming-Konfiguration
- Plant Aktivitäten
- Startet Warming-Prozess

**Parameter:**
- `account_id`: Account-ID
- `config`: Warming-Konfiguration

---

#### `stop_warming()`
**Beschreibung:** Stoppt Account-Warming.  
**Funktion:**
- Stoppt alle Aktivitäten
- Setzt Status auf inaktiv

**Parameter:**
- `warming_id`: Warming-ID

---

#### `start_all_active_warmings()`
**Beschreibung:** Startet alle aktiven Warmings beim Start.  
**Funktion:**
- Lädt alle aktiven Warmings
- Startet jeden Warming

---

#### `stop_all_warmings()`
**Beschreibung:** Stoppt alle Warmings.  
**Funktion:**
- Stoppt alle aktiven Warmings

---

#### `_execute_warming_activity()`
**Beschreibung:** Führt eine Warming-Aktivität aus.  
**Funktion:**
- Wählt zufällige Aktivität
- Führt Aktivität aus
- Speichert in Log
- Rate Limiting

**Parameter:**
- `warming_id`: Warming-ID

---

## 🗄️ Datenbank (database.py)

### Modelle

#### `User`
**Beschreibung:** Benutzer-Account für das Tool.  
**Felder:**
- `id`: Primärschlüssel
- `email`: E-Mail-Adresse (unique)
- `username`: Benutzername (unique)
- `password_hash`: Gehashtes Passwort
- `is_active`: Aktivierungsstatus
- `is_admin`: Admin-Status
- `created_at`: Erstellungsdatum
- `last_login`: Letzter Login

**Methoden:**
- `verify_password()`: Verifiziert Passwort
- `hash_password()`: Erstellt Passwort-Hash

---

#### `Account`
**Beschreibung:** Telegram Account (User oder Bot).  
**Felder:**
- `id`: Primärschlüssel
- `user_id`: Besitzer (Foreign Key)
- `name`: Account-Name
- `account_type`: "user" oder "bot"
- `api_id`, `api_hash`: API Credentials
- `bot_token`: Bot-Token
- `phone_number`: Telefonnummer
- `session_name`: Session-Name
- `proxy_id`: Proxy-Zuweisung
- `is_active`: Aktivierungsstatus
- `created_at`: Erstellungsdatum

---

#### `Group`
**Beschreibung:** Telegram Gruppe/Chat.  
**Felder:**
- `id`: Primärschlüssel
- `user_id`: Besitzer
- `name`: Gruppenname
- `chat_id`: Telegram Chat-ID (unique)
- `chat_type`: Typ (group, channel, private)
- `username`: Username
- `member_count`: Mitgliederanzahl
- `is_public`: Öffentlich/Privat
- `created_at`: Erstellungsdatum

---

#### `ScheduledMessage`
**Beschreibung:** Geplante Nachricht.  
**Felder:**
- `id`: Primärschlüssel
- `account_id`: Account (Foreign Key)
- `group_ids`: JSON-Array von Gruppen-IDs
- `message`: Nachrichtentext
- `scheduled_time`: Geplante Zeit
- `delay`: Delay zwischen Nachrichten
- `batch_size`: Nachrichten pro Batch
- `repeat_count`: Wiederholungen
- `status`: Status (pending, running, completed, failed)
- `sent_count`: Gesendete Nachrichten
- `failed_count`: Fehlgeschlagene Nachrichten

---

### Funktionen

#### `init_db()`
**Beschreibung:** Initialisiert die Datenbank.  
**Funktion:**
- Erstellt Engine (SQLite oder PostgreSQL)
- Erstellt alle Tabellen
- Gibt Engine zurück

**Parameter:**
- `db_path`: Pfad für SQLite (optional)

**Rückgabe:** SQLAlchemy Engine

---

#### `get_session()`
**Beschreibung:** Erstellt eine Datenbank-Session.  
**Funktion:**
- Erstellt SessionLocal
- Gibt Session zurück

**Parameter:**
- `engine`: Datenbank-Engine

**Rückgabe:** Datenbank-Session

---

## 📱 Phone Providers (phone_providers.py)

### `FiveSimProvider` Klasse

#### `buy_number()`
**Beschreibung:** Kauft eine Telefonnummer über 5sim.net.  
**Funktion:**
- Sendet API-Request
- Kauft Nummer
- Gibt Nummer und Order-ID zurück

**Parameter:**
- `country`: Ländercode
- `service`: Service-Name (telegram)
- `operator`: Mobilfunkbetreiber (optional)

**Rückgabe:** Nummer und Order-ID

---

#### `get_sms_code()`
**Beschreibung:** Ruft SMS-Code ab.  
**Funktion:**
- Pollt API für SMS
- Gibt Code zurück wenn verfügbar

**Parameter:**
- `order_id`: Order-ID

**Rückgabe:** SMS-Code oder None

---

#### `get_balance()`
**Beschreibung:** Ruft Guthaben ab.  
**Funktion:**
- Sendet API-Request
- Gibt Guthaben zurück

**Rückgabe:** Guthaben

---

#### `cancel_order()`
**Beschreibung:** Storniert Bestellung.  
**Funktion:**
- Sendet Stornierungs-Request
- Gibt Erfolgsstatus zurück

**Parameter:**
- `order_id`: Order-ID

**Rückgabe:** Erfolgsstatus

---

#### `finish_order()`
**Beschreibung:** Schließt Bestellung ab.  
**Funktion:**
- Sendet Abschluss-Request
- Gibt Erfolgsstatus zurück

**Parameter:**
- `order_id`: Order-ID

**Rückgabe:** Erfolgsstatus

---

## 💾 Message Storage (message_storage.py)

### `save_sent_message()`
**Beschreibung:** Speichert eine gesendete Nachricht.  
**Funktion:**
- Erstellt SentMessage-Eintrag
- Aktualisiert Template-Usage-Count
- Aktualisiert Account-Statistiken
- Speichert in Datenbank

**Parameter:**
- `db`: Datenbank-Session
- `account_id`: Account-ID
- `group_id`: Gruppen-ID (optional)
- `message`: Nachrichtentext
- `success`: Erfolgsstatus
- `error_message`: Fehlermeldung (optional)
- Weitere Parameter optional

---

### `get_account_statistics()`
**Beschreibung:** Gibt Account-Statistiken zurück.  
**Funktion:**
- Lädt Statistiken aus Datenbank
- Erstellt falls nicht vorhanden
- Gibt Statistiken zurück

**Parameter:**
- `db`: Datenbank-Session
- `account_id`: Account-ID

**Rückgabe:** Statistiken-Dict

---

## 📝 Zusammenfassung

Diese Dokumentation deckt alle wichtigen Funktionen ab:

- **API Endpoints:** 50+ Endpoints für alle Features
- **Account Manager:** Telegram-Account-Verwaltung
- **Bot Manager:** Bot-Verwaltung
- **Authentifizierung:** JWT-basierte Auth
- **Scheduler:** Nachrichten-Planung
- **Warming:** Account-Warming
- **Datenbank:** Modelle und Funktionen
- **Phone Providers:** SMS-Provider-Integration
- **Message Storage:** Nachrichten-Historie

**Nächste Schritte:**
- Funktionen testen über `/docs` Endpoint
- Code-Beispiele in Swagger UI
- Erweiterte Features dokumentieren

