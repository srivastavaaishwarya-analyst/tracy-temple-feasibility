-- =====================================================================
-- Reference (lookup) data. These are DESIGN DECISIONS of this project,
-- not observations. Real-reference rows in data_source point to public
-- documents used only for context and must be re-verified before use.
-- =====================================================================
SET search_path TO temple;

-- ---------------- data_source ----------------
INSERT INTO data_source VALUES
('SRC001','survey_response, survey_top_choice, survey_barrier, program_preference',
 'Portfolio generator (src/generate_data.py)','Synthetic — seed 20261015','2026-10-15',
 'Simulated respondents; NOT evidence of real community demand.','synthetic_placeholder','synthetic'),
('SRC002','candidate_property, property_due_diligence',
 'Portfolio generator (src/generate_data.py)','Synthetic — simulated candidate properties','2026-10-15',
 'Not real listings. Generic area labels only. No property is approved or suitable.','synthetic_placeholder','synthetic'),
('SRC003','startup_cost_estimate, operating_cost_estimate, program_option',
 'Portfolio analyst','Synthetic placeholder ranges','2026-10-15',
 'Placeholder magnitudes for method practice; replace with written quotes.','synthetic_placeholder','synthetic'),
('SRC004','funding_scenario, model_assumption',
 'Portfolio analyst','Hypothetical assumptions — see rationale fields','2026-10-15',
 'Assumptions requiring validation (BRD §12).','analyst_estimate','unverified_assumption'),
('SRC101','context: permitting pathway (City of Tracy)',
 'City of Tracy Planning Commission','https://cityoftracy.org/home/showpublisheddocument/6142/637547934931570000','2026-10-15',
 'Historical staff report (CUP for place of worship in office center; cites TMC 10.08.4250). Code may have changed.',
 'official_document','verified_official'),
('SRC102','context: joint-use parking (City of Tracy)',
 'City of Tracy Planning Commission','https://cityoftracy.org/home/showpublisheddocument/5970/637547917996300000','2026-10-15',
 'Historical staff report; references TMC 10.08.3460(j). Re-verify current ratio rules.',
 'official_document','verified_official'),
('SRC103','context: religious assembly CUP, unincorporated Tracy area',
 'San Joaquin County via CEQAnet','https://ceqanet.lci.ca.gov/2026060211','2026-10-15',
 'Single precedent (phased ag-building conversion with attendance caps); not a rule for other parcels.',
 'official_document','verified_official'),
('SRC104','context: religious assembly CUP, unincorporated Tracy area',
 'San Joaquin County via CEQAnet','https://ceqanet.lci.ca.gov/2025061188','2026-10-15',
 'Single precedent; large new-build project, different scale.','official_document','verified_official'),
('SRC105','context: regional existing temple',
 'Public organization profile','https://carnaticamerica.com/organizer/hindu-community-and-cultural-center/','2026-10-15',
 'Secondary listing; does not establish travel times or attendance.','official_document','verified_official');

-- ---------------- operating_model ----------------
INSERT INTO operating_model VALUES
('OM_RENT_EVENT','Rent venue for occasional events','STRAT_B',
 'Hourly/daily hire of a community hall or similar; portable altar; no permanent sanctum.'),
('OM_LEASE_DEDICATED','Lease dedicated facility','STRAT_A',
 'Multi-year lease of a unit converted to religious assembly; requires use approval and tenant improvements.'),
('OM_PURCHASE_ADAPT','Purchase and adapt property','STRAT_A',
 'Acquire and renovate an existing building; highest capital need and commitment.');

-- ---------------- program_category ----------------
INSERT INTO program_category VALUES
('DAILY_PUJA','Daily darshan & puja','religious'),
('WEEKLY_SATSANG','Weekly satsang / bhajan / kirtan','religious'),
('FESTIVALS','Major festival celebrations','religious'),
('SAMSKARA','Life-cycle ceremonies (samskaras)','religious'),
('SCRIPTURE','Scripture study (e.g., Gita study)','educational'),
('CHILD_EDU','Children''s religious education (Bal Vihar)','educational'),
('LANGUAGE','Language classes (Sanskrit / Indian languages)','educational'),
('YOGA_MED','Yoga & meditation','cultural'),
('MUSIC_DANCE','Classical music & dance','cultural'),
('SENIOR','Senior gatherings','community'),
('SEVA','Community service / seva & food drives','community');

