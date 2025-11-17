# 🔧 Datenbank speichert nichts - Diagnose & Fix

## ✅ Schnell-Check: Funktioniert die Datenbank?

```bash
# Prüfe ob Datenbank existiert
ls -la telegram_bot.db

# Prüfe Tabellen
sqlite3 telegram_bot.db "SELECT name FROM sqlite_master WHERE type='table';"

# Prüfe Daten
sqlite3 telegram_bot.db "SELECT COUNT(*) FROM users; SELECT COUNT(*) FROM accounts;"
```

---

## 🔍 Häufige Probleme & Lösungen

### Problem 1: `db.commit()` wird nicht aufgerufen

**Symptom:** Daten werden hinzugefügt (`db.add()`), aber nicht gespeichert.

**Lösung:** Stelle sicher, dass nach jedem `db.add()` ein `db.commit()` folgt:

```python
# ❌ FALSCH
db.add(new_account)
# Fehlt: db.commit()

# ✅ RICHTIG
db.add(new_account)
db.commit()
db.refresh(new_account)  # Optional: Aktualisiert Objekt mit DB-Werten
```

**Prüfen:** Suche in `api.py` nach `db.add(` und prüfe ob `db.commit()` danach kommt.

---

### Problem 2: Exception vor `db.commit()`

**Symptom:** Code bricht mit Fehler ab, bevor `db.commit()` erreicht wird.

**Lösung:** Verwende `try/except/finally` mit `db.rollback()`:

```python
try:
    db.add(new_account)
    db.commit()
except Exception as e:
    db.rollback()  # Wichtig: Rollback bei Fehler
    raise HTTPException(status_code=500, detail=str(e))
finally:
    db.close()  # Wird automatisch von get_db() gemacht
```

**Prüfen:** Prüfe Backend-Logs auf Fehler:
```bash
tail -f backend.log | grep -i error
```

---

### Problem 3: Falsche Datenbank-URL

**Symptom:** Daten werden in falsche Datenbank geschrieben.

**Lösung:** Prüfe `.env` Datei:

```bash
# Lokal (SQLite)
# DATABASE_URL NICHT setzen oder leer lassen

# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost/dbname
```

**Prüfen:**
```bash
# Prüfe welche Datenbank verwendet wird
python3 -c "import os; from database import init_db; engine = init_db(); print(engine.url)"
```

---

### Problem 4: Session wird nicht geschlossen

**Symptom:** Änderungen werden nicht sichtbar, obwohl `commit()` aufgerufen wurde.

**Lösung:** Die `get_db()` Dependency schließt automatisch. Aber bei manuellen Sessions:

```python
db = get_session(db_engine)
try:
    db.add(new_account)
    db.commit()
finally:
    db.close()  # WICHTIG: Session schließen
```

**Prüfen:** Prüfe ob alle manuellen Sessions geschlossen werden.

---

### Problem 5: Transaction wird zurückgerollt

**Symptom:** Daten werden temporär gespeichert, aber dann wieder gelöscht.

**Lösung:** Prüfe ob irgendwo `db.rollback()` aufgerufen wird:

```bash
grep -n "rollback" api.py
```

**Prüfen:** Prüfe ob `db.rollback()` nur bei Fehlern aufgerufen wird, nicht bei Erfolg.

---

## 🧪 Test: Funktioniert das Speichern?

### Test-Skript ausführen:

```bash
cd /Users/rebelldesign/Documents/telegram-bot
source venv/bin/activate
python test_database_save.py
```

**Erwartetes Ergebnis:**
```
✅ Test-Gruppe erstellt: ID=1
✅ Gruppe wurde erfolgreich gespeichert!
✅ Nach db.commit() ist Gruppe gespeichert
```

**Falls Fehler:** Prüfe Fehlermeldung und behebe entsprechend.

---

## 🔍 Debugging: Was wird gespeichert?

### 1. Prüfe aktuelle Daten:

```bash
sqlite3 telegram_bot.db <<EOF
SELECT 'Users:', COUNT(*) FROM users;
SELECT 'Accounts:', COUNT(*) FROM accounts;
SELECT 'Groups:', COUNT(*) FROM groups;
SELECT 'Scheduled Messages:', COUNT(*) FROM scheduled_messages;
EOF
```

