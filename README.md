# IntegraWhatsAPP - Integração WhatsApp com Python & Evolution API v2

Projeto prático para envio e recebimento de mensagens do WhatsApp utilizando Python e Evolution API v2 com banco de dados PostgreSQL via Podman.

---

## 📁 Estrutura de Arquivos

```text
IntegraWhatsAPP/
├── docker-compose.yml     # Containers da Evolution API v2 + PostgreSQL 15
├── requirements.txt       # Dependências Python (FastAPI, Uvicorn, HTTPX, Pydantic)
├── .env                   # Variáveis de ambiente e credenciais
├── evolution_client.py    # Módulo cliente Python reutilizável
├── test_conexao.py        # Script para verificar status das instâncias
├── test_enviar.py         # Script interativo para enviar mensagem de teste
├── webhook_server.py      # Servidor FastAPI para receber mensagens em tempo real
└── README.md              # Documentação de uso
```

---

## 🚀 Como Usar

### 1. Verificar o Status dos Containers
Se os containers não estiverem ativos, inicie-os:
```powershell
podman compose up -d
```
Acesse o painel web em: [http://localhost:8080/manager](http://localhost:8080/manager)

### 2. Testar a Conexão no Python
Execute para ver se o seu WhatsApp está conectado:
```powershell
python test_conexao.py
```

### 3. Enviar uma Mensagem de Teste
Modo interativo (pergunta o número e a mensagem no terminal):
```powershell
python test_enviar.py
```
Ou passe diretamente via argumentos:
```powershell
python test_enviar.py 5567999999999 "Olá do Python!"
```

### 4. Receber Mensagens em Tempo Real (Webhook / Bot)
Inicie o servidor de webhook do Python:
```powershell
python webhook_server.py
```
O servidor ficará escutando na porta `8000`.

Para registrar o webhook na Evolution API:
* No painel web [http://localhost:8080/manager](http://localhost:8080/manager), vá na sua instância > **Webhook** > informe a URL:
  `http://host.containers.internal:8000/webhook` (ou `http://SEU_IP_LOCAL:8000/webhook`).
* Ative os eventos `MESSAGES_UPSERT`.
* Quando qualquer pessoa enviar mensagem para o seu número, o terminal exibirá a mensagem e o robô responderá automaticamente se a pessoa mandar "oi" ou "menu"!
