"""
Scheduler-Service für zeitgesteuerte Nachrichten
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from account_manager import AccountManager
from bot_manager import BotManager
from database import ScheduledMessage, Account, Group, get_session, init_db

logger = logging.getLogger(__name__)


class SchedulerService:
    """Verwaltet geplante Nachrichten"""
    
    def __init__(self, account_manager: AccountManager, bot_manager: BotManager, db_engine):
        self.account_manager = account_manager
        self.bot_manager = bot_manager
        self.db_engine = db_engine
        self.scheduler = AsyncIOScheduler()
        self._started = False
        self.running_jobs: Dict[int, asyncio.Task] = {}
    
    def start(self):
        """Startet den Scheduler (muss nach Event Loop Start aufgerufen werden)"""
        if not self._started:
            self.scheduler.start()
            self._started = True
    
    async def schedule_message(self, scheduled_msg: ScheduledMessage):
        """
        Plant eine Nachricht
        
        Args:
            scheduled_msg: ScheduledMessage Objekt aus der Datenbank
        """
        def job_function():
            asyncio.create_task(self._execute_scheduled_message(scheduled_msg.id))
        
        self.scheduler.add_job(
            job_function,
            trigger=DateTrigger(run_date=scheduled_msg.scheduled_time),
            id=f"msg_{scheduled_msg.id}",
            replace_existing=True
        )
    
    async def _execute_scheduled_message(self, message_id: int):
        """Führt eine geplante Nachricht aus (Multi-Gruppen Support)"""
        db = get_session(self.db_engine)
        try:
            scheduled_msg = db.query(ScheduledMessage).filter(
                ScheduledMessage.id == message_id
            ).first()
            
            if not scheduled_msg or scheduled_msg.status != "pending":
                return
            
            # Status auf "running" setzen
            scheduled_msg.status = "running"
            scheduled_msg.started_at = datetime.utcnow()
            db.commit()
            
            # Account und Gruppen laden
            account = db.query(Account).filter(Account.id == scheduled_msg.account_id).first()
            if not account:
                scheduled_msg.status = "failed"
                scheduled_msg.error_message = "Account nicht gefunden"
                db.commit()
                return
            
            # Parse group_ids (JSON)
            try:
                group_ids = json.loads(scheduled_msg.group_ids) if scheduled_msg.group_ids else []
            except (json.JSONDecodeError, TypeError) as e:
                # Fallback für alte Daten (wenn group_ids ein String ist)
                if isinstance(scheduled_msg.group_ids, str) and not scheduled_msg.group_ids.startswith('['):
                    group_ids = [scheduled_msg.group_ids]
                else:
                    group_ids = []
                    logger.error(f"Ungültiges JSON in group_ids für Nachricht {message_id}: {e}")
            
            # Lade Gruppen aus DB
            groups = db.query(Group).filter(Group.id.in_(group_ids)).all()
            group_chat_ids = [g.chat_id for g in groups]
            
            if not group_chat_ids:
                scheduled_msg.status = "failed"
                scheduled_msg.error_message = "Keine gültigen Gruppen gefunden"
                db.commit()
                return
            
            sent = 0
            failed = 0
            
            # Für jede Wiederholung
            for repeat_idx in range(scheduled_msg.repeat_count):
                # Sende an alle Gruppen
                if account.account_type == "bot":
                    # Bot-Versand
                    for group_chat_id in group_chat_ids:
                        # Finde Gruppen-ID
                        target_group = next((g for g in groups if g.chat_id == group_chat_id), None)
                        group_id = target_group.id if target_group else None
                        
                        result = await self.bot_manager.send_message(
                            bot_id=account.id,
                            chat_id=group_chat_id,
                            message=scheduled_msg.message,
                            delay=scheduled_msg.delay if repeat_idx < scheduled_msg.repeat_count - 1 or group_chat_id != group_chat_ids[-1] else 0
                        )
                        
                        # Speichere in DB
                        save_sent_message(
                            db,
                            account_id=account.id,
                            group_id=group_id,
                            group_chat_id=group_chat_id,
                            group_name=target_group.name if target_group else None,
                            message=scheduled_msg.message,
                            success=result.get("success", False),
                            error_message=result.get("error"),
                            telegram_message_id=result.get("telegram_message_id")
                        )
                        
                        if result.get("success"):
                            sent += 1
                        else:
                            failed += 1
                            if result.get("error") == "FloodWait":
                                wait = result.get("wait_seconds", 60)
                                await asyncio.sleep(wait)
                else:
                    # User-Account Versand (Multi-Gruppen)
                    result = await self.account_manager.send_to_multiple_groups(
                        account_id=account.id,
                        group_ids=group_chat_ids,
                        message=scheduled_msg.message,
                        delay=scheduled_msg.delay,
                        group_delay=scheduled_msg.group_delay
                    )
                    
                    # Speichere jede Gruppe einzeln
                    for i, group_chat_id in enumerate(group_chat_ids):
                        target_group = next((g for g in groups if g.chat_id == group_chat_id), None)
                        group_id = target_group.id if target_group else None
                        
                        # Prüfe ob erfolgreich
                        success = i < result.get("success", 0)
                        error = None
                        if not success and result.get("errors"):
                            error_obj = next((e for e in result.get("errors", []) if e.get("group_id") == group_chat_id), None)
                            error = error_obj.get("error") if error_obj else "Unknown error"
                        
                        save_sent_message(
                            db,
                            account_id=account.id,
                            group_id=group_id,
                            group_chat_id=group_chat_id,
                            group_name=target_group.name if target_group else None,
                            message=scheduled_msg.message,
                            success=success,
                            error_message=error
                        )
                    
                    sent += result.get("success", 0)
                    failed += result.get("failed", 0)
                
                # Batch-Pause
                if (repeat_idx + 1) % scheduled_msg.batch_size == 0 and repeat_idx < scheduled_msg.repeat_count - 1:
                    await asyncio.sleep(scheduled_msg.batch_delay)
            
            # Status aktualisieren
            scheduled_msg.status = "completed" if failed == 0 else "failed"
            scheduled_msg.completed_at = datetime.utcnow()
            scheduled_msg.sent_count = sent
            scheduled_msg.failed_count = failed
            if failed > 0:
                scheduled_msg.error_message = f"{failed} Nachrichten fehlgeschlagen"
            
            db.commit()
        
        except Exception as e:
            db.rollback()
            scheduled_msg = db.query(ScheduledMessage).filter(
                ScheduledMessage.id == message_id
            ).first()
            if scheduled_msg:
                scheduled_msg.status = "failed"
                scheduled_msg.error_message = str(e)
                db.commit()
        finally:
            db.close()
            if message_id in self.running_jobs:
                del self.running_jobs[message_id]
    
    def cancel_message(self, message_id: int):
        """Bricht eine geplante Nachricht ab"""
        try:
            self.scheduler.remove_job(f"msg_{message_id}")
        except:
            pass
        
        db = get_session(self.db_engine)
        try:
            scheduled_msg = db.query(ScheduledMessage).filter(
                ScheduledMessage.id == message_id
            ).first()
            if scheduled_msg and scheduled_msg.status == "pending":
                scheduled_msg.status = "cancelled"
                db.commit()
        finally:
            db.close()
    
    async def load_pending_messages(self):
        """Lädt alle ausstehenden Nachrichten und plant sie"""
        db = get_session(self.db_engine)
        try:
            pending = db.query(ScheduledMessage).filter(
                ScheduledMessage.status == "pending",
                ScheduledMessage.scheduled_time > datetime.utcnow()
            ).all()
            
            for msg in pending:
                await self.schedule_message(msg)
        finally:
            db.close()
    
    def shutdown(self):
        """Beendet den Scheduler"""
        self.scheduler.shutdown()

