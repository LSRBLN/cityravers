# 📋 Accounts-Liste

**Stand:** $(date)

---

## 📊 Übersicht

- **Gesamt:** 7 Accounts
- **User Accounts:** 6
- **Bot Accounts:** 1
- **Aktive Accounts:** 7

---

## 🔐 Accounts-Details

| ID | Name | Typ | Telefonnummer | Session-Name | Status | Besitzer | Erstellt am |
|----|------|-----|----------------|--------------|--------|----------|-------------|
| 8 | My Bot | Bot | - | - | ✅ Aktiv | admin | 2025-11-12 15:39:38 |
| 7 | 13434382684 | User | +13434382684 | 13434382684_20251112 | ✅ Aktiv | - | 2025-11-12 00:41:48 |
| 6 | 13434372101 | User | +13434372101 | 13434372101_20251112 | ✅ Aktiv | - | 2025-11-12 00:40:42 |
| 5 | 13434362430 | User | +13434362430 | 13434362430_20251112 | ✅ Aktiv | - | 2025-11-12 00:39:36 |
| 4 | 12897086495 | User | +12897086495 | 12897086495_20251112 | ✅ Aktiv | - | 2025-11-12 00:38:30 |
| 3 | 12897046237 | User | +12897046237 | 12897046237_20251112 | ✅ Aktiv | - | 2025-11-12 00:37:24 |
| 2 | 27607848968 | User | 27607848968 | 27607848968_20251112 | ✅ Aktiv | - | 2025-11-12 00:02:45 |

---

## 📝 Details

### Bot Accounts (1)

1. **My Bot** (ID: 8)
   - Typ: Bot
   - Status: ✅ Aktiv
   - Besitzer: admin
   - Erstellt: 2025-11-12 15:39:38

### User Accounts (6)

1. **13434382684** (ID: 7)
   - Telefonnummer: +13434382684
   - Session: 13434382684_20251112
   - Status: ✅ Aktiv
   - Erstellt: 2025-11-12 00:41:48

2. **13434372101** (ID: 6)
   - Telefonnummer: +13434372101
   - Session: 13434372101_20251112
   - Status: ✅ Aktiv
   - Erstellt: 2025-11-12 00:40:42

3. **13434362430** (ID: 5)
   - Telefonnummer: +13434362430
   - Session: 13434362430_20251112
   - Status: ✅ Aktiv
   - Erstellt: 2025-11-12 00:39:36

4. **12897086495** (ID: 4)
   - Telefonnummer: +12897086495
   - Session: 12897086495_20251112
   - Status: ✅ Aktiv
   - Erstellt: 2025-11-12 00:38:30

5. **12897046237** (ID: 3)
   - Telefonnummer: +12897046237
   - Session: 12897046237_20251112
   - Status: ✅ Aktiv
   - Erstellt: 2025-11-12 00:37:24

6. **27607848968** (ID: 2)
   - Telefonnummer: 27607848968
   - Session: 27607848968_20251112
   - Status: ✅ Aktiv
   - Erstellt: 2025-11-12 00:02:45

---

## 🔍 SQL-Abfrage

```sql
SELECT 
    a.id,
    a.name,
    a.account_type,
    a.phone_number,
    a.session_name,
    a.is_active,
    u.username as owner,
    a.created_at
FROM accounts a
LEFT JOIN users u ON a.user_id = u.id
ORDER BY a.created_at DESC;
```

---

## 📊 Statistiken

- **Neuester Account:** My Bot (2025-11-12 15:39:38)
- **Ältester Account:** 27607848968 (2025-11-12 00:02:45)
- **Durchschnitt:** ~1 Account pro Stunde (am 12.11.2025)

---

## 🔄 Liste aktualisieren

```bash
cd /Users/rebelldesign/Documents/telegram-bot
sqlite3 telegram_bot.db -header -column "
SELECT 
    a.id,
    a.name,
    a.account_type,
    a.phone_number,
    a.session_name,
    a.is_active,
    u.username as owner,
    a.created_at
FROM accounts a
LEFT JOIN users u ON a.user_id = u.id
ORDER BY a.created_at DESC;
"
```

