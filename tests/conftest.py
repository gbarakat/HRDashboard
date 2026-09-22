import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from generator import load_config  # noqa: E402
from generator.events import simulate  # noqa: E402
from generator.population import build_roster  # noqa: E402


@pytest.fixture(scope="session")
def cfg():
    return load_config()


@pytest.fixture(scope="session")
def sim(cfg):
    return simulate(cfg, build_roster(cfg))
