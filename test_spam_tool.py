#!/usr/bin/env python3
"""
Unit Tests für TelegramSpamTool
"""

import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
from spam_tool import TelegramSpamTool, DEFAULT_DELAY, DEFAULT_BATCH_SIZE, DEFAULT_BATCH_DELAY


class TestTelegramSpamTool(unittest.IsolatedAsyncioTestCase):
    """Test-Klasse für TelegramSpamTool"""
    
    def setUp(self):
        """Setup für jeden Test"""
        self.api_id = "12345678"
        self.api_hash = "abcdef1234567890abcdef1234567890"
        self.session_name = "test_session"
    
    def test_init_valid(self):
        """Test: Initialisierung mit gültigen Credentials"""
        tool = TelegramSpamTool(self.api_id, self.api_hash, self.session_name)
        self.assertIsNotNone(tool.client)
        self.assertEqual(tool.sent_count, 0)
        self.assertEqual(tool.failed_count, 0)
    
    def test_init_missing_api_id(self):
        """Test: Initialisierung ohne API_ID schlägt fehl"""
        with self.assertRaises(ValueError):
            TelegramSpamTool("", self.api_hash)
    
    def test_init_missing_api_hash(self):
        """Test: Initialisierung ohne API_HASH schlägt fehl"""
        with self.assertRaises(ValueError):
            TelegramSpamTool(self.api_id, "")
    
    @patch('telethon.TelegramClient')
    async def test_connect_success(self, mock_client_class):
        """Test: Erfolgreiche Verbindung"""
        mock_client = AsyncMock()
        mock_client.is_user_authorized.return_value = True
        mock_client.get_me.return_value = MagicMock(first_name="Test", last_name="User", username="testuser")
        mock_client_class.return_value = mock_client
        
        tool = TelegramSpamTool(self.api_id, self.api_hash)
        tool.client = mock_client
        
        me = await tool.connect()
        self.assertIsNotNone(me)
        mock_client.start.assert_called_once()
    
    @patch('telethon.TelegramClient')
    async def test_send_message_success(self, mock_client_class):
        """Test: Erfolgreiches Senden einer Nachricht"""
        mock_client = AsyncMock()
        mock_client.send_message = AsyncMock()
        mock_client_class.return_value = mock_client
        
        tool = TelegramSpamTool(self.api_id, self.api_hash)
        tool.client = mock_client
        
        result = await tool.send_message("test_chat", "Test message", delay=0)
        
        self.assertTrue(result)
        self.assertEqual(tool.sent_count, 1)
        self.assertEqual(tool.failed_count, 0)
        mock_client.send_message.assert_called_once_with("test_chat", "Test message")
    
    @patch('telethon.TelegramClient')
    async def test_send_message_flood_wait(self, mock_client_class):
        """Test: FloodWait Error wird behandelt"""
        from telethon.errors import FloodWaitError
        
        mock_client = AsyncMock()
        mock_client.send_message = AsyncMock(side_effect=[
            FloodWaitError(request=MagicMock(), seconds=2),
            AsyncMock()  # Erfolgreich beim zweiten Versuch
        ])
        mock_client_class.return_value = mock_client
        
        tool = TelegramSpamTool(self.api_id, self.api_hash)
        tool.client = mock_client
        
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            result = await tool.send_message("test_chat", "Test message", delay=0)
            
            self.assertTrue(result)
            self.assertEqual(tool.sent_count, 1)
            mock_sleep.assert_called_once_with(2)
    
    @patch('telethon.TelegramClient')
    async def test_send_message_error(self, mock_client_class):
        """Test: Fehler beim Senden wird behandelt"""
        mock_client = AsyncMock()
        mock_client.send_message = AsyncMock(side_effect=Exception("Network error"))
        mock_client_class.return_value = mock_client
        
        tool = TelegramSpamTool(self.api_id, self.api_hash)
        tool.client = mock_client
        
        result = await tool.send_message("test_chat", "Test message", delay=0)
        
        self.assertFalse(result)
        self.assertEqual(tool.sent_count, 0)
        self.assertEqual(tool.failed_count, 1)
    
    @patch('telethon.TelegramClient')
    async def test_spam_repeat(self, mock_client_class):
        """Test: Wiederholtes Senden derselben Nachricht"""
        mock_client = AsyncMock()
        mock_client.send_message = AsyncMock()
        mock_client_class.return_value = mock_client
        
        tool = TelegramSpamTool(self.api_id, self.api_hash)
        tool.client = mock_client
        
        with patch('asyncio.sleep', new_callable=AsyncMock):
            await tool.spam_repeat("test_chat", "Test", count=3, delay=0, batch_size=10, batch_delay=0)
        
        self.assertEqual(tool.sent_count, 3)
        self.assertEqual(mock_client.send_message.call_count, 3)
    
    @patch('telethon.TelegramClient')
    async def test_spam_messages(self, mock_client_class):
        """Test: Senden mehrerer verschiedener Nachrichten"""
        mock_client = AsyncMock()
        mock_client.send_message = AsyncMock()
        mock_client_class.return_value = mock_client
        
        tool = TelegramSpamTool(self.api_id, self.api_hash)
        tool.client = mock_client
        
        messages = ["Nachricht 1", "Nachricht 2", "Nachricht 3"]
        
        with patch('asyncio.sleep', new_callable=AsyncMock):
            await tool.spam_messages("test_chat", messages, delay=0, batch_size=10, batch_delay=0)
        
        self.assertEqual(tool.sent_count, 3)
        self.assertEqual(mock_client.send_message.call_count, 3)
    
    @patch('telethon.TelegramClient')
    async def test_disconnect(self, mock_client_class):
        """Test: Trennen der Verbindung"""
        mock_client = AsyncMock()
        mock_client.disconnect = AsyncMock()
        mock_client_class.return_value = mock_client
        
        tool = TelegramSpamTool(self.api_id, self.api_hash)
        tool.client = mock_client
        
        await tool.disconnect()
        
        mock_client.disconnect.assert_called_once()


if __name__ == "__main__":
    unittest.main()

