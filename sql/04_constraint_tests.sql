-- FR-10 constraint test: every INSERT below must be REJECTED (expect 8 errors).
-- Run: psql -v ON_ERROR_STOP=0 -f sql/04_constraint_tests.sql
SET search_path TO temple;
\set ON_ERROR_STOP 0
INSERT INTO survey_response(respondent_id,response_date,consent_flag,attendance_frequency,is_duplicate,data_status,source_id) VALUES ('R0001','2026-04-01',true,'weekly',false,'synthetic','SRC001');
-- should FAIL: duplicate without link
INSERT INTO survey_response(respondent_id,response_date,consent_flag,attendance_frequency,is_duplicate,data_status,source_id) VALUES ('R0002','2026-04-01',true,'weekly',true,'synthetic','SRC001');
-- should FAIL: bad frequency
INSERT INTO survey_response(respondent_id,response_date,consent_flag,attendance_frequency,data_status,source_id) VALUES ('R0003','2026-04-01',true,'Weekly ','synthetic','SRC001');
-- should FAIL: rating 6
INSERT INTO program_preference VALUES ('P1','R0001','YOGA_MED',6,'weekly','synthetic','SRC001');
-- should FAIL: orphan respondent
INSERT INTO program_preference VALUES ('P2','R9999','YOGA_MED',4,'weekly','synthetic','SRC001');
-- should FAIL: simulated property claiming verified
INSERT INTO candidate_property(property_id,area_label,jurisdiction,property_type,tenure_offered,zoning_verification,is_simulated,data_status,source_id) VALUES ('SIM-P99','x','unknown','retail_unit','lease','not_checked',true,'verified_official','SRC002');
-- should FAIL: lease with sale price
INSERT INTO candidate_property(property_id,area_label,jurisdiction,property_type,tenure_offered,asking_price,zoning_verification,is_simulated,data_status,source_id) VALUES ('SIM-P98','x','unknown','retail_unit','lease',100000,'not_checked',true,'synthetic','SRC002');
-- should FAIL: low>base
INSERT INTO startup_cost_estimate VALUES ('SC1','OM_RENT_EVENT','RITUAL_SETUP','x',500,400,600,null,'synthetic_placeholder','synthetic','SRC003');
-- should FAIL: bad data_status
INSERT INTO startup_cost_estimate VALUES ('SC2','OM_RENT_EVENT','RITUAL_SETUP','x',100,400,600,null,'synthetic_placeholder','fake','SRC003');
DELETE FROM survey_response;
