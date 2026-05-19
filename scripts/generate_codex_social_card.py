from __future__ import annotations

from pathlib import Path

from agent_runtime.imagegen_codex import CodexImagegenProvider
from agent_runtime.imagegen.protocol import ImageGenInvocation

PROMPT = """
Create a premium square LinkedIn social card for Dambert Muñoz, AI Architect.

Use a Wasyra-like premium visual language: dark-first editorial SaaS design, deep navy/indigo/violet gradient, subtle cyan and amber light, elegant glassmorphism, refined shadows, strong negative space, sophisticated product-design composition.

Theme: Preflight Budget Gate for AI agents.
Concept: an abstract AI agent workflow is stopped by a refined preflight gate before side effects. Make it feel like a serious Staff/Architect engineering artifact, not a diagram from a slide deck.

Important composition requirements:
- Premium, polished, editorial, high-end SaaS campaign quality.
- No literal white circle network, no cheap node graph, no messy connector lines.
- No fake code wall, no cluttered dashboards, no cartoon robots, no glowing AI brain.
- Prefer abstract glass panels, elegant gate/checkpoint motif, subtle ledger/audit visual cues.
- Leave clean negative space for LinkedIn caption; do not overcrowd.
- Avoid small text. If text is rendered, keep only large, legible: "Preflight Budget Gate" and "Dambert Muñoz · AI Architect".
- No misspelled text. If unsure, use no text except minimal brand/title.

Mood: premium, confident, technical, calm, architecture leadership, 2026 high-end product visual.
Palette: #07111f, #172554, #3b1d68, #68e1fd, #a78bfa, #ffb86c, #ffffff.
""".strip()


def main() -> None:
    out = Path("assets/preflight-budget-gate-social-card-codex.png")
    provider = CodexImagegenProvider(timeout_seconds=360)
    response = provider.invoke(
        ImageGenInvocation(
            prompt=PROMPT,
            width=1024,
            height=1024,
            style="premium square LinkedIn editorial social card",
            role_key="visual_designer",
        )
    )
    out.write_bytes(response.image_bytes)
    print(f"provider={response.provider}")
    print(f"model={response.model}")
    print(f"cost_usd={response.cost_usd}")
    print(f"path={out.resolve()}")


if __name__ == "__main__":
    main()
