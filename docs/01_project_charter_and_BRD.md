# Tracy Hindu Temple Feasibility Study
## Part 1A — Project Charter & Business Requirements Document (BRD)

| Field | Value |
|---|---|
| Document ID | TTFS-BRD-001 |
| Version | 1.0 (draft for portfolio) |
| Date | 2026-10-15 |
| Author | Portfolio analyst (independent, hypothetical project) |
| Status | Hypothetical — **no real organization has commissioned or endorsed this work** |

> **Read this first.** This is an independent, hypothetical portfolio project. The "Community Planning Committee" is a fictional sponsor. All survey, property, cost, and funding records in this repository are **synthetic practice data** unless a record is explicitly tagged otherwise. Nothing here is evidence of real community demand, a real property's suitability, a verified cost, or an official approval.

### Labeling convention used throughout

| Tag | Meaning |
|---|---|
| **[REQ]** | Confirmed project requirement — something this project must do or produce. |
| **[ASSUMPTION — VALIDATE]** | Hypothetical input the analysis depends on; must be checked against real sources before any real-world use. |
| **[CONTEXT — SOURCED]** | Publicly documented fact, with source in `data_sources.csv` / Sources list. Still requires re-verification at time of use. |
| **[SYNTHETIC]** | Simulated record created for practice. |

Operating-model and strategy codes are used consistently across all documents, data, and SQL:

| Code | Meaning | Used for |
|---|---|---|
| `OM_RENT_EVENT` | Rent a venue (hall, community room) for occasional events | Cost & funding model |
| `OM_LEASE_DEDICATED` | Lease a dedicated facility (e.g., converted retail/office/industrial unit) | Cost & funding model |
| `OM_PURCHASE_ADAPT` | Purchase and adapt / renovate a property | Cost & funding model |
| `STRAT_A` | Establish a dedicated temple facility (realized via `OM_LEASE_DEDICATED` or `OM_PURCHASE_ADAPT`) | Decision variable X |
| `STRAT_B` | Begin with a rented or shared venue; expand only if justified (realized via `OM_RENT_EVENT`) | Decision variable X |
| `STRAT_C` | Defer pending more evidence or funding (includes no-go) | Decision variable X |

---

# PROJECT CHARTER

### C1. Refined business problem

A hypothetical community planning committee is considering whether — and **how** — a Hindu temple could be established in Tracy, California. The committee currently has no structured evidence on four things it must know before committing money or volunteer effort:

1. **Demand:** how many households would participate, how often, and in which programs.
2. **Place:** whether any property could *legally and practically* host religious assembly at a cost the community can bear.
3. **Money:** what it would cost to start and to operate, and whether funding is realistic rather than hoped-for.
4. **Permission:** what land-use, building, fire, accessibility, and parking approvals would be needed, and how long they might take.

Without that evidence, the committee risks either (a) committing to a lease or purchase it cannot sustain or legally use, or (b) dismissing a viable phased approach (e.g., starting in a rented hall). The project's purpose is to produce a decision-ready, evidence-graded recommendation among **STRAT_A, STRAT_B, STRAT_C** — explicitly including deferral or no-go.

### C2. Project objectives (SMART)

| ID | Objective | Measure |
|---|---|---|
| OBJ-1 | Quantify stated community interest with uncertainty bands | Deduplicated respondent count, attendance-frequency distribution, 95% CI on key proportions |
| OBJ-2 | Rank programs by demand and launch cost | Ranked program list with interest score and cost per interested household |
| OBJ-3 | Compare candidate properties on cost, size, parking, and due-diligence completeness | Scored property table; every property has a due-diligence status for 5 review areas |
| OBJ-4 | Estimate startup and annual operating cost for 3 operating models at low/base/high | Cost table with verified vs hypothetical share reported per model |
| OBJ-5 | Test financial sustainability under ≥4 funding scenarios | 36-month cash-flow per model × scenario; months-of-runway; break-even recurring-donation threshold |
| OBJ-6 | Produce a transparent decision scorecard with sensitivity analysis | Scorecard + tornado/weight-sensitivity table showing when the recommendation flips |

### C3. Scope summary

**In scope:** synthetic-data design, cleaning, SQL database, analysis, financial model, regulatory due-diligence *checklist* (not legal conclusions), dashboard design, decision framework.
**Out of scope:** contacting real property owners, filing permits, legal or tax advice, fundraising, representing any real organization.

### C4. Sponsor, roles, and authority (hypothetical)

| Role | Who (hypothetical) | Authority |
|---|---|---|
| Sponsor | Community Planning Committee (fictional) | Approves recommendation & weights |
| Business/Data Analyst | Portfolio author | Builds data, analysis, recommendation |
| Advisors to consult (real-world phase) | City/County planning staff, architect, attorney, CPA, insurer, fire marshal | Provide verified inputs |

### C5. High-level milestones

