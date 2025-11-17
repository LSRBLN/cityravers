# 📋 Accounts-Übersicht

**Stand:** 2025-11-17 22:31:49

---

## 📊 Zusammenfassung

- **Gesamt:** 18 Accounts
- **User Accounts:** 15
- **Bot Accounts:** 3
- **Aktive Accounts:** 18
- **Inaktive Accounts:** 0

---

## 👤 User Accounts (15)

| ID | Name | Telefonnummer | Session-Name | Session-Datei | Proxy | Status | Erstellt |
|----|------|---------------|-------------|---------------|------|--------|----------|
| 20 | User | - | user_20251115 | ❌ | - | ✅ Aktiv | 2025-11-15 13:28 |
| 19 | 19415598793 | 19415598793 | 19415598793_20251115 | ❌ | resident.telegramproxy.net:9999 | ✅ Aktiv | 2025-11-15 09:06 |
| 18 | 19413525851 | 19413525851 | 19413525851_20251115 | ❌ | resident.telegramproxy.net:9999 | ✅ Aktiv | 2025-11-15 09:06 |
| 17 | 19413248441 | 19413248441 | 19413248441_20251115 | ❌ | resident.telegramproxy.net:9999 | ✅ Aktiv | 2025-11-15 09:06 |
| 16 | 19409805962 | 19409805962 | 19409805962_20251115 | ❌ | resident.telegramproxy.net:9999 | ✅ Aktiv | 2025-11-15 09:06 |
| 15 | 19409402185 | 19409402185 | 19409402185_20251115 | ❌ | resident.telegramproxy.net:9999 | ✅ Aktiv | 2025-11-15 09:06 |
| 12 | Kiezkurier030 | +491634632984 | Kiezkurier030 | ❌ | - | ✅ Aktiv | 2025-11-14 15:12 |
| 11 | fghj | - | fghj_20251114 | ❌ | - | ✅ Aktiv | 2025-11-14 01:59 |
| 10 | vietnam | - | vietnam_20251113 | ❌ | - | ✅ Aktiv | 2025-11-13 20:29 |
| 7 | 13434382684 | +13434382684 | 13434382684_20251112 | ❌ | - | ✅ Aktiv | 2025-11-12 00:41 |
| 6 | 13434372101 | +13434372101 | 13434372101_20251112 | ❌ | - | ✅ Aktiv | 2025-11-12 00:40 |
| 5 | 13434362430 | +13434362430 | 13434362430_20251112 | ❌ | - | ✅ Aktiv | 2025-11-12 00:39 |
| 4 | 12897086495 | +12897086495 | 12897086495_20251112 | ❌ | - | ✅ Aktiv | 2025-11-12 00:38 |
| 3 | 12897046237 | +12897046237 | 12897046237_20251112 | ❌ | - | ✅ Aktiv | 2025-11-12 00:37 |
| 2 | 27607848968 | 27607848968 | 27607848968_20251112 | ❌ | - | ✅ Aktiv | 2025-11-12 00:02 |

---

## 🤖 Bot Accounts (3)

| ID | Name | Status | Erstellt |
|----|------|--------|----------|
| 14 | Berlin City Ravers 2 | ✅ Aktiv | 2025-11-14 15:43 |
| 13 | Berlin City Ravers 1 | ✅ Aktiv | 2025-11-14 15:43 |
| 8 | My Bot | ✅ Aktiv | 2025-11-12 15:39 |

---

## 📁 Session-Dateien

**Gefundene .session Dateien im Root:** 9

- `19409402185_20251115.session` (28.0 KB)
- `19409805962_20251115.session` (28.0 KB)
- `19413248441_20251115.session` (28.0 KB)
- `19413525851_20251115.session` (28.0 KB)
- `19415598793_20251115.session` (28.0 KB)
- `Kiezkurier030.session` (40.0 KB)
- `dfg.session` (28.0 KB)
- `meine.session` (28.0 KB)
- `user_20251115.session` (28.0 KB)

---

## 🔄 Liste aktualisieren

```bash
cd /Users/rebelldesign/Documents/telegram-bot
python3 -c "
import sqlite3
conn = sqlite3.connect('telegram_bot.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM accounts')
print(f'Gesamt: {cursor.fetchone()[0]} Accounts')
conn.close()
"
```