### 2. Prüfe letzte Einträge:

```bash
sqlite3 telegram_bot.db <<EOF
SELECT id, name, created_at FROM accounts ORDER BY created_at DESC LIMIT 5;
SELECT id, name, created_at FROM groups ORDER BY created_at DESC LIMIT 5;
EOF
```

### 3. Prüfe Backend-Logs:

```bash
# Live-Logs ansehen
tail -f backend.log

# Oder: Prüfe uvicorn Output
# (im Terminal wo Backend läuft)
```

---

## 🛠️ Häufige Fixes

### Fix 1: Fehlendes `db.commit()` hinzufügen

**Suche nach:**
```python
db.add(...)
# Fehlt db.commit()
```

**Füge hinzu:**
```python
db.add(...)
db.commit()  # ← Hinzufügen
```

### Fix 2: Exception-Handling verbessern

**Vorher:**
```python
db.add(new_account)
db.commit()  # Wird nicht erreicht bei Fehler
```

**Nachher:**
```python
try:
    db.add(new_account)
    db.commit()
except Exception as e:
    db.rollback()
    raise HTTPException(status_code=500, detail=str(e))
```

### Fix 3: Datenbank-URL prüfen

```bash
# Prüfe .env
cat .env | grep DATABASE_URL

# Falls PostgreSQL: Prüfe Verbindung
psql $DATABASE_URL -c "SELECT 1;"
```

---

## 📊 Prüfe spezifische Endpoints

### Account erstellen:

```bash
# Test via API
curl -X POST http://localhost:8000/api/accounts \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Account",
    "account_type": "user",
    "phone_number": "+1234567890",
    "session_name": "test_session"
  }'

# Prüfe ob gespeichert
sqlite3 telegram_bot.db "SELECT * FROM accounts WHERE name='Test Account';"
```

### Gruppe erstellen:

```bash
# Test via API
curl -X POST http://localhost:8000/api/groups \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Gruppe",
    "chat_id": "test_chat_123",
    "chat_type": "group"
  }'

# Prüfe ob gespeichert
sqlite3 telegram_bot.db "SELECT * FROM groups WHERE name='Test Gruppe';"
```

---

## ✅ Checkliste

- [ ] Datenbank-Datei existiert (`telegram_bot.db`)
- [ ] Tabellen existieren (14 Tabellen)
- [ ] `db.commit()` wird nach `db.add()` aufgerufen
- [ ] Exception-Handling mit `db.rollback()`
- [ ] Session wird geschlossen (`db.close()`)
- [ ] Keine `db.rollback()` bei Erfolg
- [ ] DATABASE_URL korrekt gesetzt (oder leer für SQLite)
- [ ] Backend-Logs zeigen keine Fehler
- [ ] Test-Skript funktioniert

---

## 🚨 Wenn nichts hilft

1. **Prüfe Backend-Logs:**
   ```bash
   tail -100 backend.log | grep -i "error\|exception\|traceback"
   ```

2. **Prüfe Datenbank-Datei:**
   ```bash
   file telegram_bot.db
   sqlite3 telegram_bot.db ".schema"
   ```

3. **Teste manuell:**
   ```bash
   source venv/bin/activate
   python test_database_save.py
   ```

4. **Prüfe ob Datenbank-Lock:**
   ```bash
   lsof telegram_bot.db
   ```

5. **Backend neu starten:**
   ```bash
   # Stoppe Backend
   lsof -ti :8000 | xargs kill
   
   # Starte neu
   ./start_backend.sh
   ```

---

## 📝 Zusammenfassung

**Die Datenbank funktioniert** (Test bestätigt), aber mögliche Probleme:

1. ❌ `db.commit()` fehlt
2. ❌ Exception vor `db.commit()`
3. ❌ Falsche DATABASE_URL
4. ❌ Session nicht geschlossen
5. ❌ Transaction zurückgerollt

**Nächste Schritte:**
1. Führe `test_database_save.py` aus
2. Prüfe Backend-Logs
3. Prüfe ob `db.commit()` aufgerufen wird
4. Teste spezifischen Endpoint der nicht funktioniert

