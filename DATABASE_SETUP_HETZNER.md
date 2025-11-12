# Datenbank-Einrichtung auf Hetzner Server

## 🗄️ Übersicht

Das Tool unterstützt zwei Datenbank-Optionen:
1. **SQLite** (Entwicklung) - Einfach, keine Konfiguration nötig
2. **PostgreSQL** (Produktion) - Empfohlen für Server, besser für mehrere Nutzer

---

## 📋 Option 1: PostgreSQL (Empfohlen für Produktion)

### Vorteile:
- ✅ Besser für mehrere gleichzeitige Nutzer
- ✅ Skalierbarer
- ✅ Backup/Restore einfacher
- ✅ Bessere Performance

### Installation:

```bash
# 1. PostgreSQL installieren
sudo apt update
sudo apt install postgresql postgresql-contrib

# 2. PostgreSQL starten
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 3. Datenbank erstellen
sudo -u postgres psql
```

### In PostgreSQL Shell:

```sql
-- User erstellen
CREATE USER telegram_bot_user WITH PASSWORD 'SICHERES_PASSWORT_HIER';

-- Datenbank erstellen
CREATE DATABASE telegram_bot_db OWNER telegram_bot_user;

-- Rechte vergeben
GRANT ALL PRIVILEGES ON DATABASE telegram_bot_db TO telegram_bot_user;

-- Verlassen
\q
```

### Konfiguration in .env:

```bash
# /var/www/telegram-bot/.env
DATABASE_URL=postgresql://telegram_bot_user:SICHERES_PASSWORT@localhost/telegram_bot_db
```

### Datenbank initialisieren:

```bash
cd /var/www/telegram-bot
source venv/bin/activate
export DATABASE_URL="postgresql://telegram_bot_user:SICHERES_PASSWORT@localhost/telegram_bot_db"
python3 -c "from database import init_db; init_db(); print('✅ Datenbank initialisiert')"
```

---

## 📋 Option 2: SQLite (Einfach, für Entwicklung)

### Vorteile:
- ✅ Keine Installation nötig
- ✅ Einfach zu verwenden
- ✅ Gut für Tests

### Nachteile:
- ⚠️ Nicht ideal für mehrere Nutzer gleichzeitig
- ⚠️ Begrenzte Skalierbarkeit

### Konfiguration:

```bash
# .env Datei - DATABASE_URL NICHT setzen
# Dann wird automatisch SQLite verwendet
```

Die Datenbank wird automatisch als `telegram_bot.db` erstellt.

---

## 🔄 Migration: SQLite → PostgreSQL

Falls du bereits SQLite verwendest und auf PostgreSQL wechseln möchtest:

### 1. Daten exportieren (SQLite):

```bash
cd /var/www/telegram-bot
source venv/bin/activate

# Python Script zum Export
python3 << EOF
from database import init_db, Account, Group, User, Subscription
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# SQLite verbinden
sqlite_engine = create_engine("sqlite:///telegram_bot.db")
Session = sessionmaker(bind=sqlite_engine)
session = Session()

# Daten lesen
accounts = session.query(Account).all()
groups = session.query(Group).all()
users = session.query(User).all()
subscriptions = session.query(Subscription).all()

print(f"Gefunden: {len(accounts)} Accounts, {len(groups)} Gruppen, {len(users)} User")
EOF
```

### 2. PostgreSQL einrichten (siehe oben)

### 3. Daten migrieren:

```bash
# Automatisches Migrations-Script
python3 migrate_to_postgresql.py
```

Oder manuell:
```bash
# 1. SQLite Datenbank exportieren
sqlite3 telegram_bot.db .dump > backup.sql

# 2. PostgreSQL importieren (angepasst)
# ACHTUNG: SQLite und PostgreSQL haben unterschiedliche Syntax!
# Besser: Python-Migration verwenden
```

---

## 🛠️ Datenbank-Verwaltung

### Backup erstellen:

```bash
# PostgreSQL Backup
sudo -u postgres pg_dump telegram_bot_db > backup_$(date +%Y%m%d).sql

# SQLite Backup
cp telegram_bot.db backup_$(date +%Y%m%d).db
```

### Backup wiederherstellen:

```bash
# PostgreSQL
sudo -u postgres psql telegram_bot_db < backup_20240101.sql

# SQLite
cp backup_20240101.db telegram_bot.db
```

### Datenbank zurücksetzen:

```bash
# VORSICHT: Löscht alle Daten!
cd /var/www/telegram-bot
source venv/bin/activate

# PostgreSQL
sudo -u postgres psql -c "DROP DATABASE telegram_bot_db;"
sudo -u postgres psql -c "CREATE DATABASE telegram_bot_db OWNER telegram_bot_user;"
python3 -c "from database import init_db; init_db()"

# SQLite
rm telegram_bot.db
python3 -c "from database import init_db; init_db()"
```

---

## 📊 Datenbank-Optimierung (PostgreSQL)

### Performance-Tuning:

```bash
sudo nano /etc/postgresql/15/main/postgresql.conf
```

Empfohlene Einstellungen für 2-4GB RAM:

```ini
shared_buffers = 512MB
effective_cache_size = 1536MB
maintenance_work_mem = 128MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 2621kB
min_wal_size = 1GB
max_wal_size = 4GB
```

```bash
sudo systemctl restart postgresql
```

---

## 🔍 Datenbank prüfen

### Verbindung testen:

```bash
# PostgreSQL
sudo -u postgres psql -U telegram_bot_user -d telegram_bot_db
# Passwort eingeben
\dt  # Tabellen anzeigen
\q   # Verlassen

# SQLite
sqlite3 telegram_bot.db
.tables  # Tabellen anzeigen
.quit    # Verlassen
```

### Datenbank-Größe prüfen:

```bash
# PostgreSQL
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('telegram_bot_db'));"

# SQLite
ls -lh telegram_bot.db
```

---

## 🚨 Troubleshooting

### PostgreSQL startet nicht:

```bash
sudo systemctl status postgresql
sudo journalctl -u postgresql -n 50
```

### Verbindungsfehler:

```bash
# Prüfe ob PostgreSQL läuft
sudo systemctl status postgresql

# Prüfe Passwort in .env
cat /var/www/telegram-bot/.env | grep DATABASE_URL

# Teste Verbindung
psql postgresql://telegram_bot_user:password@localhost/telegram_bot_db
```

### Datenbank-Lock (SQLite):

```bash
# Wenn SQLite "database is locked" Fehler:
# 1. Prüfe ob andere Prozesse die DB verwenden
lsof telegram_bot.db

# 2. Service neu starten
sudo systemctl restart telegram-bot
```

---

## ✅ Checkliste

- [ ] PostgreSQL installiert (oder SQLite verwendet)
- [ ] Datenbank erstellt
- [ ] User erstellt mit Passwort
- [ ] DATABASE_URL in .env gesetzt (PostgreSQL)
- [ ] Datenbank initialisiert
- [ ] Backup-Strategie eingerichtet
- [ ] Performance-Optimierung (PostgreSQL)

---

## 📝 Empfehlung

**Für Hetzner Server (Produktion):**
- ✅ **PostgreSQL verwenden**
- ✅ Automatische Backups einrichten
- ✅ Performance-Optimierung durchführen

**Für lokale Entwicklung:**
- ✅ SQLite ist ausreichend
- ✅ Einfacher zu testen

