"""
Account-Warming Service
Automatisiert Aktivitäten zum "Aufwärmen" von Telegram-Accounts
"""

import asyncio
import random
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional
from database import get_session, AccountWarming, WarmingActivity, Account, Group
from account_manager import AccountManager


class WarmingService:
    """Verwaltet Account-Warming Aktivitäten"""
    
    def __init__(self, account_manager: AccountManager, db_engine):
        self.account_manager = account_manager
        self.db_engine = db_engine
        self.running_tasks: Dict[int, asyncio.Task] = {}
        self._stop_flags: Dict[int, bool] = {}
    
    def _parse_time(self, time_str: str) -> time:
        """Parst Zeit-String (HH:MM) zu time-Objekt"""
        try:
            hour, minute = map(int, time_str.split(':'))
            return time(hour, minute)
        except:
            return time(9, 0)  # Default: 09:00
    
    def _is_in_time_range(self, warming: AccountWarming) -> bool:
        """Prüft ob aktuelle Zeit im erlaubten Zeitfenster liegt"""
        now = datetime.now().time()
        start = self._parse_time(warming.start_time)
        end = self._parse_time(warming.end_time)
        
        if start <= end:
            return start <= now <= end
        else:  # Über Mitternacht
            return now >= start or now <= end
    
    def _get_random_delay(self, warming: AccountWarming) -> float:
        """Gibt zufälligen Delay zwischen min und max zurück"""
        return random.uniform(warming.min_delay, warming.max_delay)
    
    async def _execute_warming_cycle(self, warming_id: int):
        """Führt einen Warming-Zyklus für einen Account aus"""
        db = get_session(self.db_engine)
        
        try:
            warming = db.query(AccountWarming).filter(AccountWarming.id == warming_id).first()
            if not warming or not warming.is_active:
                return
            
            account = db.query(Account).filter(Account.id == warming.account_id).first()
            if not account or account.account_type != "user":
                return
            
            # Prüfe Zeitfenster
            if not self._is_in_time_range(warming):
                return
            
            # Prüfe ob Warming-Phase abgeschlossen
            if warming.warming_days >= warming.max_warming_days:
                warming.is_active = False
                db.commit()
                return
            
            # Hole verfügbare Gruppen
            groups = db.query(Group).filter(Group.is_active == True).all()
            if not groups:
                return
            
            # Führe Aktivitäten aus
            activities_today = db.query(WarmingActivity).filter(
                WarmingActivity.account_id == account.id,
                WarmingActivity.executed_at >= datetime.now().replace(hour=0, minute=0, second=0)
            ).count()
            
            # Berechne Aktivitäten basierend auf Warming-Tag
            # Schrittweise Erhöhung über die Tage
            progress = min(warming.warming_days / warming.max_warming_days, 1.0)
            
            # 1. Nachrichten lesen
            read_count = int(warming.read_messages_per_day * progress)
            if read_count > 0:
                group = random.choice(groups)
                result = await self.account_manager.warm_account_read_messages(
                    account_id=account.id,
                    group_entity=group.chat_id,
                    limit=read_count
                )
                
                activity = WarmingActivity(
                    warming_id=warming.id,
                    account_id=account.id,
                    activity_type="read",
                    target_chat_id=group.chat_id,
                    target_chat_name=group.name,
                    success=result.get("success", False),
                    error_message=result.get("error")
                )
                db.add(activity)
                
                if result.get("success"):
                    warming.total_actions += 1
                    warming.last_action_at = datetime.utcnow()
                
                await asyncio.sleep(self._get_random_delay(warming))
            
            # 2. Durch Dialoge scrollen
            scroll_count = int(warming.scroll_dialogs_per_day * progress)
            if scroll_count > 0:
                result = await self.account_manager.warm_account_scroll_dialogs(
                    account_id=account.id,
                    limit=scroll_count
                )
                
                activity = WarmingActivity(
                    warming_id=warming.id,
                    account_id=account.id,
                    activity_type="scroll",
                    success=result.get("success", False),
                    error_message=result.get("error")
                )
                db.add(activity)
                
                if result.get("success"):
                    warming.total_actions += 1
                    warming.last_action_at = datetime.utcnow()
                
                await asyncio.sleep(self._get_random_delay(warming))
            
            # 3. Reaktionen (nur wenn genug Nachrichten vorhanden)
            reaction_count = int(warming.reactions_per_day * progress)
            if reaction_count > 0 and groups:
                group = random.choice(groups)
                messages = await self.account_manager.get_group_messages(
                    account_id=account.id,
                    group_entity=group.chat_id,
                    limit=10
                )
                
                if messages:
                    reactions = ["👍", "❤️", "😂", "🔥", "👏"]
                    for _ in range(min(reaction_count, len(messages))):
                        msg = random.choice(messages)
                        reaction = random.choice(reactions)
                        
                        result = await self.account_manager.warm_account_send_reaction(
                            account_id=account.id,
                            group_entity=group.chat_id,
                            message_id=msg["id"],
                            reaction=reaction
                        )
                        
                        activity = WarmingActivity(
                            warming_id=warming.id,
                            account_id=account.id,
                            activity_type="reaction",
                            target_chat_id=group.chat_id,
                            target_chat_name=group.name,
                            message_id=msg["id"],
                            success=result.get("success", False),
                            error_message=result.get("error")
                        )
                        db.add(activity)
                        
                        if result.get("success"):
                            warming.total_actions += 1
                            warming.last_action_at = datetime.utcnow()
                        
                        await asyncio.sleep(self._get_random_delay(warming))
            
            # 4. Kleine Nachrichten (nur in späteren Phasen)
            if warming.warming_days >= 3:  # Nach 3 Tagen
                message_count = int(warming.small_messages_per_day * progress)
                if message_count > 0 and groups:
                    small_messages = [
                        "👍", "👌", "OK", "Danke", "Super", "Nice", "Cool"
                    ]
                    
                    for _ in range(message_count):
                        group = random.choice(groups)
                        message = random.choice(small_messages)
                        
                        result = await self.account_manager.warm_account_send_small_message(
                            account_id=account.id,
                            group_entity=group.chat_id,
                            message=message
                        )
                        
                        activity = WarmingActivity(
                            warming_id=warming.id,
                            account_id=account.id,
                            activity_type="message",
                            target_chat_id=group.chat_id,
                            target_chat_name=group.name,
                            success=result.get("success", False),
                            error_message=result.get("error")
                        )
                        db.add(activity)
                        
                        if result.get("success"):
                            warming.total_actions += 1
                            warming.last_action_at = datetime.utcnow()
                        
                        await asyncio.sleep(self._get_random_delay(warming))
            
            # Aktualisiere Warming-Tage (wenn neuer Tag)
            if warming.last_action_at:
                days_since_start = (datetime.utcnow() - warming.created_at).days
                warming.warming_days = days_since_start
            
            warming.updated_at = datetime.utcnow()
            db.commit()
        
        except Exception as e:
            db.rollback()
            print(f"Fehler beim Warming-Zyklus: {e}")
        finally:
            db.close()
    
    async def start_warming(self, warming_id: int):
        """Startet Warming für einen Account"""
        if warming_id in self.running_tasks:
            return
        
        self._stop_flags[warming_id] = False
        
        async def warming_loop():
            while not self._stop_flags.get(warming_id, False):
                await self._execute_warming_cycle(warming_id)
                # Warte 1-2 Stunden bis zum nächsten Zyklus
                await asyncio.sleep(random.uniform(3600, 7200))
        
        task = asyncio.create_task(warming_loop())
        self.running_tasks[warming_id] = task
    
    async def stop_warming(self, warming_id: int):
        """Stoppt Warming für einen Account"""
        self._stop_flags[warming_id] = True
        
        if warming_id in self.running_tasks:
            task = self.running_tasks[warming_id]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            del self.running_tasks[warming_id]
        
        if warming_id in self._stop_flags:
            del self._stop_flags[warming_id]
    
    async def start_all_active_warmings(self):
        """Startet alle aktiven Warmings"""
        db = get_session(self.db_engine)
        try:
            warmings = db.query(AccountWarming).filter(AccountWarming.is_active == True).all()
            for warming in warmings:
                await self.start_warming(warming.id)
        finally:
            db.close()
    
    async def stop_all_warmings(self):
        """Stoppt alle Warmings"""
        for warming_id in list(self.running_tasks.keys()):
            await self.stop_warming(warming_id)

