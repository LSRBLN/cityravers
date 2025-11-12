"""
Skript zum Importieren von Session-Dateien
"""
import os
import sys
import asyncio
from pathlib import Path
from database import init_db, Account
from account_manager import AccountManager
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import shutil

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

async def import_session_file(session_path: str, account_name: str = None):
    """
    Importiert eine Session-Datei und erstellt einen Account
    
    Args:
        session_path: Pfad zur Session-Datei
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
    
    # Generiere Account-Namen falls nicht angegeben
    if not account_name:
        account_name = session_file.stem  # Verwende Dateinamen ohne .session
    
    print(f"📁 Importiere Session: {session_file.name} -> Account: {account_name}")
    
    # Generiere Session-Name
    from datetime import datetime
    session_name = f"{account_name.lower().replace(' ', '_')}_{datetime.utcnow().strftime('%Y%m%d')}"
    
    # Kopiere Session-Datei zu sessions/ Verzeichnis
    copied_path = copy_session_file(str(session_file), session_name, str(SESSIONS_DIR))
    if not copied_path:
        print(f"❌ Fehler beim Kopieren der Session-Datei")
        return None
    
    # API Credentials aus Umgebungsvariablen
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    
    # Erstelle Account in Datenbank
    db = SessionLocal()
    try:
        # Prüfe ob Account mit diesem Namen bereits existiert
        existing = db.query(Account).filter(Account.name == account_name).first()
        if existing:
            print(f"⚠️  Account '{account_name}' existiert bereits. Überspringe...")
            return existing.id
        
        db_account = Account(
            name=account_name,
            account_type="user",
            api_id=api_id,
            api_hash=api_hash,
            session_name=session_name,
            session_file_path=copied_path
        )
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        
        print(f"✅ Account erstellt: ID={db_account.id}, Name={account_name}")
        
        # Versuche Verbindung
        account_manager = AccountManager()
        result = await account_manager.add_account(
            account_id=db_account.id,
            api_id=api_id,
            api_hash=api_hash,
            session_name=session_name,
            session_file_path=copied_path
        )
        
        if result.get("status") == "connected":
            print(f"✅ Verbindung erfolgreich: {result.get('user_info', {}).get('first_name', 'N/A')}")
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
        return None
    finally:
        db.close()

async def main():
    """Hauptfunktion"""
    # Datenbank ist bereits initialisiert
    
    # Session-Dateien aus Workspace-Root
    session_files = [
        "27608217417.session",
        "27607848968.session"
    ]
    
    print("🚀 Starte Session-Import...\n")
    
    imported = []
    for session_file in session_files:
        if os.path.exists(session_file):
            account_id = await import_session_file(session_file)
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

