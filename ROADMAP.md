# Roadmap

## Marco 0 — Base (DONE)
- [x] Estrutura dos agentes e rede
- [x] Knowledge base (MD) + embeddings
- [x] Persistencia: log de mensagens no banco SQLite
- [x] Respostas sobre todas as infos do CT
- [x] Testes de duvidas e escalation com servicos de pagamento E2E no CLI

## Marco 1 — Aula experimental (IN PROGRESS)
Objetivo: quando o cliente confirmar, registrar aula experimental no banco.

- [x] Definir modelo de dados (aulas_experimentais no banco)
- [x] Implementar migrations SQL
- [ ] Criar Agent Tool: register_trial_lesson()
- [ ] Integrar tool de registrar aula experimental no fluxo interview.yaml
- [ ] Testes de agendamento de aula experimental E2E no CLI
