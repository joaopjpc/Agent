"""Persistencia SQLite para conversas, aulas experimentais e tickets de atendimento humano."""
from __future__ import annotations

import sqlite3
from pathlib import Path


_BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = _BASE_DIR.parent
DEFAULT_DB_PATH = _BASE_DIR / "data" / "data.sqlite"
DEFAULT_MIGRATIONS_DIR = PROJECT_ROOT / "db" / "migrations"


def apply_migrations(
    connection: sqlite3.Connection, migrations_dir: Path | None = None
) -> None:
    """Aplica migrations SQL em ordem alfabetica, de forma idempotente."""
    directory = Path(migrations_dir) if migrations_dir else DEFAULT_MIGRATIONS_DIR
    directory.mkdir(parents=True, exist_ok=True)

    connection.execute(
        "CREATE TABLE IF NOT EXISTS migrations ("
        "  id TEXT PRIMARY KEY,"
        "  applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        ");"
    )
    connection.commit()

    applied = {row[0] for row in connection.execute("SELECT id FROM migrations")}
    for migration_path in sorted(directory.glob("*.sql"), key=lambda path: path.name):
        migration_id = migration_path.name
        if migration_id in applied:
            continue
        sql = migration_path.read_text(encoding="utf-8")
        connection.executescript(sql)
        connection.execute(
            "INSERT INTO migrations (id) VALUES (?)",
            (migration_id,),
        )
        connection.commit()
        print(f"Applying {migration_id}... OK")


def init_db(path: Path) -> sqlite3.Connection:
    """Cria o arquivo do banco SQLite e garante migrations aplicadas."""
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    apply_migrations(connection)
    return connection


def log_message(
    connection: sqlite3.Connection,
    role: str,
    content: str,
    user_phone: str | None = None,
    session: str | None = None,
) -> None:
    """Armazena uma mensagem no historico da conversa, com opcional telefone e session."""
    connection.execute(
        "INSERT INTO conversas (role, content, user_phone, session) VALUES (?, ?, ?, ?)",
        (role, content, user_phone, session),
    )
    connection.commit()


def registrar_aula_experimental(
    connection: sqlite3.Connection,
    nome: str,
    telefone: str,
    horario_escolhido: str,
    nivel_aluno: str,
    status: str = "confirmacao_pendente",
) -> None:
    """Persiste um pedido de aula experimental."""
    if status not in {"confirmada", "confirmacao_pendente"}:
        raise ValueError("status invalido para aula experimental.")
    connection.execute(
        "INSERT INTO aulas_experimentais (nome, telefone, horario_escolhido, nivel_aluno, status) VALUES (?, ?, ?, ?, ?)",
        (nome, telefone, horario_escolhido, nivel_aluno, status),
    )
    connection.commit()


def confirmar_aula_experimental(connection: sqlite3.Connection, telefone: str) -> bool:
    """Marca como confirmada a aula experimental mais recente para o telefone."""
    cursor = connection.execute(
        "SELECT id FROM aulas_experimentais WHERE telefone = ? ORDER BY id DESC LIMIT 1",
        (telefone,),
    )
    row = cursor.fetchone()
    if not row:
        return False
    (latest_id,) = row
    connection.execute(
        "UPDATE aulas_experimentais SET status = 'confirmada' WHERE id = ?",
        (latest_id,),
    )
    connection.commit()
    return True

