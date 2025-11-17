#!/usr/bin/env python3
"""
Prüft den Status aller Accounts und zeigt welche produktionsbereit sind
"""

import os
import sys
from pathlib import Path
from database import init_db, get_session, Account, User
from account_manager import AccountManager
import asyncio

async def check_account_status(account_manager, account):
    """Prüft ob ein Account verbunden werden kann"""
    if account.account_type == 'bot':
        return {'status': 'bot', 'message': 'Bot-Account - wird beim Start automatisch verbunden'}
    
    if not account.session_file_path:
        return {'status': 'no_session', 'message': 'Keine Session-Datei vorhanden'}
    
    session_path = account.session_file_path
    if not session_path.endswith('.session'):
        session_path = session_path + '.session'
    
    if not os.path.exists(session_path):
        return {'status': 'session_missing', 'message': f'Session-Datei nicht gefunden: {session_path}'}
    
    # Versuche Verbindung
    try:
        api_id = account.api_id or os.getenv('TELEGRAM_API_ID')
        api_hash = account.api_hash or os.getenv('TELEGRAM_API_HASH')
        
        if not api_id or not api_hash:
            return {'status': 'no_credentials', 'message': 'API Credentials fehlen'}
        
        result = await account_manager.add_account(
            account_id=account.id,
            api_id=api_id,
            api_hash=api_hash,
            session_name=account.session_name,
            phone_number=account.phone_number,
            session_file_path=account.session_file_path
        )
        
        if result.get('status') == 'connected':
            return {'status': 'connected', 'message': '✅ Produktionsbereit', 'info': result.get('info')}
        elif result.get('status') == 'code_required':
            return {'status': 'code_required', 'message': '⚠️  Code erforderlich - Session abgelaufen'}
        elif result.get('status') == 'password_required':
            return {'status': 'password_required', 'message': '⚠️  2FA Passwort erforderlich'}
        else:
            return {'status': 'error', 'message': f"❌ {result.get('error', 'Unbekannter Fehler')}"}
    except Exception as e:
        return {'status': 'error', 'message': f"❌ Fehler: {str(e)}"}

def main():
    print("🔍 Prüfe Account-Status...")
    db_engine = init_db()
    db = get_session(db_engine)
    
    try:
        # Finde Admin-User
        admin_user = db.query(User).filter(User.is_admin == True).first()
        if not admin_user:
            print("❌ Kein Admin-User gefunden!")
            return
        
        print(f"✅ Admin-User: {admin_user.username} (ID: {admin_user.id})\n")
        
        # Finde alle Accounts des Admins
        admin_accounts = db.query(Account).filter(Account.user_id == admin_user.id).all()
        
        print(f"📊 Gefundene Accounts: {len(admin_accounts)}\n")
        
        account_manager = AccountManager()
        
        connected = []
        needs_code = []
        needs_password = []
        errors = []
        bots = []
        
        for account in admin_accounts:
            print(f"🔄 Prüfe: {account.name} (ID: {account.id}, Typ: {account.account_type})")
            
            if account.account_type == 'bot':
                status = {'status': 'bot', 'message': 'Bot-Account'}
                bots.append((account, status))
                print(f"  ℹ️  Bot-Account - wird beim Start automatisch verbunden")
            else:
                status = asyncio.run(check_account_status(account_manager, account))
                print(f"  {status['message']}")
                
                if status['status'] == 'connected':
                    connected.append((account, status))
                elif status['status'] == 'code_required':
                    needs_code.append((account, status))
                elif status['status'] == 'password_required':
                    needs_password.append((account, status))
                else:
                    errors.append((account, status))
        
        # Zusammenfassung
        print(f"\n{'='*60}")
        print(f"📋 ZUSAMMENFASSUNG")
        print(f"{'='*60}\n")
        
        print(f"✅ Produktionsbereit (verbunden): {len(connected)}")
        for acc, status in connected:
            info = status.get('info', {})
            username = info.get('username', 'N/A')
            phone = info.get('phone', 'N/A')
            print(f"   - {acc.name} (ID: {acc.id}) - @{username} ({phone})")
        
        print(f"\n🤖 Bot-Accounts: {len(bots)}")
        for acc, status in bots:
            print(f"   - {acc.name} (ID: {acc.id})")
        
        print(f"\n⚠️  Benötigen Code (Session abgelaufen): {len(needs_code)}")
        for acc, status in needs_code:
            print(f"   - {acc.name} (ID: {acc.id}) - {acc.phone_number}")
        
        print(f"\n🔐 Benötigen 2FA Passwort: {len(needs_password)}")
        for acc, status in needs_password:
            print(f"   - {acc.name} (ID: {acc.id}) - {acc.phone_number}")
        
        if errors:
            print(f"\n❌ Fehler: {len(errors)}")
            for acc, status in errors:
                print(f"   - {acc.name} (ID: {acc.id}) - {status['message']}")
        
        print(f"\n{'='*60}")
        print(f"📊 Gesamt: {len(admin_accounts)} Accounts")
        print(f"   ✅ Produktionsbereit: {len(connected) + len(bots)}")
        print(f"   ⚠️  Benötigen Login: {len(needs_code) + len(needs_password)}")
        print(f"   ❌ Fehler: {len(errors)}")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"❌ Fehler: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()

