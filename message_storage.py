"""
Hilfsfunktionen zum Speichern von Nachrichten und Aktualisieren von Statistiken
"""

from database import get_session, SentMessage, AccountStatistic, MessageTemplate, Account, Group
from datetime import datetime


def save_sent_message(
    db,
    account_id: int,
    group_id: int = None,
    group_chat_id: str = None,
    group_name: str = None,
    message: str = "",
    template_id: int = None,
    success: bool = True,
    error_message: str = None,
    telegram_message_id: str = None
):
    """
    Speichert eine gesendete Nachricht in der Datenbank
    
    Args:
        db: Datenbank-Session
        account_id: Account-ID
        group_id: Gruppen-ID (optional)
        group_chat_id: Chat-ID als Backup
        group_name: Gruppenname als Backup
        message: Nachrichtentext
        template_id: ID der verwendeten Vorlage (optional)
        success: Erfolgreich gesendet
        error_message: Fehlermeldung falls fehlgeschlagen
        telegram_message_id: Telegram Message ID
    """
    # Hole Gruppen-Info falls nicht vorhanden
    if group_id and not group_name:
        group = db.query(Group).filter(Group.id == group_id).first()
        if group:
            group_chat_id = group.chat_id
            group_name = group.name
    
    sent_msg = SentMessage(
        account_id=account_id,
        group_id=group_id,
        group_chat_id=group_chat_id,
        group_name=group_name,
        message=message,
        message_template_id=template_id,
        success=success,
        error_message=error_message,
        telegram_message_id=telegram_message_id
    )
    
    db.add(sent_msg)
    
    # Aktualisiere Template-Usage-Count
    if template_id:
        template = db.query(MessageTemplate).filter(MessageTemplate.id == template_id).first()
        if template:
            template.usage_count += 1
    
    # Aktualisiere Account-Statistiken
    stats = db.query(AccountStatistic).filter(AccountStatistic.account_id == account_id).first()
    if not stats:
        stats = AccountStatistic(account_id=account_id)
        db.add(stats)
    
    if success:
        stats.total_messages_sent += 1
        if not stats.first_message_at:
            stats.first_message_at = datetime.utcnow()
        stats.last_message_at = datetime.utcnow()
    else:
        stats.total_messages_failed += 1
    
    # Prüfe ob neue Gruppe (vereinfacht - könnte optimiert werden)
    if group_id:
        # Zähle verschiedene Gruppen aus gesendeten Nachrichten
        unique_groups = db.query(SentMessage.group_id).filter(
            SentMessage.account_id == account_id,
            SentMessage.group_id.isnot(None)
        ).distinct().count()
        stats.total_groups_used = unique_groups
    
    stats.last_updated = datetime.utcnow()
    
    db.commit()


def get_account_statistics(db, account_id: int) -> dict:
    """Gibt Statistiken für einen Account zurück"""
    stats = db.query(AccountStatistic).filter(AccountStatistic.account_id == account_id).first()
    
    if not stats:
        return {
            "total_messages_sent": 0,
            "total_messages_failed": 0,
            "total_groups_used": 0,
            "first_message_at": None,
            "last_message_at": None
        }
    
    return {
        "total_messages_sent": stats.total_messages_sent,
        "total_messages_failed": stats.total_messages_failed,
        "total_groups_used": stats.total_groups_used,
        "first_message_at": stats.first_message_at.isoformat() if stats.first_message_at else None,
        "last_message_at": stats.last_message_at.isoformat() if stats.last_message_at else None
    }

