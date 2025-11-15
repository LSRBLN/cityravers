import React, { useState } from 'react'
import { useDevice } from '../hooks/useDevice'
import './Handbook.css'

export default function Handbook() {
  const { isMobile } = useDevice()
  const [activeSection, setActiveSection] = useState('getting-started')

  const sections = [
    { id: 'getting-started', title: '🚀 Erste Schritte', icon: '🚀' },
    { id: 'accounts', title: '👤 Account-Verwaltung', icon: '👤' },
    { id: 'groups', title: '👥 Gruppen-Verwaltung', icon: '👥' },
    { id: 'messages', title: '📅 Nachrichten planen', icon: '📅' },
    { id: 'scraping', title: '👥 User-Scraping', icon: '👥' },
    { id: 'forwarding', title: '📤 Nachrichten weiterleiten', icon: '📤' },
    { id: 'warming', title: '🔥 Account-Warming', icon: '🔥' },
    { id: 'templates', title: '📝 Nachrichtenvorlagen', icon: '📝' },
    { id: 'proxies', title: '🔒 Proxy-Verwaltung', icon: '🔒' },
    { id: 'tips', title: '💡 Tipps & Tricks', icon: '💡' },
    { id: 'troubleshooting', title: '❓ Häufige Probleme', icon: '❓' },
  ]

  const content = {
    'getting-started': {
      title: '🚀 Erste Schritte',
      content: `
        <h2>Registrierung</h2>
        <ol>
          <li><strong>Öffne die App</strong> im Browser</li>
          <li><strong>Klicke auf "Registrieren"</strong></li>
          <li><strong>Fülle die Felder aus:</strong>
            <ul>
              <li>Email-Adresse</li>
              <li>Benutzername</li>
              <li>Passwort (mindestens 6 Zeichen)</li>
            </ul>
          </li>
          <li><strong>Klicke auf "Registrieren"</strong></li>
        </ol>
        
        <div class="info-box">
          <strong>✅ Du erhältst automatisch:</strong>
          <ul>
            <li>7 Tage kostenlosen Testzugang</li>
            <li>2 Accounts</li>
            <li>5 Gruppen</li>
            <li>10 Nachrichten pro Tag</li>
          </ul>
        </div>

        <h2>Login</h2>
        <ol>
          <li><strong>Öffne die App</strong></li>
          <li><strong>Gib deine Anmeldedaten ein:</strong>
            <ul>
              <li>Username oder Email</li>
              <li>Passwort</li>
            </ul>
          </li>
          <li><strong>Klicke auf "Einloggen"</strong></li>
        </ol>
        
        <div class="tip-box">
          <strong>💡 Tipp:</strong> Du bleibst 7 Tage eingeloggt (Token-Ablaufzeit)
        </div>
      `
    },
    'accounts': {
      title: '👤 Account-Verwaltung',
      content: `
        <h2>Neuen Account hinzufügen</h2>
        
        <h3>Option 1: User-Account (Telefonnummer)</h3>
        <ol>
          <li><strong>Klicke auf "Accounts"</strong> im Menü</li>
          <li><strong>Klicke auf "+ Neuer Account"</strong></li>
          <li><strong>Fülle die Felder aus:</strong>
            <ul>
              <li><strong>Account-Name:</strong> Beliebiger Name (z.B. "Mein Account")</li>
              <li><strong>Account-Typ:</strong> "User Account"</li>
              <li><strong>API ID:</strong> Von https://my.telegram.org/apps (optional)</li>
              <li><strong>API Hash:</strong> Von https://my.telegram.org/apps (optional)</li>
              <li><strong>Telefonnummer:</strong> Deine Telegram-Nummer (+49...)</li>
              <li><strong>Session-Name:</strong> Eindeutiger Name (z.B. "account1_session")</li>
              <li><strong>Proxy:</strong> Optional (zum Ban-Schutz)</li>
            </ul>
          </li>
          <li><strong>Klicke auf "Erstellen"</strong></li>
          <li><strong>Code eingeben:</strong>
            <ul>
              <li>Code wird automatisch an deine Telefonnummer/Telegram gesendet</li>
              <li>Gib den Code im Modal ein</li>
              <li>Bei 2FA: Gib dein Passwort ein</li>
            </ul>
          </li>
          <li><strong>Fertig!</strong> Account ist verbunden</li>
        </ol>

        <h3>Option 2: Bot-Account</h3>
        <ol>
          <li><strong>Klicke auf "Accounts"</strong> im Menü</li>
          <li><strong>Klicke auf "+ Neuer Account"</strong></li>
          <li><strong>Fülle die Felder aus:</strong>
            <ul>
              <li><strong>Account-Name:</strong> Beliebiger Name</li>
              <li><strong>Account-Typ:</strong> "Bot"</li>
              <li><strong>Bot Token:</strong> Von @BotFather</li>
            </ul>
          </li>
          <li><strong>Klicke auf "Erstellen"</strong></li>
          <li><strong>Fertig!</strong> Bot ist sofort verbunden</li>
        </ol>

        <h3>Option 3: Session-Datei hochladen</h3>
        <ol>
          <li><strong>Klicke auf "📁 Session-Datei"</strong> Button</li>
          <li><strong>Lade .session Datei hoch</strong></li>
          <li><strong>Gib Account-Name ein</strong></li>
          <li><strong>Klicke auf "Account erstellen"</strong></li>
          <li><strong>Fertig!</strong> Account wird automatisch verbunden</li>
        </ol>

        <h2>Account einloggen</h2>
        <p>Wenn ein Account nicht verbunden ist:</p>
        <ol>
          <li><strong>Klicke auf "🔐 Login"</strong> Button beim Account</li>
          <li><strong>Code wird automatisch angefordert</strong></li>
          <li><strong>Gib den Code ein</strong> (wird per Telegram gesendet)</li>
          <li><strong>Bei 2FA:</strong> Gib dein Passwort ein</li>
          <li><strong>Fertig!</strong> Account ist verbunden</li>
        </ol>

        <h2>Account löschen</h2>
        <ol>
          <li><strong>Klicke auf "Löschen"</strong> Button beim Account</li>
          <li><strong>Bestätige die Löschung</strong></li>
          <li><strong>Account wird gelöscht</strong></li>
        </ol>
      `
    },
    'groups': {
      title: '👥 Gruppen-Verwaltung',
      content: `
        <h2>Gruppen hinzufügen</h2>
        
        <h3>Option 1: Automatisch aus Dialogen</h3>
        <ol>
          <li><strong>Klicke auf "Gruppen"</strong> im Menü</li>
          <li><strong>Wähle einen verbundenen Account</strong> aus dem Dropdown</li>
          <li><strong>Klicke auf "Dialoge laden"</strong></li>
          <li><strong>Wähle Gruppen aus</strong> die du hinzufügen möchtest</li>
          <li><strong>Klicke auf "Ausgewählte hinzufügen"</strong></li>
          <li><strong>Fertig!</strong> Gruppen sind gespeichert</li>
        </ol>

        <h3>Option 2: Manuell hinzufügen</h3>
        <ol>
          <li><strong>Klicke auf "Gruppen"</strong> im Menü</li>
          <li><strong>Klicke auf "+ Manuell hinzufügen"</strong></li>
          <li><strong>Fülle die Felder aus:</strong>
            <ul>
              <li><strong>Name:</strong> Gruppenname</li>
              <li><strong>Chat-ID:</strong> Telegram Chat-ID (optional)</li>
              <li><strong>Typ:</strong> group, channel oder private</li>
              <li><strong>Username:</strong> @username (optional)</li>
            </ul>
          </li>
          <li><strong>Klicke auf "Erstellen"</strong></li>
          <li><strong>Fertig!</strong> Gruppe ist gespeichert</li>
        </ol>

        <h3>Option 3: Nach Namen suchen</h3>
        <ol>
          <li><strong>Klicke auf "Gruppen"</strong> im Menü</li>
          <li><strong>Klicke auf "Nach Namen suchen"</strong></li>
          <li><strong>Wähle Account</strong> aus dem Dropdown</li>
          <li><strong>Gib Gruppennamen ein</strong> (eine pro Zeile)</li>
          <li><strong>Klicke auf "Suchen"</strong></li>
          <li><strong>Wähle gefundene Gruppen aus</strong></li>
          <li><strong>Klicke auf "Hinzufügen"</strong></li>
          <li><strong>Fertig!</strong> Gruppen sind gespeichert</li>
        </ol>

        <h2>Gruppen löschen</h2>
        <ol>
          <li><strong>Klicke auf "Löschen"</strong> Button bei der Gruppe</li>
          <li><strong>Bestätige die Löschung</strong></li>
          <li><strong>Gruppe wird gelöscht</strong></li>
        </ol>
      `
    },
    'messages': {
      title: '📅 Nachrichten planen',
      content: `
        <h2>Neue geplante Nachricht erstellen</h2>
        <ol>
          <li><strong>Klicke auf "Geplante Nachrichten"</strong> im Menü</li>
          <li><strong>Klicke auf "+ Neue geplante Nachricht"</strong></li>
          <li><strong>Fülle die Felder aus:</strong>
            <ul>
              <li><strong>Account:</strong> Wähle verbundenen Account</li>
              <li><strong>Gruppen:</strong> Wähle eine oder mehrere Gruppen</li>
              <li><strong>Nachricht:</strong> Dein Nachrichtentext</li>
              <li><strong>Geplant für:</strong> Datum und Uhrzeit</li>
              <li><strong>Wiederholungen:</strong> Wie oft senden (Standard: 1)</li>
              <li><strong>Delay:</strong> Sekunden zwischen Nachrichten (Standard: 1s)</li>
              <li><strong>Batch-Größe:</strong> Nachrichten pro Batch (Standard: 10)</li>
              <li><strong>Batch-Delay:</strong> Pause zwischen Batches (Standard: 5s)</li>
              <li><strong>Gruppen-Delay:</strong> Pause zwischen verschiedenen Gruppen (Standard: 2s)</li>
            </ul>
          </li>
          <li><strong>Klicke auf "Erstellen"</strong></li>
          <li><strong>Fertig!</strong> Nachricht ist geplant</li>
        </ol>

        <h2>Nachricht bearbeiten</h2>
        <ol>
          <li><strong>Klicke auf "Bearbeiten"</strong> bei der Nachricht</li>
          <li><strong>Ändere die Felder</strong></li>
          <li><strong>Klicke auf "Speichern"</strong></li>
        </ol>

        <h2>Nachricht abbrechen</h2>
        <ol>
          <li><strong>Klicke auf "Abbrechen"</strong> bei der Nachricht</li>
          <li><strong>Bestätige die Abbrechung</strong></li>
          <li><strong>Nachricht wird abgebrochen</strong></li>
        </ol>

        <h2>Testnachricht senden</h2>
        <ol>
          <li><strong>Klicke auf "Geplante Nachrichten"</strong> im Menü</li>
          <li><strong>Klicke auf "Test senden"</strong> Button</li>
          <li><strong>Wähle Account und Gruppe</strong></li>
          <li><strong>Gib Nachricht ein</strong></li>
          <li><strong>Klicke auf "Senden"</strong></li>
          <li><strong>Nachricht wird sofort gesendet</strong></li>
        </ol>
      `
    },
    'scraping': {
      title: '👥 User-Scraping',
      content: `
        <h2>Mitglieder aus Gruppe scrapen</h2>
        <ol>
          <li><strong>Klicke auf "User-Scraping"</strong> im Menü</li>
          <li><strong>Wähle Account</strong> aus dem Dropdown</li>
          <li><strong>Wähle Gruppe</strong> aus dem Dropdown</li>
          <li><strong>Setze Limit</strong> (Standard: 10000)</li>
          <li><strong>Klicke auf "Mitglieder scrapen"</strong></li>
          <li><strong>Warte bis fertig</strong> (kann einige Minuten dauern)</li>
          <li><strong>Fertig!</strong> User sind gespeichert</li>
        </ol>

        <h2>Gescrapte User anzeigen</h2>
        <ol>
          <li><strong>Klicke auf "User-Scraping"</strong> im Menü</li>
          <li><strong>Gescrapte User werden automatisch angezeigt</strong></li>
          <li><strong>Du siehst:</strong>
            <ul>
              <li>Username</li>
              <li>Name</li>
              <li>Telefonnummer (falls verfügbar)</li>
              <li>Quell-Gruppe</li>
            </ul>
          </li>
        </ol>

        <h2>User zu Gruppe einladen</h2>
        <ol>
          <li><strong>Klicke auf "User-Scraping"</strong> im Menü</li>
          <li><strong>Klicke auf "User einladen"</strong> Button</li>
          <li><strong>Wähle Account</strong> (muss Admin sein)</li>
          <li><strong>Wähle Ziel-Gruppe</strong></li>
          <li><strong>Wähle User aus</strong> oder lade alle gescrapten User</li>
          <li><strong>Setze Delay</strong> zwischen Einladungen</li>
          <li><strong>Klicke auf "Einladen"</strong></li>
          <li><strong>Fertig!</strong> User werden eingeladen</li>
        </ol>
      `
    },
    'forwarding': {
      title: '📤 Nachrichten weiterleiten',
      content: `
        <h2>Nachrichten weiterleiten</h2>
        <ol>
          <li><strong>Klicke auf "Weiterleiten"</strong> im Menü</li>
          <li><strong>Wähle Account</strong> aus dem Dropdown</li>
          <li><strong>Wähle Quell-Gruppe</strong></li>
          <li><strong>Wähle Ziel-Gruppen</strong> (mehrere möglich)</li>
          <li><strong>Wähle Nachrichten:</strong>
            <ul>
              <li><strong>Option A:</strong> Nachrichten-IDs eingeben (kommagetrennt)</li>
              <li><strong>Option B:</strong> "Nachrichten laden" klicken und auswählen</li>
            </ul>
          </li>
          <li><strong>Setze Delay</strong> zwischen Weiterleitungen</li>
          <li><strong>Klicke auf "Weiterleiten"</strong></li>
          <li><strong>Fertig!</strong> Nachrichten werden weitergeleitet</li>
        </ol>

        <h2>Nachrichten aus Gruppe laden</h2>
        <ol>
          <li><strong>Klicke auf "Weiterleiten"</strong> im Menü</li>
          <li><strong>Wähle Account und Gruppe</strong></li>
          <li><strong>Klicke auf "Nachrichten laden"</strong></li>
          <li><strong>Wähle Nachrichten aus</strong> die du weiterleiten möchtest</li>
          <li><strong>Klicke auf "Ausgewählte verwenden"</strong></li>
        </ol>
      `
    },
    'warming': {
      title: '🔥 Account-Warming',
      content: `
        <h2>Was ist Account-Warming?</h2>
        <p>Account-Warming simuliert natürliche Aktivität, um das Ban-Risiko zu reduzieren.</p>

        <h2>Warming aktivieren</h2>
        <ol>
          <li><strong>Klicke auf "Account-Warmer"</strong> im Menü</li>
          <li><strong>Wähle Account</strong> aus dem Dropdown</li>
          <li><strong>Klicke auf "Warming konfigurieren"</strong></li>
          <li><strong>Fülle die Felder aus:</strong>
            <ul>
              <li><strong>Aktiv:</strong> ✅ Aktivieren</li>
              <li><strong>Nachrichten lesen/Tag:</strong> 20 (Standard)</li>
              <li><strong>Dialoge scrollen/Tag:</strong> 10 (Standard)</li>
              <li><strong>Reaktionen/Tag:</strong> 5 (Standard)</li>
              <li><strong>Kleine Nachrichten/Tag:</strong> 3 (Standard)</li>
              <li><strong>Startzeit:</strong> 09:00 (Standard)</li>
              <li><strong>Endzeit:</strong> 22:00 (Standard)</li>
              <li><strong>Min-Delay:</strong> 30 Sekunden (Standard)</li>
              <li><strong>Max-Delay:</strong> 300 Sekunden (Standard)</li>
            </ul>
          </li>
          <li><strong>Klicke auf "Speichern"</strong></li>
          <li><strong>Fertig!</strong> Warming läuft automatisch</li>
        </ol>

        <h2>Warming-Statistiken anzeigen</h2>
        <ol>
          <li><strong>Klicke auf "Account-Warmer"</strong> im Menü</li>
          <li><strong>Wähle Account</strong> aus dem Dropdown</li>
          <li><strong>Statistiken werden automatisch angezeigt:</strong>
            <ul>
              <li>Gesamt-Aktivitäten</li>
              <li>Letzte Aktivität</li>
              <li>Warming-Tage</li>
            </ul>
          </li>
        </ol>

        <h2>Warming deaktivieren</h2>
        <ol>
          <li><strong>Klicke auf "Warming konfigurieren"</strong></li>
          <li><strong>Setze "Aktiv" auf ❌</strong></li>
          <li><strong>Klicke auf "Speichern"</strong></li>
          <li><strong>Fertig!</strong> Warming ist deaktiviert</li>
        </ol>
      `
    },
    'templates': {
      title: '📝 Nachrichtenvorlagen',
      content: `
        <h2>Vorlage erstellen</h2>
        <ol>
          <li><strong>Klicke auf "Vorlagen"</strong> im Menü</li>
          <li><strong>Klicke auf "+ Neue Vorlage"</strong></li>
          <li><strong>Fülle die Felder aus:</strong>
            <ul>
              <li><strong>Name:</strong> Vorlagenname</li>
              <li><strong>Nachricht:</strong> Nachrichtentext</li>
              <li><strong>Kategorie:</strong> Optional (z.B. "marketing", "info")</li>
              <li><strong>Tags:</strong> Optional (kommagetrennt)</li>
            </ul>
          </li>
          <li><strong>Klicke auf "Erstellen"</strong></li>
          <li><strong>Fertig!</strong> Vorlage ist gespeichert</li>
        </ol>

        <h2>Vorlage verwenden</h2>
        <ol>
          <li><strong>Beim Erstellen einer geplanten Nachricht:</strong></li>
          <li><strong>Klicke auf "Vorlage auswählen"</strong></li>
          <li><strong>Wähle Vorlage aus</strong></li>
          <li><strong>Nachricht wird automatisch eingefügt</strong></li>
        </ol>

        <h2>Vorlage bearbeiten</h2>
        <ol>
          <li><strong>Klicke auf "Bearbeiten"</strong> bei der Vorlage</li>
          <li><strong>Ändere die Felder</strong></li>
          <li><strong>Klicke auf "Speichern"</strong></li>
        </ol>

        <h2>Vorlage löschen</h2>
        <ol>
          <li><strong>Klicke auf "Löschen"</strong> bei der Vorlage</li>
          <li><strong>Bestätige die Löschung</strong></li>
          <li><strong>Vorlage wird gelöscht</strong></li>
        </ol>
      `
    },
    'proxies': {
      title: '🔒 Proxy-Verwaltung',
      content: `
        <h2>Was ist ein Proxy?</h2>
        <p>Ein Proxy schützt deine Accounts vor Bans, indem er die IP-Adresse ändert.</p>

        <h2>Proxy hinzufügen</h2>
        <ol>
          <li><strong>Klicke auf "Proxies"</strong> im Menü</li>
          <li><strong>Klicke auf "+ Neuer Proxy"</strong></li>
          <li><strong>Fülle die Felder aus:</strong>
            <ul>
              <li><strong>Name:</strong> Proxy-Name</li>
              <li><strong>Typ:</strong> socks5, http, https oder mtproto</li>
              <li><strong>Host:</strong> Proxy-Adresse</li>
              <li><strong>Port:</strong> Proxy-Port</li>
              <li><strong>Username:</strong> Optional</li>
              <li><strong>Password:</strong> Optional</li>
              <li><strong>Secret:</strong> Für MTProto</li>
            </ul>
          </li>
          <li><strong>Klicke auf "Erstellen"</strong></li>
          <li><strong>Fertig!</strong> Proxy ist gespeichert</li>
        </ol>

        <h2>Proxy zu Account zuweisen</h2>
        <ol>
          <li><strong>Klicke auf "Accounts"</strong> im Menü</li>
          <li><strong>Beim Erstellen/Bearbeiten eines Accounts:</strong></li>
          <li><strong>Wähle Proxy</strong> aus dem Dropdown</li>
          <li><strong>Speichern</strong></li>
        </ol>

        <h2>Proxy testen</h2>
        <ol>
          <li><strong>Klicke auf "Proxies"</strong> im Menü</li>
          <li><strong>Klicke auf "Testen"</strong> beim Proxy</li>
          <li><strong>Warte auf Ergebnis</strong></li>
          <li><strong>Status wird angezeigt</strong></li>
        </ol>

        <h2>Proxy löschen</h2>
        <ol>
          <li><strong>Klicke auf "Löschen"</strong> beim Proxy</li>
          <li><strong>Bestätige die Löschung</strong></li>
          <li><strong>Proxy wird gelöscht</strong></li>
        </ol>
      `
    },
    'tips': {
      title: '💡 Tipps & Tricks',
      content: `
        <h2>Tipp 1: Rate Limiting beachten</h2>
        <ul>
          <li><strong>Delay zwischen Nachrichten:</strong> Mindestens 1 Sekunde</li>
          <li><strong>Batch-Größe:</strong> Nicht mehr als 10 Nachrichten</li>
          <li><strong>Batch-Delay:</strong> Mindestens 5 Sekunden</li>
          <li><strong>Gruppen-Delay:</strong> Mindestens 2 Sekunden</li>
        </ul>

        <h2>Tipp 2: Account-Warming nutzen</h2>
        <ul>
          <li><strong>Aktiviere Warming</strong> für neue Accounts</li>
          <li><strong>Lasse Warming 7-14 Tage laufen</strong></li>
          <li><strong>Erhöhe Aktivität langsam</strong></li>
        </ul>

        <h2>Tipp 3: Proxies verwenden</h2>
        <ul>
          <li><strong>Verwende Proxies</strong> für alle Accounts</li>
          <li><strong>Verwende verschiedene Proxies</strong> für verschiedene Accounts</li>
          <li><strong>Teste Proxies</strong> vor Verwendung</li>
        </ul>

        <h2>Tipp 4: Nachrichtenvorlagen</h2>
        <ul>
          <li><strong>Erstelle Vorlagen</strong> für häufig verwendete Nachrichten</li>
          <li><strong>Organisiere Vorlagen</strong> mit Kategorien</li>
          <li><strong>Verwende Vorlagen</strong> für Konsistenz</li>
        </ul>

        <h2>Tipp 5: Gruppen-Verwaltung</h2>
        <ul>
          <li><strong>Lade Dialoge automatisch</strong> statt manuell hinzuzufügen</li>
          <li><strong>Verwende Gruppennamen</strong> statt Chat-IDs</li>
          <li><strong>Prüfe Gruppen regelmäßig</strong> auf Gültigkeit</li>
        </ul>
      `
    },
    'troubleshooting': {
      title: '❓ Häufige Probleme',
      content: `
        <h2>Problem: Account wird nicht verbunden</h2>
        <p><strong>Lösung:</strong></p>
        <ol>
          <li>Prüfe ob Code korrekt eingegeben wurde</li>
          <li>Prüfe ob Telefonnummer korrekt ist</li>
          <li>Prüfe ob API ID/Hash korrekt sind</li>
          <li>Versuche Code erneut anzufordern</li>
        </ol>

        <h2>Problem: Code wird nicht gesendet</h2>
        <p><strong>Lösung:</strong></p>
        <ol>
          <li>Prüfe Telegram-App auf Code</li>
          <li>Prüfe SMS (falls aktiviert)</li>
          <li>Klicke auf "Code erneut anfordern"</li>
          <li>Warte 1-2 Minuten</li>
        </ol>

        <h2>Problem: Nachricht wird nicht gesendet</h2>
        <p><strong>Lösung:</strong></p>
        <ol>
          <li>Prüfe ob Account verbunden ist</li>
          <li>Prüfe ob Gruppe existiert</li>
          <li>Prüfe ob Account in Gruppe ist</li>
          <li>Prüfe Rate Limits</li>
          <li>Prüfe Backend-Logs</li>
        </ol>

        <h2>Problem: Gruppen werden nicht gefunden</h2>
        <p><strong>Lösung:</strong></p>
        <ol>
          <li>Prüfe ob Account verbunden ist</li>
          <li>Prüfe ob Account in Gruppe ist</li>
          <li>Prüfe ob Gruppenname korrekt ist</li>
          <li>Versuche Chat-ID statt Name</li>
        </ol>

        <h2>Problem: FloodWait-Fehler</h2>
        <p><strong>Lösung:</strong></p>
        <ol>
          <li>Warte die angegebene Zeit</li>
          <li>Reduziere Nachrichten-Rate</li>
          <li>Erhöhe Delays</li>
          <li>Verwende Account-Warming</li>
        </ol>
      `
    }
  }

  return (
    <div className={`handbook-container ${isMobile ? 'mobile' : ''}`}>
      <div className="handbook-header">
        <h1>📖 Handbuch für Diego</h1>
        <p>Vollständige Benutzeranleitung für das Berlin City Raver Marketing Tool</p>
      </div>

      <div className="handbook-content-wrapper">
        {/* Sidebar Navigation */}
        <div className={`handbook-sidebar ${isMobile ? 'mobile' : ''}`}>
          <h3>Inhaltsverzeichnis</h3>
          <nav className="handbook-nav">
            {sections.map((section) => (
              <button
                key={section.id}
                className={`handbook-nav-item ${activeSection === section.id ? 'active' : ''}`}
                onClick={() => setActiveSection(section.id)}
              >
                <span className="handbook-nav-icon">{section.icon}</span>
                <span className="handbook-nav-label">{section.title}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Main Content */}
        <div className="handbook-main">
          <div className="handbook-section">
            <h2>{content[activeSection]?.title || 'Handbuch'}</h2>
            <div 
              className="handbook-content"
              dangerouslySetInnerHTML={{ __html: content[activeSection]?.content || '<p>Inhalt wird geladen...</p>' }}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

