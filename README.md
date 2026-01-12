# 🤖 Smash Beach Tennis – AtendentePro (Multi-Agentes)

Assistente de atendimento para o CT Smash Beach Tennis, baseado no framework **AtendentePro**.

## 🧩 Arquitetura Implementada
Triage (router) direciona a conversa para:
1. 🧭 **Flow Agent**: sugere tópicos e caminhos de atendimento.
2. 🗂️ **Knowledge Agent**: responde dúvidas do CT usando RAG (embedding combinado dos `.md`).
3. 🎤 **Interview Agent**: coleta dados para aula experimental.
4. 🚨 **Escalation Agent**: registra pedidos que exigem humano (ex.: aluguel de quadra/churrasqueira). Usa horário 11h–19h (env).
5. 📨 **Feedback/Answer**: desabilitados por padrão (podem ser ativados no `network.py`).

## 📂 Estrutura do Projeto
- `beachbot/main_cli.py`: loop de chat em terminal.
- `beachbot/network.py`: cria a rede de agentes (seta canais de escalonamento).
- `beachbot/escolinha_beach/*.yaml`: prompts/configs dos agentes (triage, flow, knowledge, interview, guardrails, style).
- `beachbot/content/`: conteúdo em markdown; embeddings em `content/embeddings/ct_combined.pkl`.
- `beachbot/scripts/build_embeddings.py`: gera embeddings combinando os `.md` (usa `text-embedding-3-large`).
- `beachbot/db.py` e `tools.py`: persistência SQLite e tools expostas para agentes.

## 🔍 Evidências de Teste
- Triagem em formato dicionário validada (veja `triage-format-test/`).
- Knowledge consulta RAG via `ct_combined.pkl` (5 chunks).

## 🏃 Como Rodar
1. Ativar venv (se aplicável): `.\venv310\Scripts\activate`
2. Na raiz do projeto: `cd beachbot`
3. Gerar embeddings (opcional, se atualizou `.md`):
   ```
   python scripts/build_embeddings.py --preview-out content/embeddings/ct_combined_preview.md
   ```
4. Executar o chat:
   ```
   python -m beachbot.main_cli
   ```
5. Encerrar: digite `sair`.

## ⚙️ Configuração
- `.env` (na raiz): `ATENDENTEPRO_LICENSE_KEY`, `OPENAI_API_KEY`, `ESCALATION_HOUR_START=11`, `ESCALATION_HOUR_END=19`.
- Embeddings: `knowledge_config.yaml` aponta para `beachbot/content/embeddings/ct_combined.pkl`.
- Para ativar Answer/Feedback, ajuste `include_answer`/`include_feedback` em `beachbot/network.py`.

## 🚫 Git
- `beachbot/data/data.sqlite` ignorado (artefato de runtime).
