"""
Bot-Manager für Telegram Bot API
"""

import asyncio
from typing import Dict, Optional, List
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError, RetryAfter, TimedOut


class BotManager:
    """Verwaltet mehrere Telegram Bots"""
    
    def __init__(self):
        self.bots: Dict[int, Bot] = {}
        self.bot_info: Dict[int, dict] = {}
    
    async def add_bot(self, bot_id: int, bot_token: str) -> dict:
        """
        Fügt einen Bot hinzu und verbindet
        
        Args:
            bot_id: Datenbank-ID des Bots
            bot_token: Bot Token von @BotFather
            
        Returns:
            Bot-Informationen
        """
        try:
            bot = Bot(token=bot_token)
            
            # Teste Verbindung
            bot_info = await bot.get_me()
            
            self.bots[bot_id] = bot
            self.bot_info[bot_id] = {
                "id": bot_id,
                "username": bot_info.username,
                "first_name": bot_info.first_name,
                "is_bot": bot_info.is_bot,
                "connected_at": datetime.utcnow().isoformat()
            }
            
            return {
                "status": "connected",
                "bot_id": bot_id,
                "info": self.bot_info[bot_id]
            }
        
        except Exception as e:
            return {
                "status": "error",
                "bot_id": bot_id,
                "error": str(e)
            }
    
    async def remove_bot(self, bot_id: int):
        """Entfernt einen Bot"""
        if bot_id in self.bots:
            # Bot hat keine explizite disconnect-Methode
            del self.bots[bot_id]
        if bot_id in self.bot_info:
            del self.bot_info[bot_id]
    
    async def get_bot_info(self, bot_id: int) -> Optional[dict]:
        """Gibt Bot-Informationen zurück"""
        return self.bot_info.get(bot_id)
    
    async def list_bots(self) -> List[dict]:
        """Listet alle verbundenen Bots"""
        return list(self.bot_info.values())
    
    async def send_message(
        self,
        bot_id: int,
        chat_id: str,
        message: str,
        delay: float = 1.0
    ) -> dict:
        """
        Sendet eine Nachricht über einen Bot
        
        Args:
            bot_id: Bot-ID
            chat_id: Chat-ID, Username oder Channel-Username
            message: Nachrichtentext
            delay: Verzögerung nach dem Senden
            
        Returns:
            Ergebnis-Dict
        """
        if bot_id not in self.bots:
            return {"success": False, "error": "Bot not connected"}
        
        bot = self.bots[bot_id]
        
        try:
            # Konvertiere chat_id zu int falls möglich
            try:
                chat_id_int = int(chat_id)
            except ValueError:
                chat_id_int = chat_id
            
            await bot.send_message(chat_id=chat_id_int, text=message)
            
            if delay > 0:
                await asyncio.sleep(delay)
            
            return {"success": True, "sent_at": datetime.utcnow().isoformat()}
        
        except RetryAfter as e:
            return {
                "success": False,
                "error": "FloodWait",
                "wait_seconds": e.retry_after
            }
        except TimedOut:
            return {
                "success": False,
                "error": "Request timed out"
            }
        except TelegramError as e:
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_to_multiple_groups(
        self,
        bot_id: int,
        group_ids: List[str],
        message: str,
        delay: float = 1.0,
        group_delay: float = 2.0
    ) -> dict:
        """
        Sendet eine Nachricht an mehrere Gruppen
        
        Args:
            bot_id: Bot-ID
            group_ids: Liste von Chat-IDs
            message: Nachrichtentext
            delay: Verzögerung zwischen Nachrichten in derselben Gruppe
            group_delay: Verzögerung zwischen verschiedenen Gruppen
            
        Returns:
            Ergebnis-Dict mit Statistiken
        """
        results = {
            "total": len(group_ids),
            "success": 0,
            "failed": 0,
            "errors": []
        }
        
        for i, group_id in enumerate(group_ids):
            result = await self.send_message(bot_id, group_id, message, delay)
            
            if result.get("success"):
                results["success"] += 1
            else:
                results["failed"] += 1
                results["errors"].append({
                    "group_id": group_id,
                    "error": result.get("error", "Unknown error")
                })
            
            # Pause zwischen Gruppen (außer bei der letzten)
            if i < len(group_ids) - 1:
                if result.get("error") == "FloodWait":
                    wait = result.get("wait_seconds", 60)
                    await asyncio.sleep(wait)
                else:
                    await asyncio.sleep(group_delay)
        
        return results
    
    async def get_chats(self, bot_id: int) -> List[dict]:
        """
        Ruft verfügbare Chats eines Bots ab
        Hinweis: Bot API hat keine direkte Methode zum Auflisten aller Chats
        """
        if bot_id not in self.bots:
            return []
        
        # Bot API hat keine Methode zum Auflisten aller Chats
        # Chats müssen manuell hinzugefügt werden
        return []
    
    async def disconnect_all(self):
        """Trennt alle Verbindungen"""
        for bot_id in list(self.bots.keys()):
            await self.remove_bot(bot_id)