| Phase | Output | Target week |
|---|---|---|
| 1 | Charter, BRD, business questions, data architecture | Wk 1–2 |
| 2 | Synthetic dataset, data dictionary, DQ guide, Python cleaning | Wk 3–4 |
| 3 | SQL database, 25+ queries, financial model | Wk 5–6 |
| 4 | Regulatory checklist, ML assessment, Power BI, decision framework, testing | Wk 7–8 |
| 5 | GitHub portfolio packaging and write-up | Wk 9 |

### C6. Success definition

The project succeeds if the committee (or a portfolio reviewer) can trace **every number in the recommendation back to a table, a query, and a labeled source**, and can see which missing real-world inputs would change the answer. A "defer" outcome is an equally valid success.

---

# BUSINESS REQUIREMENTS DOCUMENT

## 1. Executive summary

The committee needs a structured feasibility assessment before deciding how to proceed with a Hindu temple in Tracy, CA. This BRD defines the requirements for a data-driven study covering community demand, program preferences, candidate properties, startup and operating costs, funding scenarios, and regulatory due diligence. The study compares three operating models (rent for events, lease dedicated, purchase and adapt) and produces a recommendation among three strategies: establish a dedicated facility (STRAT_A), start in a rented/shared venue and expand if justified (STRAT_B), or defer (STRAT_C).

Because this is a portfolio project, all quantitative inputs are synthetic or explicitly hypothetical. The BRD therefore emphasizes **traceability and evidence grading**: every record carries a `data_status`, and the decision framework reports how much of the evidence behind each criterion is verified versus assumed. The recommendation logic is designed so that a high share of unverified inputs pushes the outcome toward STRAT_B or STRAT_C rather than toward a capital commitment.

## 2. Business background and context

- **Location.** Tracy is a city in San Joaquin County. Property just outside city limits falls under **San Joaquin County** jurisdiction rather than the City of Tracy — so the permitting authority depends on the parcel. **[CONTEXT — SOURCED]** (County CEQA filings for religious-assembly projects with Tracy addresses; see Sources.)
- **Local precedent for the permitting pathway.** Past City of Tracy Planning Commission staff reports show places of worship and other places of assembly proposed in office, commercial, and shopping-center settings were processed through a **Conditional Use Permit (CUP)**, with the Planning Commission empowered to grant or deny CUPs under Tracy Municipal Code §10.08.4250, and joint-use parking arrangements considered under TMC §10.08.3460(j). **[CONTEXT — SOURCED]** These are historical reports; current code sections, zone names, and parking ratios **must be re-verified** with the City.
- **Regional precedent for phased, small-start religious facilities.** San Joaquin County filings in 2025–2026 include religious-assembly CUPs near Tracy that convert existing agricultural buildings in phases with attendance caps (e.g., a 4,765 sq ft building converted to a temple in Phase 1, with daily attendance capped at 70 and a limited number of larger annual events). **[CONTEXT — SOURCED]** This illustrates that approvals can come with **attendance and event caps** — a constraint the model must accommodate.
- **Regional alternatives.** Established Hindu temples exist elsewhere in Northern California, e.g., the Hindu Community and Cultural Center (Shiva-Vishnu Temple) in Livermore, operating since 1977. **[CONTEXT — SOURCED]** Whether any Hindu temple or regular satsang/community venue currently operates **in Tracy itself was not confirmed** during scoping; a local facility inventory is a required data item (DR-11).
- **Demographics.** No demographic figures are asserted in this BRD. Population, household, and ancestry/language data must be pulled from U.S. Census ACS tables and cited before use **[ASSUMPTION — VALIDATE]**. Census data **does not** record religion, so it can only provide context, never a demand estimate.

## 3. Problem statement

The committee lacks reliable evidence to decide whether, where, and in what form a Hindu temple could be established in Tracy. Specifically, it cannot currently answer: how many households would participate and how often; which programs to offer first; which properties could legally host religious assembly and at what cost; what startup capital and annual operating budget are required; whether pledged and recurring funds would cover those costs under conservative assumptions; and which approvals stand between a property and opening day. Acting without this evidence risks financial loss, regulatory non-compliance, and loss of community trust. The study must provide a recommendation that can equally support proceeding, phasing, gathering more information, or not proceeding.

## 4. Business objectives

| ID | Objective | Linked BR |
|---|---|---|
| BO-1 | Establish an evidence-graded estimate of potential participation | BR-01, BR-02, BR-03 |
| BO-2 | Identify a launch program portfolio matched to demand and budget | BR-04, BR-05 |
| BO-3 | Identify which candidate properties merit further due diligence | BR-06, BR-07, BR-08 |
| BO-4 | Quantify startup and operating costs per operating model | BR-09, BR-10 |
| BO-5 | Determine funding needed and the conditions for sustainability | BR-11, BR-12 |
| BO-6 | Make a transparent, reversible strategy recommendation | BR-13, BR-14 |

