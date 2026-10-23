import sys
import socket
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from evolution_client import EvolutionClient

def obter_ip_local():
    """Detecta o IP da máquina na rede local para comunicação com o container."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "192.168.10.15"

def main():
    print("=" * 60)
    print("[*] REGISTRANDO WEBHOOK NA EVOLUTION API COM IP REAL...")
    print("=" * 60)

    client = EvolutionClient()
    
    ip_host = obter_ip_local()
    webhook_url = f"http://{ip_host}:5000/webhook"
    
    print(f"Instancia: {client.instance_name}")
    print(f"URL de destino: {webhook_url}")
    
    try:
        resposta = client.configurar_webhook(webhook_url=webhook_url, enabled=True)
        print("\n[+] Webhook configurado com sucesso na Evolution API!")
        print(f"    URL registrada: {webhook_url}")
    except Exception as e:
        print(f"\n[-] Erro ao configurar webhook: {e}")

if __name__ == "__main__":
    main()
