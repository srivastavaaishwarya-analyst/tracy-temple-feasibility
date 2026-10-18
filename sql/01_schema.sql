-- =====================================================================
-- Tracy Hindu Temple Feasibility Study — PostgreSQL schema (v1.0)
-- Target: PostgreSQL 14+
-- All data loaded into this schema in the portfolio is SYNTHETIC or
-- HYPOTHETICAL unless data_status says otherwise.
-- =====================================================================

DROP SCHEMA IF EXISTS temple CASCADE;
CREATE SCHEMA temple;
SET search_path TO temple;

-- ---------------------------------------------------------------------
-- Shared domains
-- ---------------------------------------------------------------------
-- data_status distinguishes evidence types on EVERY fact table.
CREATE DOMAIN data_status_t AS TEXT
  CHECK (VALUE IN ('real_observation',      -- collected from a real person/event
                   'synthetic',             -- simulated practice record
                   'unverified_assumption', -- analyst/committee assumption
                   'verified_official'));   -- quote, official doc, or confirmed info

CREATE DOMAIN verification_t AS TEXT
  CHECK (VALUE IN ('verified_quote',        -- written quote from vendor/landlord
                   'published_rate',        -- published fee schedule / rate card
                   'official_document',     -- public agency document (context; re-verify)
                   'analyst_estimate',      -- reasoned estimate, not verified
                   'synthetic_placeholder'));-- generated for practice

CREATE DOMAIN money_t AS NUMERIC(12,2) CHECK (VALUE >= 0);

-- ---------------------------------------------------------------------
-- 1. Reference / lookup tables
-- ---------------------------------------------------------------------
CREATE TABLE data_source (
    source_id            VARCHAR(10)  PRIMARY KEY,            -- e.g. SRC001
    record_group         VARCHAR(150) NOT NULL,               -- which dataset it supports
    source_org           VARCHAR(120) NOT NULL,
    source_ref           TEXT         NOT NULL,               -- URL or citation
    date_accessed        DATE,
    limitations          TEXT,
    verification_status  verification_t NOT NULL,
    data_status          data_status_t  NOT NULL
);

CREATE TABLE operating_model (
    model_code     VARCHAR(20) PRIMARY KEY
                   CHECK (model_code IN ('OM_RENT_EVENT','OM_LEASE_DEDICATED','OM_PURCHASE_ADAPT')),
    model_name     VARCHAR(60) NOT NULL,
    strategy_code  VARCHAR(10) NOT NULL CHECK (strategy_code IN ('STRAT_A','STRAT_B')),
    description    TEXT
);

CREATE TABLE program_category (
    category_code   VARCHAR(20) PRIMARY KEY,
    category_name   VARCHAR(80) NOT NULL UNIQUE,
    category_group  VARCHAR(20) NOT NULL
                    CHECK (category_group IN ('religious','cultural','educational','community'))
);

-- Maps messy survey labels ("Bal Vihar", "kids classes") to canonical codes.
CREATE TABLE program_category_alias (
    alias_text     VARCHAR(80) PRIMARY KEY,   -- stored lower-case, trimmed
    category_code  VARCHAR(20) NOT NULL REFERENCES program_category(category_code)
);

CREATE TABLE barrier_type (
    barrier_code   VARCHAR(30) PRIMARY KEY,
    barrier_name   VARCHAR(80) NOT NULL
);

CREATE TABLE cost_category (
    cost_category_code  VARCHAR(30) PRIMARY KEY,
    cost_type           VARCHAR(10) NOT NULL CHECK (cost_type IN ('startup','operating')),
    category_name       VARCHAR(80) NOT NULL,
    description         TEXT
);

