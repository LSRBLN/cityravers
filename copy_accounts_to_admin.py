#!/usr/bin/env python3
"""
Kopiert alle funktionierenden Accounts auf das Admin-Konto
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from database import init_db, get_session, Account, User
from account_manager import AccountManager
import asyncio

def main():
    print("🔍 Initialisiere Datenbank...")
    db_engine = init_db()
    db = get_session(db_engine)
    
    try:
        # Finde Admin-User
        admin_user = db.query(User).filter(User.is_admin == True).first()
        if not admin_user:
            print("❌ Kein Admin-User gefunden!")
            return
        
        print(f"✅ Admin-User gefunden: {admin_user.username} (ID: {admin_user.id})")
        
        # Finde alle Accounts ohne user_id oder mit anderem user_id
        all_accounts = db.query(Account).all()
        accounts_to_assign = [acc for acc in all_accounts if acc.user_id != admin_user.id]
        
        print(f"\n📊 Gefundene Accounts: {len(all_accounts)}")
        print(f"📋 Accounts zum Zuweisen: {len(accounts_to_assign)}")
        
        if not accounts_to_assign:
            print("✅ Alle Accounts gehören bereits dem Admin!")
            return
        
        account_manager = AccountManager()
        assigned_count = 0
        connected_count = 0
        
        for account in accounts_to_assign:
            print(f"\n🔄 Verarbeite Account: {account.name} (ID: {account.id})")
            
            # Prüfe ob Session-Datei existiert
            session_exists = False
            if account.session_file_path:
                session_path = account.session_file_path
                if not session_path.endswith('.session'):
                    session_path = session_path + '.session'
                if os.path.exists(session_path):
                    session_exists = True
                    print(f"  ✅ Session-Datei gefunden: {session_path}")
                else:
                    print(f"  ⚠️  Session-Datei nicht gefunden: {session_path}")
            
            # Weise Account dem Admin zu
            old_user_id = account.user_id
            account.user_id = admin_user.id
            db.commit()
            print(f"  ✅ Account dem Admin zugewiesen (vorher: user_id={old_user_id})")
            assigned_count += 1
            
            # Versuche Account zu verbinden (nur wenn Session existiert)
            if account.account_type == 'user' and session_exists:
                try:
                    print(f"  🔄 Versuche Account zu verbinden...")
                    
                    # Lade API Credentials
                    api_id = account.api_id or os.getenv('TELEGRAM_API_ID')
                    api_hash = account.api_hash or os.getenv('TELEGRAM_API_HASH')
                    
                    if not api_id or not api_hash:
                        print(f"  ⚠️  API Credentials fehlen, überspringe Verbindung")
                        continue
                    
                    # Versuche Verbindung
                    result = asyncio.run(account_manager.add_account(
                        account_id=account.id,
                        api_id=api_id,
                        api_hash=api_hash,
                        session_name=account.session_name,
                        phone_number=account.phone_number,
                        session_file_path=account.session_file_path
                    ))
                    
                    if result.get('status') == 'connected':
                        print(f"  ✅ Account erfolgreich verbunden!")
                        account.last_used = datetime.now(timezone.utc)
                        db.commit()
                        connected_count += 1
                    elif result.get('status') == 'code_required':
                        print(f"  ⚠️  Code erforderlich - Account muss manuell eingeloggt werden")
                    else:
                        print(f"  ⚠️  Verbindung fehlgeschlagen: {result.get('error', 'Unbekannter Fehler')}")
                        
                except Exception as e:
                    print(f"  ❌ Fehler beim Verbinden: {str(e)}")
            elif account.account_type == 'bot':
                print(f"  ℹ️  Bot-Account - Verbindung wird beim nächsten Start automatisch hergestellt")
        
        print(f"\n✅ Zusammenfassung:")
        print(f"  📋 Accounts zugewiesen: {assigned_count}")
        print(f"  🔗 Accounts verbunden: {connected_count}")
        print(f"  ⚠️  Accounts benötigen Login: {assigned_count - connected_count}")
        
        # Zeige finale Liste
        print(f"\n📋 Alle Accounts des Admins:")
        admin_accounts = db.query(Account).filter(Account.user_id == admin_user.id).all()
        for acc in admin_accounts:
            status = "✅ Verbunden" if acc.id in account_manager.clients else "⚠️  Nicht verbunden"
            print(f"  - {acc.name} (ID: {acc.id}, Typ: {acc.account_type}) - {status}")
        
    except Exception as e:
        print(f"❌ Fehler: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()

