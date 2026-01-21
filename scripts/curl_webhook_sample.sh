#!/usr/bin/env bash
set -euo pipefail

# Envia payload de exemplo para o webhook local (porta 8000).
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

curl -s -X POST "http://localhost:8000/webhook" \
  -H "Content-Type: application/json" \
  --data @"${ROOT_DIR}/samples/messages_upsert_conversation.json"
