#!/usr/bin/env python3
"""
Setzt die OnlineSim.io API-Credentials in der Datenbank
"""

import sys
from pathlib import Path
from dotenv import load_dotenv
from database import init_db, get_session, SystemSettings

# Lade Umgebungsvariablen
load_dotenv()

# API Credentials
ONLINESIM_API_KEY = "RZ68JbHCp9MaS9X-Z7jg1883-7YmHqeC2-FmP7AgR9-kTUa8n9aPty9zBC"
ONLINESIM_USER_ID = "8505888"

def set_onlinesim_api_key(db):
    """Setzt den OnlineSim API Key in der Datenbank"""
    
    # Prüfe ob Setting bereits existiert
    setting = db.query(SystemSettings).filter(SystemSettings.key == "onlinesim_api_key").first()
    
    if setting:
        setting.value = ONLINESIM_API_KEY
        print(f"✅ OnlineSim API Key aktualisiert")
    else:
        setting = SystemSettings(
            key="onlinesim_api_key",
            value=ONLINESIM_API_KEY,
            value_type="string",
            description="OnlineSim.io API Key",
            category="api"
        )
        db.add(setting)
        print(f"✅ OnlineSim API Key hinzugefügt")
    
    # Optional: User ID speichern (falls benötigt)
    user_id_setting = db.query(SystemSettings).filter(SystemSettings.key == "onlinesim_user_id").first()
    if user_id_setting:
        user_id_setting.value = ONLINESIM_USER_ID
        print(f"✅ OnlineSim User ID aktualisiert")
    else:
        user_id_setting = SystemSettings(
            key="onlinesim_user_id",
            value=ONLINESIM_USER_ID,
            value_type="string",
            description="OnlineSim.io User ID",
            category="api"
        )
        db.add(user_id_setting)
        print(f"✅ OnlineSim User ID hinzugefügt")
    
    db.commit()
    print(f"\n✅ OnlineSim API-Credentials erfolgreich gespeichert!")
    print(f"   API Key: {ONLINESIM_API_KEY[:20]}...")
    print(f"   User ID: {ONLINESIM_USER_ID}")

if __name__ == "__main__":
    print("="*60)
    print("🔧 OnlineSim.io API-Credentials konfigurieren")
    print("="*60)
    print()
    
    # Initialisiere Datenbank und hole Engine
    db_engine = init_db()
    
    # Hole Session
    db = get_session(db_engine)
    
    try:
        set_onlinesim_api_key(db)
    except Exception as e:
        print(f"❌ Fehler: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

