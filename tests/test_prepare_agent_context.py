"""Unit tests for scripts/prepare-agent-context.py."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


def load_module(name: str, filename: str):
    path = Path(__file__).parents[1] / "scripts" / filename
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


context = load_module("prepare_agent_context", "prepare-agent-context.py")


class PrepareAgentContextTests(unittest.TestCase):
    def test_extracts_japanese_sections_and_masks_secret(self) -> None:
        body = """## 目的\nキャッシュを修正する\n\n## 完了条件\n- 回帰テストが通る\n\n## 制約\nsecret=super-secret-value\n\n## 関連ファイル\n- src/cache.py\n"""
        markdown = context.render_context(
            kind="issue",
            number="12",
            title="キャッシュ修正",
            url="https://github.com/acme/repo/issues/12",
            body=body,
        )
        self.assertIn("キャッシュを修正する", markdown)
        self.assertIn("src/cache.py", markdown)
        self.assertIn("secret=***REDACTED***", markdown)
        self.assertNotIn("super-secret-value", markdown)

    def test_project_files_can_be_supplied_explicitly(self) -> None:
        markdown = context.render_context(
            kind="pr",
            number="5",
            title="Fix API",
            url="",
            body="",
            files="src/api.ts\ntests/api.test.ts",
            ci_result="CI passed",
        )
        self.assertIn("PR #5: Fix API", markdown)
        self.assertIn("src/api.ts", markdown)
        self.assertIn("CI passed", markdown)


if __name__ == "__main__":
    unittest.main()
