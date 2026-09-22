"""Static checks of the Power BI semantic model (TMDL), runnable without Power BI Desktop.

* every 'Table'[Column] and [Measure] referenced in DAX exists; every function is a known DAX function
* every ratio uses DIVIDE() (no '/' operator), every measure lives in _Measures in an allowed folder
* relationships are single-direction many-to-one; the date table is marked; RLS role HRBP exists
* docs/metric_dictionary.md lists exactly the measures in the model
"""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DEF = ROOT / "powerbi" / "PeopleAnalytics.SemanticModel" / "definition"
FOLDERS = {"01 Headcount", "02 Turnover", "03 Recruiting", "04 Funnel", "05 Pay", "06 Equity",
           "07 Performance", "08 Training", "09 Model quality", "10 Forecast"}
DAX_FUNCTIONS = {
    "ABS", "AVERAGE", "AVERAGEX", "CALCULATE", "CALCULATETABLE", "COUNTROWS", "DATATABLE", "DISTINCTCOUNT",
    "DIVIDE", "EOMONTH", "EXP", "FILTER", "GENERATESERIES", "IF", "INTERSECT", "ISBLANK", "LOWER", "MAX",
    "MEDIAN", "MIN", "NOT", "REMOVEFILTERS", "ROW", "SELECTEDVALUE", "SUM", "SUMX", "TRUE", "USERELATIONSHIP",
    "USERPRINCIPALNAME", "VALUES",
}
NAME = r"(?:'(?:[^']|'')+'|[A-Za-z_][A-Za-z0-9_]*)"


def unquote(name: str) -> str:
    name = name.strip()
    return name[1:-1].replace("''", "'") if name.startswith("'") else name


def parse_tables() -> dict:
    tables = {}
    for f in sorted((DEF / "tables").glob("*.tmdl")):
        lines = f.read_text().splitlines()
        tname = unquote(next(l for l in lines if l.startswith("table "))[6:])
        cols, measures, props = set(), {}, {}
        i = 0
        while i < len(lines):
            line = lines[i]
            mcol = re.match(rf"^\tcolumn ({NAME})", line)
            mmea = re.match(rf"^\tmeasure ({NAME}) =(.*)$", line)
            if mcol:
                cols.add(unquote(mcol.group(1)))
            elif mmea:
                name, first = unquote(mmea.group(1)), mmea.group(2).strip()
                expr, i = [first] if first else [], i + 1
                while i < len(lines) and (lines[i].startswith("\t\t\t") or not lines[i].strip()):
                    expr.append(lines[i].strip())
                    i += 1
                p = {}
                while i < len(lines) and (lines[i].startswith("\t\t") or (
                        not lines[i].strip() and i + 1 < len(lines) and lines[i + 1].startswith("\t\t"))):
                    kv = lines[i].strip()
                    if ": " in kv:
                        p[kv.split(": ", 1)[0]] = kv.split(": ", 1)[1]
                    elif kv.startswith("annotation "):
                        k, v = kv[len("annotation "):].split(" = ", 1)
                        p[f"annotation:{k}"] = v
                    i += 1
                desc = lines[[j for j in range(len(lines)) if re.match(rf"^\tmeasure {re.escape(mmea.group(1))} =", lines[j])][0] - 1]
                p["description"] = desc.strip()[4:] if desc.strip().startswith("///") else ""
                measures[name] = "\n".join(expr).strip()
                props[name] = p
                continue
            i += 1
        tables[tname] = {"columns": cols, "measures": measures, "props": props}
    return tables


@pytest.fixture(scope="module")
def model():
    return parse_tables()


def all_measures(model) -> dict:
    return {n: e for t in model.values() for n, e in t["measures"].items()}


