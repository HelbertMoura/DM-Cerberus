import tempfile
import unittest
from pathlib import Path

from engine.index import SQLiteMemoryIndex, normalize_roots, validate_root
from engine.parser import resolve_project_and_type


class TestIndexHardening(unittest.TestCase):
    def test_nested_roots_are_removed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = root / "docs" / "brain"
            nested.mkdir(parents=True)
            roots = normalize_roots([nested, root / "docs", nested, root / "missing"])
            self.assertEqual([(root / "docs").resolve()], roots)

    def test_overlapping_roots_index_file_once_deterministically(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            brain = docs / "brain"
            brain.mkdir(parents=True)
            (brain / "LEARNINGS.md").write_text("# Stable\n\nA sufficiently long section body for indexing.\n", encoding="utf-8")
            index = SQLiteMemoryIndex(root / "index.db")
            first = index.rebuild([brain, docs])
            stats1 = index.get_stats()
            second = index.rebuild([docs, brain])
            stats2 = index.get_stats()
            self.assertEqual(1, first["indexed_files"])
            self.assertEqual(first, second)
            self.assertEqual(stats1["total_files"], stats2["total_files"])
            self.assertEqual(stats1["total_documents"], stats2["total_documents"])

    def test_same_relative_filename_in_independent_roots_does_not_collide(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            left, right = base / "left", base / "right"
            left.mkdir()
            right.mkdir()
            (left / "README.md").write_text("# Left\n\nUnique alpha content.\n", encoding="utf-8")
            (right / "README.md").write_text("# Right\n\nUnique beta content.\n", encoding="utf-8")
            index = SQLiteMemoryIndex(base / "index.db")
            result = index.rebuild([left, right])
            self.assertEqual(2, result["indexed_files"])
            self.assertEqual(2, result["total_chunks"])
            self.assertEqual(2, index.get_stats()["total_documents"])

    def test_sensitive_filename_is_not_indexed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            names = ["secrets.md", "token.md", "credential.md", ".env.production.md",
                     "my-secrets.md", "private-key-backup.md"]
            for name in names:
                (root / name).write_text("# Sensitive\n\nThis file must not be indexed.\n", encoding="utf-8")
            index = SQLiteMemoryIndex(root / "index.db")
            result = index.rebuild([root])
            self.assertEqual(0, result["indexed_files"])
            self.assertEqual(0, index.get_stats()["total_documents"])

    def test_incremental_prunes_deleted_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            document = root / "obsolete.md"
            document.write_text("# Obsolete\n\nThis document will be deleted after indexing.\n", encoding="utf-8")
            index = SQLiteMemoryIndex(root / "index.db")
            index.rebuild([root])
            document.unlink()
            index.index_roots([root])
            self.assertEqual(0, index.get_stats()["total_files"])
            self.assertEqual(0, index.get_stats()["total_documents"])

    def test_sensitive_directory_family_is_not_indexed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for dirname in ("secrets", "credentials", "tokens", "private-keys", ".env.production"):
                folder = root / dirname
                folder.mkdir()
                (folder / "notes.md").write_text("# Sensitive\n\nMust never be searchable.\n", encoding="utf-8")
            index = SQLiteMemoryIndex(root / "index.db")
            result = index.rebuild([root])
            self.assertEqual(0, result["indexed_files"])

    def test_dm_erp_root_is_classified_as_canteirohub(self) -> None:
        root = Path("C:/DevManiacs/migra/dm-erp/docs")
        project, _, _ = resolve_project_and_type(root / "BUSINESS_RULES.md", root)
        self.assertEqual("canteirohub", project)

    def test_root_validation_rejects_paths_outside_allowlist(self) -> None:
        with tempfile.TemporaryDirectory() as allowed_tmp, tempfile.TemporaryDirectory() as outside_tmp:
            allowed = Path(allowed_tmp)
            self.assertEqual(allowed.resolve(), validate_root(allowed, [allowed]))
            with self.assertRaises(ValueError):
                validate_root(Path(outside_tmp), [allowed])


if __name__ == "__main__":
    unittest.main()
