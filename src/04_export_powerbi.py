"""Export a star schema (only the columns the report uses, to keep the file under 10 MB) for Power BI from data/readmission.db into powerbi/data/.

fact_encounter holds every encounter with is_index / excluded flags, so the report can show
both the encounter-level and the patient-level (primary cohort) view from one table.
"""
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "readmission.db"
OUT = ROOT / "powerbi" / "data"

FACT_SQL = """
SELECT e.encounter_id, e.patient_nbr, e.is_index,
       CASE WHEN e.excluded_reason IS NULL THEN 0 ELSE 1 END              AS excluded,
       e.age_band, e.gender,
       e.admission_type_id, e.discharge_disposition_id, e.admission_source_id,
       e.time_in_hospital,
       CASE WHEN e.time_in_hospital <= 2 THEN '1-2 days'
            WHEN e.time_in_hospital <= 4 THEN '3-4 days'
            WHEN e.time_in_hospital <= 7 THEN '5-7 days' ELSE '8-14 days' END AS los_band,
       CASE WHEN e.time_in_hospital <= 2 THEN 1
            WHEN e.time_in_hospital <= 4 THEN 2
            WHEN e.time_in_hospital <= 7 THEN 3 ELSE 4 END                   AS los_band_sort,
       e.number_inpatient,
       CASE WHEN e.number_inpatient >= 3 THEN '3+' ELSE CAST(e.number_inpatient AS TEXT) END AS prior_inpatient_band,
       e.a1c_result, e.a1c_tested, e.med_change, e.diag_group,
       COALESCE(m.status, 'Not prescribed')                               AS insulin_status,
       e.readmit_30
FROM encounters e
LEFT JOIN medications m ON m.encounter_id = e.encounter_id AND m.drug = 'insulin'
"""

SHORT_DISCHARGE = {
    1: "Home", 2: "Another short-term hospital", 3: "Skilled nursing facility",
    4: "Intermediate care facility", 5: "Other inpatient institution",
    6: "Home with home health", 7: "Left against medical advice",
    22: "Rehab facility", 23: "Long-term care hospital",
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)

    fact = pd.read_sql_query(FACT_SQL, con)
    fact.to_csv(OUT / "fact_encounter.csv", index=False)

    pd.read_sql_query("SELECT age_band, sort_key FROM lk_age_band", con).to_csv(
        OUT / "dim_age.csv", index=False)

    dis = pd.read_sql_query("SELECT id AS discharge_disposition_id, description FROM lk_discharge_disposition", con)
    dis["short_name"] = dis["discharge_disposition_id"].map(SHORT_DISCHARGE).fillna(dis["description"])
    dis.to_csv(OUT / "dim_discharge.csv", index=False)

    pd.read_sql_query("SELECT id AS admission_source_id, description FROM lk_admission_source", con).to_csv(
        OUT / "dim_admission_source.csv", index=False)
    pd.read_sql_query("SELECT id AS admission_type_id, description FROM lk_admission_type", con).to_csv(
        OUT / "dim_admission_type.csv", index=False)

    pd.read_sql_query("SELECT * FROM dq_log ORDER BY step", con).to_csv(OUT / "dq_cleaning_log.csv", index=False)
    pd.read_sql_query("SELECT * FROM dq_missing WHERE pct_missing > 0", con).to_csv(
        OUT / "dq_missing.csv", index=False)
    con.close()

    # Reconciliation targets the Power BI report must reproduce.
    cohort = fact[(fact.is_index == 1) & (fact.excluded == 0)]
    print(f"fact_encounter rows : {len(fact):,}")
    print(f"cohort patients     : {len(cohort):,}")
    print(f"cohort readmissions : {int(cohort.readmit_30.sum()):,}")
    print(f"cohort rate         : {100 * cohort.readmit_30.mean():.2f}%")
    print(f"cohort avg LOS      : {cohort.time_in_hospital.mean():.2f} days")
    for p in sorted(OUT.glob("*.csv")):
        print(f"  {p.name:<28} {p.stat().st_size/1e6:6.2f} MB")


if __name__ == "__main__":
    main()
