# Tracy Hindu Temple Feasibility Study (Portfolio Project)

> **Hypothetical, independent portfolio project.** No real organization commissioned this work. All survey, property, cost, and funding data are **synthetic or assumed** and labeled as such at row level (`data_status`). Nothing here is evidence of real demand, a real property's suitability, a verified cost, or an official approval.

<!-- TODO (you): replace this line with 3-4 sentences in your own words: the problem, why it matters, and what the analysis decides. -->

## Status
| Part | Contents | Status |
|---|---|---|
| 1 | Charter & BRD · Business questions · Data architecture & PostgreSQL schema | ✅ |
| 2 | Synthetic raw dataset (1,481 rows) · Data-quality challenge guide · Colab cleaning notebook | ✅ data ready · 🧹 cleaning in progress |
| 3 | 25+ SQL queries · Financial feasibility model | ⏳ |
| 4 | Regulatory checklist · ML assessment · Power BI design · Testing · Decision framework | ⏳ |

## Folder structure
```
tracy-temple-feasibility/
├── docs/
│   ├── 01_project_charter_and_BRD.md
│   ├── 02_business_questions.md
│   ├── 03_data_architecture.md          # data dictionary, ERD, import steps
│   └── 04_data_quality_challenge_guide.md
├── sql/
│   ├── 01_schema.sql                    # schema, constraints, indexes, views
│   ├── 02_seed_reference.sql            # lookups + data-source registry
│   ├── 03_integrity_checks.sql          # post-load RI & DQ checks
│   └── 04_constraint_tests.sql          # known-bad inserts (must all fail)
├── data/
│   ├── reference/                       # allowed codes (exported from the SQL seed)
│   ├── raw/                             # synthetic raw CSVs with deliberate DQ issues
│   └── clean/                           # your cleaned CSVs (from Colab)
├── src/generate_data.py                 # reproducible generator (seed 20261015)
├── notebooks/01_data_cleaning_colab.ipynb
├── powerbi/                             # Part 4
└── outputs/                             # charts, model outputs
```

## Workflow
1. **Database:** in pgAdmin, create `tracy_temple`, run `sql/01_schema.sql`, then `sql/02_seed_reference.sql`.
2. **Clean:** open `notebooks/01_data_cleaning_colab.ipynb` in Google Colab, follow `docs/04_data_quality_challenge_guide.md`, export to `data/clean/`.
3. **Load:** import clean CSVs in the order given in `docs/03_data_architecture.md` §4–5.
4. **Verify:** run `sql/03_integrity_checks.sql`. IC-01 to IC-11 must return zero rows.

Regenerate the raw data at any time: `python src/generate_data.py` (identical output every run).