-- ---------------------------------------------------------------------
-- 2. Community survey (respondent grain + multi-valued child tables)
-- ---------------------------------------------------------------------
CREATE TABLE survey_response (
    respondent_id               VARCHAR(10) PRIMARY KEY,      -- R0001…
    response_date               DATE        NOT NULL,
    response_channel            VARCHAR(20) CHECK (response_channel IN ('online','paper','event_kiosk')),
    consent_flag                BOOLEAN     NOT NULL,
    age_group                   VARCHAR(10) CHECK (age_group IN ('18-24','25-34','35-44','45-54','55-64','65+')),
    household_size_range        VARCHAR(5)  CHECK (household_size_range IN ('1','2','3-4','5+')),
    attendance_frequency        VARCHAR(20) NOT NULL
                                CHECK (attendance_frequency IN
                                  ('multiple_weekly','weekly','monthly','festivals_only','rarely','unsure')),
    preferred_day               VARCHAR(15) CHECK (preferred_day IN ('weekday','saturday','sunday','no_preference')),
    preferred_time              VARCHAR(15) CHECK (preferred_time IN ('morning','afternoon','evening','no_preference')),
    max_travel_minutes          SMALLINT    CHECK (max_travel_minutes BETWEEN 0 AND 120),
    monthly_contribution_stated money_t,                      -- optional, stated intent only
    one_time_pledge_stated      money_t,                      -- optional, stated intent only
    volunteer_hours_month       SMALLINT    CHECK (volunteer_hours_month BETWEEN 0 AND 80),
    comment_text                TEXT,
    is_duplicate                BOOLEAN     NOT NULL DEFAULT FALSE,
    duplicate_of                VARCHAR(10) REFERENCES survey_response(respondent_id),
    dq_flag_count               SMALLINT    NOT NULL DEFAULT 0 CHECK (dq_flag_count >= 0),
    data_status                 data_status_t NOT NULL,
    source_id                   VARCHAR(10) NOT NULL REFERENCES data_source(source_id),
    CONSTRAINT chk_dup_link CHECK (
        (is_duplicate = FALSE AND duplicate_of IS NULL) OR
        (is_duplicate = TRUE  AND duplicate_of IS NOT NULL AND duplicate_of <> respondent_id))
);

-- Normalizes the multi-select "preferred programs" field (top choices, ranked)
CREATE TABLE survey_top_choice (
    respondent_id   VARCHAR(10) NOT NULL REFERENCES survey_response(respondent_id) ON DELETE CASCADE,
    category_code   VARCHAR(20) NOT NULL REFERENCES program_category(category_code),
    choice_rank     SMALLINT    NOT NULL CHECK (choice_rank BETWEEN 1 AND 3),
    PRIMARY KEY (respondent_id, category_code),
    UNIQUE (respondent_id, choice_rank)
);

-- Normalizes the multi-select "main participation barriers" field
CREATE TABLE survey_barrier (
    respondent_id   VARCHAR(10) NOT NULL REFERENCES survey_response(respondent_id) ON DELETE CASCADE,
    barrier_code    VARCHAR(30) NOT NULL REFERENCES barrier_type(barrier_code),
    PRIMARY KEY (respondent_id, barrier_code)
);

CREATE TABLE program_preference (
    preference_id         VARCHAR(10) PRIMARY KEY,           -- P00001…
    respondent_id         VARCHAR(10) NOT NULL REFERENCES survey_response(respondent_id) ON DELETE CASCADE,
    category_code         VARCHAR(20) NOT NULL REFERENCES program_category(category_code),
    interest_rating       SMALLINT    NOT NULL CHECK (interest_rating BETWEEN 1 AND 5),
    preferred_frequency   VARCHAR(15) CHECK (preferred_frequency IN ('daily','weekly','biweekly','monthly','occasional')),
    data_status           data_status_t NOT NULL,
    source_id             VARCHAR(10) NOT NULL REFERENCES data_source(source_id),
    UNIQUE (respondent_id, category_code)                   -- one rating per program per person
);

