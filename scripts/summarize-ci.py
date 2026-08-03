#!/usr/bin/env python3
"""Create a compact, redacted Markdown summary from a failed CI log.

Examples:
  python scripts/summarize-ci.py --input failed.log --workflow CI --job test \\
    --step "Run tests" --run-url https://github.com/acme/example/actions/runs/1
  gh run view 123 --log-failed | python scripts/summarize-ci.py --workflow CI
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable, Sequence


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

ERROR_PATTERN = re.compile(
    r"(?i)\b(error|exception|failed|failure|fatal|traceback|assertionerror|npm ERR!)\b"
)
COMMAND_PATTERN = re.compile(
    r"^\s*(?:Run\s+)?(?:\$\s*)?((?:npm|pnpm|yarn|bun|uv|poetry|pipenv|python(?:3)?|pytest|tox|nox|make)\b.+)$"
)
FILE_PATTERN = re.compile(
    r"(?<![\w-])([A-Za-z0-9_./-]+\.(?:py|pyi|ts|tsx|js|jsx|json|ya?ml|md|toml|ini|cfg|sql|sh))"
    r"(?::\d+(?::\d+)?)?"
)


def mask_secrets(text: str) -> str:
    """Return *text* with common credential-shaped values replaced."""
    masked = text
    for pattern in SECRET_PATTERNS:
        if pattern.groups >= 2:
            masked = pattern.sub(lambda match: f"{match.group(1)}***REDACTED***", masked)
        else:
            masked = pattern.sub("***REDACTED***", masked)
    return masked


def _unique(values: Iterable[str], limit: int) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = value.strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
        if len(result) >= limit:
            break
    return result


def extract_error_lines(log: str, limit: int = 8) -> list[str]:
    """Extract representative failure lines, excluding unhelpful runner noise."""
    candidates = (
        line.strip()
        for line in log.splitlines()
        if ERROR_PATTERN.search(line)
        and not re.search(r"(?i)\b(error|failed)\s+to\s+upload", line)
    )
    return _unique(candidates, limit)


def extract_related_files(log: str, limit: int = 12) -> list[str]:
    """Extract source/configuration file paths mentioned in *log*."""
    return _unique((match.group(1) for match in FILE_PATTERN.finditer(log)), limit)


def extract_reproduction_commands(log: str, limit: int = 3) -> list[str]:
    """Extract likely shell commands that can reproduce the failure locally."""
    commands = (
        match.group(1).strip()
        for line in log.splitlines()
        if (match := COMMAND_PATTERN.match(line)) is not None
    )
    return _unique(commands, limit)


def _bullet_list(items: Sequence[str], fallback: str) -> str:
    if not items:
        return f"- {fallback}"
    return "\n".join(f"- `{item}`" for item in items)


def render_summary(
    *,
    log: str,
    workflow: str = "Not identified",
    job: str = "Not identified",
    step: str = "Not identified",
    run_url: str = "Not provided",
    reproduce_command: str | None = None,
) -> str:
    """Render a redacted Markdown CI failure summary."""
    safe_log = mask_secrets(log)
    errors = extract_error_lines(safe_log)
    files = extract_related_files(safe_log)
    commands = [mask_secrets(reproduce_command)] if reproduce_command else extract_reproduction_commands(safe_log)
    error_text = _bullet_list(errors, "No explicit error line was detected; inspect the linked run.")
    file_text = _bullet_list(files, "No related source or configuration file was detected.")
    command_text = _bullet_list(commands, "No local reproduction command was detected.")
    prompt = (
        "Investigate the GitHub Actions failure below. First inspect the referenced code and tests, "
        "identify the root cause, then make the smallest safe fix. Do not disable checks or remove "
        "tests to make CI pass. Add or update a regression test when appropriate. Report the cause, "
        "changed files, commands run and their results, and any remaining risk."
    )
    return "\n".join(
        (
            "# CI Failure Summary",
            "",
            "## Failed workflow",
            f"- {mask_secrets(workflow)}",
            "",
            "## Failed job / step",
            f"- Job: {mask_secrets(job)}",
            f"- Step: {mask_secrets(step)}",
            "",
            "## Error overview",
            error_text,
            "",
            "## Related files",
            file_text,
            "",
            "## Reproduction commands",
            command_text,
            "",
            "## Actions run URL",
            f"- {mask_secrets(run_url)}",
            "",
            "## Coding agent repair request",
            prompt,
        )
    ) + "\n"


def _read_input(path: str | None) -> str:
    if path is None or path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8", errors="replace")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", help="Failed log file; omit or use '-' to read stdin")
    parser.add_argument(
        "--workflow",
        "--workflow-name",
        dest="workflow",
        default="Not identified",
        help="Workflow display name (the --workflow-name alias is workflow-compatible)",
    )
    parser.add_argument("--job", default="Not identified")
    parser.add_argument("--step", default="Not identified")
    parser.add_argument("--run-url", default="Not provided")
    parser.add_argument("--reproduce-command", help="Known local reproduction command")
    parser.add_argument("--output", help="Write Markdown to this file instead of stdout")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        summary = render_summary(
            log=_read_input(args.input),
            workflow=args.workflow,
            job=args.job,
            step=args.step,
            run_url=args.run_url,
            reproduce_command=args.reproduce_command,
        )
    except OSError as exc:
        print(f"Unable to read CI log: {exc}", file=sys.stderr)
        return 2
    if args.output:
        try:
            Path(args.output).write_text(summary, encoding="utf-8")
        except OSError as exc:
            print(f"Unable to write summary: {exc}", file=sys.stderr)
            return 2
    else:
        print(summary, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
