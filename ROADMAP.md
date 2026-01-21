# Roadmap

## Marco 0 — Base (DONE)
- [x] Estrutura dos agentes e rede
- [x] Knowledge base (MD) + embeddings pra RAG
- [x] Persistencia: log de mensagens no banco SQLite
- [x] Respostas sobre todas as infos do CT
- [x] Escalar serviços com pagamento pra ser humano
- [x] Testes de dúvidas gerais e escalation pra servicos de pagamento E2E no CLI
- [x] Investigar e corrigir ambiguidades no Triage Agent (dúvidas de agendamento x agendamento real triagem ambígua só com keywords)

## Marco 1 — Aula experimental (IN PROGRESS)
Objetivo: quando o cliente confirmar, registrar aula experimental no banco.

- [x] Definir modelo de dados (aulas_experimentais no banco)
- [x] Implementar migrations SQL
- [ ] Criar Agent Tool: registrar_aula_experimental()
- [ ] Integrar tool de registrar aula experimental no fluxo interview.yaml
- [ ] Usar Confirmation Agent pra confirmar agendamento experimental
- [ ] Testes de agendamento de aula experimental E2E no CLI
- [ ] Disponibilizar .md com testes explícitos

## Marco 2 — Smash-BT Agent no WhatsApp (NOT STARTED)
Objetivo : manter o chatbot ativo 24/7 no WhatsApp hospedado em VPS

