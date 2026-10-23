import os
import httpx
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class EvolutionClient:
    """Cliente Python para a Evolution API v2."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        instance_name: Optional[str] = None,
    ):
        self.base_url = (base_url or os.getenv("EVOLUTION_API_URL", "http://localhost:8080")).rstrip("/")
        self.api_key = api_key or os.getenv("EVOLUTION_API_KEY", "sua_chave_secreta_aqui")
        self.instance_name = instance_name or os.getenv("INSTANCE_NAME", "teste de bot zapzap")

    @property
    def headers(self) -> Dict[str, str]:
        return {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }

    def status_conexao(self, instance_name: Optional[str] = None) -> Dict[str, Any]:
        """Verifica o estado da conexão (open, connecting, close)."""
        instance = instance_name or self.instance_name
        url = f"{self.base_url}/instance/connectionState/{instance}"
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    def listar_instancias(self) -> list:
        """Lista todas as instâncias existentes no gateway."""
        url = f"{self.base_url}/instance/fetchInstances"
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    def enviar_texto(
        self,
        numero: str,
        texto: str,
        delay_ms: int = 1200,
        instance_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Envia uma mensagem de texto simples.
        
        :param numero: Telefone no formato DDI + DDD + Número (ex: 5567999999999).
        :param texto: Conteúdo da mensagem.
        :param delay_ms: Tempo em milissegundos simulando digitação antes do envio.
        """
        # Higieniza o número removendo caracteres especiais
        numero_limpo = "".join(filter(str.isdigit, numero))
        instance = instance_name or self.instance_name
        url = f"{self.base_url}/message/sendText/{instance}"

        payload = {
            "number": numero_limpo,
            "text": texto,
            "delay": delay_ms
        }

        with httpx.Client(timeout=15.0) as client:
            resp = client.post(url, json=payload, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    def enviar_midia(
        self,
        numero: str,
        media_url: str,
        caption: str = "",
        media_type: str = "image",
        file_name: Optional[str] = None,
        instance_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Envia uma imagem, documento PDF, áudio ou vídeo.
        
        :param numero: Telefone do destinatário.
        :param media_url: URL pública ou base64 do arquivo.
        :param caption: Legenda da mídia.
        :param media_type: 'image', 'document', 'audio', ou 'video'.
        """
        numero_limpo = "".join(filter(str.isdigit, numero))
        instance = instance_name or self.instance_name
        url = f"{self.base_url}/message/sendMedia/{instance}"

        payload = {
            "number": numero_limpo,
            "mediatype": media_type,
            "media": media_url,
            "caption": caption
        }
        if file_name:
            payload["fileName"] = file_name

        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, json=payload, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    def configurar_webhook(
        self,
        webhook_url: str,
        enabled: bool = True,
        instance_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Configura o webhook na Evolution API para enviar eventos ao seu backend Python.
        """
        instance = instance_name or self.instance_name
        url = f"{self.base_url}/webhook/set/{instance}"

        payload = {
            "webhook": {
                "enabled": enabled,
                "url": webhook_url,
                "byEvents": False,
                "base64": False,
                "events": [
                    "MESSAGES_UPSERT",
                    "MESSAGES_UPDATE",
                    "SEND_MESSAGE",
                    "CONNECTION_UPDATE",
                    "CHATS_UPSERT",
                    "CHATS_UPDATE"
                ]
            }
        }

        with httpx.Client(timeout=10.0) as client:
            resp = client.post(url, json=payload, headers=self.headers)
            resp.raise_for_status()
            return resp.json()
