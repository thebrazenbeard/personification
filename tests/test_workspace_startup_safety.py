"""Fail closed on tracked VS Code workspace startup execution.

This is a source-tree check. It neither runs editor tasks nor certifies any
already-installed workstation or extension.
"""

import json
from pathlib import Path
import re
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
JSONC_TOKENS = re.compile(r'"(?:\\.|[^"\\])*"|//[^\r\n]*|/\*[\s\S]*?\*/')
JSONC_TRAILING_COMMAS = re.compile(r'"(?:\\.|[^"\\])*"|,\s*(?=[}\]])')


def read_jsonc(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    # Strip JSONC comments without changing quoted strings. Keep newlines to
    # preserve useful parse locations. Reject other malformed JSONC normally.
    no_comments = JSONC_TOKENS.sub(
        lambda match: match.group(0)
        if match.group(0).startswith('"')
        else re.sub(r"[^\r\n]", " ", match.group(0)),
        text,
    )
    normalized = JSONC_TRAILING_COMMAS.sub(
        lambda match: match.group(0) if match.group(0).startswith('"') else "",
        no_comments,
    )
    return json.loads(normalized)


class WorkspaceStartupSafetyTests(unittest.TestCase):
    def test_jsonc_preserves_strings_and_accepts_comments(self):
        # A comment or trailing-comma sequence inside a quoted task value is
        # data, not syntax.  Workspace files such as launch.json also contain
        # genuine JSONC line comments.
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "tasks.json"
            config.write_text(
                '{\n'
                ' // editor metadata\n'
                ' "note": "literal ,} // not a comment",\n'
                ' /* a block comment over\n'
                ' two lines */\n'
                ' "tasks": [{"label": "safe",}], // trailing comma\n'
                '}\n',
                encoding="utf-8",
            )
            self.assertEqual(
                read_jsonc(config),
                {"note": "literal ,} // not a comment", "tasks": [{"label": "safe"}]},
            )

    def test_actual_launch_jsonc_is_parseable(self):
        # Keep the safety scanner usable with this repository's tracked VS Code
        # configuration, which contains both comments and trailing commas.
        launch = read_jsonc(ROOT / ".vscode" / "launch.json")
        self.assertIsInstance(launch.get("configurations"), list)

    def test_no_folder_open_tasks(self):
        tasks = read_jsonc(ROOT / ".vscode" / "tasks.json")
        self.assertIsInstance(tasks.get("tasks", []), list)
        for task in tasks.get("tasks", []):
            self.assertNotEqual(task.get("runOptions", {}).get("runOn"), "folderOpen")
            command = str(task.get("command", ""))
            self.assertNotIn("public/fonts/fa-solid.lkf", command)

    def test_workspace_does_not_enable_automatic_tasks(self):
        settings = read_jsonc(ROOT / ".vscode" / "settings.json")
        self.assertEqual(settings.get("task.allowAutomaticTasks"), "off")
        self.assertNotIn("tasks", settings, "no embedded startup tasks in settings")

    def test_no_pseudo_font_executable(self):
        self.assertFalse(
            list((ROOT / "public" / "fonts").glob("*.lkf")),
            "unrecognized pseudo-font extension in tracked public assets",
        )


if __name__ == "__main__":
    unittest.main()
