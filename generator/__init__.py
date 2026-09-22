"""Synthetic people-analytics population generator (seeded, deterministic)."""
from __future__ import annotations

from datetime import date
from pathlib import Path

import numpy as np
import yaml

CONFIG_PATH = Path(__file__).with_name("config.yaml")

# One independent random stream per module, so changing one module never shifts another.
_STREAMS = {"population": 1, "events": 2, "performance": 3, "training": 4,
            "recruiting": 5, "pay": 6, "load": 7}


def load_config(path: Path = CONFIG_PATH) -> dict:
    with open(path) as fh:
        return yaml.safe_load(fh)


def rng_for(cfg: dict, stream: str) -> np.random.Generator:
    return np.random.default_rng([cfg["seed"], _STREAMS[stream]])


def to_date(value) -> date:
    return value if isinstance(value, date) else date.fromisoformat(str(value))


def days(d) -> np.ndarray:
    """datetime64[D] array from dates/strings."""
    return np.asarray(d, dtype="datetime64[D]")


def completed_years(start: np.ndarray, end: np.ndarray) -> np.ndarray:
    """Whole years between two datetime64[D] arrays (same rule as Postgres age())."""
    sy = start.astype("datetime64[Y]").astype(int) + 1970
    ey = end.astype("datetime64[Y]").astype(int) + 1970
    # compare (month, day) like Postgres age(): a birthday not yet reached this year
    sm = start.astype("datetime64[M]").astype(int) % 12
    em = end.astype("datetime64[M]").astype(int) % 12
    sd = (start - start.astype("datetime64[M]").astype("datetime64[D]")).astype(int)
    ed = (end - end.astype("datetime64[M]").astype("datetime64[D]")).astype(int)
    before = (em < sm) | ((em == sm) & (ed < sd))
    return ey - sy - before.astype(int)
