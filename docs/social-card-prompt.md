# Social card image prompt

This repo uses the shared **agent-sdk social asset template** plus the **agent-runtime imagegen registry**, not a local renderer, for the premium LinkedIn social card.

Pipeline-specific customization is data, not script code: the factory/bot pipeline writes `docs/social-card-brief.json`, and the generic script reads that brief. Do not hardcode repo-specific prompt semantics into `scripts/generate_codex_social_card.py`.

The provider chain is Codex-first by design:

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
export AGENT_IMAGEGEN_CODEX_MODEL=gpt-5.4
python3.11 scripts/generate_codex_social_card.py --brief-json docs/social-card-brief.json
```

The script writes both the provider-specific reproducibility artifact and the canonical card path:

```text
assets/preflight-budget-gate-social-card-codex.png
assets/preflight-budget-gate-social-card.png
```

## Prompt customization used

The concrete repo/pipeline customization lives in:

```text
docs/social-card-brief.json
```

The reusable base template lives in `agent_sdk.social_assets`.
