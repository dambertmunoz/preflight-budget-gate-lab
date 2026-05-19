from __future__ import annotations

from pathlib import Path

from agent_sdk.social_assets import generate_dambert_linkedin_card


def main() -> None:
    out = Path("assets/preflight-budget-gate-social-card-codex.png")
    response = generate_dambert_linkedin_card(
        title="Preflight Budget Gate",
        theme="Preflight Budget Gate for AI agents",
        concept=(
            "An abstract AI agent workflow is stopped by a refined preflight "
            "gate before side effects. Make it feel like a serious "
            "Staff/Architect engineering artifact, not a diagram from a slide deck."
        ),
        out_path=out,
    )
    Path("assets/preflight-budget-gate-social-card.png").write_bytes(out.read_bytes())
    print(f"provider={response.provider}")
    print(f"model={response.model}")
    print(f"cost_usd={response.cost_usd}")
    print(f"path={out.resolve()}")


if __name__ == "__main__":
    main()
