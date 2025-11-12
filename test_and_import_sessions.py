"""
Testet alle Session-Dateien und importiert funktionierende in die Datenbank
"""
import os
import sys
import asyncio
import json
from pathlib import Path
from database import init_db, Account, Proxy
from account_manager import AccountManager
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import shutil
from datetime import datetime
from telethon import TelegramClient

# Initialisiere Datenbank
db_engine = init_db()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

# Sessions-Verzeichnis
SESSIONS_DIR = Path("sessions")
SESSIONS_DIR.mkdir(exist_ok=True)

# API Credentials (Müssen in Umgebungsvariablen gesetzt sein)
DEFAULT_API_ID = os.getenv('TELEGRAM_API_ID')
DEFAULT_API_HASH = os.getenv('TELEGRAM_API_HASH')

if not DEFAULT_API_ID or not DEFAULT_API_HASH:
    raise ValueError(
        "TELEGRAM_API_ID und TELEGRAM_API_HASH müssen in Umgebungsvariablen gesetzt sein. "
        "Erhalte diese von https://my.telegram.org/apps"
    )

DEFAULT_API_ID = int(DEFAULT_API_ID)

# Telegram Desktop API Credentials (aus JSON-Dateien)
TELEGRAM_DESKTOP_API_ID = 6
TELEGRAM_DESKTOP_API_HASH = "eb06d4abfb49dc3eeb1aeb98ae0f581e"

async def test_session(session_file: Path, json_file: Path = None) -> tuple:
    """
    Testet eine Session-Datei mit verschiedenen API Credentials
    
    Returns:
        (success: bool, api_id: int, api_hash: str, user_info: dict, error: str)
    """
    session_name = str(session_file).replace('.session', '')
    
    # Liste der zu testenden API Credentials
    api_configs = [
        (DEFAULT_API_ID, DEFAULT_API_HASH, "Standard"),
        (TELEGRAM_DESKTOP_API_ID, TELEGRAM_DESKTOP_API_HASH, "Telegram Desktop")
    ]
    
    # Wenn JSON vorhanden, füge dessen API Credentials hinzu
    if json_file and json_file.exists():
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                if 'app_id' in data and 'app_hash' in data:
                    api_id = int(data['app_id'])
                    api_hash = data['app_hash']
                    if (api_id, api_hash) not in [(c[0], c[1]) for c in api_configs]:
                        api_configs.append((api_id, api_hash, "JSON"))
        except:
            pass
    
    for api_id, api_hash, source in api_configs:
        try:
            client = TelegramClient(session_name, api_id, api_hash)
            await client.connect()
            
            if await client.is_user_authorized():
                me = await client.get_me()
                await client.disconnect()
                
                user_info = {
                    "first_name": me.first_name or "",
                    "last_name": me.last_name or "",
                    "username": me.username or None,
                    "phone": me.phone or None,
                    "id": me.id
                }
                
                return True, api_id, api_hash, user_info, None
            else:
                await client.disconnect()
        except Exception as e:
            try:
                await client.disconnect()
            except:
                pass
            # Versuche nächste API-Konfiguration
            continue
    
    return False, None, None, None, "Nicht autorisiert mit allen getesteten API Credentials"

def copy_session_file(source_path: str, target_name: str, target_dir: str = "sessions") -> str:
    """Kopiert eine Session-Datei"""
    target_dir_path = Path(target_dir)
    target_dir_path.mkdir(exist_ok=True)
    
    source_file = Path(source_path)
    if not source_file.exists():
        return None
    
    # Entferne .session Endung für Telethon
    if target_name.endswith('.session'):
        target_name = target_name[:-8]
    
    target_path = target_dir_path / f"{target_name}.session"
    shutil.copy2(source_path, target_path)
    
    return str(target_dir_path / target_name)