## 5. Scope and exclusions

**In scope**
- Design and generation of a synthetic relational dataset with deliberate data-quality issues.
- Python cleaning pipeline with flagging (no silent deletion).
- PostgreSQL schema, constraints, and ≥25 analytical queries.
- Financial model: 3 operating models × low/base/high costs × ≥4 funding scenarios, 36-month horizon.
- Regulatory due-diligence **checklist** and status tracking.
- Power BI dashboard specification (8 pages).
- Decision scorecard with sensitivity analysis.

**Exclusions**
- No legal, tax, zoning, engineering, or insurance determinations. The project lists what to ask, not what the answer is.
- No contact with real owners, brokers, agencies, or religious organizations.
- No real listings presented as available; candidate properties are **synthetic** and labeled.
- No demand prediction from population proxies (e.g., ancestry counts × assumed religiosity).
- No collection of religious-identity data about named individuals. Real-world survey work, if ever done, must be anonymous and voluntary.
- No architectural design, deity/ritual design decisions, or selection of a priest/tradition — these belong to the community.

## 6. Stakeholder analysis

| Stakeholder | Interest | Influence | Key concern | Engagement |
|---|---|---|---|---|
| Planning committee (sponsor) | High | High | Making a defensible, affordable decision | Weekly review; sets criteria weights |
| Prospective attendees / households | High | Medium | Programs, timing, travel time, cost to participate | Anonymous survey; focus groups |
| Prospective donors | High | High | Credibility, governance, use of funds | Pledge survey; financial transparency |
| Volunteers | High | Medium | Workload, scheduling | Volunteer-capacity survey |
| Priests / religious advisors | Medium | High | Ritual requirements, space, sanctum needs | Interviews on space & program requirements |
| City of Tracy / SJ County planning | Low | Very high | Code compliance, parking, traffic, neighbors | Pre-application meeting (real-world phase) |
| Fire marshal / building official | Low | Very high | Occupancy, egress, open-flame (diyas, havan), sprinklers | Pre-application consultation |
| Neighbors / adjacent businesses | Medium | Medium | Traffic, parking spillover, noise, festival crowds | Outreach before CUP hearing |
| Property owners / landlords | Medium | High | Lease terms, use clauses, insurance | Lease negotiation (real-world phase) |
| Existing regional temples | Medium | Low–Medium | Overlap vs. complement | Courtesy consultation; partnership options |
| Insurers, attorney, CPA | Low | High | Liability, nonprofit formation, tax status | Professional advice |

## 7. Business requirements

Priority: **M** = Must, **S** = Should, **C** = Could (MoSCoW).

| ID | Requirement | Rationale | Pri | Acceptance criteria (measurable) |
|---|---|---|---|---|
| BR-01 | **[REQ]** Measure stated interest and intended attendance frequency from deduplicated survey responses. | Demand is the first gate; duplicates inflate it. | M | Report shows raw n, flagged duplicates, deduplicated n, and % by frequency category; duplicates are flagged not deleted. |
| BR-02 | **[REQ]** Quantify uncertainty on demand metrics. | A single point estimate overstates confidence, especially with self-selected respondents. | M | Every headline proportion is shown with a 95% CI and a written note on self-selection bias. |
| BR-03 | **[REQ]** Convert stated frequency into a *conservative* expected-attendance range. | Stated intent overstates behavior. | M | Attendance range computed with documented intent-to-behavior discount factors (low/base/high) labeled **[ASSUMPTION — VALIDATE]**. |
| BR-04 | **[REQ]** Rank programs by interest and by cost per interested household. | Launch with what is wanted and affordable. | M | Ranked list of all programs in `program_option`; each has mean interest, % rating ≥4, launch cost, recurring cost. |
| BR-05 | **[REQ]** Classify each program as launch-phase or later-phase. | Phasing reduces initial cost and risk. | S | Every program has a phase recommendation with the rule that produced it. |
| BR-06 | **[REQ]** Compare candidate properties on floor area, parking, cost, and location. | Supports property short-listing. | M | Comparison table covers 100% of candidates; missing values shown as "unknown", never imputed silently. |
| BR-07 | **[REQ]** Track due-diligence status across zoning, building use, parking, accessibility, and fire/life safety for every property. | No property is viable until these are cleared. | M | Each property has exactly one status per review area; no property shown as "viable" unless all 5 are `verified_ok`. |
| BR-08 | **[REQ]** Estimate required parking and occupancy capacity from demand scenarios. | Parking and occupancy are common CUP conditions. | S | Required capacity computed for peak regular and festival scenarios; ratio assumptions labeled for validation with City/County. |
| BR-09 | **[REQ]** Estimate startup costs by model and category at low/base/high. | Determines capital need. | M | 3 models × all applicable categories; each line has source and verification status; % verified reported per model. |
| BR-10 | **[REQ]** Estimate recurring monthly and annual operating costs by model at low/base/high. | Determines sustainability. | M | Annual totals reconcile to monthly × 12 within $1. |
| BR-11 | **[REQ]** Model funding scenarios without treating pledges as cash. | Survey pledges are not donations. | M | Each scenario applies a documented pledge-realization rate (≤ base 40% unless validated); cash-flow excludes unrealized pledges. |
| BR-12 | **[REQ]** Compute sustainability thresholds (break-even recurring donations; months of runway). | Defines what must be true to proceed. | M | For each model × scenario: monthly break-even donations, months until reserve < 3 months of opex. |
| BR-13 | **[REQ]** Produce a weighted decision scorecard over STRAT_A/B/C with hard constraints (gates). | Transparent, reviewable recommendation. | M | Scorecard shows criteria, weights, scores, gates, and result; any failed gate overrides score. |
| BR-14 | **[REQ]** Run sensitivity analysis on weights and key assumptions. | Shows robustness and what flips the answer. | M | Report lists every assumption whose plausible change alters the recommended strategy. |
| BR-15 | **[REQ]** Report data quality and evidence grade on every dashboard page. | Prevents synthetic data being read as real. | M | Each page shows % records by `data_status`; synthetic watermark visible. |
| BR-16 | **[REQ]** Identify required real-world data and its sources. | Bridges portfolio to real decision. | S | Data-gap register lists each missing input, its source type, and which decision it affects. |

