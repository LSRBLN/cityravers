# Datenbank-Migration: SQLite → PostgreSQL

## Warum PostgreSQL?

- ✅ Besser für Produktion (Concurrent Access)
- ✅ Skalierbarer
- ✅ Backup/Restore einfacher
- ✅ Bessere Performance bei vielen Nutzern

## Migration

### 1. PostgreSQL installieren
```bash
sudo apt install postgresql postgresql-contrib
```

### 2. Datenbank erstellen
```bash
sudo -u postgres psql
CREATE USER telegram_bot_user WITH PASSWORD 'dein_sicheres_passwort';
CREATE DATABASE telegram_bot_db OWNER telegram_bot_user;
\q
```

### 3. database.py anpassen

**Vorher (SQLite):**
```python
def init_db(db_path: str = "telegram_bot.db"):
    engine = create_engine(f"sqlite:///{db_path}", ...)
```

**Nachher (PostgreSQL):**
```python
import os

def init_db():
    # PostgreSQL Connection String
    db_url = os.getenv(
        "DATABASE_URL",
        "postgresql://telegram_bot_user:password@localhost/telegram_bot_db"
    )
    engine = create_engine(db_url)
    Base.metadata.create_all(bind=engine)
    return engine
```

### 4. Dependencies
```bash
pip install psycopg2-binary
```

### 5. Daten migrieren (optional)
```python
# migrate_sqlite_to_postgres.py
from sqlalchemy import create_engine
from database import Account, Group, User, Subscription, ...

# SQLite lesen
sqlite_engine = create_engine("sqlite:///telegram_bot.db")
# PostgreSQL schreiben
pg_engine = create_engine("postgresql://user:pass@localhost/db")

# Daten kopieren...
```

