#!/usr/bin/env python3
"""
Telegram Mass Message Tool

WARNUNG: 
- Spam verstößt gegen Telegram Nutzungsbedingungen
- Kann zu Account-Sperrungen führen
- Nur für legitime Zwecke verwenden (eigene Chats, Test-Bots, etc.)
- Verantwortungsvoller Umgang erforderlich
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Optional, List
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import FloodWaitError, SessionPasswordNeededError

# Lade Umgebungsvariablen
load_dotenv()

# Konfiguration
API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
PHONE_NUMBER = os.getenv('TELEGRAM_PHONE_NUMBER')
SESSION_NAME = os.getenv('TELEGRAM_SESSION_NAME', 'spam_session')

# Standardwerte
DEFAULT_DELAY = 1.0  # Sekunden zwischen Nachrichten
DEFAULT_BATCH_SIZE = 10  # Nachrichten pro Batch
DEFAULT_BATCH_DELAY = 5.0  # Sekunden zwischen Batches


class TelegramSpamTool:
    """Tool zum Senden von Massennachrichten in Telegram"""
    
    def __init__(self, api_id: str, api_hash: str, session_name: str = SESSION_NAME):
        """
        Initialisiert den Telegram Client
        
        Args:
            api_id: Telegram API ID
            api_hash: Telegram API Hash
            session_name: Name der Session-Datei
        """
        if not api_id or not api_hash:
            raise ValueError("API_ID und API_HASH müssen gesetzt sein")
        
        self.client = TelegramClient(session_name, int(api_id), api_hash)
        self.sent_count = 0
        self.failed_count = 0
        
    async def connect(self, phone: Optional[str] = None):
        """Verbindet zum Telegram Account"""
        await self.client.start(phone=phone)
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(phone)
            try:
                code = input('Gib den Code ein, den du per Telegram erhalten hast: ')
                await self.client.sign_in(phone, code)
            except SessionPasswordNeededError:
                password = input('Zwei-Faktor-Authentifizierung aktiviert. Gib dein Passwort ein: ')
                await self.client.sign_in(password=password)
        
        me = await self.client.get_me()
        print(f"✓ Verbunden als: {me.first_name} {me.last_name or ''} (@{me.username or 'N/A'})")
        return me
    
    async def send_message(
        self, 
        entity: str, 
        message: str, 
        delay: float = DEFAULT_DELAY
    ) -> bool:
        """
        Sendet eine einzelne Nachricht
        
        Args:
            entity: Username, Telefonnummer oder Chat-ID
            message: Nachrichtentext
            delay: Verzögerung nach dem Senden (Sekunden)
            
        Returns:
            True bei Erfolg, False bei Fehler
        """
        try:
            await self.client.send_message(entity, message)
            self.sent_count += 1
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Nachricht #{self.sent_count} gesendet")
            if delay > 0:
                await asyncio.sleep(delay)
            return True
        except FloodWaitError as e:
            wait_time = e.seconds
            print(f"⚠ FloodWait: Warte {wait_time} Sekunden...")
            await asyncio.sleep(wait_time)
            return await self.send_message(entity, message, delay)
        except Exception as e:
            self.failed_count += 1
            print(f"✗ Fehler beim Senden: {e}")
            return False
    
    async def spam_messages(
        self,
        entity: str,
        messages: List[str],
        delay: float = DEFAULT_DELAY,
        batch_size: int = DEFAULT_BATCH_SIZE,
        batch_delay: float = DEFAULT_BATCH_DELAY
    ):
        """
        Sendet mehrere Nachrichten mit Rate Limiting
        
        Args:
            entity: Ziel-Chat (Username, Telefonnummer oder Chat-ID)
            messages: Liste der Nachrichten
            delay: Verzögerung zwischen einzelnen Nachrichten (Sekunden)
            batch_size: Anzahl Nachrichten pro Batch
            batch_delay: Verzögerung zwischen Batches (Sekunden)
        """
        total = len(messages)
        print(f"\n📤 Starte Versand von {total} Nachrichten an {entity}")
        print(f"⚙️  Einstellungen: delay={delay}s, batch_size={batch_size}, batch_delay={batch_delay}s\n")
        
        for i, message in enumerate(messages, 1):
            await self.send_message(entity, message, delay if i < total else 0)
            
            # Batch-Pause
            if i % batch_size == 0 and i < total:
                print(f"⏸ Batch-Pause: {batch_delay}s...")
                await asyncio.sleep(batch_delay)
        
        print(f"\n✅ Versand abgeschlossen!")
        print(f"   Erfolgreich: {self.sent_count}")
        print(f"   Fehlgeschlagen: {self.failed_count}")
    
    async def spam_repeat(
        self,
        entity: str,
        message: str,
        count: int,
        delay: float = DEFAULT_DELAY,
        batch_size: int = DEFAULT_BATCH_SIZE,
        batch_delay: float = DEFAULT_BATCH_DELAY
    ):
        """
        Sendet dieselbe Nachricht mehrfach
        
        Args:
            entity: Ziel-Chat
            message: Nachrichtentext
            count: Anzahl Wiederholungen
            delay: Verzögerung zwischen Nachrichten
            batch_size: Nachrichten pro Batch
            batch_delay: Verzögerung zwischen Batches
        """
        messages = [message] * count
        await self.spam_messages(entity, messages, delay, batch_size, batch_delay)
    
    async def disconnect(self):
        """Trennt die Verbindung"""
        await self.client.disconnect()
        print("✓ Verbindung getrennt")


async def main():
    """Hauptfunktion"""
    print("=" * 60)
    print("TELEGRAM MASS MESSAGE TOOL")
    print("=" * 60)
    print("\n⚠️  WARNUNG: Spam kann zu Account-Sperrungen führen!")
    print("⚠️  Nur für legitime Zwecke verwenden!\n")
    
    # Konfiguration prüfen
    if not API_ID or not API_HASH:
        print("❌ FEHLER: TELEGRAM_API_ID und TELEGRAM_API_HASH müssen in .env gesetzt sein")
        print("\nErstelle eine .env Datei mit:")
        print("TELEGRAM_API_ID=deine_api_id")
        print("TELEGRAM_API_HASH=dein_api_hash")
        print("TELEGRAM_PHONE_NUMBER=+491234567890")
        sys.exit(1)
    
    # Tool initialisieren
    tool = TelegramSpamTool(API_ID, API_HASH)
    
    try:
        # Verbinden
        await tool.connect(PHONE_NUMBER)
        
        # Interaktive Eingabe
        print("\n" + "=" * 60)
        target = input("Ziel-Chat (Username, Telefonnummer oder Chat-ID): ").strip()
        
        mode = input("\nModus:\n  1 = Einzelne Nachricht mehrfach senden\n  2 = Mehrere verschiedene Nachrichten senden\nWahl (1/2): ").strip()
        
        if mode == "1":
            message = input("Nachricht: ").strip()
            count = int(input("Anzahl Wiederholungen: ").strip())
            delay = float(input(f"Verzögerung zwischen Nachrichten (Sekunden, Standard {DEFAULT_DELAY}): ").strip() or DEFAULT_DELAY)
            batch_size = int(input(f"Batch-Größe (Standard {DEFAULT_BATCH_SIZE}): ").strip() or DEFAULT_BATCH_SIZE)
            batch_delay = float(input(f"Verzögerung zwischen Batches (Sekunden, Standard {DEFAULT_BATCH_DELAY}): ").strip() or DEFAULT_BATCH_DELAY)
            
            await tool.spam_repeat(target, message, count, delay, batch_size, batch_delay)
        
        elif mode == "2":
            print("\nGib Nachrichten ein (leere Zeile zum Beenden):")
            messages = []
            while True:
                msg = input(f"Nachricht #{len(messages) + 1}: ").strip()
                if not msg:
                    break
                messages.append(msg)
            
            if not messages:
                print("❌ Keine Nachrichten eingegeben")
                return
            
            delay = float(input(f"Verzögerung zwischen Nachrichten (Sekunden, Standard {DEFAULT_DELAY}): ").strip() or DEFAULT_DELAY)
            batch_size = int(input(f"Batch-Größe (Standard {DEFAULT_BATCH_SIZE}): ").strip() or DEFAULT_BATCH_SIZE)
            batch_delay = float(input(f"Verzögerung zwischen Batches (Sekunden, Standard {DEFAULT_BATCH_DELAY}): ").strip() or DEFAULT_BATCH_DELAY)
            
            await tool.spam_messages(target, messages, delay, batch_size, batch_delay)
        
        else:
            print("❌ Ungültige Auswahl")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Abgebrochen durch Benutzer")
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await tool.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

