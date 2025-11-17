# 🔍 Accounts-Zuordnung - Analyse

## ❌ Problem

**Alle 18 Telegram-Accounts gehören dem `admin` User.**

Es gibt **keinen User "Diego"** in der Datenbank.

---

## 📊 Aktuelle Situation

### System-User (Benutzer des Tools):

| Username | Email | Admin | Accounts |
|----------|-------|-------|----------|
| admin | admin@telegram-bot.local | ✅ | **18 Accounts** |
| User | user@telegram-bot.local | ❌ | 0 Accounts |
| testuser | test@test.com | ❌ | 0 Accounts |
| newuser | newuser@example.com | ❌ | 0 Accounts |
| differentuser | test_adc94ff6@example.com | ❌ | 0 Accounts |
| testuser_6332d37d | different@example.com | ❌ | 0 Accounts |

### Telegram-Accounts:

**Alle 18 Accounts gehören `admin`:**
- 15 User Accounts
- 3 Bot Accounts

---

## 🔧 Lösung: Accounts anderen Usern zuordnen

### Option 1: User "Diego" erstellen

```bash
cd /Users/rebelldesign/Documents/telegram-bot
python3 create_users.py
```

Oder manuell über die API/Frontend registrieren.

### Option 2: Accounts zu bestehendem User zuordnen

**Via SQL:**
```sql
-- 1. User-ID von Diego finden
SELECT id, username, email FROM users WHERE username = 'diego';

-- 2. Accounts zu Diego zuordnen (z.B. Account IDs 15-19)
UPDATE accounts 
SET user_id = (SELECT id FROM users WHERE username = 'diego')
WHERE id IN (15, 16, 17, 18, 19);
```

**Via Python Script:**
```python
from database import init_db, get_session, Account, User

db_engine = init_db()
db = get_session(db_engine)

# Finde Diego User
diego = db.query(User).filter(User.username == 'diego').first()
if not diego:
    print("❌ User 'Diego' nicht gefunden")
else:
    # Ordne Accounts zu (z.B. IDs 15-19)
    accounts = db.query(Account).filter(Account.id.in_([15, 16, 17, 18, 19])).all()
    for acc in accounts:
        acc.user_id = diego.id
    db.commit()
    print(f"✅ {len(accounts)} Accounts zu Diego zugeordnet")
```

---

## 📋 Accounts-Übersicht nach User

### Admin (18 Accounts):
- 19409402185
- 19409805962
- 19413248441
- 19413525851
- 19415598793
- Kiezkurier030
- fghj
- vietnam
- 13434382684
- 13434372101
- 13434362430
- 12897086495
- 12897046237
- 27607848968
- User
- Berlin City Ravers 1 (Bot)
- Berlin City Ravers 2 (Bot)
- My Bot (Bot)

### Andere User:
- **Keine Accounts zugeordnet**

---

## 🎯 Empfehlung

1. **User "Diego" erstellen** (falls noch nicht vorhanden)
2. **Accounts zuordnen** (z.B. die 5 Accounts vom 15.11.2025)
3. **Prüfen** ob weitere Accounts zugeordnet werden sollen

---

## 🔄 Accounts zuordnen - Script

```python
#!/usr/bin/env python3
"""
Script zum Zuordnen von Accounts zu einem User
"""
import sys
from database import init_db, get_session, Account, User

def assign_accounts_to_user(username: str, account_ids: list):
    db_engine = init_db()
    db = get_session(db_engine)
    
    try:
        # Finde User
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f"❌ User '{username}' nicht gefunden")
            return
        
        # Finde Accounts
        accounts = db.query(Account).filter(Account.id.in_(account_ids)).all()
        if not accounts:
            print(f"❌ Keine Accounts mit IDs {account_ids} gefunden")
            return
        
        # Ordne zu
        for acc in accounts:
            old_owner = acc.user_id
            acc.user_id = user.id
            print(f"✅ Account '{acc.name}' (ID: {acc.id}) von User {old_owner} zu {user.username} (ID: {user.id})")
        
        db.commit()
        print(f"\n✅ {len(accounts)} Accounts erfolgreich zu '{username}' zugeordnet")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Fehler: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Verwendung: python assign_accounts.py <username> <account_id1> [account_id2] ...")
        sys.exit(1)
    
    username = sys.argv[1]
    account_ids = [int(id) for id in sys.argv[2:]]
    assign_accounts_to_user(username, account_ids)
```

**Verwendung:**
```bash
python3 assign_accounts.py diego 15 16 17 18 19
```

---

## ✅ Checkliste

- [ ] User "Diego" existiert (oder erstellen)
- [ ] Welche Accounts sollen zu Diego?
- [ ] Accounts zuordnen (SQL oder Script)
- [ ] Prüfen ob Zuordnung erfolgreich

---

## 📞 Hilfe

- **Accounts-Übersicht:** Siehe `ACCOUNTS_UEBERSICHT.md`
- **User erstellen:** `create_users.py` oder Frontend-Registrierung
- **Accounts zuordnen:** SQL-Update oder Python-Script

