"""
Setzt Admin-Rechte direkt über SQL-Update
Benötigt DATABASE_URL
"""
import os
import sys
from sqlalchemy import create_engine, text

def set_admin_rights():
    """Setzt Admin-Rechte für User ID 1 direkt über SQL"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL nicht gefunden!")
        print("\nBitte setze DATABASE_URL:")
        print("   export DATABASE_URL='postgresql://user:pass@host:port/db'")
        print("   python3 set_admin_direct.py")
        sys.exit(1)
    
    print(f"🔗 Verbinde mit Datenbank...")
    print(f"   DATABASE_URL: {database_url[:50]}...")
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Setze Admin-Rechte
            result = conn.execute(text("""
                UPDATE users 
                SET is_admin = true 
                WHERE username = 'admin' OR id = 1
                RETURNING id, username, email, is_admin
            """))
            
            updated = result.fetchone()
            
            if updated:
                print(f"\n✅ Admin-Rechte gesetzt!")
                print(f"   User ID: {updated[0]}")
                print(f"   Username: {updated[1]}")
                print(f"   Email: {updated[2]}")
                print(f"   Admin: {updated[3]}")
                
                # Setze Enterprise Subscription
                conn.execute(text("""
                    UPDATE subscriptions 
                    SET plan_type = 'enterprise',
                        max_accounts = 999,
                        max_groups = 999,
                        max_messages_per_day = 9999,
                        expires_at = NULL,
                        features = '{"auto_number_purchase": true, "all_features": true}'
                    WHERE user_id = :user_id
                """), {"user_id": updated[0]})
                
                conn.commit()
                print(f"✅ Enterprise Subscription gesetzt!")
                return True
            else:
                print("❌ User 'admin' nicht gefunden!")
                return False
                
    except Exception as e:
        print(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    set_admin_rights()

