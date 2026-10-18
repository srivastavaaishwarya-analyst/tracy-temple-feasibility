# Part 1B — Business Question Register

These questions are defined **before** any data is generated, so that the data model serves the questions and not the other way round. Table names refer to the PostgreSQL schema in `sql/01_schema.sql` (documented in `docs/03_data_architecture.md`).

> **No answers are given here.** Every question that depends on survey, property, cost, or funding data can only be answered with *method-demonstration* results from synthetic data in this portfolio. A real answer requires the real-world data listed under "Limitations".

**Tool key:** PY = Python (pandas/NumPy/SciPy) · SQL = PostgreSQL · XL = Excel · PBI = Power BI
**Decision link key:** which gate / criterion in BRD §17 the answer feeds.

### Summary index

| ID | Question | Tools | Feeds |
|---|---|---|---|
| A01 | How many eligible (deduplicated, consented, in-window) responses are there? | PY, SQL | G1, K-01 |
| A02 | What share of respondents intend to attend weekly or more, and with what uncertainty? | PY, SQL | G1, K-02 |
| A03 | What is the conservative expected regular attendance range? | PY, XL | K-03, sizing |
| A04 | Which days and times do respondents prefer? | SQL, PBI | Ops schedule |
| A05 | How far are respondents willing to travel, and does travel tolerance differ by attendance intent? | SQL, PY | Location |
| A06 | What are the main barriers to participation? | SQL, PY | Program design, risk |
| A07 | How many respondents already attend a temple elsewhere, and does that reduce their intent? | SQL, PY | Demand, RK-11 |
| A08 | How sensitive are demand metrics to removing duplicates and invalid records? | PY | Evidence grade |
| A09 | What themes appear in open-ended comments? | PY | Program design, risk |
| B01 | What minimum floor area and parking are required for peak regular and festival attendance? | PY, XL | OC-03, BR-08 |
| B02 | Which candidate properties meet minimum area and parking, and which are unknown? | SQL | Shortlist |
| B03 | How do candidates compare on cost per usable sq ft and cost per parking space? | SQL, PBI | Shortlist |
| B04 | Which properties have open, failed, or unstarted due-diligence items? | SQL, PBI | G3 |
| B05 | Which jurisdiction (City vs County) governs each candidate, and how many are unknown? | SQL | G3, RD-01 |
| B06 | What planning/land-use questions remain unresolved per property, and what would it cost to resolve them? | SQL | G3, timeline |
| C01 | What is the startup cost per operating model at low/base/high? | SQL, PY, XL | FC-01 |
| C02 | What share of each model's startup cost is verified vs. hypothetical? | SQL | Evidence grade |
| C03 | What is the recurring monthly and annual operating cost per model? | SQL, PY | FC-02 |
| C04 | How much initial funding is required (startup + contingency + operating reserve)? | PY, XL | G4, FC-01 |
| C05 | What recurring giving would be needed to break even, per model? | PY, SQL | FC-02, K-07 |
| C06 | What do survey contribution statements imply after conservative realization? | SQL, PY | K-06 |
| C07 | Under which funding scenarios does each model stay solvent for 36 months? | PY, PBI | FC-03 |
| C08 | How sensitive is sustainability to lower attendance and lower pledge realization? | PY, PBI | FC-04, sensitivity |
| D01 | Which operating model has the lowest cost per expected attendee-visit? | PY, SQL | Model choice |
| D02 | What are the qualitative advantages and disadvantages of each model? | XL (structured matrix) | Model choice |
| D03 | What minimum operating resources (volunteer hours, paid roles, equipment) does each model need? | SQL, PY | OC-01, OC-02 |
| E01 | Which programs rank highest by interest, and how stable is the ranking across segments? | SQL, PY | Launch portfolio |
| E02 | Which programs give the most interested households per dollar? | SQL | Launch portfolio |
| E03 | Which programs can run in a rented venue vs. need a dedicated facility? | SQL | STRAT_B vs A |
| E04 | What total volunteer and staff hours would the launch portfolio require vs. capacity? | SQL, PY | OC-01 |
| E05 | Which programs should be phased later and why? | SQL, PY | Phasing |
| F01 | What are the top risks by likelihood × impact, and which are data-dependent? | XL, PBI | Risk |
| F02 | Which missing inputs, if verified, would most change the recommendation? | PY | Data-gap register |
| F03 | What milestones and approvals must be complete before launch under each strategy? | XL | Timeline |
| F04 | Which hard gates currently pass, fail, or are undetermined? | PY, SQL | Recommendation |
| F05 | How robust is the recommended strategy to changes in criterion weights? | PY, PBI | Sensitivity |
| F06 | How much of the evidence behind the recommendation is real vs. synthetic vs. assumed? | SQL | Evidence grade, BR-15 |