## 8. Functional requirements

| ID | Requirement | Rationale | Pri | Acceptance criteria |
|---|---|---|---|---|
| FR-01 | The system shall load all raw CSVs and log row/column counts and dtypes. | Baseline for reconciliation. | M | Load log matches file line counts (minus header) for 100% of files. |
| FR-02 | The system shall standardize text (trim, case, synonym mapping) using a version-controlled mapping table. | Equivalent categories must aggregate together. | M | After cleaning, every categorical value is in its allowed-value list or flagged. |
| FR-03 | The system shall parse mixed-format dates into ISO dates and flag unparseable values. | Time filters and survey windows need valid dates. | M | ≥99% parsed; 100% of failures flagged with reason code. |
| FR-04 | The system shall convert numeric strings (e.g., `"$1,200"`, `"1200 sqft"`) to numerics and flag failures. | Costs and areas must be computable. | M | No numeric column has object dtype after cleaning; failures flagged. |
| FR-05 | The system shall normalize unknown-value tokens (`"N/A"`, `"unknown"`, `"-"`, `""`, `"?"`) to NULL with an `*_unknown` indicator where meaningful. | Distinguish "unknown" from "zero". | M | Zero remaining unknown tokens in typed columns. |
| FR-06 | The system shall detect probable duplicate survey submissions and flag them with a group ID. | Avoid inflated demand. | M | Duplicate rule documented; flagged rows retained with `is_duplicate=TRUE` and `duplicate_of`. |
| FR-07 | The system shall validate ranges and allowed values and write violations to a `dq_issue_log`. | Auditability. | M | Every violation logged with table, key, column, rule ID, original value, action. |
| FR-08 | The system shall validate primary-key uniqueness and foreign-key integrity before export. | Database load must succeed. | M | 0 PK duplicates; 0 orphan FKs (or orphans flagged and excluded from FK tables with log). |
| FR-09 | The system shall export clean CSVs matching the PostgreSQL schema column order. | Reproducible `\copy` import. | M | `\copy` of each clean file succeeds with no errors. |
| FR-10 | The database shall enforce PK, FK, CHECK, and NOT NULL constraints defined in `sql/01_schema.sql`. | Integrity at rest. | M | Constraint test script inserts known-bad rows and every one is rejected. |
| FR-11 | The system shall compute low/base/high startup and annual operating totals per operating model. | Feeds model and dashboard. | M | Totals match independent Python calculation within $1. |
| FR-12 | The system shall generate a 36-month cash-flow for each operating model × funding scenario × cost case. | Sustainability testing. | M | 3 × ≥4 × 3 = ≥36 series exported; each has opening balance, inflows, outflows, closing balance. |
| FR-13 | The system shall compute the decision scorecard and re-run it under weight perturbations (±10 pts) and assumption sensitivity. | Robustness. | M | Output table lists recommendation under each perturbation. |
| FR-14 | The system shall export Power BI-ready fact and dimension tables. | Dashboard build. | S | Star schema exported; relationships load without ambiguity. |
| FR-15 | The system shall produce before/after cleaning comparison of key metrics. | Shows effect of cleaning. | S | Table of ≥5 metrics with raw vs clean values and delta. |
| FR-16 | The system shall classify open-ended comments into themes (rule-based baseline; optional ML). | Surfaces barriers and needs. | C | Each comment assigned ≥1 theme or `unclassified`; baseline precision reported on a hand-labeled sample. |

