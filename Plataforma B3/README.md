# Plataforma B3 - Integração com Modelos de IA

Este projeto implementa uma plataforma para integração com modelos de IA, utilizando FastAPI para a API backend e Argo Workflows para orquestração de workflows em Kubernetes.

## Estrutura do Projeto

├── /src
│ ├── /model_integration.py
│ ├── /flow_manager.py
│ ├── /app.py
│ ├── /config.py
│ ├── /database.py
│ ├── /conversion.py
├── requirements.txt
└── README.md


## Requisitos

- Python 3.8+
- Docker
- Azure CLI
- kubectl
- Helm

## Instalação

1. Clone o repositório
2. Crie um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  
   # ou
   .\venv\Scripts\activate
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure o ambiente:
   ```bash
   # Copie o arquivo de exemplo
   cp .env.example .env
   
   # Edite o arquivo .env com suas configurações
   # Substitua 'sua_chave_api_aqui' pela sua chave de API real
   ```

## Configuração

O arquivo `.env` deve conter as seguintes variáveis:

Chave de API para acesso ao modelo
API_KEY=sua_chave_api_aqui
URL do endpoint do modelo
MODEL_URL=https://b3gpt.intraservice.azr/internal-api/b3gpt-llms/v1/openai/deployments/gpt4o/chat/completions
URL do servidor Argo
ARGO_SERVER_URL=http://<EXTERNAL-IP>:2746
Configurações do banco de dados (opcional)
DATABASE_URL=sqlite:///./data/flows.db
Configurações da aplicação
APP_NAME=Plataforma B3 - IA
DEBUG=False

## Executando o Projeto

1. Crie o diretório para o banco de dados:
   ```bash
   mkdir data
   ```

2. Execute a API FastAPI:
   ```bash
   uvicorn src.app:app --host 0.0.0.0 --port 8000
   ```

## Funcionalidades

1. **Criação de Fluxos**:
   - Nome e descrição do fluxo
   - Configuração de múltiplos passos
   - System prompt para cada passo
   - Temperatura configurável

2. **Teste de Fluxos**:
   - Teste em tempo real
   - Visualização de respostas por passo
   - Resposta final consolidada

3. **Gerenciamento de Fluxos**:
   - Listagem de fluxos existentes
   - Teste de fluxos existentes
   - Deleção de fluxos

4. **Persistência**:
   - Armazenamento em banco de dados SQLite
   - Dados mantidos entre execuções
   - Backup automático

5. **Execução de Workflows com Argo**:
   - Submissão de workflows ao Argo
   - Monitoramento de execução via Argo UI

## Configuração do Docker, AKS e Argo

### Docker

1. **Criar Dockerfile**:
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY . .
   RUN pip install -r requirements.txt
   CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Construir e Publicar a Imagem Docker**:
   ```bash
   docker build -t <seu-usuario>/<seu-repositorio>:<tag> .
   docker push <seu-usuario>/<seu-repositorio>:<tag>
   ```

### Azure Kubernetes Service (AKS)

1. **Configurar Azure CLI**:
   ```bash
   az login
   az account set --subscription "Your Subscription Name"
   ```

2. **Obter Credenciais do AKS**:
   ```bash
   az aks get-credentials --resource-group <seu-grupo-de-recursos> --name <seu-cluster-aks>
   ```

3. **Criar Manifests Kubernetes**:
   ```yaml
   # deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: plataforma-b3
     namespace: default
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: plataforma-b3
     template:
       metadata:
         labels:
           app: plataforma-b3
       spec:
         containers:
         - name: plataforma-b3
           image: <seu-usuario>/<seu-repositorio>:<tag>
           ports:
           - containerPort: 8000
   ```

   ```yaml
   # service.yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: plataforma-b3
     namespace: default
   spec:
     type: LoadBalancer
     selector:
       app: plataforma-b3
     ports:
       - protocol: TCP
         port: 80
         targetPort: 8000
   ```

4. **Aplicar Manifests**:
   ```bash
   kubectl apply -f deployment.yaml
   kubectl apply -f service.yaml
   ```

### Argo Workflows

1. **Instalar o Argo Workflows**:
   ```bash
   helm repo add argo https://argoproj.github.io/argo-helm
   helm install argo argo/argo-workflows --namespace argo
   ```

2. **Expor o Argo UI**:
   ```bash
   kubectl -n argo port-forward deployment/argo-server 2746:2746
   ```

3. **Submeter Workflows**:
   - Use a API do Argo para submeter workflows definidos em YAML.

## Exemplo de Uso

1. Execute a aplicação:
   ```bash
   uvicorn src.app:app --host 0.0.0.0 --port 8000
   ```

2. Crie um novo fluxo:
   - Digite o nome e descrição
   - Configure os passos
   - Defina os prompts e temperaturas

3. Teste o fluxo:
   - Digite uma mensagem
   - Veja as respostas de cada passo
   - Analise a resposta final

4. Gerencie fluxos:
   - Visualize fluxos existentes
   - Teste fluxos salvos
   - Delete fluxos quando necessário

5. Execute workflows com Argo:
   - Submeta o YAML do workflow ao Argo
   - Monitore a execução via Argo UI