37 questions in total. Detailed specifications follow.

---

## A. Community demand

### A01 — How many eligible responses are there?
1. **ID:** A01
2. **Business reason:** All demand metrics depend on a defensible denominator; duplicates, non-consent, or out-of-window responses inflate apparent interest.
3. **Data required:** respondent ID, consent flag, response date, duplicate flags.
4. **Tables:** `survey_response`
5. **Tools:** PY (flagging), SQL (counts)
6. **Method:** Apply BRL-01/BRL-02; count raw vs flagged vs eligible.
7. **Expected output:** Funnel table: raw → valid date → consented → non-duplicate → eligible.
8. **Decision support:** Gate G1 requires minimum eligible n (K-01). Too few → STRAT_C or more outreach.
9. **Limitations:** Count reflects survey reach, not community size. Non-respondents are unobserved.

### A02 — What share intend weekly-or-more attendance, with uncertainty?
1. **ID:** A02
2. **Reason:** Regular attendance underpins recurring giving and volunteer supply.
3. **Data:** `attendance_frequency` for eligible respondents.
4. **Tables:** `survey_response`
5. **Tools:** PY (Wilson CI), SQL (proportions)
6. **Method:** Proportion by frequency category; Wilson 95% CI; segment by age group and household size.
7. **Output:** Frequency distribution with CIs; segmented bar chart.
8. **Decision:** Feeds demand criterion (25% default weight) and G1.
9. **Limitations:** Self-selection bias (interested people respond more); stated ≠ actual behavior; CI reflects sampling error only, not bias.

### A03 — What is the conservative expected regular attendance range?
1. **ID:** A03
2. **Reason:** Space, parking, and staffing must be sized to realistic, not aspirational, attendance.
3. **Data:** frequency, household size range, intent-to-behavior discount factors.
4. **Tables:** `survey_response`, `model_assumption`
5. **Tools:** PY, XL
6. **Method:** Visits/month per household = frequency midpoint × household-size midpoint × discount (low/base/high); sum; convert to typical weekend peak.
7. **Output:** Low/base/high expected weekly attendees and peak-event attendees.
8. **Decision:** Drives B01 space/parking requirement and C05 per-attendee giving.
9. **Limitations:** Discount factors are assumptions (AS-02) until pilot-event counts exist; extrapolation to non-respondents is not attempted.

### A04 — Which days and times are preferred?
1. **ID:** A04
2. **Reason:** Determines whether a rented venue's available slots match demand; affects parking conflicts with neighbors.
3. **Data:** preferred day, preferred time.
4. **Tables:** `survey_response`
5. **Tools:** SQL, PBI
6. **Method:** Cross-tab day × time; share of total.
7. **Output:** Heatmap of day × time preference.
8. **Decision:** Scheduling; joint-use parking feasibility (weekend vs weekday tenants).
9. **Limitations:** Single-choice fields may hide flexibility.

### A05 — How far will respondents travel, and does it differ by intent?
1. **ID:** A05
2. **Reason:** If regular attendees tolerate only short trips, location matters more; long tolerance implies competition with regional temples.
3. **Data:** max travel minutes, attendance frequency.
4. **Tables:** `survey_response`
5. **Tools:** SQL, PY
6. **Method:** Median and IQR travel tolerance by frequency group; Kruskal–Wallis test.
7. **Output:** Box plot; summary table.
8. **Decision:** Location criteria; positioning vs. existing temples (RK-11).
9. **Limitations:** Stated tolerance; no actual geocoded origins (privacy by design).

