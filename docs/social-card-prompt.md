# Social card image prompt

Use this with Codex image generation, DALL·E, Midjourney, or another image model for the LinkedIn post.

## Wasyra-inspired premium prompt

Create a premium square editorial social card for LinkedIn, 1:1 aspect ratio, inspired by the Wasyra visual system: dark-first gradient background, deep navy to indigo to violet, subtle cyan and warm amber glows, glassmorphism dashboard cards, soft editorial shadows, abstract blobs, dotted micro-grid, and clean high-contrast typography.

Brand/person: Dambert Muñoz, AI Architect.

Core message:
"Your agent spends before it thinks"

Secondary line:
"Preflight admission control before tool side effects."

Small badge:
"Dambert Lab"

CTA/footer:
"dambertmunoz.com"

Visual concept: left side has strong editorial headline typography. Right side shows premium floating product/architecture panels: one analytics/preflight card, one code card, and a central orbital gate diagram connecting Intent, Policy, Reserve, and Audit. The system should feel like a serious Staff/Architect engineering artifact, not generic AI hype.

Use short readable labels only:
- Intent
- Policy
- Reserve
- Audit
- manual_review
- no tool call

Style details:
- 2026 premium SaaS editorial design.
- Glass panels with translucent navy surfaces and thin white borders.
- Cyan/violet/amber accent palette.
- Soft shadows and dimensional composition.
- Crisp vector-like UI elements.
- Minimal text, large hierarchy, legible at mobile LinkedIn size.
- No humanoid robots, no glowing AI brain, no stock-photo people.
- No fake dense code blocks; if code appears, keep it abstract and secondary.
- Avoid misspelled text and avoid too many tiny labels.

## Local fallback asset

This repo also includes a deterministic local renderer inspired by the Wasyra promo pipeline:

```bash
npm install
npm run render:social-card
```

Output:

```text
assets/preflight-budget-gate-social-card.png
```
