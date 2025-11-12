# Implementierung: Registrierung, Abonnements & Automatischer Nummernkauf

## ✅ Implementierte Features

### 1. User-Authentifizierungssystem
- **Registrierung** (`POST /api/auth/register`)
  - Email, Username, Passwort
  - Automatisches Free Trial (7 Tage)
  - JWT Token wird zurückgegeben
  
- **Login** (`POST /api/auth/login`)
  - Login mit Email oder Username
  - JWT Token für Authentifizierung
  
- **User-Info** (`GET /api/auth/me`)
  - Aktuelle Benutzerinformationen
  - Abonnement-Status
  - Statistiken (Accounts, Gruppen)

### 2. Abonnement/Paket-System
- **Free Trial** (automatisch bei Registrierung)
  - 7 Tage Laufzeit
  - 1 Account
  - 5 Gruppen
  - 10 Nachrichten/Tag
  - Kein automatischer Nummernkauf

- **Paket-Typen** (vorbereitet):
  - `free_trial` - Gratis Test
  - `basic` - Basis-Paket
  - `pro` - Pro-Paket
  - `enterprise` - Enterprise-Paket

- **Features pro Paket** (konfigurierbar):
  - `max_accounts` - Maximale Accounts
  - `max_groups` - Maximale Gruppen
  - `max_messages_per_day` - Nachrichten-Limit
  - `auto_number_purchase` - Automatischer Nummernkauf

### 3. 5sim.net API Integration
- **Provider-Klassen**:
  - `FiveSimProvider` - 5sim.net Integration
  - `SMSActivateProvider` - SMS-Activate.ru Integration (Alternative)

- **Funktionen**:
  - `buy_number()` - Kauft Telefonnummer
  - `get_sms_code()` - Ruft SMS-Code ab
  - `get_balance()` - Guthaben prüfen
  - `cancel_order()` - Bestellung stornieren
  - `finish_order()` - Bestellung abschließen

- **API-Endpunkt**: `POST /api/phone/buy-number`
  - Kauft Nummer automatisch
  - Wartet auf SMS-Code (Polling)
  - Erstellt Telegram-Account (TODO: vollständig implementieren)

### 4. Geschützte Endpunkte
- Alle Account- und Gruppen-Endpunkte sind jetzt geschützt
- Benutzer sehen nur ihre eigenen Accounts/Gruppen
- Account- und Gruppen-Limits werden geprüft

### 5. Datenbank-Erweiterungen
- **User** - Benutzer-Accounts
- **Subscription** - Abonnements
- **PhoneNumberPurchase** - Gekaufte Telefonnummern
- **Account.user_id** - Verknüpfung zu Benutzer
- **Group.user_id** - Verknüpfung zu Benutzer

## 📋 Voraussetzungen für 5sim.net Integration

### API-Key erhalten:
1. Registrierung auf https://5sim.net
2. API-Key im Dashboard generieren
3. In Umgebungsvariablen setzen: `FIVESIM_API_KEY=your_api_key`

### Konfiguration:
```bash
export FIVESIM_API_KEY="your_api_key_here"
# Oder in .env Datei:
FIVESIM_API_KEY=your_api_key_here
```

### Verfügbare Länder (5sim.net):
- `germany` - Deutschland
- `usa` - USA
- `russia` - Russland
- `ukraine` - Ukraine
- ... (weitere auf 5sim.net verfügbar)

### Verfügbare Services:
- `telegram` - Telegram
- `whatsapp` - WhatsApp
- `discord` - Discord
- ... (weitere auf 5sim.net verfügbar)

## 🔧 Installation

```bash
# Abhängigkeiten installieren
pip install -r requirements.txt

# Datenbank aktualisieren
python3 -c "from database import init_db; init_db()"
```

## 🚀 Verwendung

### 1. Benutzer registrieren:
```bash
POST /api/auth/register
{
  "email": "user@example.com",
  "username": "username",
  "password": "secure_password"
}
```

### 2. Einloggen:
```bash
POST /api/auth/login
{
  "username": "username",  # oder Email
  "password": "secure_password"
}
```

### 3. Token verwenden:
```bash
# Alle weiteren Requests mit Header:
Authorization: Bearer <access_token>
```

### 4. Telefonnummer kaufen:
```bash
POST /api/phone/buy-number
Authorization: Bearer <token>
{
  "provider": "5sim",
  "country": "germany",
  "service": "telegram"
}
```

## ⚠️ Wichtige Hinweise

1. **JWT Secret Key**: Muss in Produktion geändert werden (in `auth.py`)
2. **API Keys**: 5sim.net API Key muss konfiguriert werden
3. **Account-Erstellung**: Automatische Account-Erstellung nach Nummernkauf muss noch vollständig implementiert werden
4. **Zahlungsintegration**: Stripe/PayPal Integration für Paket-Käufe noch nicht implementiert
5. **Frontend**: Login/Registrierung Frontend noch nicht implementiert

## 📝 TODO

- [ ] Frontend Login/Registrierung implementieren
- [ ] Paket-Auswahl und Zahlungsintegration (Stripe)
- [ ] Vollständige automatische Account-Erstellung nach Nummernkauf
- [ ] Webhook-Support für 5sim.net (statt Polling)
- [ ] Admin-Panel für Paket-Verwaltung
- [ ] Email-Verifizierung
- [ ] Passwort-Reset

