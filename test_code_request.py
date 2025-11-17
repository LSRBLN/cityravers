#!/usr/bin/env python3
"""
Test-Skript zum Prüfen der Code-Anfrage-Funktionalität
"""

import os
import sys
import asyncio
from pathlib import Path

# Füge das Projekt-Root-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from database import init_db, get_session, Account, User
from account_manager import AccountManager

async def test_code_request(account_id: int = None):
    """Testet die Code-Anfrage für einen Account"""
    print("🔍 Initialisiere Datenbank...")
    db_engine = init_db()
    db = get_session(db_engine)
    
    try:
        # Finde Admin-User
        admin_user = db.query(User).filter(User.is_admin == True).first()
        if not admin_user:
            print("❌ Kein Admin-User gefunden!")
            return
        
        print(f"✅ Admin-User gefunden: {admin_user.username} (ID: {admin_user.id})\n")
        
        # Finde Account
        if account_id:
            account = db.query(Account).filter(Account.id == account_id).first()
        else:
            # Nimm ersten nicht-verbundenen Account
            account = db.query(Account).filter(
                Account.user_id == admin_user.id,
                Account.account_type == 'user'
            ).first()
        
        if not account:
            print("❌ Kein Account gefunden!")
            return
        
        print(f"📋 Account gefunden:")
        print(f"   ID: {account.id}")
        print(f"   Name: {account.name}")
        print(f"   Telefonnummer: {account.phone_number}")
        print(f"   Session-Name: {account.session_name}")
        print(f"   API ID: {account.api_id or 'Nicht gesetzt'}")
        print(f"   API Hash: {'Vorhanden' if account.api_hash else 'Nicht gesetzt'}")
        print(f"   Session-Datei: {account.session_file_path or 'Nicht gesetzt'}\n")
        
        # Prüfe API Credentials
        api_id = account.api_id or os.getenv('TELEGRAM_API_ID')
        api_hash = account.api_hash or os.getenv('TELEGRAM_API_HASH')
        
        if not api_id or not api_hash:
            print("❌ API Credentials fehlen!")
            print(f"   API ID: {api_id or 'Nicht gesetzt'}")
            print(f"   API Hash: {'Vorhanden' if api_hash else 'Nicht gesetzt'}")
            print("\n💡 Lösung: Setze TELEGRAM_API_ID und TELEGRAM_API_HASH in .env oder in den Account-Einstellungen")
            return
        
        print(f"✅ API Credentials vorhanden\n")
        
        # Prüfe Telefonnummer
        if not account.phone_number:
            print("❌ Telefonnummer fehlt!")
            return
        
        # Normalisiere Telefonnummer
        phone_number = account.phone_number.strip().replace(" ", "").replace("-", "")
        if not phone_number.startswith("+"):
            if not phone_number.startswith("00"):
                phone_number = "+" + phone_number
            else:
                phone_number = "+" + phone_number[2:]
        
        print(f"📞 Telefonnummer (normalisiert): {phone_number}\n")
        
        # Teste Code-Anfrage
        print("🔄 Teste Code-Anfrage...\n")
        
        account_manager = AccountManager()
        
        result = await account_manager.add_account(
            account_id=account.id,
            api_id=api_id,
            api_hash=api_hash,
            session_name=account.session_name,
            phone_number=phone_number,
            session_file_path=account.session_file_path
        )
        
        print(f"\n📊 Ergebnis:")
        print(f"   Status: {result.get('status')}")
        
        if result.get('status') == 'code_required':
            print(f"   ✅ Code wurde angefordert!")
            print(f"   Code-Typ: {result.get('code_type', 'unknown')}")
            print(f"   Nachricht: {result.get('message', 'N/A')}")
            print(f"\n💡 Prüfe jetzt deine Telegram-App oder SMS für den Code!")
        elif result.get('status') == 'connected':
            print(f"   ✅ Account ist bereits verbunden!")
            if result.get('info'):
                info = result.get('info')
                print(f"   Username: @{info.get('username', 'N/A')}")
                print(f"   Telefon: {info.get('phone', 'N/A')}")
        elif result.get('status') == 'error':
            print(f"   ❌ Fehler: {result.get('error')}")
            print(f"\n💡 Prüfe die Logs für weitere Details")
        else:
            print(f"   ⚠️  Unbekannter Status: {result}")
        
    except Exception as e:
        print(f"❌ Fehler: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    account_id = int(sys.argv[1]) if len(sys.argv) > 1 else None
    asyncio.run(test_code_request(account_id))

