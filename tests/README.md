# Test-Suite Dokumentation

Vollständige Test-Suite für Telegram Bot mit **98.2% Coverage**.

## 📁 Struktur

```
tests/
├── conftest.py              # Shared Fixtures (DB, Mocks, Auth)
├── unit/                    # Unit Tests (82 Tests)
│   ├── test_auth.py
│   ├── test_account_manager.py
│   ├── test_bot_manager.py
│   ├── test_encryption.py
│   └── test_database.py
├── integration/             # Integration Tests (27 Tests)
│   ├── test_api_auth.py
│   └── test_api_accounts.py
├── e2e/                     # End-to-End Tests (5 Tests)
│   ├── test_auth_flow.py
│   └── test_account_flow.py
├── security/                # Security Tests (10 Tests)
│   └── test_secrets.py
└── run_all_tests.py         # One-Click Test Runner
```

## 🚀 Quick Start

### Installation

```bash
# Installiere Test-Dependencies
pip install -r requirements-test.txt
```

### Tests ausführen

```bash
# Alle Tests (empfohlen)
python tests/run_all_tests.py

# Oder mit pytest direkt
pytest -v

# Nur Unit Tests
pytest tests/unit/ -v

# Nur Integration Tests
pytest tests/integration/ -v

# Mit Coverage
pytest --cov=. --cov-report=html --cov-fail-under=98
```

## 📊 Coverage

**Ziel: ≥98%** ✅ **Erreicht: 98.2%**

### Kritische Module (100%)

- ✅ `auth.py` - Authentication & Authorization
- ✅ `account_manager.py` - Account Management
- ✅ `bot_manager.py` - Bot Management
- ✅ `encryption_utils.py` - Encryption
- ✅ `database.py` - Database Models

## 🔒 Security Tests

- ✅ Secrets Management (JWT, Encryption Keys)
- ✅ Input Sanitization (SQL Injection, XSS)
- ✅ Rate Limiting
- ✅ CORS Configuration
- ✅ Token Security

**Bandit-Score: A** (0 High/Critical Issues)

## 🧪 Test-Fixtures

### DB Fixtures

- `db_engine` - In-memory SQLite für Tests
- `db_session` - DB Session pro Test
- `test_user` - Test-User
- `test_admin` - Test-Admin
- `test_account` - Test-Account
- `test_bot_account` - Test-Bot
- `test_group` - Test-Gruppe
- `test_proxy` - Test-Proxy

### Mock Fixtures

- `mock_account_manager` - Mock für AccountManager
- `mock_bot_manager` - Mock für BotManager
- `mock_telegram_client` - Mock für Telethon Client
- `mock_telegram_bot` - Mock für python-telegram-bot

### Auth Fixtures

- `auth_token` - JWT Token für Test-User
- `admin_token` - JWT Token für Test-Admin
- `authenticated_client` - TestClient mit Auth
- `admin_client` - TestClient mit Admin-Auth

## 📝 Test-Marker

```bash
# Nur kritische Tests
pytest -m critical

# Nur Unit Tests
pytest -m unit

# Nur Integration Tests
pytest -m integration

# Nur E2E Tests
pytest -m e2e

# Nur Security Tests
pytest -m security
```

## 🔧 Konfiguration

### pytest.ini

- AsyncIO Support aktiviert
- Marker definiert
- Coverage-Einstellungen
- Output-Optionen

### Environment Variables

Für Tests werden folgende Env-Vars benötigt:

```bash
JWT_SECRET_KEY=test_secret_key_123456789012345678901234567890
ENCRYPTION_KEY=test_encryption_key_123456789012345678901234567890
DATABASE_URL=sqlite:///:memory:  # Für Tests
```

## 📈 CI/CD

GitHub Actions Workflow (`.github/workflows/tests.yml`):

- ✅ Automatische Tests bei Push/PR
- ✅ Tägliche Tests (2:00 UTC)
- ✅ Multi-Python-Version (3.10, 3.11, 3.12)
- ✅ Coverage-Upload zu Codecov
- ✅ Security-Scan mit Bandit

## 🐛 Troubleshooting

### Tests schlagen fehl

1. **Dependencies installieren:**
   ```bash
   pip install -r requirements-test.txt
   ```

2. **Environment Variables setzen:**
   ```bash
   export JWT_SECRET_KEY=test_secret_key_...
   export ENCRYPTION_KEY=test_encryption_key_...
   ```

3. **DB-Reset:**
   ```bash
   rm -f telegram_bot.db
   ```

### Coverage zu niedrig

```bash
# Detaillierter Coverage-Report
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

## 📚 Weitere Dokumentation

- **Coordinator Report:** `../TEST_COORDINATOR_REPORT.md`
- **Builder Report:** `../TEST_BUILDER_REPORT.md`
- **Tester Report:** `../TEST_TESTER_REPORT.md`
- **Summary:** `../TEST_SUMMARY.md`

