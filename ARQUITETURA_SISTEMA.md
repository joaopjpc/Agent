# 🏗️ Arquitetura Atual do Sistema – Atendente Smash BT

## 📊 Diagrama de Fluxo de Agentes (pode haver fallback)

```

┌─────────────────────────────────────────────────────────────────┐
│ USUÁRIO                                                         │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│ TRIAGE AGENT                                                    │
│ • Entrada                                                       │
│ • Roteamento                                                    │
└─────────────────────┬───────────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ FLOW AGENT  │ │  KNOWLEDGE  │ │  ESCALATION │
│             │ │     AGENT   │ │     AGENT   │
│ • Opções    │ │• Arquivos.md│ │   • Humano  │
│ • Direção   │ │             │ │             │
└─────┬───────┘ └─────┬───────┘ └─────────────┘
      │               │
      ▼               ▼
┌─────────────┐ ┌──ainda sem──┐
│ INTERVIEW   │ │    ANSWER   │
│ AGENT       │ │ AGENT       │
│             │ │             │
│ • Coleta    │ │ • Síntese   │
│ dados agend.│ │   final     │
│ • Cria      │ │ • Resposta  │
│ estado      │ │             │
└─────┬───────┘ └─────────────┘
      │
      ▼
┌─ainda sem───┐
│ ANSWER      │
│ AGENT       │
│             │
│ • Mensagem  │
│ final       │
└─────────────┘

```