## 9. Nonfunctional requirements

| ID | Category | Requirement | Acceptance criteria |
|---|---|---|---|
| NFR-01 | Reproducibility | Entire pipeline runs from raw CSVs with one command and fixed random seed. | Two runs produce byte-identical clean outputs. |
| NFR-02 | Traceability | Every record carries `data_status` and `source_id`. | 0 nulls in these columns in the database. |
| NFR-03 | Transparency | No hidden adjustments; all assumptions in a single assumptions table. | Every constant used in calculations is found in `model_assumption`. |
| NFR-04 | Privacy | No personal identifiers; synthetic IDs only; real-world survey must be anonymous and opt-in for sensitive fields. | No names, emails, phones, addresses of individuals in any table. |
| NFR-05 | Portability | Runs on Python ≥3.10, PostgreSQL ≥14, pandas ≥2.0. | CI/smoke test on clean environment passes. |
| NFR-06 | Performance | Full pipeline < 2 minutes on a laptop. | Timed run logged. |
| NFR-07 | Usability | Dashboard readable by non-technical committee members. | Each page has a one-sentence "what this means" text box. |
| NFR-08 | Honesty of labeling | Synthetic data visibly watermarked in every output. | Watermark/footer present on every chart and page. |
| NFR-09 | Maintainability | Code modular, documented, linted. | `ruff`/`flake8` passes; each function has a docstring. |
| NFR-10 | Accessibility | Dashboard uses colorblind-safe palette and text labels. | No information encoded by color alone. |

## 10. User stories and acceptance criteria

| ID | As a… | I want… | So that… | Acceptance criteria (Given/When/Then) |
|---|---|---|---|---|
| US-01 | committee chair | a one-page feasibility overview | I can brief the committee in 5 minutes | Given clean data, when I open Page 1, then I see recommended strategy, gate status, and evidence grade. |
| US-02 | committee member | to see which programs people want most | we launch the right programs | Given preference data, when I filter by age group, then program ranking updates and shows n. |
| US-03 | treasurer | startup and annual cost per operating model at low/base/high | I can plan fundraising | When I select a model, then I see totals and % of cost lines verified. |
| US-04 | treasurer | to see how long reserves last under a pessimistic scenario | we avoid insolvency | When I choose the "Conservative" scenario, then months-of-runway is shown and highlighted if < 12. |
| US-05 | facilities lead | to compare properties on parking and floor area vs. need | we shortlist realistically | Then each property shows capacity vs. required capacity and a pass/fail/unknown flag. |
| US-06 | facilities lead | to see outstanding due-diligence actions per property | I know what to investigate next | Then each property lists open actions and owner role. |
| US-07 | data analyst | a log of every cleaning decision | results are auditable | Then `dq_issue_log` has one row per issue with rule ID and action. |
| US-08 | skeptical reviewer | to see how the recommendation changes when weights change | I trust it isn't rigged | When I move a weight slider ±10 pts, then the recommended strategy updates. |
| US-09 | volunteer coordinator | estimated volunteer hours per program | we don't overcommit volunteers | Then each launch program shows volunteer hours/month; total compared to stated volunteer capacity. |
| US-10 | donor | to see what share of funding is pledged vs. realized assumption | I understand risk | Then funding is split into "pledged (stated)" and "modeled realized" with the realization rate shown. |
| US-11 | committee chair | a list of missing real-world inputs that could change the decision | we know what to collect next | Then the data-gap register ranks gaps by decision impact. |

## 11. Business rules

| ID | Rule |
|---|---|
| BRL-01 | A survey response is **eligible** for demand metrics only if `consent_flag = TRUE`, it is not a flagged duplicate, and `response_date` is within the survey window. |
| BRL-02 | Probable duplicate = same `submission_fingerprint` (after cleaning: age group + household size + set of top-choice programs + attendance frequency + preferred day + preferred time + max travel minutes) submitted within 48 hours (≤ 2 calendar days, since the survey records dates only). Keep earliest; flag later. Same fingerprint more than 48 hours apart is treated as a different person. |
| BRL-03 | Willingness-to-contribute values are **stated intent**, never cash. Modeled realized recurring giving = stated × realization rate (low 20% / base 35% / high 50%) **[ASSUMPTION — VALIDATE]**. |
| BRL-04 | One-time pledges are counted toward startup funding only at the realization rate and only after a 3-month lag. |
| BRL-05 | Grants are counted as **$0 in the base case** unless a specific program has been identified and eligibility verified; many grantmakers restrict funding for religious worship activities. |
| BRL-06 | A property may be labeled `shortlist_eligible` only if no due-diligence area is `failed`. It may be labeled `viable` only if all five areas are `verified_ok`. Synthetic data cannot produce a real `viable` label. |
| BRL-07 | Any cost line with `verification_status <> 'verified_quote'` is treated as uncertain; the high estimate is used in the conservative cost case. |
| BRL-08 | Contingency reserve = 15% (base) of startup costs for `OM_LEASE_DEDICATED`, 20% for `OM_PURCHASE_ADAPT`, 10% for `OM_RENT_EVENT` **[ASSUMPTION — VALIDATE]**. |
| BRL-09 | Operating reserve target = 6 months of base operating cost before opening a dedicated facility. |
| BRL-10 | Missing values are never imputed for decision-critical fields (cost, area, parking, zoning status); they are shown as unknown and lower the evidence grade. |
| BRL-11 | The strategy recommendation must be STRAT_C if any **hard gate** fails (see §17). |
| BRL-12 | Records with `data_status = 'synthetic'` may be used for method demonstration but must never be summarized as real findings. |

