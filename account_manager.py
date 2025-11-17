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
from telethon.tl.functions.messages import AddChatUserRequest, GetDialogsRequest, SendReactionRequest, GetHistoryRequest, GetFullChatRequest, ImportChatInviteRequest, SendMessageRequest, ExportChatInviteRequest
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
        proxy_config: Optional[dict] = None,
        phone_code_hash: Optional[str] = None
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
                
                # Normalisiere Telefonnummer (entferne Leerzeichen, behalte +)
                phone_number = phone_number.strip().replace(" ", "").replace("-", "")
                if not phone_number.startswith("+"):
                    # Wenn keine Ländervorwahl vorhanden, füge + hinzu (Standard: Deutschland)
                    if not phone_number.startswith("00"):
                        phone_number = "+" + phone_number
                    else:
                        phone_number = "+" + phone_number[2:]
                
                # Sende Code-Anfrage wenn noch kein Code vorhanden
                # force_sms=False: Versuche Code über Telegram-App zu senden (nicht per SMS)
                if not code:
                    try:
                        # Prüfe ob Client verbunden ist
                        if not client.is_connected():
                            await client.connect()
                        
                        print(f"[DEBUG] Fordere Code an für Telefonnummer: {phone_number}")
                        print(f"[DEBUG] API ID: {final_api_id}, API Hash vorhanden: {bool(final_api_hash)}")
                        
                        # Versuche Code über Telegram-App zu senden (nicht per SMS)
                        sent_code = await client.send_code_request(phone_number, force_sms=False)
                        
                        print(f"[DEBUG] Code-Anfrage erfolgreich. Type: {sent_code.type if hasattr(sent_code, 'type') else 'unknown'}")
                        
                        # Prüfe ob Code über Telegram gesendet wurde
                        code_type = sent_code.type.__class__.__name__ if hasattr(sent_code, 'type') else 'unknown'
                        phone_code_hash = sent_code.phone_code_hash if hasattr(sent_code, 'phone_code_hash') else None
                        
                        # Prüfe den tatsächlichen Typ
                        if hasattr(sent_code, 'type'):
                            if hasattr(sent_code.type, 'pattern'):
                                # Code wurde über Telegram-App gesendet
                                code_type = "telegram_app"
                                message = "✅ Code wurde über Telegram gesendet. Prüfe deine Telegram-App!"
                            elif hasattr(sent_code.type, 'length'):
                                # Code wurde per SMS gesendet
                                code_type = "sms"
                                message = "⚠️ Code wurde per SMS gesendet (Telegram-Versand nicht möglich)."
                            else:
                                message = "✅ Code wurde angefordert. Prüfe Telegram oder SMS!"
                        else:
                            message = "✅ Code wurde angefordert. Prüfe Telegram oder SMS!"
                        
                        # WICHTIG: Session speichern, damit phone_code_hash erhalten bleibt
                        # Telethon speichert den Hash automatisch in der Session
                        try:
                            await client.disconnect()
                        except:
                            pass
                        
                        return {
                            "status": "code_required", 
                            "account_id": account_id,
                            "code_type": code_type,
                            "phone_code_hash": phone_code_hash,
                            "message": message
                        }
                    except Exception as e:
                        error_msg = str(e)
                        error_type = type(e).__name__
                        print(f"[ERROR] Fehler beim Anfordern des Codes über Telegram: {error_type}: {error_msg}")
                        
                        # Wenn Telegram-Versand fehlschlägt, versuche SMS als Fallback
                        try:
                            print(f"[DEBUG] Versuche SMS-Fallback für: {phone_number}")
                            sent_code = await client.send_code_request(phone_number, force_sms=True)
                            print(f"[DEBUG] SMS-Code-Anfrage erfolgreich")
                            sms_phone_code_hash = sent_code.phone_code_hash if hasattr(sent_code, 'phone_code_hash') else None
                            # Session speichern
                            try:
                                await client.disconnect()
                            except:
                                pass
                            
                            return {
                                "status": "code_required",
                                "account_id": account_id,
                                "code_type": "sms",
                                "phone_code_hash": sms_phone_code_hash,
                                "message": "⚠️ Code wurde per SMS gesendet (Telegram-Versand nicht möglich)."
                            }
                        except Exception as sms_error:
                            sms_error_type = type(sms_error).__name__
                            sms_error_msg = str(sms_error)
                            print(f"[ERROR] SMS-Fallback fehlgeschlagen: {sms_error_type}: {sms_error_msg}")
                            await client.disconnect()
                            return {
                                "status": "error",
                                "error": f"Fehler beim Anfordern des Codes: {error_type}: {error_msg}. SMS-Fallback fehlgeschlagen: {sms_error_type}: {sms_error_msg}"
                            }
                
                # Login mit Code
                try:
                    # WICHTIG: Telethon speichert phone_code_hash automatisch in der Session
                    # Wenn phone_code_hash explizit übergeben wird, verwende ihn
                    # Ansonsten liest Telethon ihn automatisch aus der Session
                    if phone_code_hash:
                        print(f"[DEBUG] Verwende expliziten phone_code_hash: {phone_code_hash[:10]}...")
                        await client.sign_in(phone_number, code, phone_code_hash=phone_code_hash)
                    else:
                        # Telethon sollte den Hash automatisch aus der Session lesen
                        # Falls nicht, versuche ohne Hash (Telethon liest ihn aus der Session)
                        print(f"[DEBUG] Versuche Login ohne expliziten Hash (Telethon liest aus Session)")
                        try:
                            await client.sign_in(phone_number, code)
                        except Exception as sign_in_error:
                            # Falls das fehlschlägt, könnte der Hash fehlen
                            error_msg = str(sign_in_error)
                            print(f"[ERROR] Login fehlgeschlagen: {error_msg}")
                            # Versuche einen neuen Code anzufordern
                            raise Exception(f"Login fehlgeschlagen. Möglicherweise ist der Code abgelaufen oder ungültig. Bitte einen neuen Code anfordern. Fehler: {error_msg}")
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
                    "type": "unknown",
                    "chat_id": str(dialog.id)  # Chat-ID als String
                }
                
                if isinstance(entity, User):
                    dialog_info["type"] = "private"
                    dialog_info["username"] = entity.username
                    dialog_info["phone"] = entity.phone
                elif isinstance(entity, Chat):
                    dialog_info["type"] = "group"
                    dialog_info["participants_count"] = getattr(entity, "participants_count", None)
                elif isinstance(entity, Channel):
                    dialog_info["type"] = "channel" if entity.broadcast else "supergroup"
                    dialog_info["username"] = entity.username
                    dialog_info["participants_count"] = getattr(entity, "participants_count", None)
                    dialog_info["access_hash"] = str(entity.access_hash) if hasattr(entity, "access_hash") else None
                
                dialogs.append(dialog_info)
        
        except Exception as e:
            print(f"Fehler beim Abrufen der Dialoge: {e}")
        
        return dialogs
    
    async def find_group_in_dialogs(self, account_id: int, group_name: str = None, group_chat_id: str = None) -> Optional[dict]:
        """
        Sucht eine Gruppe in den Dialogen eines Accounts
        
        Args:
            account_id: Account-ID
            group_name: Gruppenname (optional)
            group_chat_id: Chat-ID der Gruppe (optional)
            
        Returns:
            Dict mit Gruppen-Informationen oder None
        """
        if account_id not in self.clients:
            return None
        
        dialogs = await self.get_dialogs(account_id)
        
        # Suche nach Chat-ID
        if group_chat_id:
            for dialog in dialogs:
                if str(dialog.get("id")) == str(group_chat_id) or dialog.get("chat_id") == str(group_chat_id):
                    return dialog
        
        # Suche nach Name
        if group_name:
            group_name_lower = group_name.lower().strip()
            for dialog in dialogs:
                if dialog.get("name", "").lower().strip() == group_name_lower:
                    return dialog
                # Prüfe auch Username
                if dialog.get("username", "").lower().strip() == group_name_lower.lstrip("@"):
                    return dialog
        
        return None
    
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
        delay: float = 2.0,
        invite_method: str = "admin"  # "admin" oder "invite_link"
    ) -> dict:
        """
        Lädt User zu einer Gruppe ein
        
        Args:
            account_id: Account-ID (muss Admin sein für "admin" Methode)
            group_entity: Chat-ID oder Username der Gruppe
            user_ids: Liste von User-IDs oder Usernames
            delay: Verzögerung zwischen Einladungen (wird nicht mehr verwendet - Delay ist jetzt zufällig zwischen 5-55 Sekunden)
            invite_method: "admin" (direkte Einladung als Admin) oder "invite_link" (Link erstellen und senden)
            
        Returns:
            Ergebnis-Dict mit Statistiken
            
        Note:
            Der Delay zwischen Einladungen ist zufällig zwischen 5 und 55 Sekunden, um Rate-Limiting zu vermeiden.
        """
        if account_id not in self.clients:
            return {"success": False, "error": "Account not connected"}
        
        client = self.clients[account_id]
        results = {
            "total": len(user_ids),
            "success": 0,
            "failed": 0,
            "errors": [],
            "invite_link": None  # Wird bei invite_link Methode gesetzt
        }
        
        try:
            # Versuche Entity zu laden
            # Konvertiere Chat-ID zu Integer, falls es eine numerische String-ID ist
            try:
                # Prüfe ob es eine numerische Chat-ID ist (z.B. "-1002139460011")
                if isinstance(group_entity, str) and (group_entity.startswith("-") or group_entity.isdigit()):
                    try:
                        chat_id_int = int(group_entity)
                        # Versuche zuerst als Integer zu laden
                        entity = await client.get_entity(chat_id_int)
                    except (ValueError, TypeError):
                        # Falls Integer-Konvertierung fehlschlägt, versuche als String
                        entity = await client.get_entity(group_entity)
                else:
                    entity = await client.get_entity(group_entity)
            except ValueError as ve:
                error_msg = str(ve)
                # Prüfe ob es ein "Cannot find entity" Fehler ist
                if "Cannot find" in error_msg or "No entity" in error_msg:
                    # Versuche die Chat-ID zu konvertieren und erneut zu laden
                    try:
                        if isinstance(group_entity, str):
                            chat_id_int = int(group_entity)
                            entity = await client.get_entity(chat_id_int)
                        else:
                            raise ve
                    except (ValueError, TypeError):
                        return {
                            "success": False,
                            "error": f"Gruppe nicht gefunden: {group_entity}. Mögliche Ursachen:\n- Der Account ist nicht in der Gruppe\n- Die Chat-ID ist falsch oder veraltet\n- Die Gruppe existiert nicht mehr\n\nFehler: {error_msg}"
                        }
                else:
                    return {
                        "success": False,
                        "error": f"Fehler beim Laden der Gruppe: {error_msg}"
                    }
            
            # Prüfe ob Account in der Gruppe ist (für bessere Fehlermeldungen)
            try:
                me = await client.get_me()
                # Versuche Teilnehmer-Info abzurufen (prüft ob Account in Gruppe ist)
                if isinstance(entity, Channel):
                    try:
                        await client(GetParticipantRequest(entity, me))
                    except:
                        # Account ist nicht in der Gruppe
                        return {
                            "success": False,
                            "error": f"Account ist nicht in der Gruppe '{getattr(entity, 'title', group_entity)}'. Bitte zuerst der Gruppe beitreten oder die Chat-ID aktualisieren."
                        }
            except Exception as e:
                # Ignoriere Fehler bei der Prüfung, versuche trotzdem fortzufahren
                pass
            
            # Bei invite_link Methode: Erstelle zuerst einen Einladungslink
            if invite_method == "invite_link":
                try:
                    # ExportChatInviteRequest funktioniert für beide (Kanäle und Gruppen)
                    invite_result = await client(ExportChatInviteRequest(entity))
                    
                    # Extrahiere Link (verschiedene Rückgabetypen möglich)
                    invite_link = None
                    if hasattr(invite_result, 'link'):
                        invite_link = invite_result.link
                    elif hasattr(invite_result, 'invite'):
                        if hasattr(invite_result.invite, 'link'):
                            invite_link = invite_result.invite.link
                        elif hasattr(invite_result.invite, 'hash'):
                            # Erstelle Link aus Hash
                            invite_hash = invite_result.invite.hash
                            if isinstance(entity, Channel) and hasattr(entity, 'username') and entity.username:
                                invite_link = f"https://t.me/{entity.username}"
                            else:
                                invite_link = f"https://t.me/joinchat/{invite_hash}"
                    elif hasattr(invite_result, 'hash'):
                        # Direkter Hash
                        invite_hash = invite_result.hash
                        if isinstance(entity, Channel) and hasattr(entity, 'username') and entity.username:
                            invite_link = f"https://t.me/{entity.username}"
                        else:
                            invite_link = f"https://t.me/joinchat/{invite_hash}"
                    
                    if not invite_link:
                        return {
                            "success": False,
                            "error": "Konnte keinen Einladungslink erstellen. Account muss Admin sein."
                        }
                    
                    results["invite_link"] = invite_link
                    
                    # Sende Link an alle User per DM
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
                            
                            # Sende Einladungslink per DM
                            message_text = f"Einladung zur Gruppe:\n{invite_link}"
                            await client.send_message(user_entity, message_text)
                            
                            results["success"] += 1
                            
                            # Rate Limiting - zufälliger Delay zwischen 5 und 55 Sekunden
                            if i < len(user_ids) - 1:
                                random_delay = random.uniform(5.0, 55.0)
                                await asyncio.sleep(random_delay)
                        
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
                                "error": "User hat Privatsphäre-Einstellungen aktiviert (DM nicht möglich)"
                            })
                        
                        except Exception as e:
                            results["failed"] += 1
                            results["errors"].append({
                                "user_id": user_id,
                                "error": str(e)
                            })
                    
                    return results
                
                except ChatAdminRequiredError:
                    return {
                        "success": False,
                        "error": "Account ist kein Admin. Kann keinen Einladungslink erstellen."
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Fehler beim Erstellen des Einladungslinks: {str(e)}"
                    }
            
            # Admin-Methode: Direkte Einladung
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
                    
                    # Rate Limiting - zufälliger Delay zwischen 5 und 55 Sekunden
                    if i < len(user_ids) - 1:
                        random_delay = random.uniform(5.0, 55.0)
                        await asyncio.sleep(random_delay)
                
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
    
    async def forward_message_by_id(
        self,
        account_id: int,
        source_group: str,
        message_id: int,
        target_groups: List[str],
        delay: float = 2.0
    ) -> dict:
        """
        Leitet eine einzelne Nachricht per Message-ID weiter
        
        Args:
            account_id: Account-ID
            source_group: Chat-ID oder Username der Quell-Gruppe
            message_id: Message-ID der zu weiterleitenden Nachricht
            target_groups: Liste von Chat-IDs der Ziel-Gruppen
            delay: Delay zwischen Weiterleitungen
            
        Returns:
            Dict mit success, forwarded, failed, errors
        """
        if account_id not in self.clients:
            return {
                "success": False,
                "error": "Account nicht verbunden"
            }
        
        client = self.clients[account_id]
        results = {
            "success": True,
            "forwarded": 0,
            "failed": 0,
            "errors": []
        }
        
        try:
            # Lade Quell-Entity
            try:
                source_entity = await client.get_entity(source_group)
            except ValueError as ve:
                error_msg = str(ve)
                # Prüfe ob es ein privater Chat ist (positive Chat-ID ohne Minus)
                # Private Chats haben positive IDs, Gruppen haben negative IDs (z.B. -100...)
                try:
                    chat_id_int = int(source_group)
                    # Wenn positive ID, könnte es ein privater Chat sein
                    if chat_id_int > 0:
                        # Versuche als User-ID zu laden
                        try:
                            from telethon.tl.types import User
                            source_entity = await client.get_entity(chat_id_int)
                            if isinstance(source_entity, User):
                                # Es ist ein privater Chat, kein Beitritt nötig
                                # Aber wir können trotzdem versuchen, die Nachricht zu laden
                                pass
                        except:
                            pass
                except ValueError:
                    pass
                
                # Wenn immer noch nicht gefunden, versuche beizutreten (nur für Gruppen)
                if 'source_entity' not in locals() or source_entity is None:
                    # Prüfe ob es eine Gruppe sein könnte (negative ID oder Username)
                    is_group = False
                    try:
                        chat_id_int = int(source_group)
                        if chat_id_int < 0:
                            is_group = True
                    except:
                        # Username oder Einladungslink - könnte Gruppe sein
                        if not source_group.startswith("http") and not source_group.startswith("t.me/"):
                            is_group = True
                    
                    if is_group:
                        join_result = await self.join_group(account_id, source_group)
                        if not join_result.get("success"):
                            return {
                                "success": False,
                                "error": f"Quell-Gruppe nicht gefunden und Beitritt fehlgeschlagen: {join_result.get('error')}"
                            }
                        # Versuche Entity erneut zu laden
                        try:
                            source_entity = await client.get_entity(source_group)
                        except:
                            return {
                                "success": False,
                                "error": f"Quell-Gruppe nicht gefunden: {source_group}"
                            }
                    else:
                        return {
                            "success": False,
                            "error": f"Quell-Chat nicht gefunden: {source_group}. Fehler: {error_msg}"
                        }
            
            # Prüfe ob Nachricht existiert
            try:
                # Konvertiere message_id zu int, falls es ein String ist
                # Telegram Message-IDs können sehr groß sein, daher sicherstellen dass es als int behandelt wird
                msg_id = int(message_id) if not isinstance(message_id, int) else message_id
                
                # Versuche Nachricht zu laden
                message = None
                error_str = None  # Initialisiere error_str
                
                try:
                    # get_messages kann eine Liste oder einzelne Nachricht zurückgeben
                    result = await client.get_messages(source_entity, ids=msg_id)
                    
                    # Prüfe ob es eine Liste ist
                    if isinstance(result, list):
                        if len(result) > 0:
                            message = result[0]
                        else:
                            message = None
                    else:
                        message = result
                        
                except Exception as msg_error:
                    error_str = str(msg_error)
                    # Bei privaten Chats kann es sein, dass wir die Nachricht nicht direkt laden können
                    # Versuche alternativ über iter_messages
                    if "source_entity" in locals() and hasattr(source_entity, 'id'):
                        # Versuche über iter_messages
                        try:
                            found = False
                            async for msg in client.iter_messages(source_entity, limit=1000):
                                if msg.id == msg_id:
                                    message = msg
                                    found = True
                                    break
                            if not found:
                                # error_str ist bereits gesetzt
                                return {
                                    "success": False,
                                    "error": f"Nachricht mit ID {message_id} nicht gefunden. Möglicherweise hast du keinen Zugriff auf diese Nachricht. Fehler: {error_str}"
                                }
                        except Exception as iter_error:
                            return {
                                "success": False,
                                "error": f"Fehler beim Laden der Nachricht: {str(iter_error)}"
                            }
                    else:
                        return {
                            "success": False,
                            "error": f"Fehler beim Laden der Nachricht: {error_str}"
                        }
                
                # Prüfe ob Nachricht gefunden wurde
                if message is None:
                    # Versuche mit iter_messages und größerem Limit
                    try:
                        found = False
                        # Erhöhe Limit für private Chats
                        search_limit = 10000
                        async for msg in client.iter_messages(source_entity, limit=search_limit):
                            if msg.id == msg_id:
                                message = msg
                                found = True
                                break
                        
                        if not found:
                            # Prüfe ob es ein privater Chat ist
                            is_private = False
                            try:
                                chat_id_int = int(source_group)
                                if chat_id_int > 0:
                                    is_private = True
                            except:
                                pass
                            
                            error_msg = f"Nachricht mit ID {msg_id} nicht gefunden im Chat {source_group}"
                            if is_private:
                                error_msg += "\n\nMögliche Ursachen für private Chats:"
                                error_msg += "\n- Die Nachricht wurde gelöscht"
                                error_msg += "\n- Die Nachricht ist zu alt (nicht mehr im Cache)"
                                error_msg += "\n- Der Account hat keinen Zugriff auf diese Nachricht"
                                error_msg += "\n- Die Message-ID ist falsch"
                            else:
                                error_msg += "\n\nMögliche Ursachen:"
                                error_msg += "\n- Die Nachricht wurde gelöscht"
                                error_msg += "\n- Der Account ist nicht in der Gruppe"
                                error_msg += "\n- Die Nachricht ist zu alt"
                                error_msg += "\n- Die Message-ID ist falsch"
                            
                            if error_str:
                                error_msg += f"\n\nTechnischer Fehler: {error_str}"
                            
                            return {
                                "success": False,
                                "error": error_msg
                            }
                    except Exception as iter_error:
                        return {
                            "success": False,
                            "error": f"Fehler beim Suchen der Nachricht: {str(iter_error)}"
                        }
                    
                # Prüfe ob die Message-ID übereinstimmt (sicherheitshalber)
                if hasattr(message, 'id') and message.id != msg_id:
                    # Versuche nochmal mit iter_messages
                    try:
                        found = False
                        async for msg in client.iter_messages(source_entity, limit=10000):
                            if msg.id == msg_id:
                                message = msg
                                found = True
                                break
                        if not found:
                            return {
                                "success": False,
                                "error": f"Nachricht mit ID {msg_id} nicht gefunden. Geladene Nachricht hat ID: {message.id if hasattr(message, 'id') else 'N/A'}"
                            }
                    except Exception as iter_error:
                        return {
                            "success": False,
                            "error": f"Fehler beim Laden der Nachricht: {str(iter_error)}"
                        }
                        
            except ValueError as ve:
                return {
                    "success": False,
                    "error": f"Ungültige Message-ID: {message_id}. Fehler: {str(ve)}"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Fehler beim Laden der Nachricht: {str(e)}"
                }
            
            # Weiterleiten an alle Ziel-Gruppen
            # Stelle sicher, dass message_id als int behandelt wird
            msg_id = int(message_id) if not isinstance(message_id, int) else message_id
            
            # Validiere dass die geladene Nachricht die richtige ID hat
            if hasattr(message, 'id'):
                if message.id != msg_id:
                    # Die geladene Nachricht hat nicht die erwartete ID
                    # Versuche nochmal mit iter_messages und größerem Limit
                    try:
                        found = False
                        async for msg in client.iter_messages(source_entity, limit=10000):
                            if msg.id == msg_id:
                                message = msg
                                found = True
                                break
                        if not found:
                            return {
                                "success": False,
                                "error": f"Nachricht mit ID {msg_id} nicht gefunden. Geladene Nachricht hat ID: {message.id}"
                            }
                    except Exception as iter_error:
                        return {
                            "success": False,
                            "error": f"Fehler beim Suchen der Nachricht: {str(iter_error)}"
                        }
            
            for target_group in target_groups:
                try:
                    target_entity = await client.get_entity(target_group)
                    
                    # Weiterleiten - verwende die geladene Nachricht direkt (besser als nur ID)
                    try:
                        # Versuche mit Message-Objekt (besser)
                        await client.forward_messages(
                            entity=target_entity,
                            messages=message,
                            from_peer=source_entity
                        )
                    except Exception as forward_error:
                        # Fallback: Versuche mit Message-ID
                        error_str = str(forward_error)
                        try:
                            await client.forward_messages(
                                entity=target_entity,
                                messages=msg_id,
                                from_peer=source_entity
                            )
                        except Exception as forward_error2:
                            raise Exception(f"Fehler beim Weiterleiten: {error_str}. Fallback-Fehler: {str(forward_error2)}")
                    
                    results["forwarded"] += 1
                    
                    # Rate Limiting zwischen Ziel-Gruppen
                    if target_group != target_groups[-1]:
                        await asyncio.sleep(delay)
                
                except FloodWaitError as e:
                    results["failed"] += 1
                    results["errors"].append({
                        "target": target_group,
                        "error": f"FloodWait: {e.seconds}s"
                    })
                    await asyncio.sleep(e.seconds)
                
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append({
                        "target": target_group,
                        "error": str(e)
                    })
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        
        return results
    
    async def join_group(self, account_id: int, group_entity: str) -> dict:
        """
        Tritt einer Gruppe bei
        
        Args:
            account_id: Account-ID
            group_entity: Chat-ID, Username oder Einladungslink
            
        Returns:
            Dict mit success und error
        """
        if account_id not in self.clients:
            return {
                "success": False,
                "error": "Account nicht verbunden"
            }
        
        client = self.clients[account_id]
        
        try:
            # Versuche Entity zu finden
            try:
                entity = await client.get_entity(group_entity)
            except ValueError:
                # Versuche über Username oder Einladungslink
                if group_entity.startswith("http") or group_entity.startswith("t.me/"):
                    # Einladungslink - extrahiere Hash
                    try:
                        # Format: https://t.me/joinchat/HASH oder t.me/joinchat/HASH
                        if "/joinchat/" in group_entity:
                            invite_hash = group_entity.split("/joinchat/")[-1].split("?")[0]
                        elif "/+" in group_entity:
                            invite_hash = group_entity.split("/+")[-1].split("?")[0]
                        else:
                            invite_hash = group_entity.split("/")[-1].split("?")[0]
                        
                        result = await client(ImportChatInviteRequest(invite_hash))
                        entity = result.chats[0] if result.chats else None
                        if not entity:
                            return {
                                "success": False,
                                "error": "Ungültiger Einladungslink"
                            }
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"Fehler beim Beitreten über Einladungslink: {str(e)}"
                        }
                else:
                    return {
                        "success": False,
                        "error": f"Gruppe nicht gefunden: {group_entity}"
                    }
            
            # Prüfe ob Account bereits Mitglied ist
            try:
                me = await client.get_me()
                if isinstance(entity, Channel):
                    # Für Kanäle/Supergruppen
                    try:
                        participant = await client(GetParticipantRequest(entity, me))
                        if participant:
                            return {
                                "success": True,
                                "message": "Account ist bereits Mitglied der Gruppe"
                            }
                    except:
                        pass  # Nicht Mitglied, versuche beizutreten
                    
                    # Versuche beizutreten
                    try:
                        await client(InviteToChannelRequest(
                            channel=entity,
                            users=[me]
                        ))
                        return {
                            "success": True,
                            "message": "Erfolgreich der Gruppe beigetreten"
                        }
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"Fehler beim Beitreten: {str(e)}. Möglicherweise benötigt die Gruppe eine Einladung."
                        }
                else:
                    # Für normale Gruppen
                    try:
                        await client(AddChatUserRequest(
                            chat_id=entity.id,
                            user_id=me,
                            fwd_limit=10
                        ))
                        return {
                            "success": True,
                            "message": "Erfolgreich der Gruppe beigetreten"
                        }
                    except Exception as e:
                        # Versuche über Username
                        if hasattr(entity, 'username') and entity.username:
                            try:
                                await client(AddChatUserRequest(
                                    chat_id=entity.username,
                                    user_id=me,
                                    fwd_limit=10
                                ))
                                return {
                                    "success": True,
                                    "message": "Erfolgreich der Gruppe beigetreten"
                                }
                            except Exception as e2:
                                return {
                                    "success": False,
                                    "error": f"Fehler beim Beitreten: {str(e2)}. Möglicherweise benötigt die Gruppe eine Einladung."
                                }
                        else:
                            return {
                                "success": False,
                                "error": f"Fehler beim Beitreten: {str(e)}. Möglicherweise benötigt die Gruppe eine Einladung."
                            }
            
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Unerwarteter Fehler: {str(e)}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Fehler: {str(e)}"
            }
    
    async def get_group_messages(
        self,
        account_id: int,
        group_entity: str,
        limit: int = 100,
        auto_join: bool = True
    ) -> dict:
        """
        Ruft Nachrichten aus einer Gruppe ab
        
        Args:
            account_id: Account-ID
            group_entity: Chat-ID oder Username
            limit: Maximale Anzahl Nachrichten
            auto_join: Automatisch beitreten, wenn nicht Mitglied
            
        Returns:
            Dict mit messages (Liste) und error (optional)
        """
        if account_id not in self.clients:
            return {
                "messages": [],
                "error": "Account nicht verbunden"
            }
        
        client = self.clients[account_id]
        messages = []
        
        try:
            # Versuche Entity zu finden
            try:
                entity = await client.get_entity(group_entity)
            except ValueError as e:
                error_msg = str(e)
                # Prüfe ob es ein "Cannot find entity" Fehler ist
                if "Cannot find" in error_msg or "No entity" in error_msg:
                    # Versuche beizutreten, wenn auto_join aktiviert ist
                    if auto_join:
                        join_result = await self.join_group(account_id, group_entity)
                        if not join_result.get("success"):
                            return {
                                "messages": [],
                                "error": f"Gruppe nicht gefunden und Beitritt fehlgeschlagen: {join_result.get('error')}"
                            }
                        # Versuche Entity erneut zu laden
                        try:
                            entity = await client.get_entity(group_entity)
                        except:
                            return {
                                "messages": [],
                                "error": f"Gruppe nicht gefunden. Chat-ID: {group_entity}"
                            }
                    else:
                        return {
                            "messages": [],
                            "error": f"Gruppe nicht gefunden. Möglicherweise ist der Account nicht in der Gruppe oder die Chat-ID ist falsch. Chat-ID: {group_entity}"
                        }
                else:
                    return {
                        "messages": [],
                        "error": f"Fehler beim Laden der Gruppe: {error_msg}"
                    }
            
            # Prüfe ob Account Zugriff auf die Gruppe hat
            try:
                # Versuche eine Nachricht abzurufen um Zugriff zu prüfen
                async for message in client.iter_messages(entity, limit=1):
                    break  # Nur prüfen ob Zugriff vorhanden
            except Exception as access_error:
                # Versuche beizutreten, wenn auto_join aktiviert ist
                if auto_join:
                    join_result = await self.join_group(account_id, group_entity)
                    if not join_result.get("success"):
                        return {
                            "messages": [],
                            "error": f"Kein Zugriff auf die Gruppe und Beitritt fehlgeschlagen: {join_result.get('error')}"
                        }
                    # Versuche erneut Nachrichten abzurufen
                    try:
                        async for message in client.iter_messages(entity, limit=1):
                            break
                    except:
                        return {
                            "messages": [],
                            "error": f"Kein Zugriff auf die Gruppe. Fehler: {str(access_error)}"
                        }
                else:
                    return {
                        "messages": [],
                        "error": f"Kein Zugriff auf die Gruppe. Möglicherweise ist der Account nicht Mitglied. Fehler: {str(access_error)}"
                    }
            
            # Lade Nachrichten
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
            
            return {
                "messages": messages,
                "error": None
            }
        
        except Exception as e:
            error_msg = str(e)
            print(f"Fehler beim Abrufen der Nachrichten: {error_msg}")
            return {
                "messages": [],
                "error": f"Fehler beim Laden der Nachrichten: {error_msg}"
            }
    
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
            # Validiere und bereinige Bot-Username gemäß Telegram-Richtlinien:
            # - Muss mit "bot" enden
            # - Nur a-z, 0-9, _ erlaubt
            # - 5-32 Zeichen lang
            
            # Konvertiere zu Kleinbuchstaben
            bot_username = bot_username.lower()
            
            # Entferne alle ungültigen Zeichen (nur a-z, 0-9, _ erlaubt)
            bot_username = ''.join(c for c in bot_username if c.isalnum() or c == '_')
            
            # Stelle sicher, dass Username auf "_bot" endet (nicht nur "bot")
            if not bot_username.endswith("_bot"):
                # Entferne "bot" oder "_bot" falls bereits vorhanden (um Duplikate zu vermeiden)
                bot_username = bot_username.rstrip("_bot").rstrip("bot")
                bot_username = bot_username + "_bot"
            
            # Stelle sicher, dass Username zwischen 5 und 32 Zeichen lang ist
            if len(bot_username) < 5:
                # Füge Ziffern hinzu falls zu kurz
                padding_needed = 5 - len(bot_username)
                bot_username = bot_username[:-4] + "0" * padding_needed + "_bot"
            elif len(bot_username) > 32:
                # Kürze auf max 32 Zeichen (behalte "_bot" Endung)
                max_base_length = 28  # 32 - 4 ("_bot")
                bot_username = bot_username[:max_base_length] + "_bot"
            
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