### A06 — What are the main barriers?
1. **ID:** A06
2. **Reason:** Barriers indicate which program design or location choices unlock participation.
3. **Data:** barrier codes (multi-select).
4. **Tables:** `survey_barrier`, `survey_response`
5. **Tools:** SQL, PY
6. **Method:** Frequency of each barrier among eligible respondents; cross-tab with frequency intent.
7. **Output:** Ranked barrier list with % of respondents.
8. **Decision:** E.g., high "parking" or "travel" barrier raises weight on location; "schedule" favors evening programs.
9. **Limitations:** Multi-select responses are not mutually exclusive; percentages don't sum to 100.

### A07 — How many already attend a temple elsewhere, and does that reduce intent?
1. **ID:** A07
2. **Reason:** A new temple may complement or compete with existing temples.
3. **Data:** `ALREADY_ATTEND_ELSEWHERE` barrier flag, attendance frequency.
4. **Tables:** `survey_barrier`, `survey_response`
5. **Tools:** SQL, PY
6. **Method:** Compare weekly-intent share between groups; chi-square test.
7. **Output:** 2×k contingency table and test result.
8. **Decision:** Positioning strategy; demand discount.
9. **Limitations:** Requires real inventory of regional temples (DR-11) to interpret.

### A08 — How sensitive are demand metrics to cleaning?
1. **ID:** A08
2. **Reason:** Shows whether conclusions depend on data quality decisions.
3. **Data:** raw and cleaned survey data; `dq_issue_log`.
4. **Tables:** `survey_response`, `dq_issue_log`
5. **Tools:** PY
6. **Method:** Compute K-01, K-02, K-03 on raw vs cleaned; report deltas.
7. **Output:** Before/after table (FR-15).
8. **Decision:** Evidence grade; confidence in G1.
9. **Limitations:** Synthetic DQ issues are designed, not observed.

### A09 — What themes appear in comments?
1. **ID:** A09
2. **Reason:** Free text reveals needs and concerns not captured in checkboxes.
3. **Data:** `comment_text`.
4. **Tables:** `survey_response`
5. **Tools:** PY (keyword rules; optional NLP in Part 4)
6. **Method:** Rule-based theme tagging; hand-label 50 for precision check.
7. **Output:** Theme frequency table, example (synthetic) comments per theme.
8. **Decision:** Program design, risk register updates.
9. **Limitations:** Synthetic comments are templated; real comments needed for meaningful NLP.

---

## B. Location and property feasibility

### B01 — What floor area and parking are needed?
1. **ID:** B01
2. **Reason:** Translates demand into physical requirements.
3. **Data:** A03 attendance range; area-per-person and attendees-per-parking-space assumptions.
4. **Tables:** `model_assumption`, derived from `survey_response`
5. **Tools:** PY, XL
6. **Method:** Required assembly sq ft = peak attendees × sq ft/person (low/base/high); add support space; required stalls = peak ÷ persons/stall.
7. **Output:** Requirements table for regular peak and festival peak.
8. **Decision:** Sets filter thresholds for B02; informs OC-03.
9. **Limitations:** Code occupant-load factors and parking ratios must come from the building code and local code via professionals.

### B02 — Which candidates meet minimum area and parking?
1. **ID:** B02
2. **Reason:** Quick shortlist filter.
3. **Data:** floor area, parking spaces, B01 thresholds.
4. **Tables:** `candidate_property`, `model_assumption`
5. **Tools:** SQL
6. **Method:** CASE classification: meets / below / unknown for area and parking.
7. **Output:** Property list with pass/fail/unknown flags.
8. **Decision:** Narrows due-diligence effort.
9. **Limitations:** Candidates are synthetic; unknown parking is common in real listings.

