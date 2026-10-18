# Part 2 — Data-Quality Challenge Guide

This guide tells you **what is wrong** with the raw data and **what "clean" must look like**. It deliberately does **not** tell you how to fix each problem: that's your job, and it's what you'll be asked about in interviews.

> All raw data is **synthetic**, produced by `src/generate_data.py` (seed 20261015). Re-running the generator recreates identical files.

## Ground rules

1. **Never silently delete a row.** Every change goes into a log (`dq_issue_log`) with: table, record key, column, rule ID (below), original value, cleaned value, and action (`corrected`, `standardized`, `set_null`, `flagged`, `excluded_from_metric`).
2. **Flag, don't drop.** Duplicates, out-of-window responses, and non-consented responses stay in `survey_response` with flags. They're excluded from *metrics*, not from the table. Rows that can't meet a NOT NULL or foreign-key rule can't enter the database. Log them as `excluded_from_metric` and keep them in your log.
3. **No imputation of decision-critical fields** (costs, floor area, parking, zoning status), per BRD rule BRL-10. Unknown stays unknown.
4. **Document every judgment call** in a markdown cell: what you decided, why, and what the alternative would have been.
5. **Clean output must load** into PostgreSQL with `sql/01_schema.sql` and pass `sql/03_integrity_checks.sql`. That's your acceptance test.

## Files

| Raw file | Rows | Target table(s) | Difficulty |
|---|---|---|---|
| community_survey.csv | 320 | survey_response, survey_top_choice, survey_barrier | ★★★ |
| program_preferences.csv | 985 | program_preference | ★★ |
| candidate_properties.csv | 12 | candidate_property | ★★ |
| property_due_diligence.csv | 60 | property_due_diligence | ★★ |
| startup_cost_estimates.csv | 31 | startup_cost_estimate | ★ |
| operating_cost_estimates.csv | 24 | operating_cost_estimate | ★ |
| program_options.csv | 14 | program_option | ★ |
| funding_scenarios.csv | 5 | funding_scenario | ★ |
| model_assumptions.csv | 21 | model_assumption | (clean) |
| data_sources.csv | 9 | data_source (already seeded) | (clean) |

Reference files in `data/reference/` hold the allowed codes. **Use `program_category_alias.csv` for program labels.** You'll need to build your own mapping dictionaries for the other categorical fields.

**Suggested order:** do the small cost/program/property files first to warm up, then the survey, then preferences (preferences depend on which survey rows survive).

---

## Rules

### General (all files)

| Rule | Problem | Clean must satisfy |
|---|---|---|
| DQ-01 | Leading/trailing whitespace and inconsistent capitalization in text and categorical fields | Categorical values exactly match the allowed list in the data dictionary |
| DQ-02 | `data_status` has several spellings | Only values in the `data_status_t` domain |
| DQ-04 | "Unknown" is written many ways: empty string, `N/A`, `-`, `unknown`, `prefer not to say`, `TBD`, `call for pricing` | Becomes NULL (empty in CSV). **Watch out:** in one file, `N/A` means something specific, not "unknown". Find it. |
| DQ-05 | Numbers stored as text: `$1,200`, `25.00`, `30 min`, `4 hrs`, `4,800 sq ft`, `$95/hr`, `35%` | Proper numeric dtype; nothing left as object dtype in numeric columns |
| DQ-06 | Booleans written as `TRUE`/`Yes`/`Y`/`1`/`true`/`No`/`N`/`0` | True boolean |

### Survey (`community_survey.csv`)

| Rule | Problem | Clean must satisfy | Things to think about |
|---|---|---|---|
| DQ-03 | `response_date` uses three formats; a couple of values can't be a real date | ISO date | Slash dates are US format (month first). How will you prove a parse didn't silently mis-read a date? |
| DQ-07 | `attendance_frequency`, `preferred_day`, `preferred_time`, `response_channel`, `age_group`, `household_size_range` have free-text variants (`once a week`, `Sat`, `kiosk`, `3 to 4`, `25 - 34`) | Allowed values only | `attendance_frequency` is **required** — a few rows are blank. What can you do with a row missing a required field? |
| DQ-08 | `max_travel_minutes` has some impossible values | 0–120 | Is 999 a typo or a sentinel? Does it matter for what you'll do with it? |
| DQ-09 | One `one_time_pledge_stated` value is wildly out of line with the rest | Documented decision | Look at the distribution before deciding. It's stated intent anyway (BRL-03). |
| DQ-10 | **Duplicate submissions.** Some people submitted twice, sometimes through different channels. Each copy got a new `respondent_id` and was formatted differently. | `is_duplicate`, `duplicate_of` set per BRL-02; originals kept | You can't detect these on raw values; you must clean first. Some matching profiles are **more than 48 hours apart**. Those are different people, so don't flag them. |
| DQ-11 | `consent_flag = FALSE` on some rows | Kept, but excluded from metrics | |
| DQ-12 | Some responses fall outside the survey window (2026-03-01 to 2026-06-30) | Kept, but excluded from metrics | Why might pilot-test responses exist? |
| DQ-13 | `preferred_programs` is a `;`-separated list of up to 3 labels using many synonyms, separators, and cases. A few people listed **the same program twice under different names**. | `survey_top_choice`: one row per respondent × category, `choice_rank` 1..n with no gaps | If "Yoga; Meditation" both map to one category, what's the rank of the next item? |
| DQ-14 | `main_barriers` uses free text; a few respondents chose "None" **plus** a real barrier | `survey_barrier`: valid `barrier_code` values; `NONE` never combined with another barrier | Which answer do you believe? Justify it. |
| DQ-15 | `volunteer_hours_month` has one impossible value | 0–80 | |
| DQ-16 | `comment_text` has stray whitespace; many are blank | Trimmed; blank → NULL | |

