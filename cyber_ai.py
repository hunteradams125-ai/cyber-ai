"""CYBER AI v1.0 entry point."""

from __future__ import annotations

from core.authorization import AuthorizationManager
from core.config import Settings
from core.evidence import EvidenceStore
from core.logging_config import configure_logging
from core.pipeline import CollectionPipeline
from centers.recon import ReconCenter
from storage.sqlite_store import SQLiteStore
from ui.menu import MainMenu
from ui.terminal import create_console


def build_menu() -> MainMenu:
    settings = Settings.from_environment()
    settings.ensure_directories()
    logger = configure_logging(settings.log_path)
    store = SQLiteStore(settings.database_path)
    authorization = AuthorizationManager(store)
    evidence_store = EvidenceStore(store, settings.evidence_path)
    pipeline = CollectionPipeline(evidence_store)
    recon = ReconCenter(authorization, pipeline, settings.development_mode)
    logger.info("CYBER AI started in development_mode=%s", settings.development_mode)
    return MainMenu(
        console=create_console(),
        store=store,
        authorization=authorization,
        recon=recon,
    )


if __name__ == "__main__":
    build_menu().run()