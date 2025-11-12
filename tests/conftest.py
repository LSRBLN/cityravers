"""
Shared Fixtures für alle Tests
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from jose import jwt

# Importiere Models und App
from database import Base, User, Account, Group, ScheduledMessage, Subscription, Proxy, AccountWarming
from auth import create_access_token, get_password_hash, SECRET_KEY, ALGORITHM
from api import app
from account_manager import AccountManager
from bot_manager import BotManager


# In-Memory SQLite für Tests
@pytest.fixture(scope="function")  # Jeder Test bekommt eine frische DB
def db_engine():
    """Erstellt eine in-memory SQLite Datenbank für Tests"""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(db_engine):
    """Erstellt eine DB-Session für jeden Test"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def test_user(db_session):
    """Erstellt einen Test-User"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    user = User(
        email=f"test_{unique_id}@example.com",
        username=f"testuser_{unique_id}",
        password_hash=get_password_hash("testpass123"),
        is_active=True,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin(db_session):
    """Erstellt einen Test-Admin"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    admin = User(
        email=f"admin_{unique_id}@example.com",
        username=f"admin_{unique_id}",
        password_hash=get_password_hash("adminpass123"),
        is_active=True,
        is_admin=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def test_subscription(db_session, test_user):
    """Erstellt ein Test-Abonnement"""
    subscription = Subscription(
        user_id=test_user.id,
        plan_type="pro",
        status="active",
        expires_at=datetime.utcnow() + timedelta(days=30),
        max_accounts=10,
        max_groups=50,
        max_messages_per_day=1000
    )
    db_session.add(subscription)
    db_session.commit()
    db_session.refresh(subscription)
    return subscription


@pytest.fixture
def auth_token(test_user):
    """Erstellt ein JWT Token für Test-User"""
    data = {"sub": str(test_user.id)}
    return create_access_token(data)


@pytest.fixture
def admin_token(test_admin):
    """Erstellt ein JWT Token für Test-Admin"""
    data = {"sub": str(test_admin.id)}
    return create_access_token(data)


@pytest.fixture
def client(db_session):
    """Erstellt einen TestClient für FastAPI mit DB-Override"""
    # Override get_db dependency um Test-DB-Session zu verwenden
    from fastapi import Depends
    from api import get_db as original_get_db
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # Session wird von db_session Fixture verwaltet
    
    # Überschreibe Dependency
    app.dependency_overrides[original_get_db] = override_get_db
    
    # Verwende httpx AsyncClient mit ASGITransport
    from httpx import ASGITransport, AsyncClient
    import asyncio
    
    transport = ASGITransport(app=app)
    async_client = AsyncClient(transport=transport, base_url="http://testserver", follow_redirects=True)
    
    # Wrapper-Klasse für synchrone API
    class SyncClient:
        def __init__(self, async_client):
            self._client = async_client
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        
        def _run(self, coro):
            return self._loop.run_until_complete(coro)
        
        def post(self, *args, **kwargs):
            return self._run(self._client.post(*args, **kwargs))
        
        def get(self, *args, **kwargs):
            return self._run(self._client.get(*args, **kwargs))
        
        def put(self, *args, **kwargs):
            return self._run(self._client.put(*args, **kwargs))
        
        def delete(self, *args, **kwargs):
            return self._run(self._client.delete(*args, **kwargs))
        
        def options(self, *args, **kwargs):
            return self._run(self._client.options(*args, **kwargs))
        
        @property
        def headers(self):
            return self._client.headers
        
        @headers.setter
        def headers(self, value):
            self._client.headers = value
        
        def close(self):
            self._run(self._client.aclose())
            self._loop.close()
    
    sync_client = SyncClient(async_client)
    yield sync_client
    
    # Cleanup: Entferne Override
    app.dependency_overrides.clear()


@pytest.fixture
def authenticated_client(client, auth_token):
    """Client mit authentifiziertem User"""
    client.headers = {"Authorization": f"Bearer {auth_token}"}
    return client


@pytest.fixture
def admin_client(client, admin_token):
    """Client mit authentifiziertem Admin"""
    client.headers = {"Authorization": f"Bearer {admin_token}"}
    return client


@pytest.fixture
def mock_account_manager():
    """Mock für AccountManager"""
    manager = Mock(spec=AccountManager)
    manager.add_account = AsyncMock(return_value={
        "status": "connected",
        "account_id": 1,
        "info": {"username": "test_account", "phone": "+1234567890"}
    })
    manager.send_message = AsyncMock(return_value={"success": True, "sent_at": datetime.utcnow().isoformat()})
    manager.send_to_multiple_groups = AsyncMock(return_value={
        "total": 2,
        "success": 2,
        "failed": 0,
        "errors": []
    })
    manager.get_dialogs = AsyncMock(return_value=[
        {"id": -1001234567890, "name": "Test Group", "type": "group"}
    ])
    manager.scrape_group_members = AsyncMock(return_value=[
        {"user_id": "123456", "username": "testuser", "first_name": "Test"}
    ])
    manager.invite_users_to_group = AsyncMock(return_value={
        "total": 1,
        "success": 1,
        "failed": 0,
        "errors": []
    })
    manager.remove_account = AsyncMock()
    manager.disconnect_all = AsyncMock()
    return manager


