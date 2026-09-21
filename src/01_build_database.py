"""Clean the raw UCI extract and load it into a normalised SQLite database.

Input : data/raw/diabetic_data.csv, data/raw/IDs_mapping.csv
Output: data/readmission.db

Every row removed or value recoded is logged to the dq_log table, so the
cleaning can be audited from the database itself.
"""
from __future__ import annotations

import io
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
DB = ROOT / "data" / "readmission.db"

MEDICATIONS = [
    "metformin", "repaglinide", "nateglinide", "chlorpropamide", "glimepiride",
    "acetohexamide", "glipizide", "glyburide", "tolbutamide", "pioglitazone",
    "rosiglitazone", "acarbose", "miglitol", "troglitazone", "tolazamide",
    "examide", "citoglipton", "insulin", "glyburide-metformin", "glipizide-metformin",
    "glimepiride-pioglitazone", "metformin-rosiglitazone", "metformin-pioglitazone",
]
# Discharge dispositions that end in death or hospice (IDs_mapping.csv).
NO_READMIT_POSSIBLE = {11, 13, 14, 19, 20, 21}

AGE_ORDER = ["[0-10)", "[10-20)", "[20-30)", "[30-40)", "[40-50)",
             "[50-60)", "[60-70)", "[70-80)", "[80-90)", "[90-100)"]


def icd9_group(code: str | None) -> str:
    """Primary-diagnosis grouping from Strack et al. (2014), Table 2."""
    if code is None or pd.isna(code):
        return "Missing"
    c = str(code).strip()
    if c.startswith(("V", "E")):
        return "Other"
    try:
        v = float(c)
    except ValueError:
        return "Other"
    if 390 <= v <= 459 or int(v) == 785:
        return "Circulatory"
    if 460 <= v <= 519 or int(v) == 786:
        return "Respiratory"
    if 520 <= v <= 579 or int(v) == 787:
        return "Digestive"
    if int(v) == 250:
        return "Diabetes"
    if 800 <= v <= 999:
        return "Injury"
    if 710 <= v <= 739:
        return "Musculoskeletal"
    if 580 <= v <= 629 or int(v) == 788:
        return "Genitourinary"
    if 140 <= v <= 239:
        return "Neoplasms"
    return "Other"


def read_id_mapping(path: Path) -> dict[str, pd.DataFrame]:
    """IDs_mapping.csv holds three small tables stacked one after another,
    separated by a line containing only a comma (or nothing)."""
    blocks: list[list[str]] = [[]]
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.strip() in ("", ","):
            if blocks[-1]:
                blocks.append([])
            continue
        blocks[-1].append(line)
    out = {}
    for b in (b for b in blocks if b):
        df = pd.read_csv(io.StringIO("\n".join(b)), keep_default_na=False)
        key = df.columns[0]
        df = df.rename(columns={key: "id", df.columns[1]: "description"})
        df["id"] = pd.to_numeric(df["id"], errors="coerce")
        df = df.dropna(subset=["id"]).astype({"id": int})
        df["description"] = df["description"].replace({"": "Not recorded", "NULL": "Not recorded"})
        out[key] = df
    return out


def find(name: str) -> Path:
    """Case-insensitive lookup: the UCI zip ships 'IDS_mapping.csv', older copies 'IDs_mapping.csv'."""
    return next(p for p in RAW.rglob("*") if p.name.lower() == name.lower())


