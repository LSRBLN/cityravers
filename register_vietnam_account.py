#!/usr/bin/env python3
"""
Registriert einen Telegram-Account mit vietnamesischer Nummer und loggt ihn ein

Verwendung:
    python3 register_vietnam_account.py [CODE] [PASSWORD]
    
    CODE: Telegram-Verifizierungscode (optional, wird interaktiv abgefragt wenn nicht angegeben)
    PASSWORD: 2FA-Passwort (optional, wird interaktiv abgefragt wenn nötig)
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneNumberInvalidError, FloodWaitError

# Lade Umgebungsvariablen
load_dotenv()

# Telefonnummer normalisieren
PHONE_NUMBER = "+84925394919"  # +84 (925) 394-919 normalisiert

# Code und Passwort aus Argumenten
CODE = sys.argv[1] if len(sys.argv) > 1 else None
PASSWORD = sys.argv[2] if len(sys.argv) > 2 else None

async def register_and_login():
    """Registriert und loggt einen Telegram-Account ein"""
    
    # Lade API Credentials
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    
    if not api_id or not api_hash:
        print("❌ FEHLER: TELEGRAM_API_ID und TELEGRAM_API_HASH müssen in .env gesetzt sein")
        sys.exit(1)
    
    # Session-Pfad erstellen
    session_dir = Path("sessions")
    session_dir.mkdir(exist_ok=True)
    
    # Session-Name: entferne + und Leerzeichen
    session_name = session_dir / f"vietnam_{PHONE_NUMBER.replace('+', '').replace(' ', '')}"
    
    print(f"📱 Registriere Account mit Nummer: {PHONE_NUMBER}")
    print(f"💾 Session wird gespeichert in: {session_name}.session")
    
    # Erstelle Client
    client = TelegramClient(str(session_name), int(api_id), api_hash)
    
    try:
        # Verbinde
        await client.connect()
        print("✅ Verbunden mit Telegram")
        
        # Prüfe ob bereits autorisiert
        if await client.is_user_authorized():
            me = await client.get_me()
            print(f"✅ Account bereits eingeloggt als: {me.first_name} {me.last_name or ''} (@{me.username or 'N/A'})")
            print(f"📞 Telefonnummer: {me.phone}")
            return
        
        # Nicht autorisiert - starte Registrierung
        print(f"📲 Sende Code-Anfrage an {PHONE_NUMBER}...")
        
        try:
            # Sende Code-Anfrage (nicht per SMS, sondern per Telegram-App wenn möglich)
            sent_code = await client.send_code_request(PHONE_NUMBER, force_sms=False)
            print(f"✅ Code-Anfrage gesendet")
            print(f"📋 Phone Code Hash: {sent_code.phone_code_hash[:10]}...")
            
            # Warte auf Code-Eingabe
            code = CODE
            if not code:
                print("\n" + "="*60)
                print("⚠️  WICHTIG: Du musst den Code eingeben, der per Telegram gesendet wurde")
                print("="*60)
                code = input("\n📝 Gib den Code ein, den du per Telegram erhalten hast: ").strip()
            
            if not code:
                print("❌ Kein Code eingegeben. Abbruch.")
                print(f"\n💡 Tipp: Du kannst den Code auch als Argument übergeben:")
                print(f"   python3 register_vietnam_account.py <CODE>")
                return
            
            # Versuche mit Code einzuloggen
            try:
                me = await client.sign_in(PHONE_NUMBER, code, phone_code_hash=sent_code.phone_code_hash)
                print(f"✅ Account erfolgreich registriert und eingeloggt!")
                print(f"👤 Name: {me.first_name} {me.last_name or ''}")
                print(f"📱 Username: @{me.username or 'N/A'}")
                print(f"📞 Telefonnummer: {me.phone}")
                print(f"🆔 User ID: {me.id}")
                
            except SessionPasswordNeededError:
                # 2FA aktiviert
                password = PASSWORD
                if not password:
                    print("\n🔐 Zwei-Faktor-Authentifizierung ist aktiviert")
                    password = input("🔑 Gib dein 2FA-Passwort ein: ").strip()
                
                if not password:
                    print("❌ Kein Passwort eingegeben. Abbruch.")
                    print(f"\n💡 Tipp: Du kannst das Passwort auch als Argument übergeben:")
                    print(f"   python3 register_vietnam_account.py <CODE> <PASSWORD>")
                    return
                
                me = await client.sign_in(password=password)
                print(f"✅ Account erfolgreich eingeloggt!")
                print(f"👤 Name: {me.first_name} {me.last_name or ''}")
                print(f"📱 Username: @{me.username or 'N/A'}")
                print(f"📞 Telefonnummer: {me.phone}")
                print(f"🆔 User ID: {me.id}")
                
        except PhoneNumberInvalidError:
            print(f"❌ FEHLER: Ungültige Telefonnummer: {PHONE_NUMBER}")
            return
        except FloodWaitError as e:
            print(f"⏳ FEHLER: Rate Limit erreicht. Warte {e.seconds} Sekunden...")
            return
        except Exception as e:
            print(f"❌ FEHLER beim Senden der Code-Anfrage: {str(e)}")
            return
        
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await client.disconnect()
        print("\n✅ Verbindung geschlossen")
        print(f"💾 Session gespeichert: {session_name}.session")

if __name__ == "__main__":
    print("="*60)
    print("🇻🇳 Telegram Account Registrierung - Vietnam")
    print("="*60)
    print()
    
    asyncio.run(register_and_login())