## 12. Assumptions and dependencies

**Assumptions (all [ASSUMPTION — VALIDATE])**

| ID | Assumption | How to validate |
|---|---|---|
| AS-01 | An anonymous, voluntary community survey could reach a meaningful share of interested households. | Pilot survey; track response channel. |
| AS-02 | Stated attendance overstates actual attendance; discount factors 0.3 / 0.5 / 0.7 apply. | Attendance counts from pilot events (STRAT_B). |
| AS-03 | Pledge realization 20% / 35% / 50%. | Track actual pledges collected over 6 months. |
| AS-04 | Rented halls permit open flame / incense; many venues do not. | Venue policies; fire marshal. |
| AS-05 | A dedicated facility requires a CUP or equivalent discretionary approval in most candidate zones. | City/County pre-application meeting. |
| AS-06 | Parking demand ≈ 1 space per 3–4 attendees at peak. | Confirm actual code ratio for religious assembly. |
| AS-07 | Volunteers supply most labor in year 1; one part-time paid role (e.g., priest honorarium/stipend) in dedicated models. | Volunteer-capacity survey; priest interviews. |
| AS-08 | Cost estimates are synthetic until replaced by quotes. | Broker, contractor, insurer quotes. |

**Dependencies**
- DEP-01: Access to City of Tracy / San Joaquin County planning staff for pre-application guidance.
- DEP-02: Professional input from architect/engineer on occupancy and life safety.
- DEP-03: Attorney/CPA on nonprofit formation and tax-exempt status.
- DEP-04: Insurer quotes for liability and property coverage.
- DEP-05: Community willingness to answer a survey (real-world phase).

## 13. Risks and mitigation strategies

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| RK-01 | Survey self-selection overstates demand | High | High | Report CIs; apply discount factors; validate with pilot events (STRAT_B). |
| RK-02 | Pledges don't materialize | High | High | Conservative realization rates; require 6-month reserve before lease. |
| RK-03 | Property cannot obtain CUP / use permit | Medium | Very high | Pre-application meetings; lease contingency on approvals; no purchase before entitlement clarity. |
| RK-04 | Parking shortfall triggers denial or caps | Medium | High | Joint-use parking agreements; attendance caps; festival off-site arrangements. |
| RK-05 | Renovation (sprinklers, ADA, egress) far exceeds estimate | Medium | High | High-case estimates + contingency; architect walkthrough before LOI. |
| RK-06 | Open-flame rituals restricted by venue or fire code | Medium | Medium | Confirm early; electric diyas; designated havan area design. |
| RK-07 | Volunteer burnout | Medium | Medium | Volunteer-hours budgeting per program; phase programs. |
| RK-08 | Neighbor opposition | Medium | Medium | Early outreach; traffic/parking plan; event scheduling. |
| RK-09 | Governance disputes (tradition, leadership) | Medium | High | Clear bylaws, board structure, conflict-resolution process before fundraising. |
| RK-10 | Synthetic data mistaken for real findings | Low (portfolio) | High (reputation) | Watermarks, `data_status`, README disclaimers. |
| RK-11 | Overlap with existing regional temples reduces local attendance | Medium | Medium | Measure travel-time tolerance; position as complement (e.g., weekday/youth programs). |
| RK-12 | Security incidents | Low–Medium | Medium | Budget for cameras, lighting, alarm; insurance. |

## 14. Data requirements

