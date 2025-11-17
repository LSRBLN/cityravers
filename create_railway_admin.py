"""
Script zum Erstellen des Admin-Users auf Railway
Verwendet die Railway-Datenbank direkt über DATABASE_URL

Verwendung:
    python3 create_railway_admin.py [DATABASE_URL]
    
Oder setze DATABASE_URL als Environment Variable:
    export DATABASE_URL="postgresql://..."
    python3 create_railway_admin.py
"""
import os
import sys

# Prüfe ob DATABASE_URL als Argument übergeben wurde
if len(sys.argv) > 1:
    os.environ["DATABASE_URL"] = sys.argv[1]

from database import init_db, get_session, User, Subscription, Account
from datetime import datetime, timedelta
import json
import bcrypt

def create_railway_admin():
    """Erstellt Admin-User auf Railway über DATABASE_URL"""
    
    # Prüfe ob DATABASE_URL gesetzt ist
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL nicht gefunden!")
        print("\nVerwendung:")
        print("   python3 create_railway_admin.py 'postgresql://user:pass@host:port/db'")
        print("\nOder setze DATABASE_URL als Environment Variable:")
        print("   export DATABASE_URL='postgresql://...'")
        print("   python3 create_railway_admin.py")
        sys.exit(1)
    
    print(f"🔗 Verbinde mit Railway-Datenbank...")
    print(f"   DATABASE_URL: {database_url[:50]}...")
    
    db_engine = init_db()
    db = get_session(db_engine)
    
    try:
        # 1. Admin-Account erstellen
        admin_email = "admin@telegram-bot.local"
        admin_username = "admin"
        admin_password = "Sabine68#"
        
        # Prüfe ob Admin bereits existiert
        existing_admin = db.query(User).filter(
            (User.email == admin_email) | (User.username == admin_username)
        ).first()
        
        if existing_admin:
            print(f"\n⚠️  Admin-Account '{admin_username}' existiert bereits")
            if not existing_admin.is_admin:
                existing_admin.is_admin = True
                existing_admin.password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                db.commit()
                print(f"✅ Admin-Account '{admin_username}' wurde aktualisiert (is_admin=True)")
            else:
                print(f"✅ Admin-Account '{admin_username}' ist bereits Admin")
            admin_user = existing_admin
        else:
            admin_user = User(
                email=admin_email,
                username=admin_username,
                password_hash=bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                is_active=True,
                is_admin=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            print(f"\n✅ Admin-Account erstellt:")
            print(f"   Username: {admin_username}")
            print(f"   Email: {admin_email}")
            print(f"   Passwort: {admin_password}")
            print(f"   Admin: ✅")
        
        # Erstelle/Update Enterprise-Abonnement für Admin
        existing_subscription = db.query(Subscription).filter(
            Subscription.user_id == admin_user.id
        ).first()
        
        if existing_subscription:
            existing_subscription.plan_type = "enterprise"
            existing_subscription.status = "active"
            existing_subscription.expires_at = None
            existing_subscription.max_accounts = 999
            existing_subscription.max_groups = 999
            existing_subscription.max_messages_per_day = 9999
            existing_subscription.features = json.dumps({"auto_number_purchase": True, "all_features": True})
            db.commit()
            print(f"✅ Subscription aktualisiert (Enterprise)")
        else:
            admin_subscription = Subscription(
                user_id=admin_user.id,
                plan_type="enterprise",
                status="active",
                started_at=datetime.utcnow(),
                expires_at=None,
                max_accounts=999,
                max_groups=999,
                max_messages_per_day=9999,
                features=json.dumps({"auto_number_purchase": True, "all_features": True})
            )
            db.add(admin_subscription)
            db.commit()
            print(f"✅ Enterprise Subscription erstellt")
        
        # 2. Prüfe lokale Accounts und kopiere sie zu Railway
        print(f"\n📋 Prüfe lokale Accounts...")
        
        # Lese lokale Datenbank
        local_db_path = "telegram_bot.db"
        if os.path.exists(local_db_path):
            import sqlite3
            local_conn = sqlite3.connect(local_db_path)
            local_conn.row_factory = sqlite3.Row
            local_cursor = local_conn.cursor()
            
            local_cursor.execute('''
                SELECT id, name, account_type, phone_number, session_name, 
                       session_file_path, api_id, api_hash, bot_token, 
                       proxy_id, is_active, created_at
                FROM accounts
                WHERE user_id = (SELECT id FROM users WHERE username = 'admin' LIMIT 1)
                ORDER BY created_at DESC
            ''')
            
            local_accounts = local_cursor.fetchall()
            print(f"   Gefunden: {len(local_accounts)} Accounts in lokaler DB")
            
            # Kopiere Accounts zu Railway
            copied_count = 0
            skipped_count = 0
            
            for local_acc in local_accounts:
                # Prüfe ob Account bereits existiert
                existing_account = db.query(Account).filter(
                    Account.name == local_acc['name'],
                    Account.user_id == admin_user.id
                ).first()
                
                if existing_account:
                    skipped_count += 1
                    continue
                
                # Erstelle Account auf Railway
                railway_account = Account(
                    user_id=admin_user.id,
                    name=local_acc['name'],
                    account_type=local_acc['account_type'] or 'user',
                    phone_number=local_acc['phone_number'],
                    session_name=local_acc['session_name'],
                    session_file_path=local_acc['session_file_path'],
                    api_id=local_acc['api_id'],
                    api_hash=local_acc['api_hash'],
                    bot_token=local_acc['bot_token'],
                    proxy_id=local_acc['proxy_id'],
                    is_active=local_acc['is_active'] if local_acc['is_active'] is not None else True
                )
                db.add(railway_account)
                copied_count += 1
            
            db.commit()
            local_conn.close()
            
            print(f"\n✅ Accounts kopiert:")
            print(f"   Neu kopiert: {copied_count}")
            print(f"   Übersprungen (bereits vorhanden): {skipped_count}")
        else:
            print(f"   ⚠️  Lokale Datenbank nicht gefunden: {local_db_path}")
        
        print(f"\n✅ Railway-Setup erfolgreich abgeschlossen!")
        print(f"\n📋 Zusammenfassung:")
        print(f"   Admin-User: {admin_username} (ID: {admin_user.id})")
        print(f"   Email: {admin_email}")
        print(f"   Passwort: {admin_password}")
        print(f"   Subscription: Enterprise (unbegrenzt)")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Erstelle Admin-User auf Railway...\n")
    create_railway_admin()

