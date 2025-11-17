"""
Script zum Erstellen von 10 Bots über BotFather
"""
import asyncio
import os
import sys
from dotenv import load_dotenv
from datetime import datetime

# Lade Umgebungsvariablen
load_dotenv()

from database import init_db, get_session, Account, User
from account_manager import AccountManager
from bot_manager import BotManager

async def create_10_bots():
    """Erstellt 10 Bots über BotFather"""
    
    # Initialisiere Datenbank
    db_engine = init_db()
    db = get_session(db_engine)
    
    account_manager = AccountManager()
    bot_manager = BotManager()
    
    try:
        # 1. Finde einen User-Account (der erste verfügbare)
        user_account = db.query(Account).filter(
            Account.account_type == "user"
        ).first()
        
        if not user_account:
            print("❌ Kein User-Account gefunden. Bitte zuerst einen User-Account erstellen.")
            return
        
        print(f"✅ User-Account gefunden: {user_account.name} (ID: {user_account.id})")
        
        # 2. Prüfe ob Account verbunden ist
        account_info = await account_manager.get_account_info(user_account.id)
        
        if not account_info:
            print(f"🔄 Verbinde Account {user_account.name}...")
            
            # Hole Proxy-Konfiguration falls vorhanden
            proxy_config = None
            if user_account.proxy_id and user_account.proxy:
                from proxy_utils import get_proxy_config_decrypted
                proxy_config = get_proxy_config_decrypted(user_account.proxy)
            
            # Verbinde Account
            result = await account_manager.add_account(
                account_id=user_account.id,
                api_id=user_account.api_id,
                api_hash=user_account.api_hash,
                session_name=user_account.session_name,
                session_file_path=user_account.session_file_path,
                proxy_config=proxy_config
            )
            
            if result.get("status") != "connected":
                print(f"❌ Fehler beim Verbinden: {result.get('error')}")
                if result.get("status") == "code_required":
                    print(f"⚠️  Code erforderlich. Bitte Account manuell verbinden.")
                return
        
        print(f"✅ Account {user_account.name} ist verbunden")
        
        # 3. Erstelle 10 Bots
        print(f"\n🤖 Erstelle 10 Bots über BotFather...")
        print("=" * 60)
        
        results = {
            "total": 10,
            "success": 0,
            "failed": 0,
            "errors": [],
            "bots": []
        }
        
        for i in range(1, 11):
            bot_name = f"Group Bot {i}"
            bot_username = f"group_bot_{i}_{int(datetime.utcnow().timestamp())}"
            
            # Stelle sicher, dass Username mit "bot" endet
            if not bot_username.lower().endswith("bot"):
                bot_username = bot_username.lower().rstrip("bot") + "bot"
            
            print(f"\n[{i}/10] Erstelle Bot: {bot_name} (@{bot_username})")
            
            try:
                # Erstelle Bot über BotFather
                result = await account_manager.create_bot_via_botfather(
                    account_id=user_account.id,
                    bot_name=bot_name,
                    bot_username=bot_username
                )
                
                if result.get("success") and result.get("bot_token"):
                    bot_token = result.get("bot_token")
                    print(f"  ✅ Bot erstellt! Token: {bot_token[:20]}...")
                    
                    # Erstelle Bot-Account in Datenbank
                    bot_account = Account(
                        user_id=user_account.user_id,
                        name=bot_name,
                        account_type="bot",
                        bot_token=bot_token
                    )
                    db.add(bot_account)
                    db.commit()
                    db.refresh(bot_account)
                    
                    # Verbinde Bot
                    bot_result = await bot_manager.add_bot(
                        bot_id=bot_account.id,
                        bot_token=bot_token
                    )
                    
                    if bot_result.get("status") == "connected":
                        results["success"] += 1
                        results["bots"].append({
                            "id": bot_account.id,
                            "name": bot_name,
                            "username": bot_username,
                            "token": bot_token,
                            "info": bot_result.get("info")
                        })
                        print(f"  ✅ Bot verbunden: @{bot_result.get('info', {}).get('username', 'N/A')}")
                    else:
                        results["failed"] += 1
                        results["errors"].append({
                            "bot": bot_name,
                            "error": f"Verbindung fehlgeschlagen: {bot_result.get('error')}"
                        })
                        print(f"  ⚠️  Bot erstellt, aber Verbindung fehlgeschlagen")
                    
                    # Rate Limiting: Warte zwischen Bot-Erstellungen
                    if i < 10:
                        wait_time = 3.0  # 3 Sekunden zwischen Bots
                        print(f"  ⏳ Warte {wait_time}s vor nächstem Bot...")
                        await asyncio.sleep(wait_time)
                
                else:
                    error_msg = result.get("error", "Unbekannter Fehler")
                    results["failed"] += 1
                    results["errors"].append({
                        "bot": bot_name,
                        "error": error_msg
                    })
                    print(f"  ❌ Fehler: {error_msg}")
                    
                    # Bei Fehler länger warten
                    if i < 10:
                        await asyncio.sleep(5.0)
            
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "bot": bot_name,
                    "error": str(e)
                })
                print(f"  ❌ Exception: {str(e)}")
                await asyncio.sleep(5.0)
        
        # 4. Zusammenfassung
        print("\n" + "=" * 60)
        print("📊 ZUSAMMENFASSUNG")
        print("=" * 60)
        print(f"✅ Erfolgreich erstellt: {results['success']}/{results['total']}")
        print(f"❌ Fehlgeschlagen: {results['failed']}/{results['total']}")
        
        if results["bots"]:
            print(f"\n✅ Erfolgreich erstellte Bots:")
            for bot in results["bots"]:
                print(f"  • {bot['name']} (ID: {bot['id']}, @{bot.get('info', {}).get('username', 'N/A')})")
        
        if results["errors"]:
            print(f"\n❌ Fehler:")
            for error in results["errors"]:
                print(f"  • {error['bot']}: {error['error']}")
        
        print("\n✅ Fertig!")
        
    except Exception as e:
        print(f"❌ Fehler: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()
        await account_manager.disconnect_all()
        await bot_manager.disconnect_all()

if __name__ == "__main__":
    print("🤖 Erstelle 10 Bots über BotFather...\n")
    asyncio.run(create_10_bots())

