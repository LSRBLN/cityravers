"""
Integration für Telefonnummern-Anbieter (5sim.net, sms-activate, sms-manager, getsmscode, onlinesim.io)
"""
import requests
import asyncio
from typing import Optional, Dict
from datetime import datetime, timedelta

class FiveSimProvider:
    """5sim.net API Integration"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://5sim.net/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }
    
    async def get_balance(self) -> Dict:
        """Gibt das Guthaben zurück"""
        try:
            response = requests.get(
                f"{self.base_url}/user/profile",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return {
                "success": True,
                "balance": data.get("balance", 0),
                "currency": data.get("currency", "EUR")
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def buy_number(
        self,
        country: str = "germany",
        service: str = "telegram",
        operator: Optional[str] = None
    ) -> Dict:
        """
        Kauft eine Telefonnummer
        
        Args:
            country: Land (z.B. 'germany', 'usa', 'russia')
            service: Service (z.B. 'telegram', 'whatsapp')
            operator: Optional: Spezifischer Operator
            
        Returns:
            Dict mit purchase_id, phone_number, etc.
        """
        try:
            url = f"{self.base_url}/user/buy/activation/{country}/{operator or 'any'}/{service}"
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            return {
                "success": True,
                "purchase_id": data.get("id"),
                "phone_number": data.get("phone"),
                "country": country,
                "service": service,
                "operator": data.get("operator"),
                "cost": data.get("price"),
                "expires_at": datetime.utcnow() + timedelta(minutes=data.get("expires", 20))
            }
        except requests.exceptions.HTTPError as e:
            error_data = e.response.json() if e.response else {}
            return {
                "success": False,
                "error": error_data.get("message", str(e)),
                "error_code": e.response.status_code if e.response else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_sms_code(self, purchase_id: str) -> Dict:
        """
        Ruft den SMS-Code ab
        
        Args:
            purchase_id: ID des Kaufs
            
        Returns:
            Dict mit sms_code, status, etc.
        """
        try:
            url = f"{self.base_url}/user/check/{purchase_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            sms_code = None
            if data.get("sms"):
                sms_list = data.get("sms", [])
                if sms_list:
                    # Neueste SMS
                    latest_sms = sms_list[-1]
                    sms_code = latest_sms.get("code")
            
            return {
                "success": True,
                "status": data.get("status"),  # 'PENDING', 'RECEIVED', 'FINISHED', 'CANCELED'
                "sms_code": sms_code,
                "phone_number": data.get("phone"),
                "expires_at": datetime.fromisoformat(data.get("expires")) if data.get("expires") else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def cancel_order(self, purchase_id: str) -> Dict:
        """Storniert eine Bestellung"""
        try:
            url = f"{self.base_url}/user/cancel/{purchase_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return {"success": True}
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def finish_order(self, purchase_id: str) -> Dict:
        """Beendet eine Bestellung (nach erfolgreicher Verwendung)"""
        try:
            url = f"{self.base_url}/user/finish/{purchase_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return {"success": True}
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class SMSActivateProvider:
    """SMS-Activate.ru API Integration (Alternative)"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://sms-activate.org/stubs/handler_api.php"
    
    async def get_balance(self) -> Dict:
        """Gibt das Guthaben zurück"""
        try:
            response = requests.get(
                f"{self.base_url}?api_key={self.api_key}&action=getBalance",
                timeout=10
            )
            response.raise_for_status()
            # Format: "ACCESS_BALANCE:123.45"
            data = response.text
            if data.startswith("ACCESS_BALANCE:"):
                balance = float(data.split(":")[1])
                return {
                    "success": True,
                    "balance": balance,
                    "currency": "RUB"
                }
            return {
                "success": False,
                "error": data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def buy_number(
        self,
        country: str = "6",  # Deutschland
        service: str = "tg"  # Telegram
    ) -> Dict:
        """Kauft eine Telefonnummer"""
        try:
            # Aktiviere Nummer
            url = f"{self.base_url}?api_key={self.api_key}&action=getNumber&service={service}&country={country}"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.text
            
            # Format: "ACCESS_NUMBER:123456:79123456789" oder "NO_NUMBERS"
            if data.startswith("ACCESS_NUMBER:"):
                parts = data.split(":")
                activation_id = parts[1]
                phone_number = parts[2]
                
                return {
                    "success": True,
                    "purchase_id": activation_id,
                    "phone_number": phone_number,
                    "country": country,
                    "service": service
                }
            else:
                return {
                    "success": False,
                    "error": data
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_sms_code(self, purchase_id: str) -> Dict:
        """Ruft den SMS-Code ab"""
        try:
            url = f"{self.base_url}?api_key={self.api_key}&action=getStatus&id={purchase_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.text
            
            # Format: "STATUS_OK:12345" oder "STATUS_WAIT_CODE" oder "STATUS_CANCEL"
            if data.startswith("STATUS_OK:"):
                sms_code = data.split(":")[1]
                return {
                    "success": True,
                    "status": "RECEIVED",
                    "sms_code": sms_code
                }
            elif data == "STATUS_WAIT_CODE":
                return {
                    "success": True,
                    "status": "PENDING",
                    "sms_code": None
                }
            else:
                return {
                    "success": False,
                    "error": data
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class SMSManagerProvider:
    """SMS-Manager.com API Integration"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://sms-manager.com/api"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def get_balance(self) -> Dict:
        """Gibt das Guthaben zurück"""
        try:
            response = requests.get(
                f"{self.base_url}/balance",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return {
                "success": True,
                "balance": data.get("balance", 0),
                "currency": data.get("currency", "USD")
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def buy_number(
        self,
        country: str = "DE",  # ISO Country Code
        service: str = "telegram",
        operator: Optional[str] = None
    ) -> Dict:
        """
        Kauft eine Telefonnummer
        
        Args:
            country: ISO Country Code (z.B. 'DE', 'US', 'RU')
            service: Service (z.B. 'telegram', 'whatsapp')
            operator: Optional: Spezifischer Operator
        """
        try:
            payload = {
                "country": country,
                "service": service
            }
            if operator:
                payload["operator"] = operator
            
            response = requests.post(
                f"{self.base_url}/order/create",
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "success":
                return {
                    "success": True,
                    "purchase_id": data.get("order_id"),
                    "phone_number": data.get("phone"),
                    "country": country,
                    "service": service,
                    "operator": data.get("operator"),
                    "cost": data.get("price"),
                    "expires_at": datetime.utcnow() + timedelta(minutes=data.get("expires_minutes", 20))
                }
            else:
                return {
                    "success": False,
                    "error": data.get("message", "Unbekannter Fehler")
                }
        except requests.exceptions.HTTPError as e:
            error_data = e.response.json() if e.response else {}
            return {
                "success": False,
                "error": error_data.get("message", str(e)),
                "error_code": e.response.status_code if e.response else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_sms_code(self, purchase_id: str) -> Dict:
        """Ruft den SMS-Code ab"""
        try:
            response = requests.get(
                f"{self.base_url}/order/{purchase_id}/status",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            status = data.get("status", "pending")
            sms_code = None
            
            if status == "completed" and data.get("code"):
                sms_code = data.get("code")
            
            return {
                "success": True,
                "status": status.upper(),  # 'PENDING', 'RECEIVED', 'COMPLETED', 'CANCELED'
                "sms_code": sms_code,
                "phone_number": data.get("phone")
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def cancel_order(self, purchase_id: str) -> Dict:
        """Storniert eine Bestellung"""
        try:
            response = requests.post(
                f"{self.base_url}/order/{purchase_id}/cancel",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return {"success": True}
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class GetSMSCodeProvider:
    """GetSMSCode.com API Integration"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.getsmscode.com"
        # GetSMSCode verwendet Format: username:token
        if ":" in api_key:
            self.user = api_key.split(":")[0]
            self.token = api_key.split(":")[1]
        else:
            # Fallback: verwende API Key als beides
            self.user = api_key
            self.token = api_key
    
    async def get_balance(self) -> Dict:
        """Gibt das Guthaben zurück"""
        try:
            response = requests.get(
                f"{self.base_url}/do.php",
                params={
                    "action": "getbalance",
                    "username": self.user,
                    "token": self.token
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.text.strip()
            
            # Format: "1|123.45" (Status|Balance) oder Fehlermeldung
            if "|" in data:
                parts = data.split("|")
                if parts[0] == "1":
                    return {
                        "success": True,
                        "balance": float(parts[1]),
                        "currency": "USD"
                    }
            
            return {
                "success": False,
                "error": data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def buy_number(
        self,
        country: str = "DE",  # ISO Country Code
        service: str = "telegram",
        operator: Optional[str] = None
    ) -> Dict:
        """
        Kauft eine Telefonnummer
        
        Args:
            country: ISO Country Code (z.B. 'DE', 'US', 'RU')
            service: Service Code (z.B. 'telegram', 'whatsapp')
        """
        try:
            # GetSMSCode verwendet spezielle Service-Codes
            service_map = {
                "telegram": "tg",
                "whatsapp": "wa",
                "discord": "dc"
            }
            service_code = service_map.get(service.lower(), service)
            
            # Country Code Mapping (ISO zu GetSMSCode Format)
            country_map = {
                "DE": "DE",
                "US": "US",
                "RU": "RU",
                "UK": "GB",
                "germany": "DE",
                "usa": "US",
                "russia": "RU"
            }
            country_code = country_map.get(country.upper(), country.upper())
            
            response = requests.get(
                f"{self.base_url}/do.php",
                params={
                    "action": "getmobile",
                    "username": self.user,
                    "token": self.token,
                    "pid": service_code,
                    "cocode": country_code
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.text.strip()
            
            # Format: "1|79123456789" (Status|PhoneNumber) oder Fehlermeldung
            if "|" in data:
                parts = data.split("|")
                if parts[0] == "1":
                    # GetSMSCode gibt nur die Nummer zurück, keine Order-ID
                    # Wir verwenden eine Kombination aus User+Timestamp als ID
                    purchase_id = f"{self.user}_{int(datetime.utcnow().timestamp())}"
                    
                    return {
                        "success": True,
                        "purchase_id": purchase_id,
                        "phone_number": parts[1],
                        "country": country_code,
                        "service": service_code,
                        "cost": None,  # Wird separat abgefragt
                        "expires_at": datetime.utcnow() + timedelta(minutes=20)
                    }
            
            return {
                "success": False,
                "error": data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_sms_code(self, purchase_id: str) -> Dict:
        """
        Ruft den SMS-Code ab
        
        Note: GetSMSCode benötigt die Phone Number, nicht die Order ID
        Wir speichern die Phone Number in purchase_id wenn möglich
        """
        try:
            # GetSMSCode verwendet Phone Number direkt
            # Format von purchase_id: "user_timestamp" oder direkt die Nummer
            phone_number = purchase_id
            if "_" in purchase_id:
                # Wenn es unser Format ist, müssen wir die Nummer anders speichern
                # In der Praxis sollte die Phone Number separat gespeichert werden
                # Für jetzt versuchen wir es mit der purchase_id
                phone_number = purchase_id.split("_")[-1] if len(purchase_id.split("_")) > 1 else purchase_id
            
            response = requests.get(
                f"{self.base_url}/do.php",
                params={
                    "action": "getsms",
                    "username": self.user,
                    "token": self.token,
                    "mobile": phone_number
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.text.strip()
            
            # Format: "1|12345" (Status|Code) oder "STATUS_WAIT" oder Fehlermeldung
            if "|" in data:
                parts = data.split("|")
                if parts[0] == "1":
                    return {
                        "success": True,
                        "status": "RECEIVED",
                        "sms_code": parts[1],
                        "phone_number": phone_number
                    }
            elif data == "STATUS_WAIT":
                return {
                    "success": True,
                    "status": "PENDING",
                    "sms_code": None,
                    "phone_number": phone_number
                }
            
            return {
                "success": False,
                "error": data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def cancel_order(self, purchase_id: str) -> Dict:
        """Storniert eine Bestellung"""
        try:
            # GetSMSCode verwendet Phone Number
            phone_number = purchase_id.split("_")[-1] if "_" in purchase_id else purchase_id
            
            response = requests.get(
                f"{self.base_url}/do.php",
                params={
                    "action": "cancel",
                    "username": self.user,
                    "token": self.token,
                    "mobile": phone_number
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.text.strip()
            
            if data == "1":
                return {"success": True}
            else:
                return {
                    "success": False,
                    "error": data
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class OnlineSimProvider:
    """OnlineSim.io API Integration"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://onlinesim.io/api"
    
    async def get_balance(self) -> Dict:
        """Gibt das Guthaben zurück"""
        try:
            response = requests.get(
                f"{self.base_url}/getBalance.php",
                params={
                    "apikey": self.api_key
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # OnlineSim gibt Balance direkt zurück
            if isinstance(data, dict) and "balance" in data:
                return {
                    "success": True,
                    "balance": float(data.get("balance", 0)),
                    "currency": data.get("currency", "USD")
                }
            elif isinstance(data, (int, float)):
                return {
                    "success": True,
                    "balance": float(data),
                    "currency": "USD"
                }
            
            return {
                "success": False,
                "error": f"Unerwartetes Format: {data}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_tariffs(self, country: Optional[str] = None) -> Dict:
        """
        Gibt die Tarife (Preise) für Länder zurück
        
        Args:
            country: Optional: Ländercode (z.B. "84" für Vietnam). Wenn None, werden alle Länder zurückgegeben.
        """
        try:
            params = {
                "apikey": self.api_key
            }
            if country:
                params["country"] = country
            
            response = requests.get(
                f"{self.base_url}/getTariffs.php",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, dict):
                return {
                    "success": True,
                    "tariffs": data
                }
            elif isinstance(data, list):
                return {
                    "success": True,
                    "tariffs": data
                }
            
            return {
                "success": False,
                "error": f"Unerwartetes Format: {data}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_countries(self) -> Dict:
        """Gibt alle verfügbaren Länder zurück"""
        try:
            response = requests.get(
                f"{self.base_url}/getNumbersStats.php",
                params={
                    "apikey": self.api_key
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, dict):
                return {
                    "success": True,
                    "countries": data
                }
            elif isinstance(data, list):
                return {
                    "success": True,
                    "countries": data
                }
            
            return {
                "success": False,
                "error": f"Unerwartetes Format: {data}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def buy_number(
        self,
        country: str = "germany",  # ISO Country Code oder Name
        service: str = "telegram",
        operator: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: float = 5.0
    ) -> Dict:
        """
        Kauft eine Telefonnummer mit Retry-Logik für Rate-Limiting
        
        Args:
            country: Land (z.B. 'germany', 'usa', 'russia' oder ISO Code)
            service: Service (z.B. 'telegram', 'whatsapp')
            operator: Optional: Spezifischer Operator
            max_retries: Maximale Anzahl Retry-Versuche
            retry_delay: Wartezeit zwischen Retries in Sekunden (wird exponentiell erhöht)
        """
        # OnlineSim verwendet Country-Codes (z.B. 7 für Russland, 49 für Deutschland)
        # Wir konvertieren Country-Namen zu Codes
        country_map = {
            "germany": "49",
            "de": "49",
            "deutschland": "49",
            "usa": "1",
            "us": "1",
            "russia": "7",
            "ru": "7",
            "ukraine": "380",
            "ua": "380",
            "poland": "48",
            "pl": "48",
            "vietnam": "84",
            "vn": "84"
        }
        
        country_code = country_map.get(country.lower(), country)
        
        # Service-Mapping
        service_map = {
            "telegram": "telegram",
            "tg": "telegram",
            "whatsapp": "whatsapp",
            "wa": "whatsapp"
        }
        service_code = service_map.get(service.lower(), service)
        
        # Retry-Logik für Rate-Limiting
        last_error = None
        for attempt in range(max_retries):
            try:
                # Hole Nummer
                params = {
                    "apikey": self.api_key,
                    "service": service_code,
                    "country": country_code
                }
                
                if operator:
                    params["operator"] = operator
                
                response = requests.get(
                    f"{self.base_url}/getNumber.php",
                    params=params,
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
                
                # Format: {"tzid": 123456, "number": "+79123456789"} oder Fehler
                if isinstance(data, dict) and "tzid" in data:
                    tzid = data.get("tzid")
                    phone_number = data.get("number")
                    
                    # Normalisiere Telefonnummer (füge + hinzu falls fehlt)
                    if phone_number and not phone_number.startswith("+"):
                        phone_number = "+" + phone_number
                    
                    return {
                        "success": True,
                        "purchase_id": str(tzid),
                        "phone_number": phone_number,
                        "country": country_code,
                        "service": service_code,
                        "cost": None,  # Wird separat abgefragt
                        "expires_at": datetime.utcnow() + timedelta(minutes=20)
                    }
                else:
                    # Fehler von OnlineSim API
                    error_msg = data.get("response", str(data)) if isinstance(data, dict) else str(data)
                    last_error = error_msg
                    
                    # Prüfe ob es ein retry-fähiger Fehler ist
                    retryable_errors = ["TRY_AGAIN_LATER", "NO_NUMBERS", "NO_BALANCE", "RATE_LIMIT"]
                    is_retryable = any(err in str(error_msg).upper() for err in retryable_errors)
                    
                    if not is_retryable or attempt >= max_retries - 1:
                        # Nicht retry-fähig oder letzter Versuch
                        return {
                            "success": False,
                            "error": error_msg,
                            "retryable": is_retryable
                        }
                    
                    # Warte vor Retry (exponentielles Backoff)
                    wait_time = retry_delay * (2 ** attempt)
                    await asyncio.sleep(wait_time)
                    continue
                    
            except requests.exceptions.HTTPError as e:
                error_data = e.response.json() if e.response and e.response.headers.get('content-type', '').startswith('application/json') else {}
                error_msg = error_data.get("response", str(e)) if error_data else str(e)
                last_error = error_msg
                
                # Prüfe ob retry-fähig
                is_retryable = e.response.status_code in [429, 503, 502] or "TRY_AGAIN" in str(error_msg).upper()
                
                if not is_retryable or attempt >= max_retries - 1:
                    return {
                        "success": False,
                        "error": error_msg,
                        "error_code": e.response.status_code if e.response else None,
                        "retryable": is_retryable
                    }
                
                # Warte vor Retry
                wait_time = retry_delay * (2 ** attempt)
                await asyncio.sleep(wait_time)
                continue
                
            except Exception as e:
                last_error = str(e)
                if attempt >= max_retries - 1:
                    return {
                        "success": False,
                        "error": str(e),
                        "retryable": False
                    }
                # Warte vor Retry
                wait_time = retry_delay * (2 ** attempt)
                await asyncio.sleep(wait_time)
                continue
        
        # Alle Retries fehlgeschlagen
        return {
            "success": False,
            "error": f"Nach {max_retries} Versuchen fehlgeschlagen: {last_error}",
            "retryable": True
        }
    
    async def get_sms_code(self, purchase_id: str) -> Dict:
        """
        Ruft den SMS-Code ab
        
        Args:
            purchase_id: TZID (Transaction ID) von OnlineSim
        """
        try:
            response = requests.get(
                f"{self.base_url}/getState.php",
                params={
                    "apikey": self.api_key,
                    "tzid": purchase_id
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Format: {"response": "STATUS_OK", "msg": "12345", "tzid": 123456}
            # oder {"response": "STATUS_WAIT_CODE", "tzid": 123456}
            if isinstance(data, dict):
                response_status = data.get("response", "")
                sms_code = data.get("msg")
                phone_number = data.get("number")
                
                if response_status == "STATUS_OK" and sms_code:
                    return {
                        "success": True,
                        "status": "RECEIVED",
                        "sms_code": sms_code,
                        "phone_number": phone_number
                    }
                elif response_status == "STATUS_WAIT_CODE":
                    return {
                        "success": True,
                        "status": "PENDING",
                        "sms_code": None,
                        "phone_number": phone_number
                    }
                elif response_status == "STATUS_CANCEL":
                    return {
                        "success": False,
                        "status": "CANCELED",
                        "error": "Bestellung wurde storniert"
                    }
                else:
                    return {
                        "success": False,
                        "error": response_status or "Unbekannter Status"
                    }
            
            return {
                "success": False,
                "error": f"Unerwartetes Format: {data}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def cancel_order(self, purchase_id: str) -> Dict:
        """Storniert eine Bestellung"""
        try:
            response = requests.get(
                f"{self.base_url}/setOperationOk.php",
                params={
                    "apikey": self.api_key,
                    "tzid": purchase_id,
                    "status": "cancel"
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, dict) and data.get("response") == "OK":
                return {"success": True}
            else:
                return {
                    "success": False,
                    "error": data.get("response", "Unbekannter Fehler")
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def finish_order(self, purchase_id: str) -> Dict:
        """Beendet eine Bestellung (nach erfolgreicher Verwendung)"""
        try:
            response = requests.get(
                f"{self.base_url}/setOperationOk.php",
                params={
                    "apikey": self.api_key,
                    "tzid": purchase_id
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, dict) and data.get("response") == "OK":
                return {"success": True}
            else:
                return {
                    "success": False,
                    "error": data.get("response", "Unbekannter Fehler")
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