### B03 — How do candidates compare on cost efficiency?
1. **ID:** B03
2. **Reason:** Normalizes cost across different sizes and tenures.
3. **Data:** asking rent/price/hourly rate, floor area, parking.
4. **Tables:** `candidate_property`
5. **Tools:** SQL, PBI
6. **Method:** Annualized cost per sq ft; per parking space; RANK() within tenure type.
7. **Output:** Ranked comparison table; scatter of area vs. annual cost.
8. **Decision:** Shortlist ordering.
9. **Limitations:** Asking ≠ negotiated price; excludes tenant-improvement costs (handled in C01).

### B04 — Which properties have open, failed, or unstarted due diligence?
1. **ID:** B04
2. **Reason:** No property is viable until five review areas are cleared (BRL-06).
3. **Data:** status by review area.
4. **Tables:** `property_due_diligence`, `candidate_property`
5. **Tools:** SQL, PBI
6. **Method:** Pivot status by area; count open items; flag any `failed`.
7. **Output:** Status matrix (property × area).
8. **Decision:** Gate G3; next actions.
9. **Limitations:** Statuses are synthetic; real statuses require agency confirmation.

### B05 — Which jurisdiction governs each candidate?
1. **ID:** B05
2. **Reason:** City of Tracy and San Joaquin County have different codes and processes.
3. **Data:** jurisdiction field.
4. **Tables:** `candidate_property`
5. **Tools:** SQL
6. **Method:** Count by jurisdiction including `unknown`.
7. **Output:** Table and list of unknowns to verify.
8. **Decision:** Determines which code and agency to consult (RD-01).
9. **Limitations:** Must be confirmed by parcel lookup.

### B06 — What land-use questions remain unresolved per property, and at what estimated resolution cost?
1. **ID:** B06
2. **Reason:** Converts due diligence into budget and timeline.
3. **Data:** next action, estimated cost to resolve, owner role.
4. **Tables:** `property_due_diligence`
5. **Tools:** SQL
6. **Method:** Filter status not in (`verified_ok`,`not_applicable`); sum resolution cost per property.
7. **Output:** Open-item list and total per property.
8. **Decision:** Adds due-diligence cost to startup estimate; property ranking.
9. **Limitations:** Resolution costs are placeholders until professional quotes.

---

## C. Financial feasibility

### C01 — What is startup cost per model at low/base/high?
1. **ID:** C01
2. **Reason:** Primary capital need.
3. **Data:** startup cost lines.
4. **Tables:** `startup_cost_estimate`, `cost_category`, `operating_model`
5. **Tools:** SQL, PY, XL
6. **Method:** SUM by model; with and without contingency (BRL-08).
7. **Output:** 3×3 table (model × case).
8. **Decision:** FC-01, G4.
9. **Limitations:** Synthetic placeholders; renovation costs highly property-specific.

### C02 — What share of startup cost is verified?
1. **ID:** C02
2. **Reason:** A low verified share means the number is soft.
3. **Data:** `verification_status` per cost line.
4. **Tables:** `startup_cost_estimate`
5. **Tools:** SQL
6. **Method:** SUM(base) by verification status ÷ total.
7. **Output:** Stacked bar by model.
8. **Decision:** Evidence grade K-10; funding-confidence criterion.
9. **Limitations:** In this portfolio, verified share is 0% by design.

### C03 — What are recurring monthly and annual costs?
1. **ID:** C03
2. **Reason:** Sustainability is about recurring costs.
3. **Data:** monthly cost lines.
4. **Tables:** `operating_cost_estimate`, `cost_category`
5. **Tools:** SQL, PY
6. **Method:** SUM monthly by model & case; × 12.
7. **Output:** Monthly and annual totals; category breakdown.
8. **Decision:** FC-02, C05.
9. **Limitations:** Utilities and insurance depend on property and coverage.