@pytest.fixture
def mock_bot_manager():
    """Mock für BotManager"""
    manager = Mock(spec=BotManager)
    manager.add_bot = AsyncMock(return_value={
        "status": "connected",
        "bot_id": 1,
        "info": {"username": "test_bot", "first_name": "Test Bot"}
    })
    manager.send_message = AsyncMock(return_value={"success": True, "sent_at": datetime.utcnow().isoformat()})
    manager.send_to_multiple_groups = AsyncMock(return_value={
        "total": 2,
        "success": 2,
        "failed": 0,
        "errors": []
    })
    manager.remove_bot = AsyncMock()
    manager.disconnect_all = AsyncMock()
    return manager


@pytest.fixture
def mock_telegram_client():
    """Mock für Telethon TelegramClient"""
    client = AsyncMock()
    client.is_connected.return_value = False
    client.is_user_authorized.return_value = True
    client.get_me = AsyncMock(return_value=Mock(
        id=123456,
        username="testuser",
        first_name="Test",
        last_name="User",
        phone="+1234567890"
    ))
    client.send_message = AsyncMock(return_value=Mock(id=1, date=datetime.utcnow()))
    client.iter_dialogs = AsyncMock(return_value=iter([]))
    client.iter_messages = AsyncMock(return_value=iter([]))
    client.get_entity = AsyncMock(return_value=Mock(id=-1001234567890, title="Test Group"))
    client.connect = AsyncMock()
    client.disconnect = AsyncMock()
    return client


@pytest.fixture
def mock_telegram_bot():
    """Mock für python-telegram-bot Bot"""
    bot = AsyncMock()
    bot.get_me = AsyncMock(return_value=Mock(
        id=123456,
        username="test_bot",
        first_name="Test Bot",
        is_bot=True
    ))
    bot.send_message = AsyncMock(return_value=Mock(message_id=1, date=datetime.utcnow()))
    return bot


@pytest.fixture
def test_account(db_session, test_user):
    """Erstellt einen Test-Account"""
    account = Account(
        user_id=test_user.id,
        name="Test Account",
        account_type="user",
        api_id="12345",
        api_hash="abcdef123456",
        phone_number="+1234567890",
        session_name="test_session",
        is_active=True
    )
    db_session.add(account)
    db_session.commit()
    db_session.refresh(account)
    return account


@pytest.fixture
def test_bot_account(db_session, test_user):
    """Erstellt einen Test-Bot-Account"""
    account = Account(
        user_id=test_user.id,
        name="Test Bot",
        account_type="bot",
        bot_token="123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
        is_active=True
    )
    db_session.add(account)
    db_session.commit()
    db_session.refresh(account)
    return account


@pytest.fixture
def test_group(db_session, test_user):
    """Erstellt eine Test-Gruppe"""
    group = Group(
        user_id=test_user.id,
        name="Test Group",
        chat_id="-1001234567890",
        chat_type="group",
        is_active=True
    )
    db_session.add(group)
    db_session.commit()
    db_session.refresh(group)
    return group


@pytest.fixture
def test_proxy(db_session):
    """Erstellt einen Test-Proxy"""
    from encryption_utils import encrypt_string
    proxy = Proxy(
        name="Test Proxy",
        proxy_type="socks5",
        host="127.0.0.1",
        port=1080,
        username="testuser",
        password=encrypt_string("testpass"),
        is_active=True
    )
    db_session.add(proxy)
    db_session.commit()
    db_session.refresh(proxy)
    return proxy


@pytest.fixture
def test_scheduled_message(db_session, test_account, test_group):
    """Erstellt eine geplante Nachricht"""
    import json
    message = ScheduledMessage(
        account_id=test_account.id,
        group_ids=json.dumps([test_group.id]),
        message="Test Message",
        scheduled_time=datetime.utcnow() + timedelta(hours=1),
        delay=1.0,
        batch_size=10,
        batch_delay=5.0,
        group_delay=2.0,
        repeat_count=1,
        status="pending"
    )
    db_session.add(message)
    db_session.commit()
    db_session.refresh(message)
    return message


@pytest.fixture
def event_loop():
    """Event Loop für async Tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Pytest-asyncio Konfiguration
pytest_plugins = ('pytest_asyncio',)