async def import_working_session(session_file: Path, json_file: Path = None, api_id: int = None, api_hash: str = None, user_info: dict = None):
    """Importiert eine funktionierende Session in die Datenbank"""
    db = SessionLocal()
    
    try:
        # Extrahiere Account-Name
        account_name = session_file.stem
        if account_name.startswith('+'):
            # Wenn JSON vorhanden, verwende Telefonnummer als Name
            if json_file and json_file.exists():
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                        account_name = data.get('phone', account_name)
                except:
                    pass
        elif user_info and user_info.get('phone'):
            account_name = user_info['phone']
        
        # Prüfe ob Account bereits existiert
        existing = db.query(Account).filter(Account.name == account_name).first()
        if existing:
            print(f"   ⚠️  Account '{account_name}' existiert bereits (ID: {existing.id})")
            # Aktualisiere Session-Pfad
            session_name = session_file.stem
            copied_path = copy_session_file(str(session_file), session_name, str(SESSIONS_DIR))
            if copied_path:
                existing.session_file_path = copied_path
                existing.api_id = str(api_id) if api_id else existing.api_id
                existing.api_hash = api_hash if api_hash else existing.api_hash
                if user_info and user_info.get('phone'):
                    existing.phone_number = user_info['phone']
                existing.last_used = datetime.utcnow()
                db.commit()
                print(f"   ✅ Account aktualisiert")
                return existing.id
            return existing.id
        
        # Kopiere Session-Datei
        session_name = session_file.stem
        copied_path = copy_session_file(str(session_file), session_name, str(SESSIONS_DIR))
        if not copied_path:
            print(f"   ❌ Fehler beim Kopieren der Session-Datei")
            return None
        
        # Proxy-Informationen aus JSON extrahieren
        proxy_id = None
        if json_file and json_file.exists():
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    proxy_data = data.get("proxy")
                    if proxy_data and len(proxy_data) >= 6:
                        proxy_type_map = {1: "socks4", 2: "socks5", 3: "http", 4: "mtproto"}
                        proxy_type = proxy_type_map.get(proxy_data[0], "socks5")
                        proxy_host = proxy_data[1]
                        proxy_port = proxy_data[2]
                        proxy_username = proxy_data[4] if len(proxy_data) > 4 else None
                        proxy_password = proxy_data[5] if len(proxy_data) > 5 else None
                        
                        # Prüfe ob Proxy bereits existiert
                        existing_proxy = db.query(Proxy).filter(
                            Proxy.host == proxy_host,
                            Proxy.port == proxy_port,
                            Proxy.username == proxy_username
                        ).first()
                        
                        if not existing_proxy:
                            new_proxy = Proxy(
                                name=f"Proxy-{proxy_host}:{proxy_port}",
                                proxy_type=proxy_type,
                                host=proxy_host,
                                port=proxy_port,
                                username=proxy_username,
                                password=proxy_password,
                                is_active=True,
                                created_at=datetime.utcnow()
                            )
                            db.add(new_proxy)
                            db.commit()
                            db.refresh(new_proxy)
                            proxy_id = new_proxy.id
                        else:
                            proxy_id = existing_proxy.id
            except Exception as e:
                print(f"   ⚠️  Fehler beim Extrahieren der Proxy-Info: {str(e)}")
        
        # Erstelle Account
        db_account = Account(
            name=account_name,
            account_type="user",
            api_id=str(api_id) if api_id else None,
            api_hash=api_hash if api_hash else None,
            phone_number=user_info.get('phone') if user_info else None,
            session_name=session_name,
            session_file_path=copied_path,
            proxy_id=proxy_id,
            created_at=datetime.utcnow(),
            last_used=datetime.utcnow()
        )
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        
        print(f"   ✅ Account erstellt: ID={db_account.id}, Name={account_name}")
        return db_account.id
        
    except Exception as e:
        print(f"   ❌ Fehler beim Erstellen des Accounts: {str(e)}")
        db.rollback()
        return None
    finally:
        db.close()

async def main():
    """Hauptfunktion"""
    print("🚀 Starte Session-Test und Import...\n")
    
    # Finde alle Session-Dateien
    session_files = sorted(Path('.').glob('*.session'))
    json_files = {f.stem: f for f in Path('.').glob('*.json')}
    
    print(f"📋 Gefundene Dateien:")
    print(f"   Session-Dateien: {len(session_files)}")
    print(f"   JSON-Dateien: {len(json_files)}")
    print()
    print("=" * 80)
    print()
    
    working_sessions = []
    broken_sessions = []
    
    for session_file in session_files:
        session_name = session_file.name
        json_file = json_files.get(session_file.stem)
        
        print(f"📱 Teste: {session_name}")
        if json_file:
            print(f"   JSON: {json_file.name}")
        
        success, api_id, api_hash, user_info, error = await test_session(session_file, json_file)
        
        if success:
            print(f"   ✅ FUNKTIONIERT")
            if user_info:
                name = f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip() or 'N/A'
                username = f"@{user_info.get('username')}" if user_info.get('username') else 'N/A'
                print(f"   Name: {name}")
                print(f"   Username: {username}")
                print(f"   Phone: {user_info.get('phone', 'N/A')}")
            print(f"   API ID: {api_id}")
            
            # Importiere in Datenbank
            print(f"   📥 Importiere in Datenbank...")
            account_id = await import_working_session(session_file, json_file, api_id, api_hash, user_info)
            if account_id:
                working_sessions.append((session_name, account_id))
        else:
            print(f"   ❌ FEHLER: {error}")
            broken_sessions.append((session_name, error))
        
        print()
    
    print("=" * 80)
    print(f"\n📊 Zusammenfassung:")
    print(f"   ✅ Funktionierende Sessions: {len(working_sessions)}")
    print(f"   ❌ Defekte Sessions: {len(broken_sessions)}")
    
    if working_sessions:
        print(f"\n✅ Importierte Accounts:")
        for session, account_id in working_sessions:
            print(f"   • {session} → Account ID: {account_id}")
    
    if broken_sessions:
        print(f"\n❌ Defekte Sessions:")
        for session, reason in broken_sessions[:10]:  # Zeige nur erste 10
            print(f"   • {session} - {reason}")
        if len(broken_sessions) > 10:
            print(f"   ... und {len(broken_sessions) - 10} weitere")

if __name__ == "__main__":
    asyncio.run(main())

