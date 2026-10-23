import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from evolution_client import EvolutionClient

def main():
    print("=" * 55)
    print("[*] DISPARO DE MENSAGEM DE TESTE VIA WHATSAPP")
    print("=" * 55)

    client = EvolutionClient()

    # Verifica status primeiro
    try:
        status_info = client.status_conexao()
        estado = status_info.get("instance", {}).get("state")
        if estado != "open":
            print(f"[!] Atencao: A instancia '{client.instance_name}' esta com status '{estado}'.")
            print("Escaneie o QR Code no painel http://localhost:8080/manager antes de enviar.")
            return
    except Exception as e:
        print(f"[!] Nao foi possivel verificar o status da instancia: {e}")

    # Argumentos por linha de comando ou interativo
    if len(sys.argv) >= 3:
        numero = sys.argv[1]
        mensagem = " ".join(sys.argv[2:])
    else:
        print("\nFormato do telefone: DDI + DDD + Numero (ex: 5567999999999)")
        numero = input("Digite o numero de destino: ").strip()
        if not numero:
            print("[-] Numero nao informado. Cancelando envio.")
            return
            
        mensagem = input("Digite o texto da mensagem: ").strip()
        if not mensagem:
            mensagem = "Ola! Esta e uma mensagem de teste enviada via Python + Evolution API! [OK]"

    print(f"\n[>] Enviando mensagem para {numero}...")
    try:
        resultado = client.enviar_texto(numero=numero, texto=mensagem)
        print("[+] Mensagem enviada com sucesso!")
        id_msg = resultado.get("key", {}).get("id")
        if id_msg:
            print(f"    ID da mensagem: {id_msg}")
    except Exception as e:
        print(f"[-] Falha ao enviar mensagem: {e}")

if __name__ == "__main__":
    main()
