import hashlib
import tempfile
import unittest
from pathlib import Path

from core.evidence import EvidenceStore, FindingInput
from storage.sqlite_store import SQLiteStore


class EvidenceTests(unittest.TestCase):
    def test_raw_evidence_is_hashed_and_indexed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            store = SQLiteStore(root / "test.sqlite3")
            bundle = EvidenceStore(store, root / "evidence").save(
                collector="test.fixture",
                target="lab.local",
                command=("fixture", "sample.txt"),
                raw_data="hello evidence",
                findings=(FindingInput("Sample", "A test finding"),),
            )
            self.assertTrue(bundle.raw_path.exists())
            self.assertEqual(
                bundle.sha256,
                hashlib.sha256(b"hello evidence").hexdigest(),
            )
            self.assertEqual(len(store.recent_evidence()), 1)
            self.assertEqual(store.counts()["findings"], 1)