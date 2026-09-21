# Analysis plan

Written before any query was run against the data, so the definitions below could not be tuned to
make the results look better. Anything decided after seeing the data is listed under *Deviations*.

## Business question

Which patient and encounter characteristics are associated with a diabetic inpatient being
readmitted within 30 days of discharge, and where should a hospital focus discharge planning?

## Data

Diabetes 130-US Hospitals for Years 1999–2008 (UCI Machine Learning Repository, CC BY 4.0).
101,766 inpatient encounters of diabetic patients, 1–14 day stays, from 130 US hospitals.
Source paper: Strack et al. (2014), *BioMed Research International*, article ID 781670.

## Definitions

| Term | Definition |
|---|---|
| **30-day readmission** (outcome) | `readmitted = '<30'` → 1. Both `'>30'` and `'NO'` → 0. |
| **Index encounter** | The first encounter for each patient. The dataset has no admission dates, so the lowest `encounter_id` per `patient_nbr` is used as a proxy for the earliest stay. |
| **Primary cohort** | Index encounters only, after exclusions. One row per patient, so a frequently admitted patient cannot dominate the rates. |
| **Excluded** | Encounters ending in death or hospice (`discharge_disposition_id` 11, 13, 14, 19, 20, 21) — these patients cannot be readmitted, so including them would deflate the rate. Encounters with gender `Unknown/Invalid`. |
| **Primary diagnosis group** | `diag_1` ICD-9 code grouped as in Strack et al. Table 2: Circulatory (390–459, 785), Respiratory (460–519, 786), Digestive (520–579, 787), Diabetes (250.xx), Injury (800–999), Musculoskeletal (710–739), Genitourinary (580–629, 788), Neoplasms (140–239), Other (everything else, including V and E codes). |
| **HbA1c tested** | `A1Cresult` is `Norm`, `>7` or `>8`. Not tested: `None`. |

## Questions

1. What is the overall 30-day readmission rate?
2. How does it vary by age band?
3. By primary diagnosis group?
4. Does HbA1c testing during the stay, and whether medication was changed, relate to readmission?
   (The question the source paper asked.)
5. By number of inpatient admissions in the prior year?
6. By length of stay?
7. By discharge destination?
8. By insulin status during the stay?
9. How concentrated is utilisation — what share of encounters come from repeat patients?
10. Data quality: missingness per field, and rows removed at each step.

## Statistics

- Each rate reported with a 95% Wilson score confidence interval.
- Differences across groups tested with a chi-square test of independence (α = 0.05).
- Groups with fewer than 100 patients are shown but not interpreted.
- These are associations in observational data. None of them shows that a factor *causes*
  readmission.

## Deviations

Two queries were added after the plan was written. Neither changes a definition or a planned result:

- **Q1b, unit of analysis** — the same outcome counted per encounter and per patient, added to show
  why the plan chose one encounter per patient. Descriptive only; no test run.
- **Q9b, readmission chain** — uses `LAG()` to compare each repeat stay with the patient's previous
  one. Added while exploring Q9. It is the ninth chi-square test, and the Bonferroni threshold
  (0.05 / 9 = 0.0056) accounts for it.

The plan set α = 0.05. After counting the tests, a **Bonferroni correction** was applied as well
(0.05 / 9 = 0.0056). This is stricter than the plan, not looser, and it demotes the two HbA1c
results (p = 0.012 and 0.031) from findings to weak evidence. Both thresholds are reported.

Chart titles were written after the results were known, as headlines for the finding each chart shows.
