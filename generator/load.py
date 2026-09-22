"""Build every source extract, write CSVs to data/raw/, and load them into the Postgres `raw` schema.

Raw tables mimic source-system extracts: all columns are text, names follow the source
(HRIS, ATS, payroll, performance, LMS), and a few re-extract duplicates are planted so
staging has something real to de-duplicate.
"""
from __future__ import annotations

import hashlib
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import create_engine

from generator import load_config, rng_for
from generator.events import simulate
from generator.pay import build_salary_history
from generator.performance import build_reviews
from generator.population import build_roster
from generator.recruiting import CHANNELS, build_requisitions
from generator.training import build_programs

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
EXTRACTED_AT = "2026-01-02 02:00:00"
RE_EXTRACTED_AT = "2026-01-02 02:17:00"


def engine():
    url = "postgresql+psycopg2://{u}:{p}@{h}:{port}/{db}".format(
        u=os.getenv("PGUSER", "pa"), p=os.getenv("PGPASSWORD", "pa_local_only"),
        h=os.getenv("PGHOST", "localhost"), port=os.getenv("PGPORT", "5432"),
        db=os.getenv("PGDATABASE", "people_analytics"))
    return create_engine(url)


def build_tables(cfg: dict) -> dict[str, pd.DataFrame]:
    pop = build_roster(cfg)
    sim = simulate(cfg, pop)
    r = pop["roster"]
    t: dict[str, pd.DataFrame] = {}

    t["hris_persons"] = pd.DataFrame({
        "emp_id": r["emp_id"], "legal_sex": r["gender"], "nationality": r["nationality"],
        "date_of_birth": r["birth_date"], "original_hire_date": r["hire_date"],
        "home_commute_km": r["commute_km"], "fte": r["fte"]})
    t["hris_job_history"] = sim.job_history()
    ou = pop["org_units"]
    t["hris_org_units"] = ou.rename(columns={"section": "section_name", "department": "department_name",
                                             "division": "division_name"})
    j = pop["jobs"]
    t["hris_jobs"] = pd.DataFrame({"job_code": j["job_code"], "job_title": j["job_title"], "job_family": j["job_family"],
                                   "grade_code": j["grade"], "critical_role": np.where(j["is_critical"], "Y", "N")})
    t["hris_locations"] = pop["stations"].assign(is_hub=np.where(pop["stations"]["is_hub"], "Y", "N"))

    t["perf_reviews"] = build_reviews(sim.reviews())

    courses = build_programs()
    t["lms_courses"] = courses.rename(columns={"hours": "duration_hours", "delivery": "delivery_mode"})
    comp = sim.training_completions()
    comp = comp[comp["completion_date"] >= pd.Timestamp(cfg["dates"]["start"])]
    comp = comp.merge(courses[["course_code", "hours", "cost_usd"]], on="course_code")
    comp = comp.sort_values(["completion_date", "emp_id", "course_code"]).reset_index(drop=True)
    comp.insert(0, "completion_id", [f"LC{i:07d}" for i in range(1, len(comp) + 1)])
    t["lms_completions"] = comp

    sal, bands = build_salary_history(cfg, sim)
    t["comp_salary_history"] = sal
    t["comp_pay_bands"] = bands.assign(currency=cfg["pay"]["currency"])

    reqs, apps = build_requisitions(cfg, sim)
    t["ats_sources"] = CHANNELS.copy()
    t["ats_requisitions"] = reqs
    t["ats_applications"] = apps

    t["sec_hrbp_access"] = pd.DataFrame(
        [(email, div) for div, email in cfg["security"]["hrbp_emails"].items()], columns=["user_email", "division_name"])
    return _add_extract_metadata(cfg, t)


def _add_extract_metadata(cfg: dict, tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    rng = rng_for(cfg, "load")
    out = {}
    for name, df in tables.items():
        df = df.copy()
        df["extracted_at"] = EXTRACTED_AT
        share = cfg["raw"]["duplicate_share"].get(name, 0)
        if share:
            dup = df.iloc[np.sort(rng.choice(len(df), size=int(len(df) * share), replace=False))].copy()
            dup["extracted_at"] = RE_EXTRACTED_AT
            df = pd.concat([df, dup], ignore_index=True)
        out[name] = df
    return out


def _as_text(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    for c in df.columns:
        s = df[c]
        if pd.api.types.is_datetime64_any_dtype(s):
            out[c] = s.dt.strftime("%Y-%m-%d")
        elif pd.api.types.is_float_dtype(s):
            out[c] = s.map(lambda v: "" if pd.isna(v) else f"{v:.10g}")
        else:
            out[c] = s.map(lambda v: "" if v is None or (isinstance(v, float) and np.isnan(v)) or v is pd.NaT
                           else str(v.date() if isinstance(v, pd.Timestamp) else v))
    return out.fillna("")


def write_csvs(tables: dict[str, pd.DataFrame]) -> dict[str, Path]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    paths = {}
    for name, df in tables.items():
        p = DATA_DIR / f"{name}.csv"
        _as_text(df).to_csv(p, index=False)
        paths[name] = p
    return paths


def load_raw(paths: dict[str, Path]) -> None:
    eng = engine()
    conn = eng.raw_connection()
    try:
        cur = conn.cursor()
        cur.execute("create schema if not exists raw")
        for name, path in paths.items():
            cols = pd.read_csv(path, nrows=0).columns
            cur.execute(f"drop table if exists raw.{name} cascade")
            cur.execute(f"create table raw.{name} ({', '.join(f'{c} text' for c in cols)})")
            with open(path) as fh:
                cur.copy_expert(f"copy raw.{name} from stdin with (format csv, header true, null '')", fh)
        conn.commit()
    finally:
        conn.close()


def fingerprint(paths: dict[str, Path]) -> str:
    h = hashlib.sha256()
    for name in sorted(paths):
        h.update(paths[name].read_bytes())
    return h.hexdigest()[:16]


def main() -> None:
    t0 = time.time()
    cfg = load_config()
    tables = build_tables(cfg)
    paths = write_csvs(tables)
    load_raw(paths)
    print(f"raw schema loaded in {time.time() - t0:.1f}s  (data fingerprint {fingerprint(paths)})")
    for name, df in tables.items():
        print(f"  raw.{name:<22} {len(df):>8,} rows")


if __name__ == "__main__":
    main()