| ID | Data item | Source (real-world) | Table | Status in portfolio |
|---|---|---|---|---|
| DR-01 | Anonymous survey responses | Committee survey | `survey_response` | Synthetic |
| DR-02 | Program interest ratings | Same survey | `program_preference` | Synthetic |
| DR-03 | Program catalog, cost and resource needs | Committee + comparable temples | `program_option` | Synthetic |
| DR-04 | Candidate properties | Broker/commercial listings, owner contact | `candidate_property` | Synthetic, labeled |
| DR-05 | Due-diligence statuses | Planning, building, fire, architect | `property_due_diligence` | Synthetic |
| DR-06 | Startup cost lines | Contractor, architect, vendor quotes | `startup_cost_estimate` | Synthetic/hypothetical |
| DR-07 | Operating cost lines | Utilities, insurer, landlord quotes | `operating_cost_estimate` | Synthetic/hypothetical |
| DR-08 | Funding scenarios | Pledge drive records, grant research | `funding_scenario` | Hypothetical |
| DR-09 | Data sources registry | All of the above | `data_source` | Mix: real references + synthetic |
| DR-10 | Zoning code text, permit fee schedules | City of Tracy, SJ County | `data_source` (refs) | To collect |
| DR-11 | Inventory of existing Hindu temples / satsang venues within ~45 min drive | Public directories, community input | future `existing_facility` | To collect |
| DR-12 | Census ACS context (households, languages) | U.S. Census Bureau | future `area_context` | To collect; context only |
| DR-13 | Pilot-event attendance (if STRAT_B is trialed) | Sign-in counts | future `event_attendance` | Does not exist yet |
| DR-14 | Model assumptions | This study | `model_assumption` | Hypothetical |

## 15. KPIs and success criteria

| KPI | Definition | Indicative threshold* |
|---|---|---|
| K-01 Eligible respondents | Deduplicated, consented, in-window responses | ≥ 150 for a usable estimate |
| K-02 Regular-intent share | % eligible respondents intending weekly or more | Reported with 95% CI |
| K-03 Expected regular attendance (base) | Σ(frequency-weighted attendance × household size midpoint × discount) | ≥ attendance needed to fill program schedule |
| K-04 Top-program interest | % rating ≥4 for top 3 programs | ≥ 40% |
| K-05 Startup capital need | Base startup + contingency + 6-mo operating reserve, per model | Compared to modeled realized funding |
| K-06 Funding coverage ratio | Modeled realized funding ÷ capital need | ≥ 1.0 base, ≥ 0.8 conservative |
| K-07 Operating coverage ratio | Modeled realized recurring income ÷ annual opex | ≥ 1.0 by month 12 |
| K-08 Months of runway | Months until reserve < 3 months opex | ≥ 24 for STRAT_A |
| K-09 Due-diligence completeness | % of property × review-area cells `verified_ok` | 100% for any property under STRAT_A |
| K-10 Evidence grade | % of decision-critical inputs with verified status | ≥ 70% for STRAT_A |
| K-11 Data-quality pass rate | % rows passing all validation rules after cleaning | ≥ 98% |

*Thresholds are **[ASSUMPTION — VALIDATE]**; the committee should set them before seeing results to avoid moving the goalposts.

## 16. Reporting requirements

| ID | Report | Audience | Frequency | Content |
|---|---|---|---|---|
| RR-01 | Executive feasibility brief | Committee | At decision point | Recommendation, gates, scorecard, top risks, data gaps |
| RR-02 | Power BI dashboard (8 pages) | Committee, treasurer, facilities lead | On refresh | See Part 4 dashboard spec |
| RR-03 | Data-quality report | Analyst, reviewer | Each pipeline run | Issue counts by rule, before/after metrics |
| RR-04 | Financial model workbook/export | Treasurer | On assumption change | Cost tables, cash-flows, thresholds |
| RR-05 | Due-diligence tracker | Facilities lead | Weekly (real-world) | Status per property × area; open actions |
| RR-06 | Data-gap register | Committee | At each phase gate | Missing inputs ranked by decision impact |

## 17. Decision criteria

**Hard gates** (any failure → STRAT_C regardless of score):

| Gate | Condition to pass |
|---|---|
| G1 Demand evidence | K-01 met and K-02 lower CI bound > 0 meaningful threshold set by committee |
| G2 Governance | A legally formed nonprofit (or fiscal sponsor) and board exist before any lease/purchase **[real-world]** |
| G3 Legal use pathway | For STRAT_A: chosen property has zoning/use pathway confirmed by planning staff. For STRAT_B: venue owner confirms religious gatherings permitted. |
| G4 Funding floor | Modeled realized funds ≥ startup need under base costs (STRAT_A) or ≥ 6 months of rental costs (STRAT_B) |

**Weighted criteria** (weights set by stakeholders — default shown):

| Criterion | Default weight | Measured by |
|---|---|---|
| Community demand strength | 25 | K-02, K-03 |
| Financial sustainability | 25 | K-06, K-07, K-08 |
| Property & regulatory feasibility | 20 | K-09, gate G3 detail |
| Funding confidence (evidence quality) | 15 | Share of funding that is realized vs pledged; K-10 |
| Operational readiness (volunteers, priest, programs) | 15 | Volunteer hours coverage, program readiness |

Full scoring scales and sensitivity rules are specified in the decision framework (Part 4).

## 18. Financial and operational feasibility criteria

