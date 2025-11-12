"""
Unit Tests für AccountManager (account_manager.py)
Kritikalität: 🔴 HOCH - 100% Coverage erforderlich
"""
import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from datetime import datetime
from telethon.errors import FloodWaitError, SessionPasswordNeededError
from account_manager import AccountManager


class TestAccountManagerInit:
    """Tests für AccountManager Initialisierung"""
    
    def test_init(self):
        """Test: AccountManager wird initialisiert"""
        manager = AccountManager()
        assert manager.clients == {}
        assert manager.account_info == {}


class TestAddAccount:
    """Tests für add_account()"""
    
    @pytest.mark.asyncio
    async def test_add_account_success(self, mock_telegram_client):
        """Test: Account wird erfolgreich hinzugefügt"""
        manager = AccountManager()
        
        with patch('account_manager.TelegramClient', return_value=mock_telegram_client):
            result = await manager.add_account(
                account_id=1,
                api_id="12345",
                api_hash="abcdef123456",
                session_name="test_session",
                phone_number="+1234567890"
            )
        
        assert result["status"] == "connected"
        assert result["account_id"] == 1
        assert "info" in result
        assert 1 in manager.clients
        assert 1 in manager.account_info
    
    @pytest.mark.asyncio
    async def test_add_account_missing_credentials(self):
        """Test: Fehler bei fehlenden API Credentials"""
        manager = AccountManager()
        
        result = await manager.add_account(
            account_id=1,
            api_id=None,
            api_hash=None,
            session_name="test_session"
        )
        
        assert result["status"] == "error"
        # Prüfe dass ein Fehler zurückgegeben wird (kann verschiedene Meldungen sein)
        assert "error" in result
        assert len(result["error"]) > 0
    
    @pytest.mark.asyncio
    async def test_add_account_code_required(self, mock_telegram_client):
        """Test: Code-Anfrage bei nicht autorisiertem Account"""
        manager = AccountManager()
        mock_telegram_client.is_user_authorized.return_value = False
        mock_telegram_client.send_code_request = AsyncMock()
        
        with patch('account_manager.TelegramClient', return_value=mock_telegram_client):
            result = await manager.add_account(
                account_id=1,
                api_id="12345",
                api_hash="abcdef123456",
                session_name="test_session",
                phone_number="+1234567890"
            )
        
        assert result["status"] == "code_required"
        assert result["account_id"] == 1
    
    @pytest.mark.asyncio
    async def test_add_account_2fa_required(self, mock_telegram_client):
        """Test: 2FA Passwort erforderlich"""
        manager = AccountManager()
        mock_telegram_client.is_user_authorized.return_value = False
        mock_telegram_client.send_code_request = AsyncMock()
        # SessionPasswordNeededError benötigt request-Argument
        mock_request = Mock()
        mock_telegram_client.sign_in = AsyncMock(side_effect=SessionPasswordNeededError(mock_request))
        
        with patch('account_manager.TelegramClient', return_value=mock_telegram_client):
            result = await manager.add_account(
                account_id=1,
                api_id="12345",
                api_hash="abcdef123456",
                session_name="test_session",
                phone_number="+1234567890",
                code="12345"
            )
        
        assert result["status"] == "password_required"
        assert result["account_id"] == 1
    
    @pytest.mark.asyncio
    async def test_add_account_with_proxy(self, mock_telegram_client):
        """Test: Account mit Proxy wird hinzugefügt"""
        manager = AccountManager()
        proxy_config = {
            "proxy_type": "socks5",
            "host": "127.0.0.1",
            "port": 1080,
            "username": "user",
            "password": "pass"
        }
        
        with patch('account_manager.TelegramClient', return_value=mock_telegram_client):
            result = await manager.add_account(
                account_id=1,
                api_id="12345",
                api_hash="abcdef123456",
                session_name="test_session",
                proxy_config=proxy_config
            )
        
        assert result["status"] == "connected"


