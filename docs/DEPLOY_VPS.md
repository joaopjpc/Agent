# Deploy em VPS (produção)

> Rascunho: personalize conforme sua infra (domínio, SSL, proxy, firewall, jobs, observabilidade).

Pontos para cobrir aqui:
- Requisitos da VPS (CPU/RAM/disk) e sistema operacional.
- Instalação do Docker/Docker Compose.
- Configuração do `.env` seguro (tokens, DATABASE_URL, WEBHOOK_SECRET).
- Subir `docker-compose.yml` com Postgres, Evolution API e o bot.
- Exposição do webhook público e apontamento no Evolution Manager.
- Rotina de migrations (`alembic upgrade head`) e backup do Postgres.
- Logs/monitoramento e política de restart.

Edite este arquivo com os detalhes específicos do seu ambiente.
