"""
Account-Manager für mehrere Telegram Accounts
"""

import asyncio
import os
import sqlite3
from typing import Dict, Optional, List
from datetime import datetime
from telethon import TelegramClient
from telethon.errors import FloodWaitError, SessionPasswordNeededError, UserPrivacyRestrictedError, ChatAdminRequiredError
from telethon.tl.types import User, Chat, Channel
from telethon.tl.functions.channels import GetParticipantsRequest, InviteToChannelRequest, GetFullChannelRequest, GetParticipantRequest
from telethon.tl.functions.messages import AddChatUserRequest, GetDialogsRequest, SendReactionRequest, GetHistoryRequest, GetFullChatRequest
from telethon.tl.types import ChannelParticipantsSearch, ReactionEmoji, InputPeerEmpty
from telethon.network.connection import ConnectionTcpMTProxyRandomizedIntermediate
import random
import socks
import re


class AccountManager:
    """Verwaltet mehrere Telegram Accounts"""
    
    def __init__(self):
        self.clients: Dict[int, TelegramClient] = {}
        self.account_info: Dict[int, dict] = {}
    
    def _extract_api_credentials_from_session(self, session_path: str) -> Optional[tuple]:
        """
        Versucht API ID und Hash aus einer Session-Datei zu extrahieren
        
        Args:
            session_path: Pfad zur Session-Datei
            
        Returns:
            Tuple (api_id, api_hash) oder None
        """
        try:
            # Telethon Session-Dateien sind SQLite-Datenbanken
            if not os.path.exists(session_path):
                return None
            
            # Prüfe ob es eine .session Datei ist
            if not session_path.endswith('.session'):
                # Versuche .session hinzuzufügen
                if os.path.exists(session_path + '.session'):
                    session_path = session_path + '.session'
                else:
                    return None
            
            conn = sqlite3.connect(session_path)
            cursor = conn.cursor()
            
            # Prüfe ob Tabelle 'sessions' existiert
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'")
            if not cursor.fetchone():
                conn.close()
                return None
            
            # Versuche API ID und Hash zu lesen
            try:
                cursor.execute("SELECT api_id, api_hash FROM sessions LIMIT 1")
                result = cursor.fetchone()
                conn.close()
                
                if result and result[0] and result[1]:
                    return (str(result[0]), result[1])
            except sqlite3.OperationalError:
                # Spalte existiert möglicherweise nicht
                pass
            
            conn.close()
            return None
        
        except Exception:
            return None
    
    def _get_proxy_config(self, proxy_config: Optional[dict]) -> Optional[dict]:
        """
        Erstellt Proxy-Konfiguration für Telethon
        
        Args:
            proxy_config: Dict mit proxy_type, host, port, username, password, secret
            
        Returns:
            Proxy-Konfiguration für TelegramClient
        """
        if not proxy_config:
            return None
        
        proxy_type = proxy_config.get("proxy_type", "socks5").lower()
        host = proxy_config.get("host")
        port = proxy_config.get("port")
        username = proxy_config.get("username")
        password = proxy_config.get("password")
        secret = proxy_config.get("secret")
        
        if not host or not port:
            return None
        
        if proxy_type == "mtproto":
            # MTProto Proxy
            if secret:
                return {
                    "connection": ConnectionTcpMTProxyRandomizedIntermediate,
                    "proxy": (host, port, secret)
                }
        elif proxy_type in ["socks5", "socks"]:
            # SOCKS5 Proxy
            if username and password:
                return {
                    "proxy": (socks.SOCKS5, host, port, True, username, password)
                }
            else:
                return {
                    "proxy": (socks.SOCKS5, host, port)
                }
        elif proxy_type == "http":
            # HTTP Proxy
            if username and password:
                return {
                    "proxy": (socks.HTTP, host, port, True, username, password)
                }
            else:
                return {
                    "proxy": (socks.HTTP, host, port)
                }
        elif proxy_type == "https":
            # HTTPS Proxy
            if username and password:
                return {
                    "proxy": (socks.HTTP, host, port, True, username, password)
                }
            else:
                return {
                    "proxy": (socks.HTTP, host, port)
                }
        
        return None
    
    async def add_account(
        self, 
        account_id: int,
        api_id: Optional[str] = None,
        api_hash: Optional[str] = None,
        session_name: str = None,
        phone_number: Optional[str] = None,
        code: Optional[str] = None,
        password: Optional[str] = None,
        session_file_path: Optional[str] = None,
        proxy_config: Optional[dict] = None
    ) -> dict:
        """
        Fügt einen Account hinzu und verbindet
        
        Args:
            account_id: Datenbank-ID des Accounts
            api_id: Telegram API ID
            api_hash: Telegram API Hash
            session_name: Session-Dateiname
            phone_number: Telefonnummer (für Login)
            code: Verifizierungscode
            password: 2FA Passwort
            
        Returns:
            Account-Informationen
        """
        try:
            # Proxy-Konfiguration erstellen
            proxy_kwargs = self._get_proxy_config(proxy_config) or {}
            
            # Versuche API Credentials zu bestimmen
            final_api_id = api_id
            final_api_hash = api_hash
            
            # Wenn Session-Datei vorhanden, versuche API Credentials zu extrahieren
            if session_file_path and os.path.exists(session_file_path):
                extracted = self._extract_api_credentials_from_session(session_file_path)
                if extracted:
                    final_api_id, final_api_hash = extracted
            
            # Fallback: Verwende Standard-API-Credentials aus Umgebungsvariablen
            if not final_api_id or not final_api_hash:
                final_api_id = final_api_id or os.getenv('TELEGRAM_API_ID')
                final_api_hash = final_api_hash or os.getenv('TELEGRAM_API_HASH')
            
            # Prüfe ob API Credentials vorhanden sind
            if not final_api_id or not final_api_hash:
                return {
                    "status": "error",
                    "error": "API ID und API Hash erforderlich. Bitte angeben oder in Umgebungsvariablen (TELEGRAM_API_ID, TELEGRAM_API_HASH) setzen."
                }
            
            # Erstelle Client
            # Telethon erwartet den Pfad ohne .session Endung
            # Wenn session_file_path vorhanden ist, verwende diesen (bereits ohne .session)
            if session_file_path and os.path.exists(session_file_path + '.session'):
                # session_file_path ist bereits ohne .session (z.B. "sessions/27608217417_20251112")
                # Telethon fügt automatisch .session hinzu
                client = TelegramClient(session_file_path, int(final_api_id), final_api_hash, **proxy_kwargs)
            elif session_file_path:
                # Versuche absoluten Pfad
                abs_path = os.path.abspath(session_file_path)
                if os.path.exists(abs_path + '.session'):
                    client = TelegramClient(abs_path, int(final_api_id), final_api_hash, **proxy_kwargs)
                else:
                    # Fallback: Verwende session_name
                    client = TelegramClient(session_name, int(final_api_id), final_api_hash, **proxy_kwargs)
            else:
                client = TelegramClient(session_name, int(final_api_id), final_api_hash, **proxy_kwargs)
            
            # Versuche zu verbinden
            if not client.is_connected():
                await client.connect()
            
            # Prüfe ob User bereits autorisiert ist
            is_authorized = await client.is_user_authorized()
            me = None
            
            if is_authorized:
                # Bereits autorisiert - hole User-Info
                try:
                    me = await client.get_me()
                except Exception as e:
                    # Fehler beim Abrufen der User-Info
                    await client.disconnect()
                    return {
                        "status": "error",
                        "error": f"Fehler beim Abrufen der User-Info: {str(e)}"
                    }
            else:
                # Nicht autorisiert - Login erforderlich
                if not phone_number:
                    await client.disconnect()
                    return {
                        "status": "error",
                        "error": "Telefonnummer erforderlich für neuen Account"
                    }
                
                # Sende Code-Anfrage wenn noch kein Code vorhanden
                if not code:
                    try:
                        await client.send_code_request(phone_number)
                        return {"status": "code_required", "account_id": account_id}
                    except Exception as e:
                        await client.disconnect()
                        return {
                            "status": "error",
                            "error": f"Fehler beim Anfordern des Codes: {str(e)}"
                        }
                
                # Login mit Code
                try:
                    await client.sign_in(phone_number, code)
                    me = await client.get_me()
                except SessionPasswordNeededError:
                    # 2FA erforderlich
                    if not password:
                        return {"status": "password_required", "account_id": account_id}
                    try:
                        await client.sign_in(password=password)
                        me = await client.get_me()
                    except Exception as e:
                        await client.disconnect()
                        return {
                            "status": "error",
                            "error": f"Fehler bei 2FA: {str(e)}"
                        }
                except Exception as e:
                    await client.disconnect()
                    return {
                        "status": "error",
                        "error": f"Fehler beim Login: {str(e)}"
                    }
            
            # Account ist jetzt verbunden und autorisiert
            
            if not me:
                await client.disconnect()
                return {
                    "status": "error",
                    "account_id": account_id,
                    "error": "Konnte User-Info nicht abrufen"
                }
            self.clients[account_id] = client
            self.account_info[account_id] = {
                "id": account_id,
                "first_name": me.first_name,
                "last_name": me.last_name,
                "username": me.username,
                "phone": me.phone,
                "connected_at": datetime.utcnow().isoformat()
            }
            
            return {
                "status": "connected",
                "account_id": account_id,
                "info": self.account_info[account_id]
            }
        
        except Exception as e:
            return {
                "status": "error",
                "account_id": account_id,
                "error": str(e)
            }
    
    async def remove_account(self, account_id: int):
        """Entfernt einen Account"""
        if account_id in self.clients:
            await self.clients[account_id].disconnect()
            del self.clients[account_id]
        if account_id in self.account_info:
            del self.account_info[account_id]
    
    async def get_account_info(self, account_id: int) -> Optional[dict]:
        """Gibt Account-Informationen zurück"""
        return self.account_info.get(account_id)
    
    async def list_accounts(self) -> List[dict]:
        """Listet alle verbundenen Accounts"""
        return list(self.account_info.values())
    
    async def send_message(
        self,
        account_id: int,
        entity: str,
        message: str,
        delay: float = 1.0
    ) -> dict:
        """
        Sendet eine Nachricht über einen Account
        
        Args:
            account_id: Account-ID
            entity: Chat-ID, Username oder Telefonnummer
            message: Nachrichtentext
            delay: Verzögerung nach dem Senden
            
        Returns:
            Ergebnis-Dict
        """
        if account_id not in self.clients:
            return {"success": False, "error": "Account not connected"}
        
        client = self.clients[account_id]
        
        try:
            await client.send_message(entity, message)
            if delay > 0:
                await asyncio.sleep(delay)
            return {"success": True, "sent_at": datetime.utcnow().isoformat()}
        
        except FloodWaitError as e:
            return {
                "success": False,
                "error": "FloodWait",
                "wait_seconds": e.seconds
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_dialogs(self, account_id: int) -> List[dict]:
        """
        Ruft alle Dialoge (Chats/Gruppen) eines Accounts ab
        
        Args:
            account_id: Account-ID
            
        Returns:
            Liste von Dialogen
        """
        if account_id not in self.clients:
            return []
        
        client = self.clients[account_id]
        dialogs = []
        
        try:
            async for dialog in client.iter_dialogs():
                entity = dialog.entity
                
                dialog_info = {
                    "id": dialog.id,
                    "name": dialog.name,
                    "type": "unknown"
                }
                
                if isinstance(entity, User):
                    dialog_info["type"] = "private"
                    dialog_info["username"] = entity.username
                    dialog_info["phone"] = entity.phone
                elif isinstance(entity, Chat):
                    dialog_info["type"] = "group"
                elif isinstance(entity, Channel):
                    dialog_info["type"] = "channel" if entity.broadcast else "supergroup"
                    dialog_info["username"] = entity.username
                
                dialogs.append(dialog_info)
        
        except Exception as e:
            print(f"Fehler beim Abrufen der Dialoge: {e}")
        
        return dialogs
    
    async def send_to_multiple_groups(
        self,
        account_id: int,
        group_ids: List[str],
        message: str,
        delay: float = 1.0,
        group_delay: float = 2.0
    ) -> dict:
        """
        Sendet eine Nachricht an mehrere Gruppen
        
        Args:
            account_id: Account-ID
            group_ids: Liste von Chat-IDs
            message: Nachrichtentext
            delay: Verzögerung zwischen Nachrichten in derselben Gruppe
            group_delay: Verzögerung zwischen verschiedenen Gruppen
            
        Returns:
            Ergebnis-Dict mit Statistiken
        """
        if account_id not in self.clients:
            return {"success": False, "error": "Account not connected"}
        
        client = self.clients[account_id]
        results = {
            "total": len(group_ids),
            "success": 0,
            "failed": 0,
            "errors": []
        }
        
        for i, group_id in enumerate(group_ids):
            try:
                await client.send_message(group_id, message)
                results["success"] += 1
                
                if delay > 0 and i < len(group_ids) - 1:
                    await asyncio.sleep(delay)
            
            except FloodWaitError as e:
                results["failed"] += 1
                results["errors"].append({
                    "group_id": group_id,
                    "error": f"FloodWait: {e.seconds}s"
                })
                await asyncio.sleep(e.seconds)
            
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "group_id": group_id,
                    "error": str(e)
                })
            
            # Pause zwischen Gruppen (außer bei der letzten)
            if i < len(group_ids) - 1:
                await asyncio.sleep(group_delay)
        
        return results
    
    async def scrape_group_members(
        self,
        account_id: int,
        group_entity: str,
        limit: int = 10000
    ) -> List[dict]:
        """
        Scrapt Mitglieder aus einer Gruppe oder einem Kanal
        
        Args:
            account_id: Account-ID
            group_entity: Chat-ID, Username oder Entity
            limit: Maximale Anzahl zu scrapender User
            
        Returns:
            Liste von User-Informationen
        """
        if account_id not in self.clients:
            return []
        
        client = self.clients[account_id]
        members = []
        
        try:
            # Hole Entity
            entity = await client.get_entity(group_entity)
            
            # Prüfe ob es eine Gruppe/Kanal ist
            if not isinstance(entity, (Chat, Channel)):
                return []
            
            # Scrape Mitglieder
            offset = 0
            batch_size = 200
            
            while len(members) < limit:
                try:
                    participants = await client.get_participants(
                        entity,
                        limit=batch_size,
                        offset=offset,
                        aggressive=True
                    )
                    
                    if not participants:
                        break
                    
                    for participant in participants:
                        if isinstance(participant, User) and not participant.bot:
                            member_info = {
                                "user_id": str(participant.id),
                                "username": participant.username,
                                "first_name": participant.first_name,
                                "last_name": participant.last_name,
                                "phone": participant.phone,
                                "is_premium": getattr(participant, 'premium', False),
                                "access_hash": str(participant.access_hash) if hasattr(participant, 'access_hash') else None
                            }
                            members.append(member_info)
                            
                            if len(members) >= limit:
                                break
                    
                    offset += len(participants)
                    
                    # Rate Limiting
                    await asyncio.sleep(1)
                    
                    if len(participants) < batch_size:
                        break
                        
                except FloodWaitError as e:
                    await asyncio.sleep(e.seconds)
                except Exception as e:
                    print(f"Fehler beim Scrapen: {e}")
                    break
        
        except Exception as e:
            print(f"Fehler beim Scrapen der Gruppe: {e}")
        
        return members
    
    async def invite_users_to_group(
        self,
        account_id: int,
        group_entity: str,
        user_ids: List[str],
        delay: float = 2.0
    ) -> dict:
        """
        Lädt User zu einer Gruppe ein (als Admin)
        
        Args:
            account_id: Account-ID (muss Admin sein)
            group_entity: Chat-ID oder Username der Gruppe
            user_ids: Liste von User-IDs oder Usernames
            delay: Verzögerung zwischen Einladungen
            
        Returns:
            Ergebnis-Dict mit Statistiken
        """
        if account_id not in self.clients:
            return {"success": False, "error": "Account not connected"}
        
        client = self.clients[account_id]
        results = {
            "total": len(user_ids),
            "success": 0,
            "failed": 0,
            "errors": []
        }
        
        try:
            entity = await client.get_entity(group_entity)
            
            for i, user_id in enumerate(user_ids):
                try:
                    # Versuche User zu laden
                    try:
                        user_entity = await client.get_entity(user_id)
                    except:
                        results["failed"] += 1
                        results["errors"].append({
                            "user_id": user_id,
                            "error": "User nicht gefunden"
                        })
                        continue
                    
                    # Lade User zur Gruppe ein
                    if isinstance(entity, Channel):
                        # Für Kanäle/Supergruppen
                        await client(InviteToChannelRequest(
                            channel=entity,
                            users=[user_entity]
                        ))
                    else:
                        # Für normale Gruppen
                        await client(AddChatUserRequest(
                            chat_id=entity.id,
                            user_id=user_entity,
                            fwd_limit=10
                        ))
                    
                    results["success"] += 1
                    
                    # Rate Limiting
                    if i < len(user_ids) - 1:
                        await asyncio.sleep(delay)
                
                except FloodWaitError as e:
                    results["failed"] += 1
                    results["errors"].append({
                        "user_id": user_id,
                        "error": f"FloodWait: {e.seconds}s"
                    })
                    await asyncio.sleep(e.seconds)
                
                except UserPrivacyRestrictedError:
                    results["failed"] += 1
                    results["errors"].append({
                        "user_id": user_id,
                        "error": "User hat Privatsphäre-Einstellungen aktiviert"
                    })
                
                except ChatAdminRequiredError:
                    results["failed"] += 1
                    results["errors"].append({
                        "user_id": user_id,
                        "error": "Account ist kein Admin"
                    })
                    break  # Stoppe wenn kein Admin
                
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append({
                        "user_id": user_id,
                        "error": str(e)
                    })
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        
        return results
    
    async def add_account_to_groups(
        self,
        account_id: int,
        group_entities: List[str],
        delay: float = 3.0
    ) -> dict:
        """
        Fügt einen Account zu mehreren Gruppen hinzu
        
        Args:
            account_id: Account-ID des Accounts, der zu Gruppen hinzugefügt werden soll
            group_entities: Liste von Gruppen (Chat-ID, Username oder Entity)
            delay: Verzögerung zwischen Gruppen-Einladungen
            
        Returns:
            Dict mit Erfolgs- und Fehlerstatistiken
        """
        if account_id not in self.clients:
            return {
                "success": False,
                "error": "Account nicht verbunden"
            }
        
        client = self.clients[account_id]
        
        results = {
            "success": True,
            "total": len(group_entities),
            "added": 0,
            "failed": 0,
            "errors": []
        }
        
        for i, group_entity in enumerate(group_entities):
            try:
                # Versuche Gruppe zu laden
                entity = await client.get_entity(group_entity)
                
                # Prüfe ob Account bereits in Gruppe ist
                try:
                    me = await client.get_me()
                    # Versuche Teilnehmer-Info abzurufen
                    if isinstance(entity, Channel):
                        await client(GetParticipantRequest(entity, me))
                    # Wenn erfolgreich, ist Account bereits Mitglied
                    results["added"] += 1
                    results["errors"].append({
                        "group": group_entity,
                        "status": "already_member",
                        "message": "Account ist bereits Mitglied"
                    })
                    continue
                except:
                    # Account ist nicht in Gruppe, versuche beizutreten
                    pass
                
                # Versuche beizutreten
                if isinstance(entity, Channel):
                    # Für Kanäle/Supergruppen
                    await client(InviteToChannelRequest(
                        channel=entity,
                        users=[await client.get_me()]
                    ))
                else:
                    # Für normale Gruppen - versuche über Einladungslink oder direkt
                    try:
                        # Versuche direkt beizutreten (falls öffentlich)
                        await client(AddChatUserRequest(
                            chat_id=entity.id,
                            user_id=await client.get_me(),
                            fwd_limit=10
                        ))
                    except:
                        # Falls nicht möglich, versuche über Username
                        if hasattr(entity, 'username') and entity.username:
                            await client(AddChatUserRequest(
                                chat_id=entity.username,
                                user_id=await client.get_me(),
                                fwd_limit=10
                            ))
                
                results["added"] += 1
                
                # Rate Limiting
                if i < len(group_entities) - 1:
                    await asyncio.sleep(delay)
            
            except FloodWaitError as e:
                results["failed"] += 1
                results["errors"].append({
                    "group": group_entity,
                    "status": "flood_wait",
                    "error": f"FloodWait: {e.seconds}s"
                })
                await asyncio.sleep(e.seconds)
            
            except UserPrivacyRestrictedError:
                results["failed"] += 1
                results["errors"].append({
                    "group": group_entity,
                    "status": "privacy_restricted",
                    "error": "Gruppe hat Privatsphäre-Einstellungen aktiviert"
                })
            
            except ChatAdminRequiredError:
                results["failed"] += 1
                results["errors"].append({
                    "group": group_entity,
                    "status": "admin_required",
                    "error": "Account muss Admin sein oder Einladungslink verwenden"
                })
            
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "group": group_entity,
                    "status": "error",
                    "error": str(e)
                })
        
        return results
    
    async def forward_message(
        self,
        account_id: int,
        source_group: str,
        message_ids: List[int],
        target_groups: List[str],
        delay: float = 2.0
    ) -> dict:
        """
        Leitet Nachrichten per Message-ID weiter
        
        Args:
            account_id: Account-ID
            source_group: Quell-Gruppe (Chat-ID oder Username)
            message_ids: Liste von Message-IDs zum Weiterleiten
            target_groups: Liste von Ziel-Gruppen
            delay: Verzögerung zwischen Weiterleitungen
            
        Returns:
            Ergebnis-Dict mit Statistiken
        """
        if account_id not in self.clients:
            return {"success": False, "error": "Account not connected"}
        
        client = self.clients[account_id]
        results = {
            "total_messages": len(message_ids),
            "total_targets": len(target_groups),
            "success": 0,
            "failed": 0,
            "errors": []
        }
        
        try:
            # Hole Quell-Entity
            source_entity = await client.get_entity(source_group)
            
            for target_group in target_groups:
                try:
                    target_entity = await client.get_entity(target_group)
                    
                    # Leite alle Nachrichten weiter (als Liste für bessere Performance)
                    try:
                        await client.forward_messages(
                            entity=target_entity,
                            messages=message_ids,
                            from_peer=source_entity
                        )
                        results["success"] += len(message_ids)
                        
                        # Rate Limiting zwischen Ziel-Gruppen
                        if target_group != target_groups[-1]:
                            await asyncio.sleep(delay)
                    
                    except FloodWaitError as e:
                        results["failed"] += len(message_ids)
                        results["errors"].append({
                            "target": target_group,
                            "error": f"FloodWait: {e.seconds}s"
                        })
                        await asyncio.sleep(e.seconds)
                    
                    except Exception as e:
                        results["failed"] += len(message_ids)
                        results["errors"].append({
                            "target": target_group,
                            "error": str(e)
                        })
                
                except Exception as e:
                    results["failed"] += len(message_ids)
                    results["errors"].append({
                        "target": target_group,
                        "error": f"Gruppe nicht gefunden: {str(e)}"
                    })
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        
        return results
    
    async def get_group_messages(
        self,
        account_id: int,
        group_entity: str,
        limit: int = 100
    ) -> List[dict]:
        """
        Ruft Nachrichten aus einer Gruppe ab
        
        Args:
            account_id: Account-ID
            group_entity: Chat-ID oder Username
            limit: Maximale Anzahl Nachrichten
            
        Returns:
            Liste von Nachrichten mit IDs und Metadaten
        """
        if account_id not in self.clients:
            return []
        
        client = self.clients[account_id]
        messages = []
        
        try:
            entity = await client.get_entity(group_entity)
            
            async for message in client.iter_messages(entity, limit=limit):
                msg_info = {
                    "id": message.id,
                    "date": message.date.isoformat() if message.date else None,
                    "text": message.text or "",
                    "from_id": str(message.from_id.user_id) if message.from_id and hasattr(message.from_id, 'user_id') else None,
                    "is_reply": message.is_reply,
                    "is_forward": message.forward is not None,
                    "media": message.media is not None
                }
                messages.append(msg_info)
        
        except Exception as e:
            print(f"Fehler beim Abrufen der Nachrichten: {e}")
        
        return messages
    
    async def warm_account_read_messages(
        self,
        account_id: int,
        group_entity: str,
        limit: int = 10
    ) -> dict:
        """
        Liest Nachrichten in einer Gruppe (simuliert Lesen)
        
        Args:
            account_id: Account-ID
            group_entity: Chat-ID oder Username
            limit: Anzahl zu lesender Nachrichten
            
        Returns:
            Ergebnis-Dict
        """
        if account_id not in self.clients:
            return {"success": False, "error": "Account not connected"}
        
        client = self.clients[account_id]
        
        try:
            entity = await client.get_entity(group_entity)
            
            # Lese Nachrichten (ohne sie zu markieren)
            count = 0
            async for message in client.iter_messages(entity, limit=limit):
                # Simuliere Lesen durch kurze Pause
                await asyncio.sleep(random.uniform(0.5, 2.0))
                count += 1
            
            return {
                "success": True,
                "read_count": count,
                "group": group_entity
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def warm_account_scroll_dialogs(
        self,
        account_id: int,
        limit: int = 20
    ) -> dict:
        """
        Scrollt durch Dialoge (simuliert Chat-Öffnen)
        
        Args:
            account_id: Account-ID
            limit: Anzahl zu durchsuchender Dialoge
            
        Returns:
            Ergebnis-Dict
        """
        if account_id not in self.clients:
            return {"success": False, "error": "Account not connected"}
        
        client = self.clients[account_id]
        
        try:
            count = 0
            async for dialog in client.iter_dialogs(limit=limit):
                # Simuliere Chat-Öffnen durch kurze Pause
                await asyncio.sleep(random.uniform(1.0, 3.0))
                count += 1
            
            return {
                "success": True,
                "scrolled_count": count
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def warm_account_send_reaction(
        self,
        account_id: int,
        group_entity: str,
        message_id: int,
        reaction: str = "👍"
    ) -> dict:
        """
        Sendet eine Reaktion auf eine Nachricht
        
        Args:
            account_id: Account-ID
            group_entity: Chat-ID oder Username
            message_id: Message-ID
            reaction: Reaktions-Emoji (👍, ❤️, 😂, etc.)
            
        Returns:
            Ergebnis-Dict
        """
        if account_id not in self.clients:
            return {"success": False, "error": "Account not connected"}
        
        client = self.clients[account_id]
        
        try:
            entity = await client.get_entity(group_entity)
            
            # Sende Reaktion
            await client.send_reaction(
                entity=entity,
                message=message_id,
                reaction=ReactionEmoji(emoticon=reaction)
            )
            
            return {
                "success": True,
                "message_id": message_id,
                "reaction": reaction
            }
        
        except FloodWaitError as e:
            return {
                "success": False,
                "error": f"FloodWait: {e.seconds}s",
                "wait_seconds": e.seconds
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def warm_account_send_small_message(
        self,
        account_id: int,
        group_entity: str,
        message: str
    ) -> dict:
        """
        Sendet eine kleine Nachricht (für Warming)
        
        Args:
            account_id: Account-ID
            group_entity: Chat-ID oder Username
            message: Nachrichtentext
            
        Returns:
            Ergebnis-Dict
        """
        if account_id not in self.clients:
            return {"success": False, "error": "Account not connected"}
        
        client = self.clients[account_id]
        
        try:
            entity = await client.get_entity(group_entity)
            
            await client.send_message(entity, message)
            
            return {
                "success": True,
                "message": message
            }
        
        except FloodWaitError as e:
            return {
                "success": False,
                "error": f"FloodWait: {e.seconds}s",
                "wait_seconds": e.seconds
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def check_group_exists(
        self,
        account_id: int,
        group_entity: str
    ) -> dict:
        """
        Prüft ob eine Gruppe existiert und gibt Informationen zurück
        
        Args:
            account_id: Account-ID
            group_entity: Chat-ID, Username oder Entity
            
        Returns:
            Dict mit Gruppen-Informationen
        """
        if account_id not in self.clients:
            return {
                "exists": False,
                "error": "Account nicht verbunden"
            }
        
        client = self.clients[account_id]
        
        try:
            entity = await client.get_entity(group_entity)
            
            group_info = {
                "exists": True,
                "id": entity.id,
                "title": getattr(entity, "title", None) or getattr(entity, "first_name", None),
                "username": getattr(entity, "username", None),
                "type": "unknown"
            }
            
            if isinstance(entity, Chat):
                group_info["type"] = "group"
                group_info["members_count"] = getattr(entity, "participants_count", None)
            elif isinstance(entity, Channel):
                group_info["type"] = "channel" if entity.broadcast else "supergroup"
                group_info["members_count"] = getattr(entity, "participants_count", None)
                group_info["access_hash"] = entity.access_hash
            elif isinstance(entity, User):
                group_info["type"] = "private"
                group_info["error"] = "Dies ist ein privater Chat, keine Gruppe"
            
            return group_info
        
        except ValueError as e:
            return {
                "exists": False,
                "error": f"Gruppe nicht gefunden: {str(e)}"
            }
        except Exception as e:
            return {
                "exists": False,
                "error": str(e)
            }
    
    async def check_bot_can_be_added(
        self,
        account_id: int,
        group_entity: str,
        bot_username: Optional[str] = None,
        bot_id: Optional[int] = None
    ) -> dict:
        """
        Prüft ob ein Bot zu einer Gruppe hinzugefügt werden kann
        
        Args:
            account_id: Account-ID (muss Admin sein)
            group_entity: Chat-ID oder Username der Gruppe
            bot_username: Bot-Username (z.B. "@mybot")
            bot_id: Bot-ID (alternativ zu username)
            
        Returns:
            Dict mit Prüf-Ergebnissen
        """
        if account_id not in self.clients:
            return {
                "can_add": False,
                "error": "Account nicht verbunden"
            }
        
        client = self.clients[account_id]
        result = {
            "can_add": False,
            "group_exists": False,
            "is_admin": False,
            "bot_exists": False,
            "bot_already_in_group": False,
            "bot_adding_allowed": True,
            "errors": []
        }
        
        try:
            # Schritt 1: Prüfe ob Gruppe existiert
            try:
                entity = await client.get_entity(group_entity)
                result["group_exists"] = True
                result["group_id"] = entity.id
                result["group_title"] = getattr(entity, "title", None)
            except Exception as e:
                result["errors"].append(f"Gruppe nicht gefunden: {str(e)}")
                return result
            
            # Schritt 2: Prüfe ob Account Admin ist
            try:
                if isinstance(entity, Channel):
                    # Für Supergruppen/Kanäle
                    participant = await client(GetParticipantRequest(
                        channel=entity,
                        participant=await client.get_me()
                    ))
                    
                    # Prüfe Admin-Rechte
                    if hasattr(participant, "participant"):
                        participant_obj = participant.participant
                        if hasattr(participant_obj, "admin_rights"):
                            result["is_admin"] = True
                            result["admin_rights"] = {
                                "add_admins": getattr(participant_obj.admin_rights, "add_admins", False),
                                "invite_users": getattr(participant_obj.admin_rights, "invite_users", False),
                                "ban_users": getattr(participant_obj.admin_rights, "ban_users", False)
                            }
                elif isinstance(entity, Chat):
                    # Für normale Gruppen
                    full_chat = await client(GetFullChatRequest(entity.id))
                    if hasattr(full_chat, "full_chat"):
                        chat = full_chat.full_chat
                        # Prüfe ob User Admin ist
                        me = await client.get_me()
                        if hasattr(chat, "participants"):
                            for participant in chat.participants.participants:
                                if participant.user_id == me.id:
                                    if hasattr(participant, "admin_rights"):
                                        result["is_admin"] = True
                                        break
            except Exception as e:
                result["errors"].append(f"Fehler beim Prüfen der Admin-Rechte: {str(e)}")
            
            # Schritt 3: Prüfe ob Bot existiert
            if bot_username or bot_id:
                try:
                    if bot_username:
                        bot_entity = await client.get_entity(bot_username)
                    else:
                        bot_entity = await client.get_entity(bot_id)
                    
                    result["bot_exists"] = True
                    result["bot_id"] = bot_entity.id
                    result["bot_username"] = getattr(bot_entity, "username", None)
                    
                    # Prüfe ob Bot bereits in Gruppe ist
                    try:
                        if isinstance(entity, Channel):
                            participant = await client(GetParticipantRequest(
                                channel=entity,
                                participant=bot_entity
                            ))
                            result["bot_already_in_group"] = True
                        elif isinstance(entity, Chat):
                            full_chat = await client(GetFullChatRequest(entity.id))
                            if hasattr(full_chat, "full_chat") and hasattr(full_chat.full_chat, "participants"):
                                for participant in full_chat.full_chat.participants.participants:
                                    if participant.user_id == bot_entity.id:
                                        result["bot_already_in_group"] = True
                                        break
                    except:
                        # Bot ist nicht in Gruppe
                        result["bot_already_in_group"] = False
                
                except Exception as e:
                    result["errors"].append(f"Bot nicht gefunden: {str(e)}")
            
            # Schritt 4: Finale Prüfung
            if result["group_exists"] and result["is_admin"]:
                if bot_username or bot_id:
                    if result["bot_exists"] and not result["bot_already_in_group"]:
                        result["can_add"] = True
                    elif result["bot_already_in_group"]:
                        result["errors"].append("Bot ist bereits in der Gruppe")
                else:
                    # Kein spezifischer Bot angegeben, prüfe nur ob Bots generell hinzugefügt werden können
                    result["can_add"] = True
                    result["message"] = "Account ist Admin, Bots können hinzugefügt werden"
            
            return result
        
        except FloodWaitError as e:
            return {
                "can_add": False,
                "error": f"FloodWait: {e.seconds} Sekunden warten",
                "wait_seconds": e.seconds
            }
        except Exception as e:
            return {
                "can_add": False,
                "error": str(e),
                "errors": [str(e)]
            }
    
    async def disconnect_all(self):
        """Trennt alle Verbindungen"""
        for account_id in list(self.clients.keys()):
            await self.remove_account(account_id)
    
    async def create_bot_via_botfather(
        self,
        account_id: int,
        bot_name: str,
        bot_username: str,
        timeout: float = 30.0
    ) -> dict:
        """
        Erstellt einen neuen Bot über BotFather
        
        Args:
            account_id: Account-ID des User-Accounts
            bot_name: Name des Bots (z.B. "Mein Bot")
            bot_username: Username des Bots (muss mit "bot" enden, z.B. "mein_bot")
            timeout: Timeout für Antworten von BotFather (Sekunden)
            
        Returns:
            Dict mit Bot-Token und Informationen
        """
        if account_id not in self.clients:
            return {
                "success": False,
                "error": "Account nicht verbunden"
            }
        
        client = self.clients[account_id]
        botfather_username = "BotFather"
        
        try:
            # Hole BotFather Entity
            botfather = await client.get_entity(botfather_username)
            
            # Schritt 1: Sende /newbot Befehl
            await client.send_message(botfather, "/newbot")
            await asyncio.sleep(2)  # Warte auf Antwort
            
            # Schritt 2: Sende Bot-Namen
            await client.send_message(botfather, bot_name)
            await asyncio.sleep(2)  # Warte auf Antwort
            
            # Schritt 3: Sende Bot-Username
            # Stelle sicher, dass Username mit "bot" endet
            if not bot_username.lower().endswith("bot"):
                bot_username = bot_username.lower().rstrip("bot") + "bot"
            
            await client.send_message(botfather, bot_username)
            await asyncio.sleep(3)  # Warte auf Token
            
            # Schritt 4: Hole letzte Nachrichten von BotFather
            messages = await client.get_messages(botfather, limit=5)
            
            # Suche nach Bot-Token in den Nachrichten
            bot_token = None
            bot_info = {}
            
            for msg in messages:
                if msg.text:
                    # Token-Pattern: "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
                    token_pattern = r'(\d{8,10}:[A-Za-z0-9_-]{35})'
                    match = re.search(token_pattern, msg.text)
                    if match:
                        bot_token = match.group(1)
                        
                        # Extrahiere Bot-Info aus der Nachricht
                        if "Congratulations" in msg.text or "Done!" in msg.text:
                            # Versuche Bot-Username und Name zu extrahieren
                            username_match = re.search(r'@(\w+)', msg.text)
                            if username_match:
                                bot_info["username"] = username_match.group(1)
                            
                            name_match = re.search(r'"(.*?)"', msg.text)
                            if name_match:
                                bot_info["name"] = name_match.group(1)
                        
                        break
            
            if not bot_token:
                # Fallback: Versuche Token aus anderen Nachrichten zu extrahieren
                for msg in messages:
                    if msg.text and "token" in msg.text.lower():
                        token_pattern = r'(\d{8,10}:[A-Za-z0-9_-]{35})'
                        match = re.search(token_pattern, msg.text)
                        if match:
                            bot_token = match.group(1)
                            break
            
            if bot_token:
                return {
                    "success": True,
                    "bot_token": bot_token,
                    "bot_name": bot_name,
                    "bot_username": bot_username,
                    "info": bot_info,
                    "message": "Bot erfolgreich erstellt"
                }
            else:
                # Versuche Fehler aus Nachrichten zu extrahieren
                error_msg = "Bot-Token nicht gefunden"
                for msg in messages:
                    if msg.text and ("error" in msg.text.lower() or "sorry" in msg.text.lower()):
                        error_msg = msg.text[:200]  # Erste 200 Zeichen
                        break
                
                return {
                    "success": False,
                    "error": error_msg,
                    "bot_name": bot_name,
                    "bot_username": bot_username
                }
        
        except FloodWaitError as e:
            return {
                "success": False,
                "error": f"FloodWait: {e.seconds} Sekunden warten",
                "wait_seconds": e.seconds
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

