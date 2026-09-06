#!/usr/bin/env python3
"""Root-level shim for agent.backend_worker."""
from agent.backend_worker import BackendOrchestrator, run_backend

__all__ = ["BackendOrchestrator", "run_backend"]

if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    run_backend()
