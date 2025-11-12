"""
Einfaches Skript zum Importieren von Session-Dateien ohne Login-Code
"""
import os
import sys
import asyncio
from pathlib import Path
from database import init_db, Account, Proxy
from account_manager import AccountManager
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import shutil
from datetime import datetime

# Initialisiere Datenbank und erstelle Engine
db_engine = init_db()

# Session-Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

# Sessions-Verzeichnis
SESSIONS_DIR = Path("sessions")
SESSIONS_DIR.mkdir(exist_ok=True)

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

async def import_session_file(session_file_path: str, account_name: str = None, proxy_id: int = None):
    """
    Importiert eine Session-Datei direkt ohne Login-Code
    
    Args:
        session_file_path: Pfad zur Session-Datei
        account_name: Name für den Account (optional)
        proxy_id: Proxy-ID (optional)
    """
    session_file = Path(session_file_path)
    
    if not session_file.exists():
        print(f"❌ Session-Datei nicht gefunden: {session_file_path}")
        return None
    
    # Bestimme Account-Namen
    if not account_name:
        account_name = session_file.stem.replace('_20251112', '').replace('+', '')
    
    print(f"📁 Importiere Session: {session_file.name} -> Account: {account_name}")
    
    # Generiere Session-Name
    session_name = f"{account_name.lower().replace(' ', '_').replace('+', '')}_{datetime.now().strftime('%Y%m%d')}"
    
    # Kopiere Session-Datei zu sessions/ Verzeichnis
    copied_path = copy_session_file(str(session_file), session_name, str(SESSIONS_DIR))
    if not copied_path:
        print(f"❌ Fehler beim Kopieren der Session-Datei")
        return None
    
    # API Credentials aus Umgebungsvariablen
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    
    if not api_id or not api_hash:
        print("⚠️  API Credentials nicht in Umgebungsvariablen gefunden")
        print("   Setze TELEGRAM_API_ID und TELEGRAM_API_HASH")
        return None
    
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
            session_file_path=copied_path,
            proxy_id=proxy_id
        )
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        
        print(f"✅ Account erstellt: ID={db_account.id}, Name={account_name}")
        
        # Versuche Verbindung (OHNE Code-Anfrage)
        account_manager = AccountManager()
        result = await account_manager.add_account(
            account_id=db_account.id,
            api_id=api_id,
            api_hash=api_hash,
            session_name=session_name,
            session_file_path=copied_path
        )
        
        if result.get("status") == "connected":
            user_info = result.get('info', {})
            print(f"✅ Verbindung erfolgreich!")
            print(f"   Name: {user_info.get('first_name', 'N/A')} {user_info.get('last_name', '')}")
            print(f"   Username: @{user_info.get('username', 'N/A')}")
            print(f"   Telefon: {user_info.get('phone', 'N/A')}")
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
    print("🚀 Starte Session-Import (ohne Login-Code)...\n")
    
    # Session-Dateien im aktuellen Verzeichnis
    session_files = [
        "27608217417.session",
        "27607848968.session",
        "+12897046237.session",
        "+12897086495.session",
        "+13434362430.session",
        "+13434372101.session",
        "+13434382684.session"
    ]
    
    # Prüfe ob Proxy ID 1 existiert (der Proxy mit Port 9999)
    db = SessionLocal()
    proxy = db.query(Proxy).filter(Proxy.id == 1).first()
    proxy_id = proxy.id if proxy else None
    db.close()
    
    if proxy_id:
        print(f"✅ Verwende Proxy ID {proxy_id} für alle Accounts\n")
    
    imported = []
    for session_file in session_files:
        if os.path.exists(session_file):
            account_id = await import_session_file(session_file, proxy_id=proxy_id)
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

