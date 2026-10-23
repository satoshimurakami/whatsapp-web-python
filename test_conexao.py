import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from evolution_client import EvolutionClient

def main():
    print("=" * 55)
    print("[*] VERIFICANDO CONEXAO COM A EVOLUTION API...")
    print("=" * 55)

    client = EvolutionClient()
    
    try:
        instancias = client.listar_instancias()
        print(f"[+] Total de instancias encontradas: {len(instancias)}")
        
        for inst in instancias:
            nome = inst.get("name")
            status = inst.get("connectionStatus")
            status_desc = "Conectado" if status == "open" else "Desconectado"
            numero = inst.get("ownerJid") or inst.get("number")
            print(f"\n[>] Instancia: {nome}")
            print(f"    Status: {status} ({status_desc})")
            print(f"    Numero Conectado: {numero}")
            
    except Exception as e:
        print(f"[-] Erro ao consultar a API: {e}")
        print("Certifique-se de que o container 'evolution_api' esta rodando na porta 8080.")

if __name__ == "__main__":
    main()
