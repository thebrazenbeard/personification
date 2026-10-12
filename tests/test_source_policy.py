"""Prevent historical actor-specific material from becoming a default profile."""
import tempfile
import unittest
from pathlib import Path
from personification.source_policy import (
    AdmissionKind, classify_source_path, read_active_source
)

ROOT = Path(__file__).resolve().parents[1]


class SourceAdmissionTests(unittest.TestCase):
    def test_active_neutral_sources_explicitly_admitted(self):
        for p in (
            "README.md", "PERSONIFICATION_V1.md",
            "src/personification/core.py",
            "src/personification/source_policy.py",
        ):
            self.assertEqual(classify_source_path(p), AdmissionKind.ACTIVE)
            self.assertGreater(len(read_active_source(ROOT, p)), 30)

    def test_historical_brigit_and_vera_sources_never_admitted(self):
        for p in (
            "history/brigit/BRIGIT_PERSONIFICATION_V1.md",
            "history/brigit/notes/2026-09-08-first-dot-observation.md",
            "history/vera/2026-09-08-self-appraisal.md",
        ):
            self.assertEqual(classify_source_path(p), AdmissionKind.HISTORICAL)
            with self.assertRaises(ValueError):
                read_active_source(ROOT, p)

        for p in ("notes/old.md", "vera/self-report.md", "BRIGIT_old.md"):
            self.assertEqual(classify_source_path(p), AdmissionKind.NOT_ADMITTED)
            with self.assertRaises(ValueError):
                read_active_source(ROOT, p)

    def test_path_traversal_and_unexpected_inputs_rejected(self):
        for p in (
            "../history/brigit/notes/secret.md", "/README.md",
            "src/personification/../other.py", "C:\\secret",
            "README.md/../history", "src//personification/core.py",
            "", "README.md\x00", "README.md/hidden.py",
        ):
            with self.subTest(p=p):
                self.assertEqual(classify_source_path(p), AdmissionKind.NOT_ADMITTED)
                with self.assertRaises(ValueError):
                    read_active_source(ROOT, p)

    def test_extra_docs_are_not_automatically_whitelisted(self):
        self.assertEqual(classify_source_path("experiments/future-secret.txt"), AdmissionKind.NOT_ADMITTED)
        with self.assertRaises(ValueError):
            read_active_source(ROOT, "experiments/future-secret.txt")

    def test_importable_core_has_no_embedded_named_actors(self):
        for file in (ROOT / "src" / "personification").glob("*.py"):
            with self.subTest(file=file.name):
                text = file.read_text(encoding="utf-8")
                self.assertNotIn("Brigit", text)
                self.assertNotIn("Vera", text)

    def test_no_auto_profile_load_from_repository_history(self):
        allowed = read_active_source(ROOT, "PERSONIFICATION_V1.md")
        self.assertIn("identity-neutral", allowed)
        self.assertNotIn("Brigit Personification V1", allowed)


if __name__ == "__main__":
    unittest.main()
