# Social card image prompt

This repo uses the shared **agent-sdk social asset template** plus the **agent-runtime imagegen registry**, not a local renderer, for the premium LinkedIn social card. The provider chain is Codex-first by design:

```text
codex_imagegen → openai_dalle → local_fallback
```

Actual provider used for the checked-in image:

```text
provider=codex_imagegen
model=gpt-5.4
tool=image_gen.imagegen
```

The final asset is:

```text
assets/preflight-budget-gate-social-card.png
```

## Regenerate with Codex imagegen

From the repo root:

```bash
export PYTHONPATH=/Users/dambert.munoz/factory/agent-sdk/src:/Users/dambert.munoz/factory/agent-runtime/src:/Users/dambert.munoz/factory/agent-learning/src:$PYTHONPATH
export NEXUSFACTORY_IMAGEGEN_CODEX_MODEL=gpt-5.4
python3.11 scripts/generate_codex_social_card.py
```

The script writes both the provider-specific reproducibility artifact and the canonical card path:

```text
assets/preflight-budget-gate-social-card-codex.png
assets/preflight-budget-gate-social-card.png
```

## Prompt used

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