def check_dax(expr: str, model: dict, measures: set, home_table: str | None = None) -> list[str]:
    errors = []
    code = re.sub(r'"[^"]*"', '""', expr)
    if code.count("(") != code.count(")"):
        errors.append("unbalanced parentheses")
    for tq, col in re.findall(rf"({NAME})\[([^\]]+)\]", code):
        t = unquote(tq)
        if t not in model:
            errors.append(f"unknown table {t}")
        elif col not in model[t]["columns"]:
            errors.append(f"unknown column {t}[{col}]")
    stripped = re.sub(rf"{NAME}\[[^\]]+\]", "", code)
    for ref in re.findall(r"\[([^\]]+)\]", stripped):
        if ref not in measures and not (home_table and ref in model[home_table]["columns"]):
            errors.append(f"unknown measure [{ref}]")
    for fn in re.findall(r"\b([A-Z][A-Z0-9_.]*)\s*\(", stripped):
        if fn not in DAX_FUNCTIONS:
            errors.append(f"unknown function {fn}")
    if "/" in stripped:
        errors.append("uses '/' instead of DIVIDE()")
    return errors


def test_every_measure_resolves_and_uses_divide(model):
    measures = all_measures(model)
    problems = {n: check_dax(e, model, set(measures)) for n, e in measures.items()}
    assert not {n: p for n, p in problems.items() if p}


def test_measures_live_in_measures_table_with_folders_and_docs(model):
    others = [t for t, v in model.items() if v["measures"] and t != "_Measures"]
    assert not others, f"measures outside _Measures: {others}"
    props = model["_Measures"]["props"]
    assert len(props) >= 100
    for name, p in props.items():
        assert p.get("displayFolder") in FOLDERS, name
        assert p.get("formatString"), name
        assert p["description"], name
        for k in ("Numerator", "Denominator", "Owner"):
            assert p.get(f"annotation:{k}"), (name, k)


def test_required_measures_exist(model):
    names = set(model["_Measures"]["measures"])
    required = {
        "Headcount End", "Headcount Start", "Headcount Avg", "Hires", "Separations", "Voluntary Turnover %",
        "Regretted Turnover %", "12M Retention %", "First-Year Attrition %", "Internal Mobility %", "Promotion %",
        "Avg Time to Fill Days", "Avg Time to Start Days", "Offer Acceptance %", "Channel Yield %", "Cost per Hire",
        "True Internal Cost per Hire", "Backfill Rate Value", "Avg Compa-Ratio", "Avg Range Penetration %",
        "Raw Gap %", "Adjusted Gap %", "Remediation Cost", "Nine-Box Count", "Training Hours per FTE",
        "Training ROI Proxy", "True Positives", "False Negatives", "False Positives", "True Negatives",
        "Cutoff Value", "Recall %", "Precision %", "Expected Cost", "Forecast vs Actual", "MAPE Holdout %",
    }
    assert required <= names, required - names


def test_relationships_single_direction_and_date_roles():
    text = (DEF / "relationships.tmdl").read_text()
    assert "bothDirections" not in text and "crossFilteringBehavior" not in text
    assert "toCardinality: many" not in text and "fromCardinality: one" not in text
    rels = re.findall(r"relationship \S+\n((?:\t.*\n)+)", text + "\n")
    date_rels = {}
    for r in rels:
        frm = re.search(r"fromColumn: (.*)", r).group(1)
        to = re.search(r"toColumn: (.*)", r).group(1)
        if to == "Date.date":
            table = unquote(frm.rsplit(".", 1)[0])
            date_rels.setdefault(table, []).append("isActive: false" not in r)
    for table in ("Employee Event", "Separation"):
        assert sorted(date_rels[table]) == [False, True], table


def test_date_table_marked_and_rls_role(model):
    date = (DEF / "tables" / "Date.tmdl").read_text()
    assert "dataCategory: Time" in date and "isKey" in date
    role = (DEF / "roles" / "HRBP.tmdl").read_text()
    assert "tablePermission 'Org Unit'" in role and "'Security HRBP'[user_email]" in role
    measures = set(all_measures(model))
    for line in role.splitlines():
        if "tablePermission" in line:
            table, expr = re.match(rf"\ttablePermission ({NAME}) = (.*)", line).groups()
            assert not check_dax(expr, model, measures, home_table=unquote(table)), line


def test_metric_dictionary_matches_model(model):
    doc = (ROOT / "docs" / "metric_dictionary.md").read_text()
    documented = set(re.findall(r"^### (.+)$", doc, flags=re.M))
    in_model = set(model["_Measures"]["measures"])
    assert documented == in_model, {"missing": in_model - documented, "extra": documented - in_model}