### C04 — How much initial funding is required?
1. **ID:** C04
2. **Reason:** Defines fundraising target.
3. **Data:** C01, C03, reserve rule (BRL-09), contingency rule (BRL-08), B06 resolution costs.
4. **Tables:** `startup_cost_estimate`, `operating_cost_estimate`, `model_assumption`, `property_due_diligence`
5. **Tools:** PY, XL
6. **Method:** Startup + contingency + 6 × monthly opex (+ due-diligence costs).
7. **Output:** Capital need per model × case.
8. **Decision:** G4, FC-01.
9. **Limitations:** Excludes financing (mortgage) unless modeled explicitly.

### C05 — What recurring giving is needed to break even?
1. **ID:** C05
2. **Reason:** Converts costs into a concrete community target.
3. **Data:** C03; program fee assumptions (if any).
4. **Tables:** `operating_cost_estimate`, `program_option`, `model_assumption`
5. **Tools:** PY, SQL
6. **Method:** Break-even monthly donations = monthly opex − other income; ÷ expected households (A03) = per-household monthly gift needed.
7. **Output:** $/month total and per household by model.
8. **Decision:** FC-02, K-07.
9. **Limitations:** Per-household figure assumes giving spread evenly; real giving is concentrated.

### C06 — What do stated contributions imply after realization?
1. **ID:** C06
2. **Reason:** Stated willingness is not cash (BRL-03).
3. **Data:** stated monthly contribution, one-time pledge, realization rates.
4. **Tables:** `survey_response`, `model_assumption`
5. **Tools:** SQL, PY
6. **Method:** Sum eligible stated amounts; apply low/base/high realization; report median and concentration (top-10% share).
7. **Output:** Stated vs modeled-realized totals.
8. **Decision:** K-06, funding-confidence criterion.
9. **Limitations:** Contribution field is optional and voluntarily provided; non-response is not zero.

### C07 — Which scenarios stay solvent for 36 months?
1. **ID:** C07
2. **Reason:** Tests financial survival, not just year-1 balance.
3. **Data:** funding scenarios, costs by model and case.
4. **Tables:** `funding_scenario`, `startup_cost_estimate`, `operating_cost_estimate`, `model_assumption`
5. **Tools:** PY, PBI
6. **Method:** Monthly cash-flow simulation; minimum balance; month reserve falls below 3 months opex.
7. **Output:** Grid: model × scenario × case → solvent? months of runway.
8. **Decision:** FC-03, financial criterion.
9. **Limitations:** Deterministic scenarios; Monte Carlo optional extension.

### C08 — How sensitive is sustainability to lower attendance and realization?
1. **ID:** C08
2. **Reason:** Identifies the assumptions that matter most.
3. **Data:** C07 model; ranges for attendance discount, realization rate, rent, insurance.
4. **Tables:** `model_assumption`, `funding_scenario`
5. **Tools:** PY, PBI
6. **Method:** One-at-a-time tornado analysis; two-way grid (attendance × realization).
7. **Output:** Tornado chart; break-even contour.
8. **Decision:** FC-04; data-gap prioritization (F02).
9. **Limitations:** One-at-a-time ignores interactions (two-way grid partially addresses).

---

## D. Operating model

### D01 — Which model has the lowest cost per expected attendee-visit?
1. **ID:** D01
2. **Reason:** Normalizes cost by service delivered.
3. **Data:** annual cost per model; expected annual visits per model (rent model has fewer sessions).
4. **Tables:** `operating_cost_estimate`, `startup_cost_estimate`, `model_assumption`
5. **Tools:** PY, SQL
6. **Method:** (Annual opex + startup annualized over 5 yrs) ÷ expected annual visits.
7. **Output:** Cost per visit by model × case.
8. **Decision:** Model choice within STRAT_A vs STRAT_B.
9. **Limitations:** Visits depend on A03 assumptions; rented model caps sessions by venue availability.

### D02 — What are the advantages and disadvantages of each model?
1. **ID:** D02
2. **Reason:** Some factors (flexibility, ritual continuity, permanence) aren't monetary.
3. **Data:** structured criteria ratings by stakeholders.
4. **Tables:** — (stakeholder matrix; optional future table)
5. **Tools:** XL
6. **Method:** Structured pros/cons matrix with criteria: commitment, flexibility, ritual suitability, permitting burden, community identity, exit cost.
7. **Output:** Comparison matrix.
8. **Decision:** Qualitative input to scorecard.
9. **Limitations:** Requires real stakeholder input; analyst can only frame the criteria.

