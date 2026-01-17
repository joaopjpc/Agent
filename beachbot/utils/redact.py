"""Funcoes utilitarias para mascarar dados sensiveis em logs."""
from __future__ import annotations

import re
from typing import Any


def mask_phone(phone: Any, keep_last: int = 4) -> str:
    """Mascara um numero de telefone, mantendo apenas os ultimos digitos visiveis."""
    if phone is None:
        return "***"

    digits = re.findall(r"\d", str(phone))
    if not digits:
        return "***"

    keep_last = max(0, keep_last)
    visible = "".join(digits[-keep_last:]) if keep_last else ""
    hidden_len = max(len(digits) - len(visible), 0)
    masked_prefix = "*" * hidden_len if hidden_len else "*" * len(visible or digits)

    return f"{masked_prefix}{visible}" if visible else masked_prefix
