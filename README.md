# Yamamotto AI Agent

Este repositório contém o código fonte do Agente de IA da Yamamotto Multimarcas, desenvolvido para atuar como um especialista em suporte via WhatsApp. O agente é construído sobre o Google ADK (Agent Development Kit) e customizado para rodar em containers Docker, pronto para deploy no Google Cloud Run.

## 🚀 Funcionalidades

- **Persona Especializada:** Atua como um especialista técnico da Yamamotto, focado em hardware e suporte.
- **Integração WhatsApp:** Otimizado para respostas curtas e diretas, estilo chat.
- **Containerizado:** Pronto para execução em qualquer ambiente Docker.
- **Resiliência:** Inclui scripts de correção automática (`patch_genai.py` e `run_server.py`) para garantir compatibilidade entre bibliotecas modernas (Pydantic v2) e o Google ADK.

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.12
- **Framework:** Google ADK & FastAPI
- **Infraestrutura:** Docker & Google Cloud Run
- **IA:** Google Gemini (via `google-genai`)

## 📂 Estrutura do Projeto

```
.
├── my_agent/           # Código fonte do agente (prompts e lógica)
├── Dockerfile          # Definição da imagem Docker
├── requirements.txt    # Dependências do projeto
├── run_server.py       # Entrypoint customizado com correções de runtime
├── patch_genai.py      # Script de correção de bibliotecas (build-time)
└── README.md           # Documentação
```

## ⚙️ Como Rodar Localmente

### Pré-requisitos

- Docker instalado
- Chave de API do Google Gemini (`GOOGLE_API_KEY`)

### 1. Build da Imagem

```bash
docker build -t yamamotto-agent .
```

### 2. Executar o Container

```bash
docker run -p 8080:8080 -e GOOGLE_API_KEY="sua_chave_aqui" yamamotto-agent
```

O servidor estará acessível em `http://localhost:8080`.

> **Nota:** A documentação interativa (`/docs`) pode apresentar um aviso de erro de schema devido a correções de compatibilidade, mas a API estará funcional.

## ☁️ Deploy no Google Cloud Run

1. **Subir a imagem para o Docker Hub:**
   ```bash
   docker tag yamamotto-agent seu-usuario/yamamotto-agent:latest
   docker push seu-usuario/yamamotto-agent:latest
   ```

2. **Criar Serviço no Cloud Run:**
   - Selecione "Deploy one revision from an existing container image".
   - Use a imagem que você acabou de subir.
   - Em "Variables & Secrets", adicione a variável de ambiente `GOOGLE_API_KEY`.
   - Defina a porta do container como `8080`.

## 🔧 Solução de Problemas (Patches)

Este projeto utiliza dois mecanismos de correção para contornar incompatibilidades conhecidas entre o `google-adk` e o `pydantic` v2:

1. **`patch_genai.py`**: Executado durante o build do Docker, corrige problemas de serialização na biblioteca `google-genai`.
2. **`run_server.py`**: Um wrapper que inicia o servidor FastAPI, aplicando correções em tempo de execução para evitar erros de validação de tipos (`types.GenericAlias`) e garantir a estabilidade do serviço.

---
Desenvolvido por Masterbarreto.