### D03 — What minimum operating resources does each model need?
1. **ID:** D03
2. **Reason:** Volunteer and staff capacity is a binding constraint.
3. **Data:** program resource needs; volunteer capacity from survey.
4. **Tables:** `program_option`, `survey_response`, `model_assumption`
5. **Tools:** SQL, PY
6. **Method:** Sum volunteer & paid hours for programs feasible in each model; compare to realized volunteer capacity.
7. **Output:** Required vs available hours per model.
8. **Decision:** OC-01, OC-02.
9. **Limitations:** Stated volunteer hours overstate actual.

---

## E. Community programs and services

### E01 — Which programs rank highest, and is the ranking stable across segments?
1. **ID:** E01
2. **Reason:** Launch with programs broadly valued, not just by one segment.
3. **Data:** interest ratings, segments.
4. **Tables:** `program_preference`, `program_category`, `survey_response`
5. **Tools:** SQL (RANK/DENSE_RANK), PY (Kendall tau between segment rankings)
6. **Method:** Mean rating, % top-2-box; rank overall and by age group.
7. **Output:** Ranked list; segment rank table.
8. **Decision:** Launch portfolio (BR-04).
9. **Limitations:** Respondents rated only programs they selected to rate → not all categories have equal n.

### E02 — Which programs give the most interested households per dollar?
1. **ID:** E02
2. **Reason:** Budget efficiency.
3. **Data:** interested count (rating ≥4), launch + 12-mo recurring cost.
4. **Tables:** `program_preference`, `program_option`
5. **Tools:** SQL
6. **Method:** First-year cost ÷ interested households.
7. **Output:** Cost per interested household, ranked.
8. **Decision:** Launch selection.
9. **Limitations:** Program costs synthetic.

### E03 — Which programs can run in a rented venue?
1. **ID:** E03
2. **Reason:** Determines what STRAT_B can actually deliver.
3. **Data:** space need, open flame, kitchen, min area.
4. **Tables:** `program_option`
5. **Tools:** SQL
6. **Method:** CASE rule: rented-feasible if no permanent sanctum, no open flame (unless venue confirms), area ≤ typical hall.
7. **Output:** Program × model feasibility matrix.
8. **Decision:** STRAT_B viability.
9. **Limitations:** Venue policies vary (AS-04).

### E04 — Total volunteer and staff hours vs capacity?
1. **ID:** E04
2. **Reason:** Avoid volunteer burnout (RK-07).
3. **Data:** program hours, survey volunteer hours.
4. **Tables:** `program_option`, `survey_response`, `model_assumption`
5. **Tools:** SQL, PY
6. **Method:** Sum launch-portfolio hours; compare with stated × realization.
7. **Output:** Coverage ratio.
8. **Decision:** OC-01.
9. **Limitations:** Skills mismatch not captured.

### E05 — Which programs should be phased later, and why?
1. **ID:** E05
2. **Reason:** Phasing lowers launch cost and risk.
3. **Data:** E01–E04 outputs.
4. **Tables:** `program_option`, `program_preference`
5. **Tools:** SQL, PY
6. **Method:** Rule-based: launch if (top-half interest) AND (rented-feasible OR model=dedicated) AND (cost per interested household ≤ median); else later phase.
7. **Output:** Phase assignment with rule trace.
8. **Decision:** BR-05.
9. **Limitations:** Rules are transparent but arbitrary until committee agrees thresholds.

---

## F. Risk and implementation

### F01 — What are the top risks, and which are data-dependent?
1. **ID:** F01
2. **Reason:** Focus mitigation effort.
3. **Data:** risk register (BRD §13) with likelihood/impact scores.
4. **Tables:** — (risk register exported as `risk_register.csv` in Part 4)
5. **Tools:** XL, PBI
6. **Method:** Likelihood × impact heatmap; tag risks reducible by data collection.
7. **Output:** Risk heatmap.
8. **Decision:** Mitigation plan; data-gap priorities.
9. **Limitations:** Scores are judgment-based.

