# Roadmap

## Marco 0 — Base (DONE)
Objetivo: agente funcional em CLI, com RAG, triagem e persistência básica.

- [x] Estrutura dos agentes e rede (AtendentePro)
- [x] Knowledge base (MD) + geração de embeddings para RAG
- [x] Persistência inicial de mensagens (SQLite)
- [x] Respostas sobre todas as informações do CT (FAQ)
- [x] Escalonamento de serviços pagos para atendimento humano
- [x] Testes E2E de dúvidas gerais e escalation no CLI
- [x] Investigação e correção de ambiguidades no Triage Agent
      (agendamento x dúvidas sobre agendamento)

---

## Marco 1 — Backend estruturado e banco relacional (DONE)
Objetivo: preparar o backend para produção real.

- [x] Migração de SQLite para PostgreSQL
- [x] Modelagem relacional (clients, conversations, messages, aulas_experimentais)
- [x] Configuração de SQLAlchemy + sessões
- [x] Implementação de migrations com Alembic
- [x] Persistência completa de histórico de conversas
- [x] Fetch de histórico recente para contexto do agente
- [x] CLI rodando exclusivamente com PostgreSQL
- [x] Separação de ambientes via `.env` e `.env.example`

---

## Marco 2 — Aula experimental (IN PROGRESS)
Objetivo: registrar aulas experimentais confirmadas no banco.

- [x] Definir modelo de dados (aulas_experimentais)
- [x] Criar migrations SQL correspondentes
- [ ] Criar Agent Tool: `registrar_aula_experimental()`
- [ ] Integrar tool no fluxo `interview.yaml`
- [ ] Usar Confirmation Agent para confirmar agendamento
- [ ] Testes E2E de agendamento de aula experimental no CLI
- [ ] Documentar casos de teste em `.md`

---

## Marco 3 — Infraestrutura local com Docker (DONE)
Objetivo: padronizar ambiente de desenvolvimento e banco.

- [x] Docker Compose para Postgres local (CLI mode)
- [x] Volume Docker para persistência de dados
- [x] Alinhamento de `DATABASE_URL` com SQLAlchemy
- [x] Documentação de execução do CLI local
- [x] Separação clara entre CLI local e produção

---

## Marco 4 — Integração WhatsApp (DONE)
Objetivo: conectar o agente ao WhatsApp via gateway.

- [x] Integração com Evolution API (Baileys)
- [x] Webhook FastAPI para eventos `messages.upsert`
- [x] Parser tolerante para mensagens WhatsApp
- [x] Envio de respostas via Evolution Client
- [x] Buffer de mensagens (janela de 15s)
- [x] Persistência de mensagens recebidas e enviadas
- [x] Testes de conversas reais via WhatsApp

---

## Marco 5 — Deploy em VPS (DONE)
Objetivo: manter o bot ativo 24/7 em produção.

- [x] Docker Compose com bot, PostgreSQL e Evolution API
- [x] Configuração de rede interna Docker
- [x] Uso de volumes para persistência em produção
- [x] Variáveis de ambiente segregadas (produção)
- [x] Execução de migrations em container
- [x] Documentação completa de deploy em VPS
- [x] Estratégia de update seguro (`git pull` + rebuild)
- [x] Procedimento de backup e restore do banco
- [x] Diagnóstico de falhas e monitoramento via logs

---

## Marco 6 — Estabilização e próximos passos (PLANNED)
Objetivo: consolidar a solução e preparar evolução futura.

- [ ] Melhorar observabilidade (logs estruturados)
- [ ] Healthcheck HTTP do bot
- [ ] Rotação de logs
- [ ] Dashboard administrativo básico
- [ ] Suporte a múltiplas instâncias WhatsApp
- [ ] Cache (Redis) para otimização
- [ ] Multi-tenancy
