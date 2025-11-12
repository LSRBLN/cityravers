"""
Script zum Erstellen von Benutzer-Accounts
"""
import os
import sys
from dotenv import load_dotenv

# Lade Umgebungsvariablen
load_dotenv()

from database import init_db, get_session, User, Subscription
from datetime import datetime, timedelta
import json
import bcrypt

def create_users():
    """Erstellt Admin- und Benutzer-Accounts"""
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
            print(f"⚠️  Admin-Account '{admin_username}' existiert bereits")
            if not existing_admin.is_admin:
                existing_admin.is_admin = True
                existing_admin.password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                db.commit()
                print(f"✅ Admin-Account '{admin_username}' wurde aktualisiert (is_admin=True)")
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
            
            # Erstelle Free Trial Abonnement für Admin
            admin_subscription = Subscription(
                user_id=admin_user.id,
                plan_type="enterprise",  # Admin bekommt Enterprise
                status="active",
                started_at=datetime.utcnow(),
                expires_at=None,  # Kein Ablaufdatum für Admin
                max_accounts=999,
                max_groups=999,
                max_messages_per_day=9999,
                features=json.dumps({"auto_number_purchase": True, "all_features": True})
            )
            db.add(admin_subscription)
            db.commit()
            
            print(f"✅ Admin-Account erstellt:")
            print(f"   Username: {admin_username}")
            print(f"   Email: {admin_email}")
            print(f"   Passwort: {admin_password}")
            print(f"   Admin: ✅")
        
        # 2. Benutzer-Account erstellen
        user_email = "user@telegram-bot.local"
        user_username = "User"
        user_password = "Sabine68#"
        
        # Prüfe ob Benutzer bereits existiert
        existing_user = db.query(User).filter(
            (User.email == user_email) | (User.username == user_username)
        ).first()
        
        if existing_user:
            print(f"\n⚠️  Benutzer-Account '{user_username}' existiert bereits")
            existing_user.password_hash = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            db.commit()
            print(f"✅ Passwort für '{user_username}' wurde aktualisiert")
        else:
            normal_user = User(
                email=user_email,
                username=user_username,
                password_hash=bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                is_active=True,
                is_admin=False
            )
            db.add(normal_user)
            db.commit()
            db.refresh(normal_user)
            
            # Erstelle Free Trial Abonnement für Benutzer
            user_subscription = Subscription(
                user_id=normal_user.id,
                plan_type="free_trial",
                status="active",
                started_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=7),  # 7 Tage Free Trial
                max_accounts=2,
                max_groups=5,
                max_messages_per_day=10,
                features=json.dumps({"auto_number_purchase": False})
            )
            db.add(user_subscription)
            db.commit()
            
            print(f"\n✅ Benutzer-Account erstellt:")
            print(f"   Username: {user_username}")
            print(f"   Email: {user_email}")
            print(f"   Passwort: {user_password}")
            print(f"   Admin: ❌")
        
        print("\n✅ Alle Accounts erfolgreich erstellt/aktualisiert!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Fehler beim Erstellen der Accounts: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    print("🔄 Erstelle Benutzer-Accounts...\n")
    create_users()

