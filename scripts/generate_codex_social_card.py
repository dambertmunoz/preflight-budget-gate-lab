from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path
from typing import Any

from agent_sdk.social_assets import SocialCardBrief, generate_dambert_linkedin_card_from_brief


DEFAULT_BRIEF_PATH = Path("docs/social-card-brief.json")
DEFAULT_OUT_PATH = Path("assets/preflight-budget-gate-social-card-codex.png")
DEFAULT_CANONICAL_PATH = Path("assets/preflight-budget-gate-social-card.png")


def _load_brief(path: Path) -> SocialCardBrief:
    if not path.exists():
        raise FileNotFoundError(
            f"social card brief not found: {path}. "
            "The factory/bot pipeline must provide a JSON brief; do not hardcode "
            "pipeline-specific prompt customization in this script."
        )
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return SocialCardBrief.from_mapping(data)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a Dambert LinkedIn social card from a pipeline-provided JSON brief."
    )
    parser.add_argument(
        "--brief-json",
        default=os.environ.get("SOCIAL_CARD_BRIEF_JSON", str(DEFAULT_BRIEF_PATH)),
        help="Path to the pipeline-generated social card brief JSON.",
    )
    parser.add_argument(
        "--out",
        default=os.environ.get("SOCIAL_CARD_OUT", str(DEFAULT_OUT_PATH)),
        help="Provider-specific output PNG path.",
    )
    parser.add_argument(
        "--canonical-out",
        default=os.environ.get("SOCIAL_CARD_CANONICAL_OUT", str(DEFAULT_CANONICAL_PATH)),
        help="Canonical social card PNG path to update after generation.",
    )
    args = parser.parse_args()

    brief = _load_brief(Path(args.brief_json))
    out = Path(args.out)
    canonical = Path(args.canonical_out)
    response = generate_dambert_linkedin_card_from_brief(brief, out_path=out)
    canonical.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(out, canonical)

    print(f"provider={response.provider}")
    print(f"model={response.model}")
    print(f"cost_usd={response.cost_usd}")
    print(f"brief={Path(args.brief_json).resolve()}")
    print(f"path={out.resolve()}")
    print(f"canonical_path={canonical.resolve()}")


if __name__ == "__main__":
    main()
