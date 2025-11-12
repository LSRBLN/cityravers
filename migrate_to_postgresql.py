#!/usr/bin/env python3
"""
Migration Script: SQLite → PostgreSQL
Kopiert alle Daten von SQLite zu PostgreSQL
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import (
    Base, Account, Group, ScheduledMessage, ScrapedUser,
    AccountWarming, WarmingActivity, MessageTemplate, SentMessage,
    AccountStatistic, Proxy, User, Subscription, PhoneNumberPurchase
)

def migrate():
    # SQLite Source
    sqlite_url = "sqlite:///telegram_bot.db"
    if not os.path.exists("telegram_bot.db"):
        print("❌ SQLite Datenbank nicht gefunden: telegram_bot.db")
        return False
    
    # PostgreSQL Target
    pg_url = os.getenv("DATABASE_URL")
    if not pg_url:
        print("❌ DATABASE_URL nicht gesetzt!")
        print("Bitte setze: export DATABASE_URL='postgresql://user:pass@localhost/db'")
        return False
    
    print("🔄 Starte Migration SQLite → PostgreSQL...")
    print(f"Quelle: {sqlite_url}")
    print(f"Ziel: {pg_url}")
    
    # Verbindungen
    sqlite_engine = create_engine(sqlite_url)
    pg_engine = create_engine(pg_url)
    
    # Sessions
    SQLiteSession = sessionmaker(bind=sqlite_engine)
    PGSession = sessionmaker(bind=pg_engine)
    
    sqlite_session = SQLiteSession()
    pg_session = PGSession()
    
    try:
        # Tabellen in PostgreSQL erstellen
        print("📋 Erstelle Tabellen in PostgreSQL...")
        Base.metadata.create_all(pg_engine)
        
        # Migriere User
        print("👤 Migriere User...")
        users = sqlite_session.query(User).all()
        user_map = {}
        for user in users:
            new_user = User(
                id=user.id,
                email=user.email,
                username=user.username,
                password_hash=user.password_hash,
                is_active=user.is_active,
                is_admin=user.is_admin,
                created_at=user.created_at,
                last_login=user.last_login
            )
            pg_session.add(new_user)
            user_map[user.id] = new_user
        pg_session.commit()
        print(f"✅ {len(users)} User migriert")
        
        # Migriere Subscriptions
        print("📦 Migriere Subscriptions...")
        subscriptions = sqlite_session.query(Subscription).all()
        for sub in subscriptions:
            new_sub = Subscription(
                id=sub.id,
                user_id=sub.user_id,
                plan_type=sub.plan_type,
                status=sub.status,
                started_at=sub.started_at,
                expires_at=sub.expires_at,
                max_accounts=sub.max_accounts,
                max_groups=sub.max_groups,
                max_messages_per_day=sub.max_messages_per_day,
                features=sub.features
            )
            pg_session.add(new_sub)
        pg_session.commit()
        print(f"✅ {len(subscriptions)} Subscriptions migriert")
        
        # Migriere Proxies
        print("🔒 Migriere Proxies...")
        proxies = sqlite_session.query(Proxy).all()
        proxy_map = {}
        for proxy in proxies:
            new_proxy = Proxy(
                id=proxy.id,
                name=proxy.name,
                proxy_type=proxy.proxy_type,
                host=proxy.host,
                port=proxy.port,
                username=proxy.username,
                password=proxy.password,
                secret=proxy.secret,
                country=proxy.country,
                is_active=proxy.is_active,
                is_verified=proxy.is_verified,
                last_used=proxy.last_used,
                usage_count=proxy.usage_count,
                created_at=proxy.created_at,
                notes=proxy.notes
            )
            pg_session.add(new_proxy)
            proxy_map[proxy.id] = new_proxy
        pg_session.commit()
        print(f"✅ {len(proxies)} Proxies migriert")
        
        # Migriere Accounts
        print("👤 Migriere Accounts...")
        accounts = sqlite_session.query(Account).all()
        account_map = {}
        for acc in accounts:
            new_acc = Account(
                id=acc.id,
                user_id=acc.user_id,
                name=acc.name,
                account_type=acc.account_type,
                api_id=acc.api_id,
                api_hash=acc.api_hash,
                bot_token=acc.bot_token,
                phone_number=acc.phone_number,
                session_name=acc.session_name,
                session_file_path=acc.session_file_path,
                tdata_path=acc.tdata_path,
                proxy_id=acc.proxy_id,
                is_active=acc.is_active,
                created_at=acc.created_at,
                last_used=acc.last_used
            )
            pg_session.add(new_acc)
            account_map[acc.id] = new_acc
        pg_session.commit()
        print(f"✅ {len(accounts)} Accounts migriert")
        
        # Migriere Groups
        print("👥 Migriere Groups...")
        groups = sqlite_session.query(Group).all()
        for group in groups:
            new_group = Group(
                id=group.id,
                user_id=group.user_id,
                name=group.name,
                chat_id=group.chat_id,
                chat_type=group.chat_type,
                username=group.username,
                is_active=group.is_active,
                created_at=group.created_at,
                member_count=group.member_count,
                is_public=group.is_public,
                bot_invite_allowed=group.bot_invite_allowed,
                description=group.description,
                invite_link=group.invite_link,
                last_checked=group.last_checked
            )
            pg_session.add(new_group)
        pg_session.commit()
        print(f"✅ {len(groups)} Groups migriert")
        
        # Migriere ScheduledMessages
        print("📅 Migriere ScheduledMessages...")
        messages = sqlite_session.query(ScheduledMessage).all()
        for msg in messages:
            new_msg = ScheduledMessage(
                id=msg.id,
                account_id=msg.account_id,
                message=msg.message,
                group_ids=msg.group_ids,
                scheduled_time=msg.scheduled_time,
                group_delay=msg.group_delay,
                delay=msg.delay,
                batch_size=msg.batch_size,
                batch_delay=msg.batch_delay,
                repeat_count=msg.repeat_count,
                status=msg.status,
                created_at=msg.created_at
            )
            pg_session.add(new_msg)
        pg_session.commit()
        print(f"✅ {len(messages)} ScheduledMessages migriert")
        
        # Weitere Tabellen (falls vorhanden)
        tables = [
            (ScrapedUser, "ScrapedUser"),
            (AccountWarming, "AccountWarming"),
            (WarmingActivity, "WarmingActivity"),
            (MessageTemplate, "MessageTemplate"),
            (SentMessage, "SentMessage"),
            (AccountStatistic, "AccountStatistic"),
            (PhoneNumberPurchase, "PhoneNumberPurchase"),
        ]
        
        for model, name in tables:
            try:
                items = sqlite_session.query(model).all()
                if items:
                    print(f"📋 Migriere {name}...")
                    for item in items:
                        # Kopiere alle Attribute
                        data = {c.name: getattr(item, c.name) for c in item.__table__.columns}
                        new_item = model(**data)
                        pg_session.add(new_item)
                    pg_session.commit()
                    print(f"✅ {len(items)} {name} migriert")
            except Exception as e:
                print(f"⚠️  {name}: {e}")
        
        print("\n✅ Migration erfolgreich abgeschlossen!")
        return True
        
    except Exception as e:
        print(f"\n❌ Fehler bei Migration: {e}")
        pg_session.rollback()
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        sqlite_session.close()
        pg_session.close()

if __name__ == "__main__":
    success = migrate()
    sys.exit(0 if success else 1)

