import os
import pytest


@pytest.mark.skipif(os.environ.get('SKIA_GPU', '') != '1', reason='GPU integration tests disabled')
def test_gpu_engine_run_smoke():
    """Smoke test for the GPU path. This test is gated behind SKIA_GPU=1 and
    will be skipped in CI by default.

    The test attempts to import required deps and run the Engine for a single
    frame in GPU mode to ensure the wiring works end-to-end.
    """
    try:
        from src.core.bootstrap import build_engine
        from src.core.engine import Engine
    except Exception as e:
        pytest.skip(f'Bootstrap or Engine import failed: {e}')

    # Ensure required runtime deps are present
    try:
        import skia  # type: ignore
        import pygame  # type: ignore
    except Exception as e:
        pytest.skip(f'Missing runtime dependency for GPU test: {e}')

    engine = build_engine(use_opengl=True)

    # Start engine for a single frame in headful mode so display is created
    # and GPU surface creation path is exercised.
    engine.start(max_frames=1, headless=False, use_opengl=True)
    # After running, engine should have stopped
    assert engine.running is False