| ID | Criterion | Pass condition (base case) |
|---|---|---|
| FC-01 | Capital adequacy | Realized startup funds ≥ startup cost + contingency + 6-mo operating reserve |
| FC-02 | Operating sustainability | Realized recurring income ≥ 100% of operating cost by month 12, ≥ 80% in conservative case |
| FC-03 | Runway | Conservative case keeps ≥ 3 months reserve for 24 months |
| FC-04 | Downside resilience | At 50% of base attendance, deficit can be covered by reserve for ≥ 12 months |
| FC-05 | Lease exposure | Total committed lease obligation ≤ realized reserves + 12 months realized income |
| OC-01 | Volunteer coverage | Required volunteer hours/month ≤ 70% of stated volunteer capacity × realization rate |
| OC-02 | Religious staffing | Priest/officiant availability confirmed for launch schedule |
| OC-03 | Space fit | Assembly area and parking meet peak-regular demand; festivals handled by caps or off-site |

## 19. Regulatory due-diligence requirements

The study shall **track**, not determine, the following for each property. Real answers come only from the agencies and professionals listed.

| ID | Area | Questions to resolve | Who answers (real-world) |
|---|---|---|---|
| RD-01 | Jurisdiction | Is the parcel in the City of Tracy or unincorporated San Joaquin County? | City/County GIS & planning |
| RD-02 | Zoning & allowable use | Is religious assembly permitted, conditionally permitted, or prohibited in the zone? Any specific plan overlays? | Planning division; municipal/development code |
| RD-03 | Discretionary approval | Is a CUP (or equivalent) required? Hearing body, timeline, fees, conditions (attendance caps, hours)? | Planning staff; pre-application meeting |
| RD-04 | Change of use / occupancy | Does the change to assembly occupancy trigger building upgrades (egress, restrooms, sprinklers, structural)? | Building official; architect |
| RD-05 | Accessibility | Path of travel, restrooms, parking stalls, entrances (state & federal accessibility requirements) | Architect / CASp inspector |
| RD-06 | Fire & life safety | Occupant load, sprinklers, alarms, exits, open flame/incense/havan policy, kitchen hood | Fire marshal / fire district |
| RD-07 | Parking & traffic | Code-required spaces for assembly; joint-use parking options; traffic study need | Planning; traffic engineer |
| RD-08 | Environmental review | CEQA exemption vs. further review | Planning |
| RD-09 | Kitchen / food service | Health permit for prasad/community meals | County environmental health |
| RD-10 | Signage, noise, hours | Sign permits; noise limits for festivals | Planning; code enforcement |
| RD-11 | Organization & tax | Nonprofit incorporation, federal/state tax exemption, property-tax exemption options | Attorney; CPA |
| RD-12 | Insurance | General liability, property, D&O, event coverage | Insurance broker |

## 20. Project timeline and deliverables

| # | Deliverable | Part | Week |
|---|---|---|---|
| 1 | Project charter & refined problem | 1 | 1 |
| 2 | BRD (this document) | 1 | 1–2 |
| 3 | Business question register (≥30) | 1 | 2 |
| 4 | Data architecture: dictionary, ERD, PostgreSQL DDL | 1 | 2 |
| 5 | Synthetic dataset + generator script | 2 | 3 |
| 6 | Data-quality challenge guide | 2 | 3 |
| 7 | Python cleaning workflow (notebook + module) | 2 | 4 |
| 8 | ≥25 SQL queries | 3 | 5 |
| 9 | Financial feasibility model | 3 | 5–6 |
| 10 | Property & regulatory due-diligence checklist | 4 | 7 |
| 11 | ML assessment | 4 | 7 |
| 12 | Power BI dashboard design | 4 | 7–8 |
| 13 | Testing & validation plan | 4 | 8 |
| 14 | Decision framework & scorecard | 4 | 8 |
| 15 | GitHub README & folder structure | 4 | 9 |

---

### Sources (context only — re-verify before real-world use)
- City of Tracy Planning Commission staff report, CUP for place of worship in Edgewood Corporate Center (cites TMC §10.08.4250): https://cityoftracy.org/home/showpublisheddocument/6142/637547934931570000
- City of Tracy staff report, CUP for place of worship incl. joint-use parking under TMC §10.08.3460(j): https://cityoftracy.org/home/showpublisheddocument/5970/637547917996300000
- City of Tracy staff report, CUP for expansion of religious assembly in MO zone: https://cityoftracy.org/home/showpublisheddocument/5930/637547917300170000
- San Joaquin County CEQA filing, CUP PA-2400506 (agricultural building conversion to temple, phased, attendance caps): https://ceqanet.lci.ca.gov/2026060211
- San Joaquin County CEQA filing, CUP PA-1900085 (religious assembly, Tracy area): https://ceqanet.lci.ca.gov/2025061188
- Hindu Community and Cultural Center, Livermore (regional context): https://carnaticamerica.com/organizer/hindu-community-and-cultural-center/
