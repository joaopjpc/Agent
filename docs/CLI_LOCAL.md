# Rodando o CLI local

Este guia parte de um clone limpo do repositório e usa **apenas Postgres** (SQLite legado foi removido). A Evolution API não é necessária para o CLI.

## 1) Pré-requisitos
- Python 3.10
- Postgres acessível (local ou remoto) e um banco vazio, por exemplo `beachbot_db`.
- Chaves: `OPENAI_API_KEY` e `ATENDENTEPRO_LICENSE_KEY`.

## 2) Clonar e preparar o ambiente
```bash
git clone <seu-repo>.git
cd Smash-BT-Agent
py -3.10 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 3) Configurar variáveis de ambiente
Copie o modelo e preencha:
```bash
copy .env.example .env
```
Edite `.env` com pelo menos:
```
DATABASE_URL=postgresql://user:senha@localhost:5432/beachbot_db
OPENAI_API_KEY=...
ATENDENTEPRO_LICENSE_KEY=...
ESCALATION_HOUR_START=11
ESCALATION_HOUR_END=19
```
> Dica: se estiver usando Postgres em Docker local, suba-o antes ou aponte `DATABASE_URL` para um servidor existente.

## 4) Aplicar migrations
Crie o schema no Postgres:
```bash
alembic upgrade head
```

## 5) Gerar embeddings (RAG)
```bash
python beachbot/scripts/build_embeddings.py --preview-out beachbot/knowledge/embeddings/ct_combined_preview.md
```

## 6) Rodar o chat em terminal
```bash
python -m beachbot.main_cli
```
Siga o prompt (modo triage padrão ou custom). Digite `sair` para encerrar.

## 7) (Opcional) Verificar dados no banco
Conecte-se ao Postgres e consulte:
```sql
SELECT id, phone, last_seen_at FROM clients ORDER BY id DESC LIMIT 5;
SELECT role, direction, text FROM messages ORDER BY ts DESC LIMIT 5;
```
