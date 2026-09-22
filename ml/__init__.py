"""Statistical models. Each script reads a dbt feature view, fits in Python, writes ml.* tables."""
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import yaml
from sqlalchemy import create_engine, text

SEED = 42
CONFIG = yaml.safe_load((Path(__file__).resolve().parents[1] / "generator" / "config.yaml").read_text())


def engine():
    url = "postgresql+psycopg2://{u}:{p}@{h}:{port}/{db}".format(
        u=os.getenv("PGUSER", "pa"), p=os.getenv("PGPASSWORD", "pa_local_only"),
        h=os.getenv("PGHOST", "localhost"), port=os.getenv("PGPORT", "5432"),
        db=os.getenv("PGDATABASE", "people_analytics"))
    return create_engine(url)


def read(sql: str) -> pd.DataFrame:
    with engine().connect() as conn:
        return pd.read_sql(text(sql), conn)


def write(df: pd.DataFrame, table: str) -> None:
    """Replace ml.<table>. Power BI reads these tables; it never fits anything itself."""
    with engine().begin() as conn:
        conn.execute(text("create schema if not exists ml"))
        conn.execute(text(f"drop table if exists ml.{table} cascade"))
        df.to_sql(table, conn, schema="ml", index=False, method="multi", chunksize=5000)


def banner(title: str) -> None:
    print(f"\n=== {title} " + "=" * max(0, 60 - len(title)))