class TestSendMessage:
    """Tests für send_message()"""
    
    @pytest.mark.asyncio
    async def test_send_message_success(self, mock_telegram_client):
        """Test: Nachricht wird erfolgreich gesendet"""
        manager = AccountManager()
        manager.clients[1] = mock_telegram_client
        
        result = await manager.send_message(
            account_id=1,
            entity="-1001234567890",
            message="Test Message"
        )
        
        assert result["success"] is True
        assert "sent_at" in result
        mock_telegram_client.send_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_message_account_not_connected(self):
        """Test: Fehler bei nicht verbundenem Account"""
        manager = AccountManager()
        
        result = await manager.send_message(
            account_id=999,
            entity="-1001234567890",
            message="Test Message"
        )
        
        assert result["success"] is False
        assert "not connected" in result["error"]
    
    @pytest.mark.asyncio
    async def test_send_message_flood_wait(self, mock_telegram_client):
        """Test: FloodWait wird behandelt"""
        manager = AccountManager()
        manager.clients[1] = mock_telegram_client
        
        # FloodWaitError benötigt request-Argument, seconds wird als Attribut gesetzt
        mock_request = Mock()
        error = FloodWaitError(mock_request, capture=0)
        error.seconds = 60  # Setze seconds-Attribut
        mock_telegram_client.send_message = AsyncMock(side_effect=error)
        
        result = await manager.send_message(
            account_id=1,
            entity="-1001234567890",
            message="Test Message"
        )
        
        assert result["success"] is False
        assert result["error"] == "FloodWait"
        assert result["wait_seconds"] == 60
    
    @pytest.mark.asyncio
    async def test_send_message_with_delay(self, mock_telegram_client):
        """Test: Delay wird nach dem Senden angewendet"""
        import asyncio
        manager = AccountManager()
        manager.clients[1] = mock_telegram_client
        
        start = datetime.now()
        result = await manager.send_message(
            account_id=1,
            entity="-1001234567890",
            message="Test Message",
            delay=0.1
        )
        elapsed = (datetime.now() - start).total_seconds()
        
        assert result["success"] is True
        assert elapsed >= 0.1  # Mindestens Delay-Zeit


class TestSendToMultipleGroups:
    """Tests für send_to_multiple_groups()"""
    
    @pytest.mark.asyncio
    async def test_send_to_multiple_groups_success(self, mock_telegram_client):
        """Test: Nachricht wird an mehrere Gruppen gesendet"""
        manager = AccountManager()
        manager.clients[1] = mock_telegram_client
        
        result = await manager.send_to_multiple_groups(
            account_id=1,
            group_ids=["-1001234567890", "-1001234567891"],
            message="Test Message"
        )
        
        assert result["total"] == 2
        assert result["success"] == 2
        assert result["failed"] == 0
        assert len(result["errors"]) == 0
        assert mock_telegram_client.send_message.call_count == 2
    
    @pytest.mark.asyncio
    async def test_send_to_multiple_groups_partial_failure(self, mock_telegram_client):
        """Test: Teilweise Fehler werden korrekt behandelt"""
        manager = AccountManager()
        manager.clients[1] = mock_telegram_client
        
        # Erste Nachricht erfolgreich, zweite fehlgeschlagen
        mock_telegram_client.send_message = AsyncMock(side_effect=[
            Mock(id=1),
            Exception("Group not found")
        ])
        
        result = await manager.send_to_multiple_groups(
            account_id=1,
            group_ids=["-1001234567890", "-1001234567891"],
            message="Test Message"
        )
        
        assert result["total"] == 2
        assert result["success"] == 1
        assert result["failed"] == 1
        assert len(result["errors"]) == 1


class TestGetDialogs:
    """Tests für get_dialogs()"""
    
    @pytest.mark.asyncio
    async def test_get_dialogs_success(self, mock_telegram_client):
        """Test: Dialoge werden abgerufen"""
        manager = AccountManager()
        manager.clients[1] = mock_telegram_client
        
        # Mock iter_dialogs - muss async generator sein
        dialog1 = Mock()
        dialog1.id = -1001234567890
        dialog1.name = "Test Group"
        dialog1.entity = Mock()
        # Simuliere Channel-Typ
        dialog1.entity.__class__.__name__ = "Channel"
        dialog1.entity.broadcast = False
        dialog1.entity.username = None
        
        async def mock_iter_dialogs():
            yield dialog1
        
        mock_telegram_client.iter_dialogs = mock_iter_dialogs
        
        result = await manager.get_dialogs(account_id=1)
        
        assert len(result) == 1
        assert result[0]["id"] == -1001234567890
        assert result[0]["name"] == "Test Group"
    
    @pytest.mark.asyncio
    async def test_get_dialogs_account_not_connected(self):
        """Test: Fehler bei nicht verbundenem Account"""
        manager = AccountManager()
        
        result = await manager.get_dialogs(account_id=999)
        
        assert result == []


class TestRemoveAccount:
    """Tests für remove_account()"""
    
    @pytest.mark.asyncio
    async def test_remove_account(self, mock_telegram_client):
        """Test: Account wird entfernt"""
        manager = AccountManager()
        manager.clients[1] = mock_telegram_client
        manager.account_info[1] = {"id": 1}
        
        await manager.remove_account(account_id=1)
        
        assert 1 not in manager.clients
        assert 1 not in manager.account_info
        mock_telegram_client.disconnect.assert_called_once()


class TestDisconnectAll:
    """Tests für disconnect_all()"""
    
    @pytest.mark.asyncio
    async def test_disconnect_all(self, mock_telegram_client):
        """Test: Alle Accounts werden getrennt"""
        manager = AccountManager()
        manager.clients[1] = mock_telegram_client
        manager.clients[2] = mock_telegram_client
        
        await manager.disconnect_all()
        
        assert len(manager.clients) == 0
        assert len(manager.account_info) == 0