-- ---------------------------------------------------------------------
-- 3. Programs
-- ---------------------------------------------------------------------
CREATE TABLE program_option (
    program_id              VARCHAR(10) PRIMARY KEY,         -- PG01…
    category_code           VARCHAR(20) NOT NULL REFERENCES program_category(category_code),
    program_name            VARCHAR(100) NOT NULL,
    intended_audience       VARCHAR(20)  NOT NULL
                            CHECK (intended_audience IN ('all_ages','children','youth','adults','seniors','families')),
    est_launch_cost         money_t      NOT NULL,
    est_monthly_cost        money_t      NOT NULL,
    volunteer_hours_month   SMALLINT     NOT NULL CHECK (volunteer_hours_month >= 0),
    paid_hours_month        SMALLINT     NOT NULL DEFAULT 0 CHECK (paid_hours_month >= 0),
    min_area_sqft           INTEGER      CHECK (min_area_sqft > 0),
    requires_open_flame     BOOLEAN      NOT NULL,
    requires_kitchen        BOOLEAN      NOT NULL,
    requires_permanent_space BOOLEAN     NOT NULL,           -- e.g., sanctum with installed murtis
    evidence_note           TEXT,
    verification_status     verification_t NOT NULL,
    data_status             data_status_t  NOT NULL,
    source_id               VARCHAR(10)  NOT NULL REFERENCES data_source(source_id)
);

-- ---------------------------------------------------------------------
-- 4. Properties and due diligence
-- ---------------------------------------------------------------------
CREATE TABLE candidate_property (
    property_id             VARCHAR(10) PRIMARY KEY,         -- SIM-P01… (SIM = simulated)
    area_label              VARCHAR(60) NOT NULL,            -- generic, e.g. "Simulated Area – North Commercial"
    jurisdiction            VARCHAR(15) NOT NULL
                            CHECK (jurisdiction IN ('city_tracy','sj_county','unknown')),
    property_type           VARCHAR(25) NOT NULL
                            CHECK (property_type IN ('community_hall','retail_unit','office_unit',
                                                     'light_industrial','former_church','agricultural_building',
                                                     'vacant_land','school_facility')),
    tenure_offered          VARCHAR(15) NOT NULL CHECK (tenure_offered IN ('hourly_rental','lease','sale')),
    floor_area_sqft         INTEGER     CHECK (floor_area_sqft > 0),
    lot_area_acres          NUMERIC(6,2) CHECK (lot_area_acres > 0),
    hourly_rate             money_t,
    asking_monthly_rent     money_t,
    asking_price            money_t,
    parking_spaces          SMALLINT    CHECK (parking_spaces >= 0),
    current_use             VARCHAR(60),
    building_condition      VARCHAR(15) CHECK (building_condition IN ('good','fair','poor','unknown')),
    zoning_label            VARCHAR(30),                     -- as listed; NOT a verified determination
    zoning_verification     VARCHAR(20) NOT NULL
                            CHECK (zoning_verification IN ('not_checked','listing_claim','staff_confirmed','not_permitted')),
    date_verified           DATE,
    is_simulated            BOOLEAN     NOT NULL,
    data_status             data_status_t NOT NULL,
    source_id               VARCHAR(10) NOT NULL REFERENCES data_source(source_id),
    -- Tenure-specific price must be present when known; allow NULL for unknown but not wrong-tenure prices
    CONSTRAINT chk_tenure_price CHECK (
        (tenure_offered = 'hourly_rental' AND asking_monthly_rent IS NULL AND asking_price IS NULL) OR
        (tenure_offered = 'lease'         AND hourly_rate IS NULL AND asking_price IS NULL) OR
        (tenure_offered = 'sale'          AND hourly_rate IS NULL AND asking_monthly_rent IS NULL)),
    -- Simulated properties can never be marked as staff-confirmed real determinations
    CONSTRAINT chk_sim_not_verified CHECK (
        NOT (is_simulated AND data_status IN ('real_observation','verified_official')))
);

-- Long format: one row per property per review area (raw CSV is also long)
CREATE TABLE property_due_diligence (
    dd_id                   VARCHAR(12) PRIMARY KEY,         -- DD-P01-ZON
    property_id             VARCHAR(10) NOT NULL REFERENCES candidate_property(property_id) ON DELETE CASCADE,
    review_area             VARCHAR(20) NOT NULL
                            CHECK (review_area IN ('zoning','building_use','parking','accessibility','fire_life_safety')),
    status                  VARCHAR(15) NOT NULL
                            CHECK (status IN ('not_started','in_progress','issue_found','verified_ok','failed','not_applicable')),
    est_cost_to_resolve     money_t,
    next_action             TEXT,
    owner_role              VARCHAR(40),
    last_updated            DATE,
    data_status             data_status_t NOT NULL,
    source_id               VARCHAR(10) NOT NULL REFERENCES data_source(source_id),
    UNIQUE (property_id, review_area)
);

