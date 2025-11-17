# 📖 Handbuch für Diego

**Berlin City Raver - Marketing Tool**  
**Vollständige Benutzeranleitung**

---

## 📋 Inhaltsverzeichnis

1. [Erste Schritte](#erste-schritte)
2. [Account-Verwaltung](#account-verwaltung)
3. [Gruppen-Verwaltung](#gruppen-verwaltung)
4. [Nachrichten planen](#nachrichten-planen)
5. [User-Scraping](#user-scraping)
6. [Nachrichten weiterleiten](#nachrichten-weiterleiten)
7. [Account-Warming](#account-warming)
8. [Nachrichtenvorlagen](#nachrichtenvorlagen)
9. [Proxy-Verwaltung](#proxy-verwaltung)
10. [Tipps & Tricks](#tipps--tricks)
11. [Häufige Probleme](#häufige-probleme)

---

## 🚀 Erste Schritte

### Registrierung

1. **Öffne die App** im Browser
2. **Klicke auf "Registrieren"**
3. **Fülle die Felder aus:**
   - Email-Adresse
   - Benutzername
   - Passwort (mindestens 6 Zeichen)
4. **Klicke auf "Registrieren"**

**✅ Du erhältst automatisch:**
- 7 Tage kostenlosen Testzugang
- 2 Accounts
- 5 Gruppen
- 10 Nachrichten pro Tag

### Login

1. **Öffne die App**
2. **Gib deine Anmeldedaten ein:**
   - Username oder Email
   - Passwort
3. **Klicke auf "Einloggen"**

**💡 Tipp:** Du bleibst 7 Tage eingeloggt (Token-Ablaufzeit)

---

## 👤 Account-Verwaltung

### Neuen Account hinzufügen

#### Option 1: User-Account (Telefonnummer)

1. **Klicke auf "Accounts"** im Menü
2. **Klicke auf "+ Neuer Account"**
3. **Fülle die Felder aus:**
   - **Account-Name:** Beliebiger Name (z.B. "Mein Account")
   - **Account-Typ:** "User Account"
   - **API ID:** Von https://my.telegram.org/apps (optional)
   - **API Hash:** Von https://my.telegram.org/apps (optional)
   - **Telefonnummer:** Deine Telegram-Nummer (+49...)
   - **Session-Name:** Eindeutiger Name (z.B. "account1_session")
   - **Proxy:** Optional (zum Ban-Schutz)
4. **Klicke auf "Erstellen"**
5. **Code eingeben:**
   - Code wird automatisch an deine Telefonnummer/Telegram gesendet
   - Gib den Code im Modal ein
   - Bei 2FA: Gib dein Passwort ein
6. **Fertig!** Account ist verbunden

#### Option 2: Bot-Account

1. **Klicke auf "Accounts"** im Menü
2. **Klicke auf "+ Neuer Account"**
3. **Fülle die Felder aus:**
   - **Account-Name:** Beliebiger Name
   - **Account-Typ:** "Bot"
   - **Bot Token:** Von @BotFather
4. **Klicke auf "Erstellen"**
5. **Fertig!** Bot ist sofort verbunden

#### Option 3: Session-Datei hochladen

1. **Klicke auf "📁 Session-Datei"** Button
2. **Lade .session Datei hoch**
3. **Gib Account-Name ein**
4. **Klicke auf "Account erstellen"**
5. **Fertig!** Account wird automatisch verbunden

### Account einloggen

Wenn ein Account nicht verbunden ist:

1. **Klicke auf "🔐 Login"** Button beim Account
2. **Code wird automatisch angefordert**
3. **Gib den Code ein** (wird per Telegram gesendet)
4. **Bei 2FA:** Gib dein Passwort ein
5. **Fertig!** Account ist verbunden

### Account löschen

1. **Klicke auf "Löschen"** Button beim Account
2. **Bestätige die Löschung**
3. **Account wird gelöscht**

---

## 👥 Gruppen-Verwaltung

### Gruppen hinzufügen

#### Option 1: Automatisch aus Dialogen

1. **Klicke auf "Gruppen"** im Menü
2. **Wähle einen verbundenen Account** aus dem Dropdown
3. **Klicke auf "Dialoge laden"**
4. **Wähle Gruppen aus** die du hinzufügen möchtest
5. **Klicke auf "Ausgewählte hinzufügen"**
6. **Fertig!** Gruppen sind gespeichert

#### Option 2: Manuell hinzufügen

1. **Klicke auf "Gruppen"** im Menü
2. **Klicke auf "+ Manuell hinzufügen"**
3. **Fülle die Felder aus:**
   - **Name:** Gruppenname
   - **Chat-ID:** Telegram Chat-ID (optional)
   - **Typ:** group, channel oder private
   - **Username:** @username (optional)
4. **Klicke auf "Erstellen"**
5. **Fertig!** Gruppe ist gespeichert

#### Option 3: Nach Namen suchen

1. **Klicke auf "Gruppen"** im Menü
2. **Klicke auf "Nach Namen suchen"**
3. **Wähle Account** aus dem Dropdown
4. **Gib Gruppennamen ein** (eine pro Zeile)
5. **Klicke auf "Suchen"**
6. **Wähle gefundene Gruppen aus**
7. **Klicke auf "Hinzufügen"**
8. **Fertig!** Gruppen sind gespeichert

### Gruppen löschen

1. **Klicke auf "Löschen"** Button bei der Gruppe
2. **Bestätige die Löschung**
3. **Gruppe wird gelöscht**

---

## 📅 Nachrichten planen

### Neue geplante Nachricht erstellen

1. **Klicke auf "Geplante Nachrichten"** im Menü
2. **Klicke auf "+ Neue geplante Nachricht"**
3. **Fülle die Felder aus:**
   - **Account:** Wähle verbundenen Account
   - **Gruppen:** Wähle eine oder mehrere Gruppen
   - **Nachricht:** Dein Nachrichtentext
   - **Geplant für:** Datum und Uhrzeit
   - **Wiederholungen:** Wie oft senden (Standard: 1)
   - **Delay:** Sekunden zwischen Nachrichten (Standard: 1s)
   - **Batch-Größe:** Nachrichten pro Batch (Standard: 10)
   - **Batch-Delay:** Pause zwischen Batches (Standard: 5s)
   - **Gruppen-Delay:** Pause zwischen verschiedenen Gruppen (Standard: 2s)
4. **Klicke auf "Erstellen"**
5. **Fertig!** Nachricht ist geplant

### Nachricht bearbeiten

1. **Klicke auf "Bearbeiten"** bei der Nachricht
2. **Ändere die Felder**
3. **Klicke auf "Speichern"**

### Nachricht abbrechen

1. **Klicke auf "Abbrechen"** bei der Nachricht
2. **Bestätige die Abbrechung**
3. **Nachricht wird abgebrochen**

### Testnachricht senden

1. **Klicke auf "Geplante Nachrichten"** im Menü
2. **Klicke auf "Test senden"** Button
3. **Wähle Account und Gruppe**
4. **Gib Nachricht ein**
5. **Klicke auf "Senden"**
6. **Nachricht wird sofort gesendet**

---

## 👥 User-Scraping

### Mitglieder aus Gruppe scrapen

1. **Klicke auf "User-Scraping"** im Menü
2. **Wähle Account** aus dem Dropdown
3. **Wähle Gruppe** aus dem Dropdown
4. **Setze Limit** (Standard: 10000)
5. **Klicke auf "Mitglieder scrapen"**
6. **Warte bis fertig** (kann einige Minuten dauern)
7. **Fertig!** User sind gespeichert

### Gescrapte User anzeigen

1. **Klicke auf "User-Scraping"** im Menü
2. **Gescrapte User werden automatisch angezeigt**
3. **Du siehst:**
   - Username
   - Name
   - Telefonnummer (falls verfügbar)
   - Quell-Gruppe

### User zu Gruppe einladen

1. **Klicke auf "User-Scraping"** im Menü
2. **Klicke auf "User einladen"** Button
3. **Wähle Account** (muss Admin sein)
4. **Wähle Ziel-Gruppe**
5. **Wähle User aus** oder lade alle gescrapten User
6. **Setze Delay** zwischen Einladungen
7. **Klicke auf "Einladen"**
8. **Fertig!** User werden eingeladen

---

## 📤 Nachrichten weiterleiten

### Nachrichten weiterleiten

1. **Klicke auf "Weiterleiten"** im Menü
2. **Wähle Account** aus dem Dropdown
3. **Wähle Quell-Gruppe**
4. **Wähle Ziel-Gruppen** (mehrere möglich)
5. **Wähle Nachrichten:**
   - **Option A:** Nachrichten-IDs eingeben (kommagetrennt)
   - **Option B:** "Nachrichten laden" klicken und auswählen
6. **Setze Delay** zwischen Weiterleitungen
7. **Klicke auf "Weiterleiten"**
8. **Fertig!** Nachrichten werden weitergeleitet

### Nachrichten aus Gruppe laden

1. **Klicke auf "Weiterleiten"** im Menü
2. **Wähle Account und Gruppe**
3. **Klicke auf "Nachrichten laden"**
4. **Wähle Nachrichten aus** die du weiterleiten möchtest
5. **Klicke auf "Ausgewählte verwenden"**

---

## 🔥 Account-Warming

### Was ist Account-Warming?

Account-Warming simuliert natürliche Aktivität, um das Ban-Risiko zu reduzieren.

### Warming aktivieren

1. **Klicke auf "Account-Warmer"** im Menü
2. **Wähle Account** aus dem Dropdown
3. **Klicke auf "Warming konfigurieren"**
4. **Fülle die Felder aus:**
   - **Aktiv:** ✅ Aktivieren
   - **Nachrichten lesen/Tag:** 20 (Standard)
   - **Dialoge scrollen/Tag:** 10 (Standard)
   - **Reaktionen/Tag:** 5 (Standard)
   - **Kleine Nachrichten/Tag:** 3 (Standard)
   - **Startzeit:** 09:00 (Standard)
   - **Endzeit:** 22:00 (Standard)
   - **Min-Delay:** 30 Sekunden (Standard)
   - **Max-Delay:** 300 Sekunden (Standard)
5. **Klicke auf "Speichern"**
6. **Fertig!** Warming läuft automatisch

### Warming-Statistiken anzeigen

1. **Klicke auf "Account-Warmer"** im Menü
2. **Wähle Account** aus dem Dropdown
3. **Statistiken werden automatisch angezeigt:**
   - Gesamt-Aktivitäten
   - Letzte Aktivität
   - Warming-Tage

### Warming deaktivieren

1. **Klicke auf "Warming konfigurieren"**
2. **Setze "Aktiv" auf ❌**
3. **Klicke auf "Speichern"**
4. **Fertig!** Warming ist deaktiviert

---

## 📝 Nachrichtenvorlagen

### Vorlage erstellen

1. **Klicke auf "Vorlagen"** im Menü
2. **Klicke auf "+ Neue Vorlage"**
3. **Fülle die Felder aus:**
   - **Name:** Vorlagenname
   - **Nachricht:** Nachrichtentext
   - **Kategorie:** Optional (z.B. "marketing", "info")
   - **Tags:** Optional (kommagetrennt)
4. **Klicke auf "Erstellen"**
5. **Fertig!** Vorlage ist gespeichert

### Vorlage verwenden

1. **Beim Erstellen einer geplanten Nachricht:**
2. **Klicke auf "Vorlage auswählen"**
3. **Wähle Vorlage aus**
4. **Nachricht wird automatisch eingefügt**

### Vorlage bearbeiten

1. **Klicke auf "Bearbeiten"** bei der Vorlage
2. **Ändere die Felder**
3. **Klicke auf "Speichern"**

### Vorlage löschen

1. **Klicke auf "Löschen"** bei der Vorlage
2. **Bestätige die Löschung**
3. **Vorlage wird gelöscht**

---

## 🔒 Proxy-Verwaltung

### Was ist ein Proxy?

Ein Proxy schützt deine Accounts vor Bans, indem er die IP-Adresse ändert.

### Proxy hinzufügen

1. **Klicke auf "Proxies"** im Menü
2. **Klicke auf "+ Neuer Proxy"**
3. **Fülle die Felder aus:**
   - **Name:** Proxy-Name
   - **Typ:** socks5, http, https oder mtproto
   - **Host:** Proxy-Adresse
   - **Port:** Proxy-Port
   - **Username:** Optional
   - **Password:** Optional
   - **Secret:** Für MTProto
4. **Klicke auf "Erstellen"**
5. **Fertig!** Proxy ist gespeichert

### Proxy zu Account zuweisen

1. **Klicke auf "Accounts"** im Menü
2. **Beim Erstellen/Bearbeiten eines Accounts:**
3. **Wähle Proxy** aus dem Dropdown
4. **Speichern**

### Proxy testen

1. **Klicke auf "Proxies"** im Menü
2. **Klicke auf "Testen"** beim Proxy
3. **Warte auf Ergebnis**
4. **Status wird angezeigt**

### Proxy löschen

1. **Klicke auf "Löschen"** beim Proxy
2. **Bestätige die Löschung**
3. **Proxy wird gelöscht**

---

## 💡 Tipps & Tricks

### Tipp 1: Rate Limiting beachten

- **Delay zwischen Nachrichten:** Mindestens 1 Sekunde
- **Batch-Größe:** Nicht mehr als 10 Nachrichten
- **Batch-Delay:** Mindestens 5 Sekunden
- **Gruppen-Delay:** Mindestens 2 Sekunden

### Tipp 2: Account-Warming nutzen

- **Aktiviere Warming** für neue Accounts
- **Lasse Warming 7-14 Tage laufen**
- **Erhöhe Aktivität langsam**

### Tipp 3: Proxies verwenden

- **Verwende Proxies** für alle Accounts
- **Verwende verschiedene Proxies** für verschiedene Accounts
- **Teste Proxies** vor Verwendung

### Tipp 4: Nachrichtenvorlagen

- **Erstelle Vorlagen** für häufig verwendete Nachrichten
- **Verwende Variablen** in Vorlagen (wird später unterstützt)
- **Organisiere Vorlagen** mit Kategorien

### Tipp 5: Gruppen-Verwaltung

- **Lade Dialoge automatisch** statt manuell hinzuzufügen
- **Verwende Gruppennamen** statt Chat-IDs
- **Prüfe Gruppen regelmäßig** auf Gültigkeit

---

## ❓ Häufige Probleme

### Problem: Account wird nicht verbunden

**Lösung:**
1. Prüfe ob Code korrekt eingegeben wurde
2. Prüfe ob Telefonnummer korrekt ist
3. Prüfe ob API ID/Hash korrekt sind
4. Versuche Code erneut anzufordern

### Problem: Code wird nicht gesendet

**Lösung:**
1. Prüfe Telegram-App auf Code
2. Prüfe SMS (falls aktiviert)
3. Klicke auf "Code erneut anfordern"
4. Warte 1-2 Minuten

### Problem: Nachricht wird nicht gesendet

**Lösung:**
1. Prüfe ob Account verbunden ist
2. Prüfe ob Gruppe existiert
3. Prüfe ob Account in Gruppe ist
4. Prüfe Rate Limits
5. Prüfe Backend-Logs

### Problem: Gruppen werden nicht gefunden

**Lösung:**
1. Prüfe ob Account verbunden ist
2. Prüfe ob Account in Gruppe ist
3. Prüfe ob Gruppenname korrekt ist
4. Versuche Chat-ID statt Name

### Problem: FloodWait-Fehler

**Lösung:**
1. Warte die angegebene Zeit
2. Reduziere Nachrichten-Rate
3. Erhöhe Delays
4. Verwende Account-Warming

---

## 📞 Support

Bei Problemen oder Fragen:

1. **Prüfe dieses Handbuch**
2. **Prüfe die Funktions-Dokumentation**
3. **Kontaktiere den Support**

---

## 🎯 Schnellstart-Checkliste

- [ ] Account registriert
- [ ] Ersten Account hinzugefügt
- [ ] Account eingeloggt
- [ ] Erste Gruppe hinzugefügt
- [ ] Erste Nachricht geplant
- [ ] Proxy hinzugefügt (optional)
- [ ] Account-Warming aktiviert (empfohlen)

---

**Viel Erfolg mit dem Berlin City Raver Marketing Tool! 🎉**

