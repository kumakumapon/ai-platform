"""Structural checks for the task prompts distributed to projects.

These guard the conventions described in CLAUDE.md: every task prompt keeps the
same sections and frontmatter, carries no project-specific names, and stays in
sync with the command table in templates/CLAUDE.bridge.md.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parents[1]
PROMPTS_DIR = REPO_ROOT / "prompts"
BRIDGE_TEMPLATE = REPO_ROOT / "templates" / "CLAUDE.bridge.md"

# coding-agent-typescript-python.md is a rules document, not a command, and
# quick-request.md is the combined entry point rather than a single task.
NON_TASK_PROMPTS = frozenset({"coding-agent-typescript-python", "quick-request"})

REQUIRED_SECTIONS = ("依頼形式", "手順", "完了基準", "禁止事項", "報告形式")
REQUIRED_FRONTMATTER_KEYS = ("description", "argument-hint", "disable-model-invocation")

# Retired heading names that earlier prompt generations used.
RETIRED_SECTIONS = ("作業手順", "完了条件", "診断手順", "確認手順", "調査手順", "報告基準", "報告")

# templates/ legitimately points at this platform repository; nothing else may
# name a specific project. Keep the owner in one place so a rename is one edit.
PLATFORM_OWNER = "kumakumapon"
ALLOWED_OWNER_REFERENCE = f"{PLATFORM_OWNER}/ai-platform"


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Return the YAML-ish frontmatter mapping and the body below it."""
    if not text.startswith("---\n"):
        return {}, text
    _, frontmatter, body = text.split("---\n", 2)
    fields: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if not line.strip() or ":" not in line:
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields, body


def strip_code_fences(body: str) -> str:
    """Drop fenced blocks so report/Issue templates don't look like sections.

    Several prompts embed a ```md template whose own headings would otherwise
    be indistinguishable from the prompt's structure.
    """
    kept: list[str] = []
    fence: str | None = None
    for line in body.splitlines():
        marker = re.match(r"\s*(`{3,}|~{3,})", line)
        if fence is None:
            if marker:
                fence = marker.group(1)[0] * 3
                continue
            kept.append(line)
        elif marker and marker.group(1).startswith(fence):
            fence = None
    return "\n".join(kept)


def headings(body: str) -> list[str]:
    return re.findall(r"^## (.+?)\s*$", strip_code_fences(body), re.MULTILINE)


def task_prompts() -> list[Path]:
    return sorted(p for p in PROMPTS_DIR.glob("*.md") if p.stem not in NON_TASK_PROMPTS)


class TaskPromptStructureTests(unittest.TestCase):
    def test_task_prompts_are_discovered(self) -> None:
        self.assertTrue(task_prompts(), "no task prompts found under prompts/")

    def test_every_task_prompt_declares_required_frontmatter(self) -> None:
        for path in task_prompts():
            with self.subTest(prompt=path.name):
                fields, _ = split_frontmatter(path.read_text(encoding="utf-8"))
                self.assertTrue(fields, "frontmatter block is missing")
                for key in REQUIRED_FRONTMATTER_KEYS:
                    self.assertIn(key, fields)
                self.assertEqual(fields["disable-model-invocation"], "true")

    def test_argument_hint_starts_with_the_target_repository(self) -> None:
        for path in task_prompts():
            with self.subTest(prompt=path.name):
                fields, _ = split_frontmatter(path.read_text(encoding="utf-8"))
                self.assertTrue(
                    fields["argument-hint"].startswith("<owner/repo>"),
                    f"argument-hint must start with <owner/repo>: {fields['argument-hint']!r}",
                )

    def test_every_task_prompt_has_the_required_sections(self) -> None:
        for path in task_prompts():
            with self.subTest(prompt=path.name):
                found = headings(split_frontmatter(path.read_text(encoding="utf-8"))[1])
                for section in REQUIRED_SECTIONS:
                    self.assertIn(section, found)

    def test_required_sections_keep_their_canonical_order(self) -> None:
        for path in task_prompts():
            with self.subTest(prompt=path.name):
                found = headings(split_frontmatter(path.read_text(encoding="utf-8"))[1])
                positions = [found.index(section) for section in REQUIRED_SECTIONS]
                self.assertEqual(
                    positions,
                    sorted(positions),
                    f"sections out of order: {[s for s in found if s in REQUIRED_SECTIONS]}",
                )

    def test_no_retired_section_names_remain(self) -> None:
        for path in task_prompts():
            with self.subTest(prompt=path.name):
                found = headings(split_frontmatter(path.read_text(encoding="utf-8"))[1])
                for section in RETIRED_SECTIONS:
                    self.assertNotIn(section, found)

    def test_report_section_provides_a_markdown_template(self) -> None:
        for path in task_prompts():
            with self.subTest(prompt=path.name):
                body = split_frontmatter(path.read_text(encoding="utf-8"))[1]
                report = body.split("## 報告形式", 1)[1]
                self.assertIn("```md", report, "報告形式 must contain a ```md template")


class SharedAssetTests(unittest.TestCase):
    """prompts/, templates/ and agents/ ship to every project."""

    def shared_files(self) -> list[Path]:
        return sorted(
            path
            for directory in ("prompts", "templates", "agents")
            for path in (REPO_ROOT / directory).rglob("*")
            if path.is_file()
        )

    def test_shared_assets_name_no_specific_project(self) -> None:
        pattern = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
        for path in self.shared_files():
            with self.subTest(asset=path.relative_to(REPO_ROOT).as_posix()):
                for match in pattern.finditer(path.read_text(encoding="utf-8")):
                    slug = match.group(0)
                    if not slug.startswith(f"{PLATFORM_OWNER}/"):
                        continue
                    self.assertEqual(
                        slug,
                        ALLOWED_OWNER_REFERENCE,
                        f"shared assets may only reference {ALLOWED_OWNER_REFERENCE}",
                    )

    def test_omakase_issue_limit_is_five(self) -> None:
        paths = (
            REPO_ROOT / "prompts" / "implement-issue.md",
            REPO_ROOT / "prompts" / "quick-request.md",
            REPO_ROOT / "templates" / "CHATGPT-WORK.project-instructions.md",
            REPO_ROOT / "README.md",
        )
        legacy_limit = re.compile(r"1-3|最大3件|上限3件|`3件` を指定")
        for path in paths:
            with self.subTest(path=path.relative_to(REPO_ROOT).as_posix()):
                text = path.read_text(encoding="utf-8")
                self.assertIn("5件", text)
                self.assertIsNone(legacy_limit.search(text))


class BridgeTemplateTests(unittest.TestCase):
    """templates/CLAUDE.bridge.md becomes the target project's CLAUDE.md."""

    def test_command_table_lists_every_task_prompt(self) -> None:
        listed = set(re.findall(r"^\| `/([a-z0-9-]+)`", BRIDGE_TEMPLATE.read_text(encoding="utf-8"), re.MULTILINE))
        expected = {path.stem for path in task_prompts()} | {"quick-request"}
        self.assertEqual(
            listed,
            expected,
            f"missing from the table: {sorted(expected - listed)}; unknown entries: {sorted(listed - expected)}",
        )


if __name__ == "__main__":
    unittest.main()
