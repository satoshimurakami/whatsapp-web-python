import os
import sys
import json
import socket
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import uvicorn
from fastapi import FastAPI, Request, BackgroundTasks
from dotenv import load_dotenv
from evolution_client import EvolutionClient

load_dotenv()

app = FastAPI(
    title="WhatsApp Webhook Receiver",
    description="Servidor para receber mensagens em tempo real da Evolution API"
)

client = EvolutionClient()

def obter_ip_local() -> str:
    """Detecta o IP local da máquina na rede para registrar o webhook."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def salvar_log_debug(payload: dict):
    """Salva o payload recebido em um arquivo json para inspecao."""
    try:
        entrada = {
            "timestamp": datetime.now().isoformat(),
            "payload": payload
        }
        with open("webhook_debug.json", "a", encoding="utf-8") as f:
            f.write(json.dumps(entrada, ensure_ascii=False) + "\n")
    except Exception:
        pass

def processar_evento(payload: dict):
    salvar_log_debug(payload)

    event = payload.get("event", "")
    event_norm = str(event).lower().replace("_", ".").strip()
    
    print("\n" + "-" * 55)
    print(f"🔔 [WEBHOOK] Evento recebido: '{event}'")

    # Verifica se e evento de mensagem
    if "messages.upsert" not in event_norm and "message" not in event_norm:
        print(f"   (Evento ignorado por nao ser de mensagem: {event})")
        return

    data = payload.get("data", {})
    if isinstance(data, list):
        data = data[0] if len(data) > 0 else {}

    key = data.get("key", {})
    from_me = key.get("fromMe", False)
    remetente_jid = key.get("remoteJid", "")
    origem = remetente_jid.replace("@s.whatsapp.net", "").replace("@g.us", " (Grupo)")
    nome = data.get("pushName") or "Desconhecido"

    # Extrai o texto de varios formatos possiveis
    mensagem_obj = data.get("message", {})
    texto = (
        mensagem_obj.get("conversation")
        or mensagem_obj.get("extendedTextMessage", {}).get("text")
        or mensagem_obj.get("imageMessage", {}).get("caption")
        or mensagem_obj.get("videoMessage", {}).get("caption")
        or mensagem_obj.get("documentMessage", {}).get("caption")
        or "[Midia/Outro formato]"
    )

    print("=" * 55)
    if from_me:
        print(f"📤 [MENSAGEM ENVIADA POR VOCE]")
        print(f"   Para: {origem}")
        print(f"   Texto: {texto}")
        print("   (Auto-resposta nao acionada para evitar loop)")
    else:
        print(f"📥 [NOVA MENSAGEM DO WHATSAPP]")
        print(f"   De: {nome} ({origem})")
        print(f"   Texto: {texto}")

        # Auto-resposta para saudacao / menu
        texto_lower = texto.strip().lower()
        if texto_lower in ["oi", "ola", "olá", "menu", "ajuda", "teste"]:
            resposta = (
                f"Olá, {nome}! Sou o robô em Python.\n\n"
                "Escolha uma opção:\n"
                "1 - Horário de Atendimento\n"
                "2 - Localização\n"
                "3 - Falar com atendente humano"
            )
            try:
                client.enviar_texto(numero=origem, texto=resposta)
                print(f"[+] Resposta automatica enviada para {origem}")
            except Exception as e:
                print(f"[-] Erro ao enviar resposta automatica: {e}")
    print("=" * 55)

@app.on_event("startup")
def sincronizar_webhook_automatico():
    """Garante que a Evolution API sempre aponte para o IP atual desta maquina ao iniciar."""
    ip_atual = obter_ip_local()
    porta = int(os.getenv("WEBHOOK_PORT", 5000))
    webhook_url = f"http://{ip_atual}:{porta}/webhook"
    
    print(f"[*] Sincronizando Webhook na Evolution API para: {webhook_url}...")
    try:
        client.configurar_webhook(webhook_url=webhook_url, enabled=True)
        print(f"[+] Webhook sincronizado com sucesso com o IP atual ({ip_atual})!")
    except Exception as e:
        print(f"[-] Nao foi possivel sincronizar webhook automaticamente: {e}")

@app.get("/")
def home():
    return {
        "status": "online",
        "service": "WhatsApp Webhook Receiver",
        "instancia": client.instance_name,
        "ip_local": obter_ip_local()
    }

@app.get("/webhook")
def webhook_info():
    return {
        "status": "online",
        "message": "Endpoint de Webhook ativo. Aguardando requisicoes HTTP POST da Evolution API.",
        "ip_local": obter_ip_local()
    }

@app.post("/webhook")
async def webhook_handler(request: Request, background_tasks: BackgroundTasks):
    try:
        payload = await request.json()
        background_tasks.add_task(processar_evento, payload)
        return {"status": "ok"}
    except Exception as e:
        print(f"[-] Erro no webhook_handler: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    porta = int(os.getenv("WEBHOOK_PORT", 5000))
    print("=" * 55)
    print(f"[*] Iniciando Webhook Server na porta {porta}...")
    print(f"[*] Escutando eventos para a instancia: '{client.instance_name}'")
    print("=" * 55)
    uvicorn.run(app, host="0.0.0.0", port=porta)
