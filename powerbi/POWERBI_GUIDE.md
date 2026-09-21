# Building the Power BI report

This is the step you do yourself. It takes about 45–60 minutes, and doing it is what makes
"Power BI" on your CV true. Everything the report needs is in `powerbi/data/` and
`powerbi/measures.dax`.

**You need:** Power BI Desktop (free from the Microsoft Store, Windows only).

---

## 1. Load the data (5 min)

1. **Home → Get data → Text/CSV.** Load each file in `powerbi/data/`:
   `fact_encounter`, `dim_age`, `dim_discharge`, `dim_admission_source`,
   `dim_admission_type`, `dq_cleaning_log`, `dq_missing`.
2. For `fact_encounter`, click **Transform Data** first and check the column types:
   `encounter_id`, `patient_nbr` → Whole number; `readmit_30`, `is_index`, `excluded`,
   `a1c_tested` → Whole number; `age_band`, `los_band`, `prior_inpatient_band` → Text.
   **Close & Apply.**

## 2. Build the model (5 min)

Open **Model view** and create these relationships (drag the column from the dimension onto
the fact). Every one should be **one-to-many, single direction**, dimension → fact:

| From (one side) | To (many side) |
|---|---|
| `dim_age[age_band]` | `fact_encounter[age_band]` |
| `dim_discharge[discharge_disposition_id]` | `fact_encounter[discharge_disposition_id]` |
| `dim_admission_source[admission_source_id]` | `fact_encounter[admission_source_id]` |
| `dim_admission_type[admission_type_id]` | `fact_encounter[admission_type_id]` |

That's a star schema. Take a screenshot of this view for the README.

**Sort orders** (otherwise the charts sort alphabetically and "[10-20)" lands before "[0-10)"):

- Select `dim_age[age_band]` → **Column tools → Sort by column → `sort_key`**
- Select `fact_encounter[los_band]` → **Sort by column → `los_band_sort`**

## 3. Add the measures (10 min)

Open `powerbi/measures.dax`. For each measure: **Modeling → New measure**, paste one block,
press Enter. Then format them:

- `Readmission Rate %`, `Rate CI Low %`, `Rate CI High %`, `Overall Rate %`,
  `Encounter-level Rate %` → **Percentage, 1 decimal**
- `Avg Length of Stay`, `Rate vs Overall (pp)` → **Decimal, 1 place**
- `Encounters`, `Unique Patients`, `Cohort Patients`, `Cohort Readmissions` →
  **Whole number, thousands separator on**

## 4. Page 1 — Overview (15 min)

| Visual | Settings |
|---|---|
| 4 × **Card** | `Cohort Patients`, `Readmission Rate %`, `Avg Length of Stay`, `Encounters` |
| **Clustered column chart** | X-axis `fact_encounter[prior_inpatient_band]`, Y-axis `Readmission Rate %`. Title: *Each prior admission raises the rate* |
| **Clustered bar chart** | Y-axis `dim_discharge[short_name]`, X-axis `Readmission Rate %`. Add a **visual-level filter**: `Cohort Patients` is greater than 100 (hides destinations too small to read). Sort descending. |
| **Slicers** (one row across the top) | `dim_age[age_band]`, `fact_encounter[gender]`, `fact_encounter[diag_group]` |

On both charts: **Analytics pane → Constant line** at 0.0897 (the overall rate), dashed grey.

## 5. Page 2 — Clinical drivers (10 min)

| Visual | Settings |
|---|---|
| **Column chart** | `dim_age[age_band]` × `Readmission Rate %` |
| **Column chart** | `fact_encounter[los_band]` × `Readmission Rate %` |
| **Table** | `fact_encounter[diag_group]`, `Cohort Patients`, `Readmission Rate %`, `Rate CI Low %`, `Rate CI High %`, `Rate vs Overall (pp)`. Conditional formatting on `Rate vs Overall (pp)`: background colour, diverging, centre 0. |
| **Column chart** | `fact_encounter[insulin_status]` × `Readmission Rate %` |

## 6. Page 3 — Data quality (5 min)

| Visual | Settings |
|---|---|
| **Table** | `dq_cleaning_log` — all columns |
| **Bar chart** | `dq_missing[field]` × `dq_missing[pct_missing]`, sorted descending |
| **Card** | `Encounter-level Rate %`, next to a card for `Readmission Rate %`. Text box beside them: *"Counting per encounter gives 11.4%; per patient, 9.0%. Frequent readmitters inflate the encounter-level figure."* |

## 7. Reconcile against SQL — do not skip this

With **no slicers selected**, the Overview cards must show exactly:

| Card | Expected |
|---|---|
| Cohort Patients | **69,970** |
| Readmission Rate % | **9.0%** (8.97%) |
| Avg Length of Stay | **4.3** (4.27) |
| Encounters | **101,766** |

and `Encounter-level Rate %` on page 3 must show **11.4%** (11.39%).

If any number differs, a relationship or a column type is wrong. Fix it before moving on.
This check is worth mentioning in interviews: *"I reconciled the dashboard against the SQL
output before trusting it."*

## 8. Publish the evidence

1. **File → Save as** `hospital_readmission.pbix` in the repo's `powerbi/` folder.
2. Screenshot each page (**Win + Shift + S**) and save as `powerbi/screenshots/page1_overview.png`,
   `page2_drivers.png`, `page3_data_quality.png`, plus `model_view.png`.
3. Upload the `.pbix` and screenshots to the GitHub repo. The README already links to
   those screenshot paths.
