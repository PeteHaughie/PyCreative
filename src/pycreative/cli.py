# Delegation shim so console script entrypoint works in development layout
try:
    from src.runner.cli import main
except Exception:
    # Fallback to package path if available
    from runner.cli import main  # type: ignore

__all__ = ["main"]
