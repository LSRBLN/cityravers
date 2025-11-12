"""
Skript zum Bulk-Import von Session-Dateien mit JSON-Metadaten
"""
import os
import sys
import asyncio
import json
from pathlib import Path
from database import init_db, Account
from account_manager import AccountManager
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import shutil
from datetime import datetime

# Initialisiere Datenbank und erstelle Engine
db_engine = init_db()

# Session-Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

def validate_session_file(session_path: str):
    """Einfache Validierung einer Session-Datei"""
    session_file = Path(session_path)
    if not session_file.exists():
        return False, "Datei existiert nicht"
    if session_file.suffix != ".session":
        return False, "Datei hat nicht die .session Endung"
    if session_file.stat().st_size < 100:
        return False, "Datei zu klein"
    return True, None

def copy_session_file(source_path: str, target_name: str, target_dir: str = "sessions"):
    """Kopiert eine Session-Datei"""
    target_dir_path = Path(target_dir)
    target_dir_path.mkdir(exist_ok=True)
    
    source_file = Path(source_path)
    if not source_file.exists():
        return None
    
    if target_name.endswith('.session'):
        target_name = target_name[:-8]
    
    target_path = target_dir_path / f"{target_name}.session"
    shutil.copy2(source_path, target_path)
    
    return str(target_dir_path / target_name)

# Sessions-Verzeichnis
SESSIONS_DIR = Path("sessions")
SESSIONS_DIR.mkdir(exist_ok=True)

def load_json_metadata(json_path: str):
    """Lädt Metadaten aus JSON-Datei"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  Fehler beim Laden von {json_path}: {e}")
        return None

async def import_session_file(session_path: str, json_path: str = None, account_name: str = None):
    """
    Importiert eine Session-Datei und erstellt einen Account
    
    Args:
        session_path: Pfad zur Session-Datei
        json_path: Pfad zur JSON-Metadatendatei (optional)
        account_name: Name für den Account (optional)
    """
    session_file = Path(session_path)
    
    if not session_file.exists():
        print(f"❌ Session-Datei nicht gefunden: {session_path}")
        return None
    
    # Validiere Session-Datei
    is_valid, error = validate_session_file(str(session_file))
    if not is_valid:
        print(f"❌ Ungültige Session-Datei: {error}")
        return None
    
    # Lade JSON-Metadaten falls vorhanden
    metadata = None
    if json_path and os.path.exists(json_path):
        metadata = load_json_metadata(json_path)
    
    # Bestimme Account-Namen
    if not account_name:
        if metadata and metadata.get('phone'):
            account_name = metadata.get('phone').replace('+', '')
        elif metadata and metadata.get('first_name'):
            account_name = f"{metadata.get('first_name')}_{metadata.get('phone', session_file.stem).replace('+', '')}"
        else:
            account_name = session_file.stem.replace('_20251112', '').replace('+', '')
    
    print(f"📁 Importiere Session: {session_file.name} -> Account: {account_name}")
    
    # Generiere Session-Name
    session_name = f"{account_name.lower().replace(' ', '_').replace('+', '')}_{datetime.now().strftime('%Y%m%d')}"
    
    # Kopiere Session-Datei zu sessions/ Verzeichnis
    copied_path = copy_session_file(str(session_file), session_name, str(SESSIONS_DIR))
    if not copied_path:
        print(f"❌ Fehler beim Kopieren der Session-Datei")
        return None
    
    # API Credentials aus JSON oder Umgebungsvariablen
    api_id = None
    api_hash = None
    
    if metadata:
        # Versuche aus JSON zu extrahieren
        api_id = str(metadata.get('app_id', '')) if metadata.get('app_id') else None
        api_hash = metadata.get('app_hash', '')
    
    # Fallback: Umgebungsvariablen
    if not api_id or not api_hash:
        api_id = api_id or os.getenv('TELEGRAM_API_ID')
        api_hash = api_hash or os.getenv('TELEGRAM_API_HASH')
    
    # Erstelle Account in Datenbank
    db = SessionLocal()
    try:
        # Prüfe ob Account mit diesem Namen bereits existiert
        existing = db.query(Account).filter(Account.name == account_name).first()
        if existing:
            print(f"⚠️  Account '{account_name}' existiert bereits. Überspringe...")
            return existing.id
        
        # Telefonnummer aus Metadaten
        phone_number = None
        if metadata and metadata.get('phone'):
            phone_number = metadata.get('phone')
        
        db_account = Account(
            name=account_name,
            account_type="user",
            api_id=api_id,
            api_hash=api_hash,
            phone_number=phone_number,
            session_name=session_name,
            session_file_path=copied_path
        )
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        
        print(f"✅ Account erstellt: ID={db_account.id}, Name={account_name}")
        
        # Versuche Verbindung
        account_manager = AccountManager()
        proxy_config = None
        
        # Proxy aus Metadaten falls vorhanden
        if metadata and metadata.get('proxy') and isinstance(metadata.get('proxy'), list) and len(metadata.get('proxy')) >= 6:
            proxy_data = metadata.get('proxy')
            proxy_config = {
                "proxy_type": "socks5",  # Standard für Telegram Proxy
                "host": proxy_data[1] if len(proxy_data) > 1 else None,
                "port": proxy_data[2] if len(proxy_data) > 2 else None,
                "username": proxy_data[4] if len(proxy_data) > 4 else None,
                "password": proxy_data[5] if len(proxy_data) > 5 else None
            }
        
        result = await account_manager.add_account(
            account_id=db_account.id,
            api_id=api_id,
            api_hash=api_hash,
            session_name=session_name,
            session_file_path=copied_path,
            proxy_config=proxy_config
        )
        
        if result.get("status") == "connected":
            user_info = result.get('user_info', {})
            print(f"✅ Verbindung erfolgreich: {user_info.get('first_name', 'N/A')} (@{user_info.get('username', 'N/A')})")
        elif result.get("status") == "code_required":
            print(f"⚠️  Code erforderlich für Account {account_name}")
        else:
            print(f"⚠️  Verbindungsstatus: {result.get('status', 'unknown')}")
            if result.get("error"):
                print(f"   Fehler: {result.get('error')}")
        
        return db_account.id
    
    except Exception as e:
        db.rollback()
        print(f"❌ Fehler beim Erstellen des Accounts: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

async def main():
    """Hauptfunktion"""
    # Session-Dateien mit optionalen JSON-Metadaten
    session_files = [
        ("+12897046237.session", "+12897046237.json"),
        ("+12897086495.session", "+12897086495.json"),
        ("+13434362430.session", "+13434362430.json"),
        ("+13434372101.session", "+13434372101.json"),
        ("+13434382684.session", "+13434382684.json"),
        ("27607848968_20251112.session", None),
        ("27608217417_20251112.session", None),
    ]
    
    print("🚀 Starte Bulk-Session-Import...\n")
    
    imported = []
    for session_file, json_file in session_files:
        if os.path.exists(session_file):
            account_id = await import_session_file(session_file, json_file)
            if account_id:
                imported.append(account_id)
            print()  # Leerzeile
        else:
            print(f"❌ Session-Datei nicht gefunden: {session_file}\n")
    
    print(f"\n✅ Import abgeschlossen: {len(imported)} Account(s) importiert")
    if imported:
        print(f"   Account-IDs: {', '.join(map(str, imported))}")

if __name__ == "__main__":
    asyncio.run(main())

