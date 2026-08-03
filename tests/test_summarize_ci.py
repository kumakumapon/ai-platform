"""Unit tests for scripts/summarize-ci.py."""

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


summary = load_module("summarize_ci", "summarize-ci.py")


class SummarizeCiTests(unittest.TestCase):
    def test_summary_extracts_useful_details_and_masks_secrets(self) -> None:
        log = (
            "Run pytest -q\n"
            "app/service.py:42: AssertionError: expected 200\n"
            "ERROR tests/test_service.py failed with token=ghp_abcdefghijklmnopqrstuvwxyz123456\n"
        )
        markdown = summary.render_summary(
            log=log,
            workflow="CI",
            job="test",
            step="pytest",
            run_url="https://github.com/acme/repo/actions/runs/7",
        )
        self.assertIn("app/service.py", markdown)
        self.assertIn("tests/test_service.py", markdown)
        self.assertIn("pytest -q", markdown)
        self.assertIn("***REDACTED***", markdown)
        self.assertNotIn("ghp_abcdefghijklmnopqrstuvwxyz123456", markdown)

    def test_explicit_reproduction_command_takes_precedence(self) -> None:
        markdown = summary.render_summary(log="ERROR fail", reproduce_command="python -m pytest tests/test_api.py")
        self.assertIn("python -m pytest tests/test_api.py", markdown)


if __name__ == "__main__":
    unittest.main()
