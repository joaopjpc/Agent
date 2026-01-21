# 🚀 Deploy em VPS (Produção)

Este documento descreve como o **Smash BT Agent** é executado em produção,
rodando 24/7 em uma VPS Linux, integrado ao WhatsApp via **Evolution API**,
com persistência em **PostgreSQL** e backend em **FastAPI**.

O deploy foi pensado para ser **simples, estável e reproduzível**, sem uso de Kubernetes,
API oficial do Meta ou serviços gerenciados.

---

## 🧠 Visão geral da arquitetura

```text
Usuário (WhatsApp)
        ↓
Evolution API (WhatsApp Gateway)
        ↓  Webhook HTTP
Bot FastAPI (Uvicorn)
        ↓
PostgreSQL (persistência)
```

Todos os serviços rodam na **mesma VPS**, isolados via **Docker Compose**.

---

## 🖥️ Ambiente de produção

- VPS: DigitalOcean
- Sistema operacional: Ubuntu 22.04+
- Execução: Docker + Docker Compose
- Caminho do projeto na VPS:

```text
/opt/ct-bot
```

---

## 🧱 Serviços em produção

O ambiente é composto por **3 containers principais**:

### 1️⃣ PostgreSQL
- Banco relacional para persistência
- Armazena:
  - clientes
  - conversas
  - mensagens
  - agendamentos de aula experimental
- Dados persistidos via **volume Docker**

### 2️⃣ Evolution API
- Gateway WhatsApp (Baileys)
- Recebe mensagens do WhatsApp
- Encaminha eventos para o webhook do bot
- Envia respostas geradas pelo bot

### 3️⃣ Bot (FastAPI)
- Backend em Python
- Recebe eventos do WhatsApp via webhook
- Executa lógica do agente (AtendentePro / MonkAI)
- Persiste dados no PostgreSQL
- Envia respostas via Evolution API

---

## ⚙️ Variáveis de ambiente (produção)

As variáveis sensíveis **não são versionadas**.

Arquivo `.env` (exemplo):

```env
# === Bot ===
PORT=8000
LOG_LEVEL=INFO
DATABASE_URL=postgresql://evolution:********@postgres:5432/beachbot_db

# === OpenAI / MonkAI ===
OPENAI_API_KEY=********
ATENDENTEPRO_LICENSE_KEY=********

# === Evolution API ===
EVOLUTION_BASE_URL=http://evolution-api:8080
EVOLUTION_APIKEY=********
EVOLUTION_INSTANCE=Smash_MONKAI
```

⚠️ **Importante**:
- O hostname `postgres` funciona apenas **dentro da rede Docker**
- Fora do Docker (ex: CLI local), o acesso deve ser via `localhost`

---

## 🐳 Subindo o ambiente em produção

Na VPS, dentro do diretório do projeto:

```bash
docker compose up -d
```

Verificar status dos containers:

```bash
docker compose ps
```

Visualizar logs do bot:

```bash
docker compose logs -f bot
```

---

## 🔁 Atualizando o código em produção

O fluxo de atualização é:

```text
git pull
docker compose up -d --build
```

⚠️ **Observação importante**  
O `git pull` **não altera containers em execução**.  
Somente ao rodar `docker compose up -d` o novo código é aplicado.

---

## 🛑 Cuidados em produção

- ❌ Nunca rodar:
```bash
docker compose down -v
```

Isso apagaria os volumes e o banco de dados.

- ❌ Não alterar em produção sem cuidado:
  - POSTGRES_USER
  - POSTGRES_PASSWORD
  - POSTGRES_DB
  - volumes Docker

- ✅ Logs devem ser monitorados via `docker compose logs`

---

## 🧪 CLI e ambiente local

O **CLI de desenvolvimento** não deve ser executado na VPS.

- CLI usa **PostgreSQL local**
- Produção usa **PostgreSQL do Docker na VPS**
- Ambientes são isolados propositalmente

📄 Veja: `docs/CLI_LOCAL.md`

---

## 📦 Persistência de dados

- O banco utiliza **volume Docker**
- Reiniciar containers **não apaga dados**
- Apenas `down -v` remove o volume

---

## 📌 Observações finais

Este deploy prioriza:
- simplicidade
- baixo custo
- controle total da infraestrutura
- facilidade de debug

A arquitetura permite evoluir futuramente para:
- múltiplas instâncias WhatsApp
- dashboard administrativo
- cache (Redis)
- multi-tenancy

---

## 🗺️ Roadmap

📄 Veja: `docs/ROADMAP.md`
