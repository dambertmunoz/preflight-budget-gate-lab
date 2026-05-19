# LinkedIn post draft

Si tu agente ejecuta primero y mide después, no gobiernas nada: solo documentas el incidente.

El anti-patrón junior en agentes con tools es sumar tokens al final, ponerle un dashboard encima y llamarlo “control de costo”. Eso sirve para contabilidad retroactiva, no para operación.

Cuando un agente puede publicar, escribir en una base, disparar un build, llamar un API o tocar un sistema externo, la pregunta importante no es solo:

> ¿Cuánto gastó?

La pregunta importante es:

> ¿Debía permitirse que esto ocurriera?

Y esa pregunta debe responderse antes del tool call.

Por eso armé un demo pequeño pero production-shaped: un preflight budget gate para agentes.

La idea:

1. El planner no llama una tool directamente.
2. Primero emite un `ActionIntent` tipado: tool, propósito, costo estimado, riesgo e idempotency key.
3. Una política determinística decide si la acción se ejecuta, se manda a revisión humana o se niega.
4. El ledger reserva presupuesto antes de ejecutar.
5. La reserva solo se confirma después de éxito.
6. Si falla antes del commit boundary, se libera.
7. Cada decisión genera un `AuditEvent` estable.

No es un billing system.  
No es un dashboard de observabilidad.  
No es otro “hello world” de LangGraph.

Es el boundary que falta en muchos agentes: admission control antes del side effect.

Posthoc evaluators answer: “What happened?”  
Preflight gates answer: “Should this be allowed to happen?”

Para agentes con tools, la segunda pregunta va primero.

Repo:
https://github.com/dambertmunoz/preflight-budget-gate-lab

Más sobre mi trabajo:
https://dambertmunoz.com/

#AIArchitecture #AIAgents #SoftwareArchitecture #AgenticAI #EngineeringLeadership
