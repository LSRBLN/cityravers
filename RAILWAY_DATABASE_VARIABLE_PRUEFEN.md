# ✅ Railway: DATABASE_URL Variable prüfen

## 📋 Was du siehst

**Railway "Connect to Postgres" Modal zeigt:**
- ✅ Private Network Tab: `${{ Postgres.DATABASE_URL }}`
- ✅ Public Network Tab: Connection URL (für externe Tools)

**Das ist korrekt!** ✅

---

## 🔍 Prüfen: Ist DATABASE_URL im Backend-Service gesetzt?

### Schritt 1: Railway Dashboard öffnen

1. **Railway Dashboard → "tele" Service** (Backend)
2. **Settings → Variables Tab**

### Schritt 2: DATABASE_URL prüfen

**Muss vorhanden sein:**
- ✅ **Key:** `DATABASE_URL`
- ✅ **Value:** `${{ Postgres.DATABASE_URL }}`

**Falls NICHT vorhanden:**
- Klicke auf **"Add Variable"**
- Key: `DATABASE_URL`
- Value: `${{ Postgres.DATABASE_URL }}`
- Save

**Falls vorhanden, aber falsch:**
- Klicke auf `DATABASE_URL`
- Value sollte sein: `${{ Postgres.DATABASE_URL }}`
- Falls nicht: Korrigieren und Save

---

## ✅ Warum `${{ Postgres.DATABASE_URL }}`?

**Railway Variable Reference:**
- `${{ Postgres.DATABASE_URL }}` = Verweis auf die DATABASE_URL des "Postgres" Services
- Railway ersetzt das automatisch beim Deployment
- ✅ Automatisch aktualisiert, wenn Postgres-URL sich ändert
- ✅ Keine manuelle URL nötig

**Alternative (nicht empfohlen):**
- Direkte URL: `postgresql://postgres:pass@host:port/db`
- ❌ Muss manuell aktualisiert werden
- ❌ Fehleranfällig

---

## 🔧 Was passiert beim Backend-Start?

**`api.py` liest `DATABASE_URL`:**

```python
db_url = os.getenv("DATABASE_URL")

if db_url:
    # PostgreSQL verwenden
    engine = create_engine(db_url)
    Base.metadata.create_all(bind=engine)  # Tabellen erstellen
```

**Railway ersetzt `${{ Postgres.DATABASE_URL }}` automatisch:**
- ✅ Beim Deployment
- ✅ Zur Laufzeit
- ✅ Mit aktueller Postgres-URL

---

## 📋 Checkliste

### Railway "tele" Service (Backend):
- [ ] `DATABASE_URL` Variable vorhanden
- [ ] Value = `${{ Postgres.DATABASE_URL }}`
- [ ] Service wurde nach Änderung neu gestartet

### Railway "Postgres" Service:
- [ ] Service läuft (grüner Checkmark)
- [ ] Connection URL funktioniert (im Modal sichtbar)

### Backend Logs prüfen:
- [ ] Railway → "tele" Service → Logs
- [ ] Suche nach: `✅ Datenbank-Migration erfolgreich`
- [ ] Keine Fehler wie: `Database connection failed`

---

## 🎯 Zusammenfassung

**Was du siehst:**
- ✅ Railway zeigt "Connect to Postgres" Modal
- ✅ Private Network: `${{ Postgres.DATABASE_URL }}`
- ✅ Public Network: Connection URL

**Was prüfen:**
1. **Railway → "tele" Service → Variables**
2. **`DATABASE_URL` = `${{ Postgres.DATABASE_URL }}`** ✅
3. **Falls nicht:** Variable hinzufügen/korrigieren
4. **Service neu starten** (falls geändert)

**Dann sollte alles funktionieren!** ✅

---

## 🔍 Schnell-Prüfung

**Railway Dashboard:**
1. **"tele" Service → Variables Tab**
2. **Suche nach `DATABASE_URL`**
3. **Value sollte sein:** `${{ Postgres.DATABASE_URL }}`

**Falls korrekt:** ✅ Alles passt!  
**Falls nicht:** Variable hinzufügen/korrigieren