### F02 — Which missing inputs would most change the recommendation?
1. **ID:** F02
2. **Reason:** Directs real-world data collection to what matters.
3. **Data:** C08 and F05 sensitivity outputs; `verification_status` fields.
4. **Tables:** `model_assumption`, `startup_cost_estimate`, `operating_cost_estimate`, `property_due_diligence`
5. **Tools:** PY
6. **Method:** Value-of-information proxy: assumptions whose plausible range flips the recommendation, ranked by swing.
7. **Output:** Data-gap register (RR-06).
8. **Decision:** Next steps under STRAT_C or B.
9. **Limitations:** Ranges themselves are assumptions.

### F03 — What milestones and approvals precede launch?
1. **ID:** F03
2. **Reason:** Realistic timeline; avoid committing before approvals.
3. **Data:** due-diligence areas, governance steps.
4. **Tables:** `property_due_diligence` (+ Part 4 checklist)
5. **Tools:** XL (Gantt)
6. **Method:** Dependency-ordered milestone plan per strategy.
7. **Output:** Milestone plan.
8. **Decision:** Timeline feasibility; G2/G3.
9. **Limitations:** Agency timelines unknown until consulted.

### F04 — Which hard gates pass, fail, or are undetermined?
1. **ID:** F04
2. **Reason:** Gates override scores (BRL-11).
3. **Data:** outputs of A01, A02, B04, C04, C06; governance status.
4. **Tables:** multiple (see dependencies)
5. **Tools:** PY, SQL
6. **Method:** Evaluate each gate with three-valued logic (pass / fail / undetermined).
7. **Output:** Gate status table.
8. **Decision:** Undetermined gates → STRAT_C or STRAT_B with data collection.
9. **Limitations:** With synthetic data, gates demonstrate logic only.

### F05 — How robust is the recommendation to weight changes?
1. **ID:** F05
2. **Reason:** Shows whether the choice is driven by arbitrary weights.
3. **Data:** criterion scores, default weights.
4. **Tables:** derived (scorecard output)
5. **Tools:** PY, PBI
6. **Method:** ±10-point perturbations; random weight sampling (Dirichlet) → % of draws selecting each strategy.
7. **Output:** Stability table; "flip points".
8. **Decision:** Confidence in recommendation.
9. **Limitations:** Doesn't fix bad scores — only tests weights.

### F06 — How much evidence is real vs synthetic vs assumed?
1. **ID:** F06
2. **Reason:** Honest evidence grading (BR-15).
3. **Data:** `data_status` on every table.
4. **Tables:** all
5. **Tools:** SQL
6. **Method:** UNION ALL counts by table × data_status.
7. **Output:** Evidence-grade table on dashboard Page 8.
8. **Decision:** K-10; low grade blocks STRAT_A.
9. **Limitations:** Counts rows, not decision weight — paired with F02.

---

## Real-world data needed before any real recommendation

| Needed | Source type | Unblocks |
|---|---|---|
| Anonymous community survey (voluntary, opt-in) | Committee outreach | A01–A09, C06, E01 |
| Pilot-event attendance and donations (STRAT_B trial) | Sign-in counts, donation records | A03 discount factors, C06 realization rate |
| Inventory of existing temples/venues within ~45 min | Directories, community input | A07, positioning |
| Real listings and owner/broker confirmation of use clauses | Brokers, owners | B02, B03 |
| Zoning, CUP, parking ratio, occupancy guidance | City of Tracy / SJ County planning & building, fire district | B01, B04–B06, G3 |
| Contractor, architect, insurer, utility quotes | Professionals | C01–C03, C02 verified share |
| Governance & tax-status plan | Attorney, CPA | G2 |
| Priest/officiant availability and space requirements | Religious advisors | OC-02, E03 |