-- ---------------------------------------------------------------------
-- 5. Costs
-- ---------------------------------------------------------------------
CREATE TABLE startup_cost_estimate (
    cost_id               VARCHAR(10) PRIMARY KEY,           -- SC001…
    model_code            VARCHAR(20) NOT NULL REFERENCES operating_model(model_code),
    cost_category_code    VARCHAR(30) NOT NULL REFERENCES cost_category(cost_category_code),
    line_description      VARCHAR(120) NOT NULL,
    low_estimate          money_t NOT NULL,
    base_estimate         money_t NOT NULL,
    high_estimate         money_t NOT NULL,
    estimate_basis        TEXT,
    verification_status   verification_t NOT NULL,
    data_status           data_status_t  NOT NULL,
    source_id             VARCHAR(10) NOT NULL REFERENCES data_source(source_id),
    CONSTRAINT chk_sc_order CHECK (low_estimate <= base_estimate AND base_estimate <= high_estimate)
);

CREATE TABLE operating_cost_estimate (
    op_cost_id            VARCHAR(10) PRIMARY KEY,           -- OC001…
    model_code            VARCHAR(20) NOT NULL REFERENCES operating_model(model_code),
    cost_category_code    VARCHAR(30) NOT NULL REFERENCES cost_category(cost_category_code),
    line_description      VARCHAR(120) NOT NULL,
    monthly_low           money_t NOT NULL,
    monthly_base          money_t NOT NULL,
    monthly_high          money_t NOT NULL,
    estimate_basis        TEXT,
    verification_status   verification_t NOT NULL,
    data_status           data_status_t  NOT NULL,
    source_id             VARCHAR(10) NOT NULL REFERENCES data_source(source_id),
    CONSTRAINT chk_oc_order CHECK (monthly_low <= monthly_base AND monthly_base <= monthly_high),
    UNIQUE (model_code, cost_category_code, line_description)
);

-- ---------------------------------------------------------------------
-- 6. Funding scenarios & model assumptions
-- ---------------------------------------------------------------------
CREATE TABLE funding_scenario (
    scenario_id                 VARCHAR(10) PRIMARY KEY,     -- FS01…
    scenario_name               VARCHAR(60) NOT NULL UNIQUE,
    initial_funds_assumed       money_t NOT NULL,            -- cash on hand at month 0 (realized)
    monthly_recurring_assumed   money_t NOT NULL,            -- realized recurring donations at steady state
    ramp_months                 SMALLINT NOT NULL CHECK (ramp_months BETWEEN 0 AND 24),
    pledge_realization_rate     NUMERIC(4,3) NOT NULL CHECK (pledge_realization_rate BETWEEN 0 AND 1),
    annual_event_fundraising_net money_t NOT NULL,
    grant_amount_assumed        money_t NOT NULL DEFAULT 0,
    attendance_discount         NUMERIC(4,3) NOT NULL CHECK (attendance_discount BETWEEN 0 AND 1),
    confidence_level            VARCHAR(10) NOT NULL CHECK (confidence_level IN ('low','medium','high')),
    assumptions_text            TEXT NOT NULL,
    data_status                 data_status_t NOT NULL,
    source_id                   VARCHAR(10) NOT NULL REFERENCES data_source(source_id)
);

-- Every constant used in calculations lives here (NFR-03)
CREATE TABLE model_assumption (
    assumption_id        VARCHAR(10) PRIMARY KEY,            -- MA01…
    assumption_name      VARCHAR(60) NOT NULL UNIQUE,        -- snake_case key used in code
    value_low            NUMERIC(12,4) NOT NULL,
    value_base           NUMERIC(12,4) NOT NULL,
    value_high           NUMERIC(12,4) NOT NULL,
    unit                 VARCHAR(30) NOT NULL,
    applies_to           VARCHAR(40) NOT NULL,               -- model_code, 'all', or analysis area
    rationale            TEXT NOT NULL,
    verification_status  verification_t NOT NULL,
    data_status          data_status_t  NOT NULL,
    source_id            VARCHAR(10) NOT NULL REFERENCES data_source(source_id),
    CONSTRAINT chk_ma_order CHECK (value_low <= value_base AND value_base <= value_high)
);

