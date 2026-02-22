"""
day03_text_analyzer.py

Minimal text analyzer for a financial advisor reviewing long notes.

Usage:
  python3 day03_text_analyzer.py              # reads input.txt, prompts for read mode
  python3 day03_text_analyzer.py path/to.txt  # reads provided path, prompts for read mode

Read modes:
  - 30-second read: Quick scan (3 bullets, 3 risks, 3 questions)
  - 2-minute read: Detailed analysis (7 bullets, 8 risks, 8 questions)
"""

from __future__ import annotations

import sys
from pathlib import Path


def read_text_file(path: str) -> str:
    """Read text from a file path (UTF-8)."""
    return Path(path).read_text(encoding="utf-8")


def split_sentences(text: str) -> list[str]:
    """
    Dead-simple sentence splitter.
    Assumption: input notes are mostly plain sentences separated by punctuation/newlines.
    """
    cleaned = " ".join(text.replace("\n", " ").split())
    if not cleaned:
        return []

    # Normalize a few common sentence separators into periods.
    cleaned = cleaned.replace("?", ".").replace("!", ".")
    parts = [p.strip() for p in cleaned.split(".")]
    return [p for p in parts if p]


def summarize_bullets(text: str, bullet_count: int = 5) -> list[str]:
    """
    Concise, heuristic summary:
    - Split into sentences
    - Pick sentences evenly across the document (beginning/middle/end)
    """
    sentences = split_sentences(text)
    if not sentences:
        return ["(No text found)"]

    if len(sentences) <= bullet_count:
        return sentences

    step = max(1, len(sentences) // bullet_count)
    selected = [sentences[i * step] for i in range(bullet_count)]
    return selected[:bullet_count]


def key_risks_uncertainties(text: str, max_items: int = 6) -> list[str]:
    """
    Extract a "key risks / uncertainties" list using keyword scanning.
    Logic: keep sentences that contain risk/uncertainty language; de-duplicate.
    """
    risk_terms = [
        "risk",
        "uncertain",
        "unknown",
        "concern",
        "concerns",
        "might",
        "could",
        "may",
        "exposure",
        "volatility",
        "drawdown",
        "liquidity",
        "default",
        "lawsuit",
        "regulatory",
        "tax",
        "inflation",
        "recession",
    ]

    out: list[str] = []
    seen: set[str] = set()
    for s in split_sentences(text):
        s_low = s.lower()
        if any(term in s_low for term in risk_terms):
            norm = s_low.strip()
            if norm not in seen:
                seen.add(norm)
                out.append(s)
        if len(out) >= max_items:
            break

    return out or ["(No explicit risks/uncertainties detected — consider asking about downside scenarios.)"]


def questions_to_ask_next(text: str) -> list[str]:
    """
    Suggest next questions for a financial advisor.
    Logic: generic prompts + a few keyword-driven prompts (goals/timeline/liquidity/taxes/etc.).
    """
    t = text.lower()
    questions: list[str] = []

    # Always useful, regardless of content.
    questions.extend(
        [
            "What is the primary objective (growth, income, capital preservation), and what’s the time horizon?",
            "What is the client’s risk tolerance and maximum acceptable drawdown?",
            "Any upcoming liquidity needs (cash outlays) in the next 6–24 months?",
        ]
    )

    # Add a few targeted questions if signals appear in the notes.
    if "tax" in t or "ira" in t or "401" in t or "capital gain" in t:
        questions.append("What tax bracket and account types apply (taxable vs retirement), and are there unrealized gains/losses?")
    if "debt" in t or "loan" in t or "mortgage" in t or "credit" in t:
        questions.append("What are the balances, rates, and payoff priorities for outstanding debts?")
    if "business" in t or "startup" in t or "equity" in t or "options" in t:
        questions.append("Any concentrated positions (employer equity/options)? What’s the plan for diversification and liquidity events?")
    if "insurance" in t or "life" in t or "disability" in t or "umbrella" in t:
        questions.append("Is insurance coverage adequate (life/disability/liability), and when was it last reviewed?")
    if "estate" in t or "trust" in t or "beneficiary" in t:
        questions.append("Are beneficiaries, wills, and estate documents current, and are there any planned gifts/charitable goals?")

    # Keep it short.
    return questions[:6]


def format_section(title: str, items: list[str], bullet: str = "- ") -> str:
    lines = [title]
    for item in items:
        lines.append(f"{bullet}{item}")
    return "\n".join(lines)


def get_read_mode() -> str:
    """Prompt user to choose between 30-second or 2-minute read mode."""
    print("\nChoose read mode:")
    print("  1) 30-second read (quick scan)")
    print("  2) 2-minute read (detailed analysis)")
    
    while True:
        choice = input("Enter choice (1 or 2, default=1): ").strip()
        if not choice:
            return "30s"
        if choice == "1":
            return "30s"
        if choice == "2":
            return "2min"
        print("Invalid choice. Please enter 1 or 2.")


def main(argv: list[str]) -> int:
    path = argv[1] if len(argv) > 1 else "input.txt"
    try:
        text = read_text_file(path)
    except FileNotFoundError:
        print(f"Error: file not found: {path}")
        return 2

    # Get read mode preference
    mode = get_read_mode()
    
    # Adjust detail level based on mode
    # 30-second: concise (3 bullets, 3 risks, 3 questions)
    # 2-minute: detailed (7 bullets, 8 risks, 8 questions)
    if mode == "30s":
        bullet_count = 3
        max_risks = 3
        max_questions = 3
        mode_label = "30-second read"
    else:  # 2min
        bullet_count = 7
        max_risks = 8
        max_questions = 8
        mode_label = "2-minute read"

    summary = summarize_bullets(text, bullet_count=bullet_count)
    risks = key_risks_uncertainties(text, max_items=max_risks)
    questions = questions_to_ask_next(text)[:max_questions]

    print(f"\n{'=' * 60}")
    print(f"ANALYSIS ({mode_label})")
    print(f"{'=' * 60}\n")
    
    print(format_section(f"## Concise summary ({bullet_count} bullets)", summary))
    print()
    print(format_section("## Key risks / uncertainties", risks))
    print()
    print(format_section("## Questions to ask next", questions))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

