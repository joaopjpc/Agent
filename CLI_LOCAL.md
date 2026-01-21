# Rodando o CLI local

Use este passo a passo para rodar o chat em terminal, com Postgres local (ou remoto) e sem precisar da Evolution API.

## 1) Pré-requisitos
- Python 3.10
- Docker + Docker Compose (usaremos o compose para subir o Postgres e criar o DB automaticamente)
- Chaves: `OPENAI_API_KEY` e `ATENDENTEPRO_LICENSE_KEY`

## 2) Clone e ambiente
```bash
git clone <seu-repo>.git
cd Smash-BT-Agent
py -3.10 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 3) Subir Postgres (via Docker Compose)
Use o `docker-compose.yml` do projeto para criar o banco automaticamente:
```bash
docker compose up -d
```
Isso cria um Postgres local em `localhost:5432` com user/pass/db `beachbot`.

## 4) Configurar `.env`
```bash
copy .env.example .env
```
Edite `.env` com pelo menos:
```
DATABASE_URL=postgresql://beachbot:beachbot@localhost:5432/beachbot_db   # ou seu servidor
OPENAI_API_KEY=...
ATENDENTEPRO_LICENSE_KEY=...
ESCALATION_HOUR_START=11
ESCALATION_HOUR_END=19
```
Campos da Evolution podem ficar comentados para o CLI.

## 5) Criar schema
```bash
alembic upgrade head
```

## 6) Gerar embeddings (RAG)
```bash
python beachbot/scripts/build_embeddings.py --preview-out beachbot/knowledge/embeddings/ct_combined_preview.md
```

## 7) Rodar o chat
```bash
python -m beachbot.main_cli
```
Siga o prompt (triage padrão ou custom). Digite `sair` para encerrar.

## 8) (Opcional) Conferir dados
```sql
SELECT id, phone, last_seen_at FROM clients ORDER BY id DESC LIMIT 5;
SELECT role, direction, text FROM messages ORDER BY ts DESC LIMIT 5;
```
