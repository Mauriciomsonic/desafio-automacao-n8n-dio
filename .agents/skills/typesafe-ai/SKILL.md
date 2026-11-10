---
name: typesafe-ai
description: >-
  Build AI-powered software with TypeSafe: small units of AI intelligence you
  can use like programming primitives. Its System One models, including Jev,
  turn natural language and application state into typed judgments and
  probabilities that code can combine. Use when a feature needs programmable
  common sense, when brainstorming what AI could make possible in an app, or
  when an LLM prompt-and-parse step could become a structured decision.
  Applications include routing, ranking, extraction, verification, and
  interactive experiences.
---

# Build with TypeSafe (System One AI)

TypeSafe makes units of AI intelligence usable like programming primitives: small
judgments you can compose into larger capabilities. Its **System One models** return
fast, focused judgments that software can consume directly. **Jev** is TypeSafe's
flagship and first System One model. It understands natural language and returns
typed answers and probabilities rather than generating unconstrained text or reasoning
explanations. Code owns the workflow; the model supplies programmable common sense
where ordinary code needs semantic understanding.

---

## 1. Core Principles

- **Code Owns the Workflow**: Do not delegate execution logic or control flow to the model. Use code for loops, database lookups, business rules, math, and API calls.
- **Fast, Structured Decisions**: System One models (inspired by Daniel Kahneman's fast, intuitive cognitive processing) output typed, calibrated values in milliseconds instead of slow, token-by-token generative text.
- **Confidence as a Second Axis**: Every TypeSafe decision returns both the chosen answer/probability and a **confidence score** ($0.0$ to $1.0$). Code uses confidence to determine whether to act autonomously, flag for human review, or cascade to fallback logic.

---

## 2. The Three Question Primitives

Every interaction with TypeSafe is structured as application state plus one or more typed questions.

### 1. `Choice` (Selection from Closed Options)
Selects the best option from a predefined list and returns the probability distribution across all choices.
```json
{
  "type": "choice",
  "question": "Qual é o perfil de risco mais adequado para este investidor com base no histórico?",
  "options": [
    { "id": "conservador", "description": "Foco estrito em preservação de capital e liquidez imediata" },
    { "id": "moderado", "description": "Aceita oscilações moderadas em busca de ganhos reais acima do CDI" },
    { "id": "arrojado", "description": "Tolera alta volatilidade em busca de retorno máximo no longo prazo" }
  ]
}
```

### 2. `Score` (Ordinal Rating against Explicit Levels)
Rates content against ordered, descriptive levels (e.g., risk level, suitability score, compliance tier).
```json
{
  "type": "score",
  "question": "Qual é o grau de aderência deste produto financeiro à capacidade financeira do cliente?",
  "levels": [
    { "score": 1, "description": "Incompatível: aporte mínimo excede o patrimônio disponível" },
    { "score": 2, "description": "Ajustado: consome entre 50% e 100% do saldo em conta" },
    { "score": 3, "description": "Excelente: aporte representa menos de 50% do saldo, permitindo diversificação" }
  ]
}
```

### 3. `Noul` (Calibrated Yes/No Probability)
Evaluates whether a specific condition or assertion holds true, returning a well-calibrated probability ($0.0$ to $1.0$).
```json
{
  "type": "noul",
  "question": "O cliente possui reserva de emergência mínima suficiente para alocar em ativos de risco?"
}
```

---

## 3. Key Architectural Patterns

### Pattern A: Confidence-Gated Routing
Use the model's confidence to gate autonomous actions:
- **Confidence $\ge 0.85$**: Execute automated action directly in code.
- **Confidence $0.60 - 0.84$**: Request secondary confirmation or route to human specialist.
- **Confidence $< 0.60$**: Fallback to safe default (fail-safe mode).

### Pattern B: Route and Fill Known Arguments
Combine intent classification and parameter extraction in a single request:
1. Define handlers and their required inputs.
2. Send all branch-specific questions up front.
3. Code checks the selected route and consumes only the parameters for that branch.

### Pattern C: Speculative Fan-Out (Batch Processing)
Send dozens of atomic questions in a single call over the same state context. Because TypeSafe processes questions in parallel internally, batching yields up to $10\times$ speedups and lower costs.

### Pattern D: Guardrails & Suitability Verification
Before dispatching recommendations to clients, run companion Nouls:
- Does the message contain unapproved financial promises?
- Is the recommended asset aligned with the client's registered suitability?

---

## 4. SDK Usage

### Python Integration
```python
import os
from typesafe import TypeSafeClient

client = TypeSafeClient(api_key=os.environ.get("TYPESAFE_API_KEY"))

state = """
Cliente: Mariana Rios
Saldo em Conta: R$ 15.000,00
Perfil Registrado: Moderado
Produtos Selecionados: CDB Prefixado (14% a.a.), Fundo Multimercado (16% a.a.)
"""

response = client.evaluate(
    state=state,
    questions={
        "adequacao": {
            "type": "choice",
            "question": "A recomendação está compatível com as normas de Suitability?",
            "options": ["conforme", "risco_excessivo", "subalocacao"]
        },
        "precisa_revisao": {
            "type": "noul",
            "question": "A alocação exige revisão presencial de um assessor de investimentos?"
        }
    }
)

if response.answers["adequacao"].value == "conforme" and response.confidence >= 0.80:
    print("Recomendação aprovada com alta confiança!")
```

### JavaScript / TypeScript Integration
```typescript
import { TypeSafeClient } from "@typesafe/sdk";

const client = new TypeSafeClient({
  apiKey: process.env.TYPESAFE_API_KEY,
});

const result = await client.evaluate({
  state: JSON.stringify(clientData),
  questions: {
    suitabilityCheck: {
      type: "noul",
      question: "Is this asset allocation strictly compliant with the client's risk profile?",
    }
  }
});
```

---

## 5. Application in this Investment Automation Project

When working on this Santander / N8N investment assistant:
1. **RPA Data Ingestion**: Use TypeSafe primitives to evaluate legacy table data consistency and detect anomalies in account balances.
2. **Deterministic Match Engine**: Keep the financial matching logic (balance $\ge$ minimum deposit) strictly in deterministic code/N8N nodes.
3. **Suitability & Guardrail Gate**: Use TypeSafe Jev as a high-speed verification gate before dispatching automated recommendations to clients, ensuring zero regulatory non-compliance.
4. **Confidence-Aware Reporting**: Expose the model's confidence in the terminal dashboard alongside the 60 FPS motion graphics telemetry.
