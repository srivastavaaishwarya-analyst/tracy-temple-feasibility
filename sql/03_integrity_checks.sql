-- =====================================================================
-- Referential-integrity & data-quality checks. Run after every load.
-- Every query should return 0 rows (or count = 0) unless noted.
-- =====================================================================
SET search_path TO temple;

-- IC-01 Orphan preference records (FK enforced; this is a defense-in-depth check for staging loads)
SELECT 'IC-01' AS check_id, COUNT(*) AS violations
FROM program_preference pp
LEFT JOIN survey_response sr USING (respondent_id)
WHERE sr.respondent_id IS NULL;

-- IC-02 Every candidate property has exactly 5 due-diligence rows
SELECT 'IC-02' AS check_id, p.property_id, COUNT(d.dd_id) AS dd_rows
FROM candidate_property p
LEFT JOIN property_due_diligence d USING (property_id)
GROUP BY p.property_id
HAVING COUNT(d.dd_id) <> 5;

-- IC-03 Duplicates must point to a non-duplicate original
SELECT 'IC-03' AS check_id, d.respondent_id, d.duplicate_of
FROM survey_response d
JOIN survey_response o ON o.respondent_id = d.duplicate_of
WHERE d.is_duplicate AND o.is_duplicate;

-- IC-04 Duplicate should not precede its original
SELECT 'IC-04' AS check_id, d.respondent_id
FROM survey_response d
JOIN survey_response o ON o.respondent_id = d.duplicate_of
WHERE d.response_date < o.response_date;

-- IC-05 Simulated properties must be labeled synthetic
SELECT 'IC-05' AS check_id, property_id
FROM candidate_property
WHERE is_simulated AND data_status <> 'synthetic';

-- IC-06 Records using a synthetic source must not claim real/verified status
SELECT 'IC-06' AS check_id, t.tbl, t.k
FROM (
  SELECT 'survey_response' tbl, respondent_id k, data_status, source_id FROM survey_response
  UNION ALL SELECT 'program_preference', preference_id, data_status, source_id FROM program_preference
  UNION ALL SELECT 'candidate_property', property_id, data_status, source_id FROM candidate_property
  UNION ALL SELECT 'startup_cost_estimate', cost_id, data_status, source_id FROM startup_cost_estimate
  UNION ALL SELECT 'operating_cost_estimate', op_cost_id, data_status, source_id FROM operating_cost_estimate
) t
JOIN data_source s USING (source_id)
WHERE s.data_status = 'synthetic' AND t.data_status IN ('real_observation','verified_official');

-- IC-07 Purchase-only categories used by non-purchase models
SELECT 'IC-07' AS check_id, cost_id, model_code, cost_category_code
FROM startup_cost_estimate
WHERE cost_category_code = 'ACQUISITION' AND model_code <> 'OM_PURCHASE_ADAPT'
UNION ALL
SELECT 'IC-07', op_cost_id, model_code, cost_category_code
FROM operating_cost_estimate
WHERE cost_category_code = 'MORTGAGE' AND model_code <> 'OM_PURCHASE_ADAPT';

-- IC-08 Cost category type matches table (startup vs operating)
SELECT 'IC-08' AS check_id, s.cost_id
FROM startup_cost_estimate s JOIN cost_category c USING (cost_category_code)
WHERE c.cost_type <> 'startup'
UNION ALL
SELECT 'IC-08', o.op_cost_id
FROM operating_cost_estimate o JOIN cost_category c USING (cost_category_code)
WHERE c.cost_type <> 'operating';

-- IC-09 Survey top choices: rank sequence has no gaps (1..n)
SELECT 'IC-09' AS check_id, respondent_id
FROM survey_top_choice
GROUP BY respondent_id
HAVING MAX(choice_rank) <> COUNT(*);

-- IC-10 'NONE' barrier must not co-occur with another barrier
SELECT 'IC-10' AS check_id, respondent_id
FROM survey_barrier
GROUP BY respondent_id
HAVING BOOL_OR(barrier_code = 'NONE') AND COUNT(*) > 1;

-- IC-11 Due-diligence 'verified_ok' on a simulated property can't make it 'viable'
SELECT 'IC-11' AS check_id, property_id
FROM v_property_dd_wide v JOIN candidate_property p USING (property_id)
WHERE p.is_simulated AND v.dd_classification = 'viable';

-- IC-12 Missing-data profile (informational, not a failure)
SELECT 'IC-12' AS check_id,
       COUNT(*)                                             AS respondents,
       COUNT(*) FILTER (WHERE age_group IS NULL)            AS missing_age_group,
       COUNT(*) FILTER (WHERE household_size_range IS NULL) AS missing_household,
       COUNT(*) FILTER (WHERE max_travel_minutes IS NULL)   AS missing_travel,
       COUNT(*) FILTER (WHERE monthly_contribution_stated IS NULL) AS missing_contribution,
       COUNT(*) FILTER (WHERE comment_text IS NULL)         AS missing_comment
FROM survey_response;

-- IC-13 Evidence profile by table (feeds dashboard page 8 / question F06)
SELECT 'IC-13' AS check_id, tbl, data_status, COUNT(*) AS n
FROM (
  SELECT 'survey_response' tbl, data_status FROM survey_response
  UNION ALL SELECT 'program_preference', data_status FROM program_preference
  UNION ALL SELECT 'program_option', data_status FROM program_option
  UNION ALL SELECT 'candidate_property', data_status FROM candidate_property
  UNION ALL SELECT 'property_due_diligence', data_status FROM property_due_diligence
  UNION ALL SELECT 'startup_cost_estimate', data_status FROM startup_cost_estimate
  UNION ALL SELECT 'operating_cost_estimate', data_status FROM operating_cost_estimate
  UNION ALL SELECT 'funding_scenario', data_status FROM funding_scenario
  UNION ALL SELECT 'model_assumption', data_status FROM model_assumption
) x
GROUP BY tbl, data_status
ORDER BY tbl, data_status;
