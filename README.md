# 🤖 Smash Beach Tennis – AtendentePro 
### ⚠️ Projeto em desenvolvimento (MVP)
Assistente de atendimento para o CT Smash Beach Tennis, baseado no framework **AtendentePro**.

Este projeto implementa um atendente virtual inteligente para um Centro de Treinamento (CT), com o objetivo de substituir o atendimento humano de primeiro nível, automatizando dúvidas frequentes e o agendamento de serviços, utilizando um framework de agentes.

### 🧠 Capacidades do Agente
#### 📝 FAQ
Responder qualquer tipo de pergunta sobre o CT, como local, horários, planos, infos sobre estrutura e serviços etc

#### 🎾 Agendmaneto de Aula Experimental
Agendar aulas experimentais gratuitas com informações mínimas necessárias e registrar/notificar o registro

#### ➕ Agendamento de Outros Serviços 
O CT possui serviços pagos pra alunos matriculados, como Fisioterapia, e serviços pagos pra alunos não matriculados, como aluguel de quadras.
Nesses casos, de serviços pagos, o agente deve ser capaz de escalar a conversa pra um funcionário real, de maneira que notifique o usuário que 
um humano assumirá a conversa em breve. 

## 🧩 Arquitetura Multiagente
Triage (router) direciona a conversa para:
1.  **Flow Agent**: sugere tópicos possíveis e caminhos de atendimento.
2.  **Knowledge Agent**: responde dúvidas do CT usando RAG (embedding combinado dos docs `.md`).
3.  **Interview Agent**: coleta dados para aula experimental.
4.  **Escalation Agent**: chama humano pra registrar pedidos que exigem pagamento (ex.: aluguel de quadra/churrasqueira). Usa horário 11h–19h (env).


## 📂 Estrutura do Projeto
- `beachbot/main_cli.py`: loop de chat em terminal.
- `beachbot/network.py`: cria a rede de agentes (seta canais de escalonamento).
- `beachbot/config/*.yaml`: prompts/configs dos agentes (triage, flow, knowledge, interview, guardrails, style).
- `beachbot/knowledge/`: conteúdo em markdown; embeddings em `knowledge/embeddings/ct_combined.pkl`.
- `beachbot/scripts/build_embeddings.py`: gera embeddings combinando os `.md` (usa `text-embedding-3-large`).
- (Removido) Camada SQLite legado; toda a persistência agora é Postgres via `beachbot/storage/db.py` e migrations Alembic.


## 🏃 Como Rodar
### Pré-requisito: Python 3.10, Crie e ative um ambiente virtual.
  ```
py -3.10 -m venv venv
venv\Scripts\activate
  ```

### 1. Instalar dependencias:
   ```
   pip install -r requirements.txt
   ```
### 2. Configurar `.env` na raiz:
   ```
   ATENDENTEPRO_LICENSE_KEY=...
   OPENAI_API_KEY=...
   ESCALATION_HOUR_START=11
   ESCALATION_HOUR_END=19
   ```
### 3. Gerar embeddings:
   ```
   python beachbot/scripts/build_embeddings.py --preview-out beachbot/knowledge/embeddings/ct_combined_preview.md
   ```
### 4. Criar o banco aplicando migrations: (a partir da raiz do repo)
   ```
   python -m db.migrate
   ```
### 5. Executar o chat:
   ```
   python -m beachbot.main_cli
   ```
### 6. Encerrar: digite `sair`.

## ⚙️ Configuração
- `.env` (na raiz): `ATENDENTEPRO_LICENSE_KEY`, `OPENAI_API_KEY`, `ESCALATION_HOUR_START=11`, `ESCALATION_HOUR_END=19`.
- Embeddings: `knowledge_config.yaml` usa RAG com embeddings de `beachbot/knowledge/embeddings/ct_combined.pkl`.


## Banco de Dados (Dev)
Este projeto utiliza SQLite para desenvolvimento local.
- O banco utilizado é o Postgres apontado por `DATABASE_URL` (migrations Alembic).
- O arquivo do banco **não é versionado** no repositório.
### Aplicar migrations
Cria o banco (se não existir) e aplica todas as migrations:
```bash
python -m db.migrate