-- ---------------------------------------------------------------------
-- 7. Data-quality audit log (written by the Python pipeline)
-- ---------------------------------------------------------------------
CREATE TABLE dq_issue_log (
    issue_id        SERIAL PRIMARY KEY,
    table_name      VARCHAR(40) NOT NULL,
    record_key      VARCHAR(30) NOT NULL,
    column_name     VARCHAR(40),
    rule_id         VARCHAR(10) NOT NULL,                    -- e.g. DQ-07
    original_value  TEXT,
    cleaned_value   TEXT,
    action_taken    VARCHAR(20) NOT NULL
                    CHECK (action_taken IN ('corrected','standardized','set_null','flagged','excluded_from_metric')),
    logged_at       TIMESTAMP NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------
-- 8. Indexes (FK columns + common filters)
-- ---------------------------------------------------------------------
CREATE INDEX ix_sr_date        ON survey_response (response_date);
CREATE INDEX ix_sr_freq        ON survey_response (attendance_frequency);
CREATE INDEX ix_sr_eligible    ON survey_response (respondent_id) WHERE consent_flag AND NOT is_duplicate;
CREATE INDEX ix_sr_source      ON survey_response (source_id);
CREATE INDEX ix_stc_cat        ON survey_top_choice (category_code);
CREATE INDEX ix_sb_barrier     ON survey_barrier (barrier_code);
CREATE INDEX ix_pp_cat         ON program_preference (category_code);
CREATE INDEX ix_pp_resp        ON program_preference (respondent_id);
CREATE INDEX ix_po_cat         ON program_option (category_code);
CREATE INDEX ix_cp_juris       ON candidate_property (jurisdiction, tenure_offered);
CREATE INDEX ix_dd_prop        ON property_due_diligence (property_id);
CREATE INDEX ix_dd_status      ON property_due_diligence (status);
CREATE INDEX ix_sc_model       ON startup_cost_estimate (model_code, cost_category_code);
CREATE INDEX ix_oc_model       ON operating_cost_estimate (model_code, cost_category_code);
CREATE INDEX ix_dq_table_rule  ON dq_issue_log (table_name, rule_id);

-- ---------------------------------------------------------------------
-- 9. Convenience views
-- ---------------------------------------------------------------------
-- Eligible respondents per BRL-01 (survey window set here; adjust if needed)
CREATE VIEW v_eligible_respondent AS
SELECT *
FROM survey_response
WHERE consent_flag
  AND NOT is_duplicate
  AND response_date BETWEEN DATE '2026-03-01' AND DATE '2026-06-30';

-- Due diligence pivoted wide (one row per property)
CREATE VIEW v_property_dd_wide AS
SELECT p.property_id,
       MAX(CASE WHEN d.review_area = 'zoning'           THEN d.status END) AS zoning_status,
       MAX(CASE WHEN d.review_area = 'building_use'     THEN d.status END) AS building_use_status,
       MAX(CASE WHEN d.review_area = 'parking'          THEN d.status END) AS parking_status,
       MAX(CASE WHEN d.review_area = 'accessibility'    THEN d.status END) AS accessibility_status,
       MAX(CASE WHEN d.review_area = 'fire_life_safety' THEN d.status END) AS fire_status,
       COUNT(*) FILTER (WHERE d.status = 'verified_ok')                    AS areas_verified,
       COUNT(*) FILTER (WHERE d.status = 'failed')                         AS areas_failed,
       CASE WHEN COUNT(*) FILTER (WHERE d.status = 'failed') > 0 THEN 'not_eligible'
            WHEN COUNT(*) FILTER (WHERE d.status = 'verified_ok') = 5
                 AND NOT p.is_simulated                                    THEN 'viable'
            ELSE 'shortlist_eligible' END                                   AS dd_classification
FROM candidate_property p
LEFT JOIN property_due_diligence d USING (property_id)
GROUP BY p.property_id, p.is_simulated;
