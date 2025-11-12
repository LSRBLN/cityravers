"""
Unit Tests für BotManager (bot_manager.py)
Kritikalität: 🔴 HOCH - 100% Coverage erforderlich
"""
import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime
from telegram.error import TelegramError, RetryAfter, TimedOut
from bot_manager import BotManager


class TestBotManagerInit:
    """Tests für BotManager Initialisierung"""
    
    def test_init(self):
        """Test: BotManager wird initialisiert"""
        manager = BotManager()
        assert manager.bots == {}
        assert manager.bot_info == {}


class TestAddBot:
    """Tests für add_bot()"""
    
    @pytest.mark.asyncio
    async def test_add_bot_success(self, mock_telegram_bot):
        """Test: Bot wird erfolgreich hinzugefügt"""
        manager = BotManager()
        
        with patch('bot_manager.Bot', return_value=mock_telegram_bot):
            result = await manager.add_bot(
                bot_id=1,
                bot_token="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
            )
        
        assert result["status"] == "connected"
        assert result["bot_id"] == 1
        assert "info" in result
        assert 1 in manager.bots
        assert 1 in manager.bot_info
    
    @pytest.mark.asyncio
    async def test_add_bot_invalid_token(self):
        """Test: Fehler bei ungültigem Token"""
        manager = BotManager()
        
        with patch('bot_manager.Bot') as mock_bot_class:
            mock_bot = AsyncMock()
            mock_bot.get_me = AsyncMock(side_effect=TelegramError("Invalid token"))
            mock_bot_class.return_value = mock_bot
            
            result = await manager.add_bot(
                bot_id=1,
                bot_token="invalid_token"
            )
        
        assert result["status"] == "error"
        assert "error" in result


class TestSendMessage:
    """Tests für send_message()"""
    
    @pytest.mark.asyncio
    async def test_send_message_success(self, mock_telegram_bot):
        """Test: Nachricht wird erfolgreich gesendet"""
        manager = BotManager()
        manager.bots[1] = mock_telegram_bot
        
        result = await manager.send_message(
            bot_id=1,
            chat_id="-1001234567890",
            message="Test Message"
        )
        
        assert result["success"] is True
        assert "sent_at" in result
        mock_telegram_bot.send_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_message_bot_not_connected(self):
        """Test: Fehler bei nicht verbundenem Bot"""
        manager = BotManager()
        
        result = await manager.send_message(
            bot_id=999,
            chat_id="-1001234567890",
            message="Test Message"
        )
        
        assert result["success"] is False
        assert "not connected" in result["error"]
    
    @pytest.mark.asyncio
    async def test_send_message_retry_after(self, mock_telegram_bot):
        """Test: RetryAfter wird behandelt"""
        manager = BotManager()
        manager.bots[1] = mock_telegram_bot
        
        error = RetryAfter(retry_after=60)
        mock_telegram_bot.send_message = AsyncMock(side_effect=error)
        
        result = await manager.send_message(
            bot_id=1,
            chat_id="-1001234567890",
            message="Test Message"
        )
        
        assert result["success"] is False
        assert result["error"] == "FloodWait"
        assert result["wait_seconds"] == 60
    
    @pytest.mark.asyncio
    async def test_send_message_timed_out(self, mock_telegram_bot):
        """Test: TimedOut wird behandelt"""
        manager = BotManager()
        manager.bots[1] = mock_telegram_bot
        
        error = TimedOut("Request timed out")
        mock_telegram_bot.send_message = AsyncMock(side_effect=error)
        
        result = await manager.send_message(
            bot_id=1,
            chat_id="-1001234567890",
            message="Test Message"
        )
        
        assert result["success"] is False
        assert result["error"] == "Request timed out"
    
    @pytest.mark.asyncio
    async def test_send_message_chat_id_string(self, mock_telegram_bot):
        """Test: String Chat-ID wird akzeptiert"""
        manager = BotManager()
        manager.bots[1] = mock_telegram_bot
        
        result = await manager.send_message(
            bot_id=1,
            chat_id="@testchannel",
            message="Test Message"
        )
        
        assert result["success"] is True


class TestSendToMultipleGroups:
    """Tests für send_to_multiple_groups()"""
    
    @pytest.mark.asyncio
    async def test_send_to_multiple_groups_success(self, mock_telegram_bot):
        """Test: Nachricht wird an mehrere Gruppen gesendet"""
        manager = BotManager()
        manager.bots[1] = mock_telegram_bot
        
        result = await manager.send_to_multiple_groups(
            bot_id=1,
            group_ids=["-1001234567890", "-1001234567891"],
            message="Test Message"
        )
        
        assert result["total"] == 2
        assert result["success"] == 2
        assert result["failed"] == 0
        assert len(result["errors"]) == 0
    
    @pytest.mark.asyncio
    async def test_send_to_multiple_groups_flood_wait(self, mock_telegram_bot):
        """Test: FloodWait zwischen Gruppen wird behandelt"""
        manager = BotManager()
        manager.bots[1] = mock_telegram_bot
        
        # Erste Nachricht erfolgreich, zweite FloodWait
        error = RetryAfter(retry_after=60)
        mock_telegram_bot.send_message = AsyncMock(side_effect=[
            Mock(message_id=1),
            error
        ])
        
        result = await manager.send_to_multiple_groups(
            bot_id=1,
            group_ids=["-1001234567890", "-1001234567891"],
            message="Test Message"
        )
        
        assert result["total"] == 2
        assert result["success"] == 1
        assert result["failed"] == 1
        assert len(result["errors"]) == 1


class TestRemoveBot:
    """Tests für remove_bot()"""
    
    @pytest.mark.asyncio
    async def test_remove_bot(self, mock_telegram_bot):
        """Test: Bot wird entfernt"""
        manager = BotManager()
        manager.bots[1] = mock_telegram_bot
        manager.bot_info[1] = {"id": 1}
        
        await manager.remove_bot(bot_id=1)
        
        assert 1 not in manager.bots
        assert 1 not in manager.bot_info


class TestListBots:
    """Tests für list_bots()"""
    
    @pytest.mark.asyncio
    async def test_list_bots(self):
        """Test: Alle Bots werden gelistet"""
        manager = BotManager()
        manager.bot_info[1] = {"id": 1, "username": "bot1"}
        manager.bot_info[2] = {"id": 2, "username": "bot2"}
        
        result = await manager.list_bots()
        
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["id"] == 2