### Preferences (`program_preferences.csv`)

| Rule | Problem | Clean must satisfy | Things to think about |
|---|---|---|---|
| DQ-17 | `program_category` holds alias labels, not codes | `category_code` from the alias table | |
| DQ-18 | `interest_rating` has numbers as text, numbers as words, blanks, and out-of-range values | Integer 1–5 | |
| DQ-19 | `preferred_frequency` variants (`Bi-weekly`, `fortnightly`, `as needed`, `every day`) | Allowed values | |
| DQ-20 | Some rows reference respondents who **don't exist** in the survey. Others belong to survey rows you couldn't keep. | FK to `survey_response` holds | These are different problems. Log them differently. |
| DQ-21 | A few respondents rated **the same category twice** under different labels, with different ratings | One row per respondent × category | Keep max? Mean? First? Pick one and defend it. |

Also: duplicate submitters' preference rows are re-submitted too. They're valid rows (FK is fine), but think about which rows belong in demand metrics.

### Properties and due diligence

| Rule | Problem | Clean must satisfy | Things to think about |
|---|---|---|---|
| DQ-22 | `jurisdiction`, `property_type`, `area_label` formatting | Allowed values | `County` → which code? |
| DQ-23 | `floor_area_sqft`, `parking_spaces`, prices in mixed formats: `~80`, `shared`, `shared (center)`, `unknown`, `TBD`, `$95/hr` | Integers/numerics or NULL | Is `~80` a number or unknown? Is `shared` zero? (It's not.) |
| DQ-24 | One lease listing has its price in the **wrong column** | Satisfies `chk_tenure_price` | How can you tell it's a monthly rent and not a sale price? |
| DQ-25 | `review_area` and `status` free-text variants; one status is blank | Allowed values | Here `N/A` is **not** unknown. Blank status: what's the safest assumption, and how do you log it? |
| DQ-26 | One `dd_id` appears twice (an older and a newer version of the same record) | Unique `dd_id` | Which one is current? |
| DQ-27 | One property is **missing** one review area | Every property has exactly 5 rows (check IC-02) | Adding a row is a cleaning action too. Log it. |
| DQ-28 | `est_cost_to_resolve` contains `unknown` and `$` amounts | Numeric or NULL | |

### Costs, programs, funding

| Rule | Problem | Clean must satisfy |
|---|---|---|
| DQ-29 | `operating_model` and `cost_category` sometimes use labels instead of codes (raw column names also differ from the schema) | Valid `model_code`, `cost_category_code` |
| DQ-30 | One startup line has **low and high swapped**; one operating line has **low > base** | low ≤ base ≤ high (check constraints). Fix differently? Explain why. |
| DQ-31 | The operating-cost sheet has one line **copy-pasted** under a new ID | Unique (model, category, description) |
| DQ-32 | `verification_status` variants | Allowed `verification_t` values |
| DQ-33 | `program_options.csv`: one `category_code` holds a label; booleans as text; one audience with whitespace; one blank `min_area_sqft` | Valid codes & types; blank area stays NULL |
| DQ-34 | `funding_scenarios.csv`: money as text, one rate written as a percentage | Numeric; rates in 0–1 |

---

## Self-check checkpoints

If your cleaning follows the rules above, you should land **close to** these numbers. Small differences are fine if you can explain them. Large differences mean something's off.

| Checkpoint | Expect |
|---|---|
| Survey rows that can enter `survey_response` (meet NOT NULL rules) | ~316 |
| Rows flagged `is_duplicate` | 13 |
| Eligible respondents (consented, not duplicate, in window) | ~283 |
| `survey_barrier` rows containing NONE with another code | 0 |
| `program_preference` rows loaded | ~950 |
| True orphan preference rows (respondent never existed) | 5 |
| `property_due_diligence` rows | 60 (12 × 5) |
| `startup_cost_estimate` rows / `operating_cost_estimate` rows | 31 / 23 |
| All checks in `03_integrity_checks.sql` (IC-01 to IC-11) | 0 violations |

## Before vs after (required, FR-15)

Compute these on the **raw** data (as best you can) and on the **clean** data, and show the table in your notebook:

1. Number of respondents
2. % weekly-or-more attendance intent
3. Mean `max_travel_minutes`
4. Sum of `monthly_contribution_stated`
5. Top 3 program categories by mean rating

Write 2–3 sentences: which cleaning step changed the picture most? That paragraph is portfolio gold.

---

## Getting your clean files into PostgreSQL (Colab → pgAdmin)

1. At the end of your Colab notebook, write each clean table to CSV **with columns in the same order as `sql/01_schema.sql`**, and with `survey_response` sorted so originals (`is_duplicate = False`) come before duplicates (the self-FK needs this).
2. Download: `from google.colab import files; files.download('survey_response.csv')` (or zip the folder and download once).
3. Put the files in `data/clean/` in your repo.
4. In pgAdmin, run `01_schema.sql` then `02_seed_reference.sql` (to reset).
5. Load each table in the order from `docs/03_data_architecture.md` §4: right-click table → **Import/Export Data** → Import, Format `csv`, Header **on**, NULL string empty. Or use the `\copy` commands in §5 from psql.
6. Run `03_integrity_checks.sql`. Every check from IC-01 to IC-11 must return zero rows.

If an import fails, the error message names the constraint. That tells you which DQ rule you missed.
