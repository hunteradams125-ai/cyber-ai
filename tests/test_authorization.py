import tempfile
import unittest
from pathlib import Path

from core.authorization import AuthorizedTarget, AuthorizationManager
from storage.sqlite_store import SQLiteStore


class AuthorizationTests(unittest.TestCase):
    def test_target_must_be_authorized_before_use(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manager = AuthorizationManager(SQLiteStore(Path(directory) / "test.sqlite3"))
            with self.assertRaises(PermissionError):
                manager.require_authorized("LAB.LOCAL/")
            manager.authorize(AuthorizedTarget("LAB.LOCAL/", "owned training lab"))
            manager.require_authorized("lab.local")

    def test_scope_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manager = AuthorizationManager(SQLiteStore(Path(directory) / "test.sqlite3"))
            with self.assertRaises(ValueError):
                manager.authorize(AuthorizedTarget("lab.local", ""))