-- ---------------- program_category_alias (lower-case, trimmed) ----------------
INSERT INTO program_category_alias VALUES
('daily puja','DAILY_PUJA'),('daily darshan','DAILY_PUJA'),('puja','DAILY_PUJA'),('pooja','DAILY_PUJA'),
('weekly satsang','WEEKLY_SATSANG'),('satsang','WEEKLY_SATSANG'),('bhajans','WEEKLY_SATSANG'),('bhajan','WEEKLY_SATSANG'),('kirtan','WEEKLY_SATSANG'),
('festivals','FESTIVALS'),('festival celebrations','FESTIVALS'),('diwali/holi events','FESTIVALS'),
('samskaras','SAMSKARA'),('life events','SAMSKARA'),('weddings & ceremonies','SAMSKARA'),
('scripture study','SCRIPTURE'),('gita study','SCRIPTURE'),('gita class','SCRIPTURE'),
('bal vihar','CHILD_EDU'),('kids classes','CHILD_EDU'),('children''s education','CHILD_EDU'),('sunday school','CHILD_EDU'),
('language classes','LANGUAGE'),('sanskrit','LANGUAGE'),('hindi/telugu/tamil classes','LANGUAGE'),
('yoga','YOGA_MED'),('yoga & meditation','YOGA_MED'),('meditation','YOGA_MED'),
('music & dance','MUSIC_DANCE'),('classical dance','MUSIC_DANCE'),('carnatic/hindustani music','MUSIC_DANCE'),
('seniors','SENIOR'),('senior gatherings','SENIOR'),('elders group','SENIOR'),
('seva','SEVA'),('community service','SEVA'),('food drive','SEVA'),('volunteering','SEVA');

-- ---------------- barrier_type ----------------
INSERT INTO barrier_type VALUES
('TRAVEL_DISTANCE','Travel distance / time'),
('SCHEDULE_CONFLICT','Schedule conflicts (work, school)'),
('COST','Cost of participation'),
('PARKING','Parking availability'),
('LANGUAGE','Language of services'),
('CHILDCARE','Childcare'),
('ATTEND_ELSEWHERE','Already attend a temple elsewhere'),
('ACCESSIBILITY','Physical accessibility'),
('NONE','No significant barrier');

-- ---------------- cost_category ----------------
INSERT INTO cost_category VALUES
('ACQUISITION','startup','Property acquisition / down payment','Purchase deposit and closing costs (purchase model only).'),
('LEASE_DEPOSIT','startup','Lease deposit & first month','Security deposit, first/last month rent.'),
('PERMITS_FEES','startup','Permits & application fees','CUP application, building permit, plan check fees.'),
('PROFESSIONAL','startup','Professional services','Architect, engineer, attorney, CPA, CASp.'),
('RENOVATION','startup','Tenant improvements / renovation','Interior build-out, finishes, restrooms.'),
('ACCESSIBILITY','startup','Accessibility upgrades','Path of travel, accessible restrooms & parking.'),
('FIRE_LIFE_SAFETY','startup','Fire & life-safety improvements','Sprinklers, alarms, exits, signage.'),
('RITUAL_SETUP','startup','Altar, murtis & ritual items','Altar, murtis, puja items (portable for rent model).'),
('FURNITURE_AV','startup','Furniture, AV & equipment','Seating, sound system, storage.'),
('KITCHEN','startup','Kitchen equipment','Prasad preparation equipment; health-permit compliance.'),
('SECURITY','startup','Security systems','Cameras, alarms, lighting.'),
('ORG_FORMATION','startup','Nonprofit formation','Incorporation & tax-exemption filings.'),
('RENT','operating','Rent / venue hire','Monthly lease or aggregated hourly hire.'),
('MORTGAGE','operating','Mortgage / financing','Debt service (purchase model only).'),
('UTILITIES','operating','Utilities','Electricity, gas, water, waste.'),
('INSURANCE','operating','Insurance','General liability, property, D&O, event riders.'),
('MAINTENANCE','operating','Maintenance & cleaning','Janitorial, repairs, landscaping.'),
('STAFF','operating','Priest honorarium & staff','Officiant stipend/honorarium; part-time admin.'),
('PROGRAMS','operating','Program supplies','Class materials, festival supplies, prasad.'),
('ADMIN','operating','Administration','Accounting, software, bank fees, communications.'),
('PROPERTY_TAX','operating','Property tax / assessments','Before any exemption is obtained.'),
('RESERVE_CONTRIB','operating','Capital reserve contribution','Monthly set-aside for repairs/replacement.');
