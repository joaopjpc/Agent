# 🤖 Deploy em VPS (Produção)

Este documento descreve como o **Smash BT Agent** é executado em produção,
rodando 24/7 em uma VPS Linux, integrado ao WhatsApp via **Evolution API**,
com persistência em **PostgreSQL** e backend em **FastAPI**.

O deploy foi pensado para ser **simples, estável e reproduzível**, sem uso de Kubernetes,
API oficial do Meta ou serviços gerenciados.

---

## 🛰️ Visão geral da arquitetura

```text
Usuário (WhatsApp)
        ↕
Evolution API (WhatsApp Gateway)
        ↕  Webhook HTTP
Bot FastAPI (Uvicorn)
        ↕
PostgreSQL (persistência)
```

Todos os serviços rodam na **mesma VPS**, isolados via **Docker Compose**.

---

## 🏗️ Ambiente de produção

- VPS: ex. DigitalOcean
- SO: Ubuntu 22.04+
- Execução: Docker + Docker Compose
- Caminho do projeto na VPS: `/opt/ct-bot`

---

## 🛠️ Primeiro deploy em produção

1) Criar `.env` na VPS (exemplo):
   ```env
   PORT=8000
   LOG_LEVEL=INFO
   DATABASE_URL=postgresql://evolution:********@postgres:5432/beachbot_db

   OPENAI_API_KEY=********
   ATENDENTEPRO_LICENSE_KEY=********

   EVOLUTION_BASE_URL=http://evolution-api:8080
   EVOLUTION_APIKEY=********
   EVOLUTION_INSTANCE=Smash_MONKAI
   ```
   > `postgres` só resolve dentro da rede Docker; fora use `localhost` ou IP.

2) Subir containers:
   ```bash
   docker compose up -d
   docker compose ps
   ```

3) Executar migrations (primeira vez e a cada mudança de schema):
   ```bash
   docker compose exec bot alembic upgrade head
   ```

4) Verificar logs:
   ```bash
   docker compose logs -f bot
   docker compose logs -f evolution-api
   ```

---

## 🔄 Atualização de código (deploys posteriores)

Fluxo seguro:
1) Atualizar código
   ```bash
   git pull
   ```
2) Rebuild/reativar containers
   ```bash
   docker compose up -d --build
   ```
3) Rodar migrations (se mudou schema)
   ```bash
   docker compose exec bot alembic upgrade head
   ```
4) Conferir status/logs
   ```bash
   docker compose ps
   docker compose logs -f bot
   ```

> `git pull` sozinho **não** atualiza containers em execução. Use `docker compose up -d --build` após trazer código novo.

---

## 🗄️ Migrations de banco (Alembic)

- **Primeiro deploy**: obrigatório rodar `alembic upgrade head` (no container do bot).
- **Atualizações**: rodar sempre que houver mudança de schema.
- **Não é automático**: se não rodar, o bot pode falhar ao acessar colunas/tabelas novas.

Comando padrão:
```bash
docker compose exec bot alembic upgrade head
```

---

## 💾 Backup e restore do PostgreSQL

- Faça backup offsite (fora da VPS).
- Não dependa do volume Docker como único ponto de recuperação.

Exemplos:
```bash
# Backup
docker compose exec postgres pg_dump -U evolution -d beachbot_db > /tmp/beachbot_backup.sql

# Restore (atenção: sobrescreve dados)
docker compose exec -T postgres psql -U evolution -d beachbot_db < /tmp/beachbot_backup.sql
```

---

## 🩺 Estabilidade e saúde

- Logs: `docker compose logs -f bot` e `docker compose logs -f evolution-api`
- Health do Postgres: `docker compose exec postgres pg_isready -U evolution -d beachbot_db`
- Se o bot reiniciar em loop:
  - confira `.env` (chaves/URLs/DB)
  - veja trace em `docker compose logs -f bot`
  - garanta Postgres up (`pg_isready`) e migrations aplicadas

---

## 🔒 Segurança operacional

- Restrinja portas expostas (ideal: só 80/443 via proxy; evite expor 5432).
- Proteja o `.env` (somente root/usuário de deploy).
- Use firewall (UFW ou regras na cloud) liberando só o necessário.
- Nunca rode `docker compose down -v` em produção (apaga o banco).

---

## 🧭 CLI local x Produção

- CLI local: Postgres local (`DATABASE_URL` para localhost/compose local), sem Evolution.
- Produção: containers na VPS (Postgres, Evolution API, bot) 24/7.
- Mantenha `.env` separados (local vs. produção).

---

## 🗺️ Roadmap

📌 Veja: [ROADMAP.md](ROADMAP.md)