def main() -> None:
    raw_path = find("diabetic_data.csv")
    map_path = find("IDs_mapping.csv")

    # '?' is the dataset's missing marker. Keep the literal string 'None' (A1C / glucose not measured).
    df = pd.read_csv(raw_path, keep_default_na=False, na_values=["?"], low_memory=False)
    log: list[tuple[int, str, int, int]] = []
    step = 0

    def record(what: str, before: int, after: int) -> None:
        nonlocal step
        step += 1
        log.append((step, what, before, after))

    record("Raw encounters loaded", len(df), len(df))

    # --- missingness profile, before anything is dropped -------------------------
    miss = (df.isna().mean() * 100).round(2).rename("pct_missing").reset_index()
    miss.columns = ["field", "pct_missing"]
    miss = miss.sort_values("pct_missing", ascending=False)

    # --- duplicates --------------------------------------------------------------
    before = len(df)
    df = df.drop_duplicates(subset="encounter_id")
    record("Drop duplicate encounter_id", before, len(df))

    # --- flags -------------------------------------------------------------------
    df["readmit_30"] = (df["readmitted"] == "<30").astype(int)

    df = df.sort_values(["patient_nbr", "encounter_id"])
    df["encounter_seq"] = df.groupby("patient_nbr").cumcount() + 1
    df["is_index"] = (df["encounter_seq"] == 1).astype(int)

    df["excluded_reason"] = None
    df.loc[df["discharge_disposition_id"].isin(NO_READMIT_POSSIBLE), "excluded_reason"] = "Death or hospice"
    df.loc[df["gender"] == "Unknown/Invalid", "excluded_reason"] = "Invalid gender"
    n_all = len(df)
    record("Encounters discharged to death or hospice (flagged, excluded from rates)",
           n_all, n_all - int((df["excluded_reason"] == "Death or hospice").sum()))
    record("Encounters with invalid gender (flagged, excluded from rates)",
           n_all, n_all - int((df["excluded_reason"] == "Invalid gender").sum()))

    cohort_n = int(((df["is_index"] == 1) & df["excluded_reason"].isna()).sum())
    record("Primary cohort: first encounter per patient, after exclusions", n_all, cohort_n)

    df["a1c_tested"] = (df["A1Cresult"].isin(["Norm", ">7", ">8"])).astype(int)
    df["diag_group"] = df["diag_1"].map(icd9_group)

    # --- normalised tables ------------------------------------------------------------
    encounters = df.rename(columns={
        "age": "age_band", "A1Cresult": "a1c_result", "change": "med_change",
        "diabetesMed": "diabetes_med",
    })[[
        "encounter_id", "patient_nbr", "encounter_seq", "is_index", "excluded_reason",
        "race", "gender", "age_band", "admission_type_id", "discharge_disposition_id",
        "admission_source_id", "time_in_hospital", "medical_specialty", "payer_code",
        "num_lab_procedures", "num_procedures", "num_medications", "number_outpatient",
        "number_emergency", "number_inpatient", "number_diagnoses", "max_glu_serum",
        "a1c_result", "a1c_tested", "med_change", "diabetes_med", "diag_group",
        "readmitted", "readmit_30",
    ]]

    diagnoses = (
        df.melt(id_vars="encounter_id", value_vars=["diag_1", "diag_2", "diag_3"],
                var_name="position", value_name="icd9")
        .dropna(subset=["icd9"])
    )
    diagnoses["position"] = diagnoses["position"].str[-1].astype(int)
    diagnoses["diag_group"] = diagnoses["icd9"].map(icd9_group)

    meds = (
        df.melt(id_vars="encounter_id", value_vars=MEDICATIONS,
                var_name="drug", value_name="status")
    )
    meds = meds[meds["status"] != "No"]  # keep only drugs actually prescribed

    maps = read_id_mapping(map_path)

    DB.unlink(missing_ok=True)
    con = sqlite3.connect(DB)
    encounters.to_sql("encounters", con, index=False)
    diagnoses.to_sql("diagnoses", con, index=False)
    meds.to_sql("medications", con, index=False)
    maps["admission_type_id"].to_sql("lk_admission_type", con, index=False)
    maps["discharge_disposition_id"].to_sql("lk_discharge_disposition", con, index=False)
    maps["admission_source_id"].to_sql("lk_admission_source", con, index=False)
    pd.DataFrame({"age_band": AGE_ORDER, "sort_key": range(len(AGE_ORDER))}).to_sql(
        "lk_age_band", con, index=False)
    pd.DataFrame(log, columns=["step", "action", "rows_before", "rows_after"]).to_sql(
        "dq_log", con, index=False)
    miss.to_sql("dq_missing", con, index=False)

    con.executescript("""
        CREATE UNIQUE INDEX ix_enc ON encounters(encounter_id);
        CREATE INDEX ix_enc_pat ON encounters(patient_nbr);
        CREATE INDEX ix_diag ON diagnoses(encounter_id);
        CREATE INDEX ix_med ON medications(encounter_id);
        -- The primary analysis population: one index encounter per patient, exclusions removed.
        CREATE VIEW cohort AS
            SELECT * FROM encounters
            WHERE is_index = 1 AND excluded_reason IS NULL;
    """)
    con.commit()
    con.close()

    for s, what, b, a in log:
        print(f"{s:>2}. {what:<75} {b:>7,} -> {a:>7,}")
    print(f"\nDatabase written: {DB}")


if __name__ == "__main__":
    main()
