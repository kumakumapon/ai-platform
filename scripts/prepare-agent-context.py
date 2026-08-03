#!/usr/bin/env python3
"""Build a redacted Markdown brief for an Issue or pull request.

Examples:
  python scripts/prepare-agent-context.py --input issue.json --kind issue
  python scripts/prepare-agent-context.py --kind pr --number 42 --title "Fix cache" \\
    --purpose "Avoid stale results" --completion-condition "Tests pass" --file src/cache.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


SECRET_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\b(?:xox[baprs]-)[A-Za-z0-9-]{10,}\b"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    re.compile(
        r"(?i)(\b(?:api[_-]?key|access[_-]?token|auth[_-]?token|token|secret|password)\b"
        r"\s*(?:=|:|is)\s*)([^\s,;]+)"
    ),
    re.compile(r"(?i)(\bAuthorization\s*:\s*Bearer\s+)([^\s,;]+)"),
)

SECTION_ALIASES: Mapping[str, tuple[str, ...]] = {
    "purpose": ("目的", "purpose", "goal", "概要", "summary"),
    "completion": ("完了条件", "acceptance criteria", "acceptance", "done when", "definition of done"),
    "constraints": ("制約", "変更禁止事項", "禁止事項", "constraints", "out of scope", "do not"),
    "files": ("関連ファイル", "affected files", "related files"),
    "instructions": ("作業指示", "implementation notes", "notes"),
}


def mask_secrets(text: str) -> str:
    """Redact common credential-shaped values before placing text in a brief."""
    masked = text
    for pattern in SECRET_PATTERNS:
        if pattern.groups >= 2:
            masked = pattern.sub(lambda match: f"{match.group(1)}***REDACTED***", masked)
        else:
            masked = pattern.sub("***REDACTED***", masked)
    return masked


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (list, tuple)):
        return "\n".join(_as_text(item) for item in value if _as_text(item))
    return str(value).strip()


def _lookup(data: Mapping[str, Any], *names: str) -> str:
    for name in names:
        value = _as_text(data.get(name))
        if value:
            return value
    return ""


def extract_section(body: str, names: Sequence[str]) -> str:
    """Extract a Markdown section whose heading matches one of *names*."""
    heading = "|".join(re.escape(name) for name in names)
    pattern = re.compile(
        rf"^#{{1,6}}[ \t]*(?:{heading})[ \t]*:?[ \t]*\r?\n(.*?)(?=^#{{1,6}}[ \t]+|\Z)",
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(body)
    return match.group(1).strip() if match else ""


def _format_section(value: str, fallback: str) -> str:
    cleaned = mask_secrets(value).strip()
    if not cleaned:
        return f"- {fallback}"
    if cleaned.startswith("-") or cleaned.startswith("*") or cleaned.startswith("1."):
        return cleaned
    return cleaned


def _normalise_files(value: str, body: str) -> list[str]:
    candidates = re.findall(r"[A-Za-z0-9_./-]+\.(?:py|pyi|ts|tsx|js|jsx|json|ya?ml|md|toml|ini|cfg|sql|sh)", value)
    if not candidates:
        candidates = re.findall(r"[A-Za-z0-9_./-]+\.(?:py|pyi|ts|tsx|js|jsx|json|ya?ml|md|toml|ini|cfg|sql|sh)", body)
    output: list[str] = []
    for candidate in candidates:
        if candidate not in output:
            output.append(candidate)
    return output[:20]


def render_context(
    *,
    kind: str,
    number: str,
    title: str,
    url: str,
    body: str,
    purpose: str = "",
    completion: str = "",
    constraints: str = "",
    files: str = "",
    ci_result: str = "",
    instructions: str = "",
) -> str:
    """Render an Issue/PR context document with explicit safe defaults."""
    extracted_purpose = extract_section(body, SECTION_ALIASES["purpose"])
    extracted_completion = extract_section(body, SECTION_ALIASES["completion"])
    extracted_constraints = extract_section(body, SECTION_ALIASES["constraints"])
    extracted_files = extract_section(body, SECTION_ALIASES["files"])
    extracted_instructions = extract_section(body, SECTION_ALIASES["instructions"])
    target = f"{kind.upper()} #{number}: {title}".strip(": ") if number else f"{kind.upper()}: {title}".strip(": ")
    related_files = _normalise_files(files or extracted_files, body)
    file_section = "\n".join(f"- `{mask_secrets(path)}`" for path in related_files) or "- Identify during investigation."
    default_instruction = (
        "Inspect the relevant implementation and tests before editing. Respect the existing architecture, "
        "validate external input, and make the smallest safe change. Do not alter authentication, authorization, "
        "database behavior, or public APIs based on assumptions."
    )
    default_report = (
        "Summarize changed files, implementation decisions, tests/commands and their results, risks, and "
        "any verification that was not performed. Do not report an unrun check as successful."
    )
    return "\n".join(
        (
            "# ChatGPT Work Agent Context",
            "",
            "## Target Issue / PR",
            f"- {mask_secrets(target) or 'Not specified'}",
            f"- URL: {mask_secrets(url) or 'Not provided'}",
            "",
            "## Purpose",
            _format_section(purpose or extracted_purpose, "Derive the intended outcome from the linked Issue/PR."),
            "",
            "## Completion criteria",
            _format_section(completion or extracted_completion, "Confirm acceptance criteria with the Issue/PR."),
            "",
            "## Constraints",
            _format_section(constraints or extracted_constraints, "Follow existing project rules; do not expose secrets or personal information."),
            "",
            "## Related files",
            file_section,
            "",
            "## CI result",
            _format_section(ci_result, "Not provided."),
            "",
            "## Work instructions",
            _format_section(instructions or extracted_instructions, default_instruction),
            "",
            "## Completion report format",
            default_report,
        )
    ) + "\n"


def _load_data(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    raw = Path(path).read_text(encoding="utf-8")
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError("The input JSON must contain one object.")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", help="JSON object from an Issue/PR API or a hand-authored brief")
    parser.add_argument("--kind", choices=("issue", "pr"), default="issue")
    parser.add_argument("--number")
    parser.add_argument("--title")
    parser.add_argument("--url")
    parser.add_argument("--body")
    parser.add_argument("--purpose")
    parser.add_argument("--completion-condition", dest="completion")
    parser.add_argument("--constraint", action="append", default=[])
    parser.add_argument("--file", action="append", default=[])
    parser.add_argument("--ci-summary", help="Markdown CI summary to embed")
    parser.add_argument("--instruction")
    parser.add_argument("--output", help="Write Markdown to this path instead of stdout")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        data = _load_data(args.input)
        ci_result = Path(args.ci_summary).read_text(encoding="utf-8") if args.ci_summary else ""
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Unable to load context input: {exc}", file=sys.stderr)
        return 2

    constraints = "\n".join(args.constraint) or _lookup(data, "constraints", "restriction", "restrictions")
    files = "\n".join(args.file) or _lookup(data, "files", "related_files", "changed_files")
    result = render_context(
        kind=args.kind,
        number=args.number or _lookup(data, "number", "id"),
        title=args.title or _lookup(data, "title", "name"),
        url=args.url or _lookup(data, "html_url", "url", "web_url"),
        body=args.body or _lookup(data, "body", "description"),
        purpose=args.purpose or _lookup(data, "purpose", "goal"),
        completion=args.completion or _lookup(data, "completion", "completion_condition", "acceptance_criteria"),
        constraints=constraints,
        files=files,
        ci_result=ci_result or _lookup(data, "ci_result", "ci_summary"),
        instructions=args.instruction or _lookup(data, "instructions", "work_instructions"),
    )
    try:
        if args.output:
            Path(args.output).write_text(result, encoding="utf-8")
        else:
            print(result, end="")
    except OSError as exc:
        print(f"Unable to write context: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
