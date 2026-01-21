# Smash Beach Tennis - AtendentePro

Assistente virtual para o CT Smash Beach Tennis, usando o framework **AtendentePro**. Atende FAQ, agenda aula experimental e faz handoff para humano quando necessário.

## Capacidades
- FAQ: informações gerais do CT (estrutura, serviços, planos, localização).
- Aula experimental: coleta dados mínimos e registra intenção.
- Escalonamento: direciona pedidos pagos para atendimento humano (janela 11h–19h).

## Arquitetura Multiagente
- **Triage/Router**: decide qual agente atende.
- **Flow Agent**: sugere próximos passos.
- **Knowledge Agent**: responde via RAG com os arquivos `beachbot/knowledge/*.md`.
- **Interview Agent**: coleta dados da aula experimental.
- **Escalation Agent**: cuida de solicitações pagas e handoff.

## Estrutura do Projeto
- `beachbot/main_cli.py`: chat via terminal (usa o mesmo handler do webhook).
- `beachbot/webhook/server.py`: FastAPI com `/webhook` (Evolution API).
- `beachbot/core/handler.py`: orquestra parser, buffer de 15s, agentes e persistência.
- `beachbot/storage/db.py`: modelos SQLAlchemy (Postgres) e helpers.
- `alembic/`: migrations do Postgres.
- `beachbot/config/*.yaml`: prompts e guardrails dos agentes.
- `beachbot/knowledge/`: base de conhecimento + embeddings em `knowledge/embeddings/ct_combined.pkl`.
- `beachbot/scripts/build_embeddings.py`: geração de embeddings (text-embedding-3-large).
- `docker-compose.yml` e `dockerfile`: suporte a deploy com Evolution API + Postgres.

## Documentação
- [Deploy em VPS (produção)](docs/DEPLOY_VPS.md)
- [Rodando o CLI local](docs/CLI_LOCAL.md)
- [Roadmap](docs/ROADMAP.md)
