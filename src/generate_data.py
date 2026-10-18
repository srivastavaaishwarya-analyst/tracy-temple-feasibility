#!/usr/bin/env python3
"""
generate_data.py - builds the SYNTHETIC raw dataset for the Tracy temple
feasibility portfolio project.

* Every record produced here is SIMULATED practice data (data_status = synthetic
  or unverified_assumption). None of it is evidence of real community demand,
  real properties, or verified costs.
* Deliberate, controlled data-quality issues are injected so the data can be
  used to practise cleaning. They are described (without solutions) in
  docs/04_data_quality_challenge_guide.md.
* Reproducible: fixed seed. Re-running produces identical files.

Usage (from the repo root):
    python src/generate_data.py
Outputs: data/raw/*.csv  (reads lookup values from data/reference/*.csv)
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 20261015
rng = np.random.default_rng(SEED)

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "reference"
OUT = ROOT / "data" / "raw"
OUT.mkdir(parents=True, exist_ok=True)

SURVEY_START = dt.date(2026, 3, 1)
SURVEY_END = dt.date(2026, 6, 30)


# ---------------------------------------------------------------------------
# Small helpers for injecting realistic formatting noise
# ---------------------------------------------------------------------------
def pick(options, p=None):
    """Random choice that returns a plain Python object."""
    idx = rng.choice(len(options), p=p)
    return options[idx]


def case_noise(s: str, p_noise: float = 0.25) -> str:
    """Return s unchanged most of the time, otherwise a case/whitespace variant."""
    if s is None or rng.random() > p_noise:
        return s
    variant = pick(["upper", "title", "lower", "pad"])
    if variant == "upper":
        return s.upper()
    if variant == "title":
        return s.title()
    if variant == "lower":
        return s.lower()
    return f" {s} " if rng.random() < 0.5 else f"{s}  "


def variant(options: list[str], canonical_weight: float = 0.6) -> str:
    """options[0] is canonical; the rest are messy variants."""
    if len(options) == 1 or rng.random() < canonical_weight:
        return options[0]
    return pick(options[1:])


def fmt_date(d: dt.date) -> str:
    r = rng.random()
    if r < 0.60:
        return d.strftime("%Y-%m-%d")
    if r < 0.85:
        return d.strftime("%m/%d/%Y")
    return d.strftime("%d-%b-%Y")


def fmt_money(x: float, p_dollar=0.15, p_decimal=0.10) -> str:
    r = rng.random()
    if r < p_dollar:
        return f"${x:,.0f}"
    if r < p_dollar + p_decimal:
        return f"{x:.2f}"
    return f"{x:.0f}"


def status_label() -> str:
    return variant(["synthetic", "Synthetic", "SYNTHETIC "], canonical_weight=0.9)


# ---------------------------------------------------------------------------
# Reference data (single source of truth = data/reference/*.csv, exported from SQL seed)
# ---------------------------------------------------------------------------
alias_df = pd.read_csv(REF / "program_category_alias.csv")
ALIASES: dict[str, list[str]] = alias_df.groupby("category_code")["alias_text"].apply(list).to_dict()
CATEGORIES = sorted(ALIASES)

# ---------------------------------------------------------------------------
# 1. Community survey (latent "true" respondents first, then messy rendering)
# ---------------------------------------------------------------------------
AGE = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
AGE_P = [0.06, 0.18, 0.27, 0.22, 0.15, 0.12]
HH = ["1", "2", "3-4", "5+"]
FREQ = ["multiple_weekly", "weekly", "monthly", "festivals_only", "rarely", "unsure"]

BASE_INTEREST = {
    "DAILY_PUJA": 1.0, "WEEKLY_SATSANG": 1.1, "FESTIVALS": 1.6, "SAMSKARA": 0.5,
    "SCRIPTURE": 0.6, "CHILD_EDU": 0.9, "LANGUAGE": 0.6, "YOGA_MED": 0.8,
    "MUSIC_DANCE": 0.6, "SENIOR": 0.3, "SEVA": 0.5,
}

COMMENT_TEMPLATES = {
    "parking": [
        "Parking was a problem at the last community event I went to.",
        "Please make sure there is enough parking for festivals.",
        "Parking matters more to us than the exact location.",
    ],
    "children": [
        "Would love weekend classes for the kids.",
        "Our children need a place to learn about our traditions closer to home.",
        "Bal Vihar on Sunday mornings would be great for our family.",
    ],
    "travel": [
        "Driving to the Bay Area temples takes too long on weekends.",
        "Anything within 20 minutes of home would work for us.",
        "Traffic on 580 makes the current drive hard.",
    ],
    "festivals": [
        "Mainly interested in Diwali and other big festivals.",
        "Festival celebrations bring the whole community together.",
    ],
    "seniors": [
        "My parents are visiting for months at a time and need somewhere to go during the week.",
        "A weekday morning gathering for elders would be valuable.",
    ],
    "cost": [
        "Happy to support but cannot commit to a large monthly amount.",
        "Please be transparent about how donations are used.",
    ],
    "volunteer": [
        "I can help with setup and cleanup on weekends.",
        "Willing to volunteer for teaching or events.",
    ],
    "elsewhere": [
        "We already go to a temple elsewhere but would attend local events too.",
        "Would still visit our regular temple for major pujas.",
    ],
    "schedule": [
        "Evening programs after work would suit us best.",
        "Weekdays are hard because of work schedules.",
    ],
    "general": [
        "Start small and grow - a rented hall is fine to begin with.",
        "Glad someone is looking into this.",
        "A permanent place would mean a lot to our family.",
        "Please keep it welcoming for all traditions.",
    ],
}

BARRIER_VARIANTS = {
    "TRAVEL_DISTANCE": ["Travel distance", "travel time", "Too far", "distance"],
    "SCHEDULE_CONFLICT": ["Schedule conflicts", "work schedule", "Schedule", "busy weekends"],
    "COST": ["Cost", "cost of participation", "Expense"],
    "PARKING": ["Parking", "parking availability", "PARKING"],
    "LANGUAGE": ["Language", "language of services"],
    "CHILDCARE": ["Childcare", "child care", "No babysitter"],
    "ATTEND_ELSEWHERE": ["Already attend a temple elsewhere", "attend elsewhere", "Go to another temple"],
    "ACCESSIBILITY": ["Accessibility", "physical accessibility", "Mobility"],
    "NONE": ["None", "no barriers", "None really", "n/a"],
}

FREQ_VARIANTS = {
    "multiple_weekly": ["multiple_weekly", "Multiple times a week", "2-3 times/week", "Multiple Weekly"],
    "weekly": ["weekly", "Weekly", " WEEKLY ", "once a week"],
    "monthly": ["monthly", "Monthly", "once a month"],
    "festivals_only": ["festivals_only", "Festivals only", "only on festivals", "Festivals Only "],
    "rarely": ["rarely", "Rarely", "hardly ever"],
    "unsure": ["unsure", "Not sure", "Unsure"],
}
DAY_VARIANTS = {
    "weekday": ["weekday", "Weekday", "weekdays", "Mon-Fri"],
    "saturday": ["saturday", "Saturday", "Sat", "SATURDAY"],
    "sunday": ["sunday", "Sunday", "Sun", " sunday"],
    "no_preference": ["no_preference", "No preference", "any", "Any day"],
}
TIME_VARIANTS = {
    "morning": ["morning", "Morning", "mornings"],
    "afternoon": ["afternoon", "Afternoon"],
    "evening": ["evening", "Evening", "evenings"],
    "no_preference": ["no_preference", "No preference", "anytime"],
}


def freq_probs(age: str, elsewhere: bool) -> list[float]:
    if elsewhere:
        return [0.04, 0.18, 0.27, 0.30, 0.13, 0.08]
    if age in ("55-64", "65+"):
        return [0.14, 0.33, 0.22, 0.17, 0.08, 0.06]
    if age == "18-24":
        return [0.04, 0.15, 0.25, 0.30, 0.16, 0.10]
    return [0.08, 0.27, 0.25, 0.22, 0.10, 0.08]


def hh_probs(age: str) -> list[float]:
    if age in ("18-24",):
        return [0.35, 0.30, 0.25, 0.10]
    if age in ("25-34",):
        return [0.15, 0.35, 0.40, 0.10]
    if age in ("35-44", "45-54"):
        return [0.05, 0.15, 0.60, 0.20]
    return [0.15, 0.50, 0.25, 0.10]


def program_weights(age: str, hh: str) -> np.ndarray:
    w = dict(BASE_INTEREST)
    family = hh in ("3-4", "5+") and age in ("25-34", "35-44", "45-54")
    if family:
        w["CHILD_EDU"] *= 3.0
        w["LANGUAGE"] *= 2.0
        w["MUSIC_DANCE"] *= 1.8
    if age in ("55-64", "65+"):
        w["SENIOR"] *= 4.0
        w["DAILY_PUJA"] *= 1.6
        w["SCRIPTURE"] *= 1.6
    if age in ("18-24", "25-34"):
        w["YOGA_MED"] *= 1.8
        w["SEVA"] *= 1.6
    arr = np.array([w[c] for c in CATEGORIES])
    return arr / arr.sum()


def day_time(age: str, hh: str) -> tuple[str, str]:
    if age in ("55-64", "65+") and rng.random() < 0.5:
        return "weekday", "morning"
    if hh in ("3-4", "5+") and rng.random() < 0.6:
        return pick(["sunday", "saturday"], p=[0.65, 0.35]), pick(["morning", "afternoon"], p=[0.7, 0.3])
    d = pick(["weekday", "saturday", "sunday", "no_preference"], p=[0.30, 0.25, 0.30, 0.15])
    t = pick(["morning", "afternoon", "evening", "no_preference"], p=[0.30, 0.15, 0.40, 0.15])
    return d, t


def travel_minutes(freq: str) -> int:
    mean = {"multiple_weekly": 18, "weekly": 22, "monthly": 30, "festivals_only": 45,
            "rarely": 35, "unsure": 30}[freq]
    v = rng.normal(mean, 9)
    return int(np.clip(round(v / 5) * 5, 5, 90))


def contribution(freq: str) -> float | None:
    if rng.random() > 0.65:
        return None
    if rng.random() < 0.15:
        return 0.0
    median = {"multiple_weekly": 50, "weekly": 40, "monthly": 20, "festivals_only": 10,
              "rarely": 10, "unsure": 15}[freq]
    v = rng.lognormal(np.log(median), 0.7)
    return float(min(500, max(5, round(v / 5) * 5)))


def pledge() -> float | None:
    if rng.random() > 0.45:
        return None
    v = rng.lognormal(np.log(250), 1.0)
    return float(min(10000, max(50, round(v / 50) * 50)))


def volunteer_hours() -> int | None:
    if rng.random() > 0.60:
        return None
    return int(pick([0, 2, 4, 6, 8, 10, 12, 16, 20],
                    p=[0.40, 0.15, 0.13, 0.08, 0.08, 0.06, 0.04, 0.03, 0.03]))


def barriers(age, hh, freq, travel, elsewhere) -> list[str]:
    out = []
    if elsewhere:
        out.append("ATTEND_ELSEWHERE")
    p = {
        "TRAVEL_DISTANCE": 0.40 if travel <= 20 else 0.18,
        "SCHEDULE_CONFLICT": 0.35 if age not in ("65+",) else 0.10,
        "PARKING": 0.12, "COST": 0.08, "LANGUAGE": 0.07,
        "CHILDCARE": 0.15 if hh in ("3-4", "5+") else 0.03,
        "ACCESSIBILITY": 0.15 if age == "65+" else 0.03,
    }
    for code, prob in p.items():
        if rng.random() < prob:
            out.append(code)
    out = out[:3]
    return out or ["NONE"]


def comment_for(r) -> str | None:
    if rng.random() > 0.45:
        return None
    themes = ["general"]
    if "PARKING" in r["barriers"]:
        themes += ["parking"] * 3
    if "ATTEND_ELSEWHERE" in r["barriers"]:
        themes += ["elsewhere"] * 3
    if "TRAVEL_DISTANCE" in r["barriers"]:
        themes += ["travel"] * 2
    if "SCHEDULE_CONFLICT" in r["barriers"]:
        themes += ["schedule"] * 2
    if "CHILD_EDU" in r["top"]:
        themes += ["children"] * 2
    if "SENIOR" in r["top"]:
        themes += ["seniors"] * 2
    if r["freq"] == "festivals_only":
        themes += ["festivals"] * 2
    if r["contribution"] is not None and r["contribution"] <= 10:
        themes += ["cost"]
    if r["volunteer"] and r["volunteer"] >= 4:
        themes += ["volunteer"]
    theme = pick(themes)
    text = pick(COMMENT_TEMPLATES[theme])
    return text


def make_latent(n: int) -> list[dict]:
    """Latent (true) respondent attributes, including which optional fields are missing."""
    people = []
    span = (SURVEY_END - SURVEY_START).days
    # response volume heavier at launch (March) and around an April event
    day_weights = np.array([3.0 if d < 31 else (2.0 if 40 <= d <= 50 else 1.0) for d in range(span + 1)])
    day_weights /= day_weights.sum()
    for _ in range(n):
        age = pick(AGE, p=AGE_P)
        hh = pick(HH, p=hh_probs(age))
        elsewhere = rng.random() < 0.30
        freq = pick(FREQ, p=freq_probs(age, elsewhere))
        k = pick([1, 2, 3], p=[0.15, 0.30, 0.55])
        top = list(rng.choice(CATEGORIES, size=k, replace=False, p=program_weights(age, hh)))
        day, time = day_time(age, hh)
        travel = travel_minutes(freq)
        r = dict(
            date=SURVEY_START + dt.timedelta(days=int(rng.choice(span + 1, p=day_weights))),
            hour=int(rng.integers(7, 23)),
            channel=pick(["online", "paper", "event_kiosk"], p=[0.70, 0.15, 0.15]),
            consent=rng.random() > 0.03,
            age=age, hh=hh, top=top, freq=freq, day=day, time=time, travel=travel,
            contribution=contribution(freq), pledge=pledge(), volunteer=volunteer_hours(),
            elsewhere=elsewhere,
        )
        r["barriers"] = barriers(age, hh, freq, travel, elsewhere)
        r["comment"] = comment_for(r)
        # optional-field missingness is a property of the person, not of the rendering
        r["age_missing"] = pick(["no", "blank", "pnts"], p=[0.89, 0.08, 0.03])
        r["hh_missing"] = rng.random() < 0.06
        r["travel_missing"] = rng.random() < 0.05
        r["day_missing"] = rng.random() < 0.04
        r["channel_missing"] = rng.random() < 0.03
        people.append(r)
    return people


N_UNIQUE, N_DUP, N_DECOY = 304, 13, 3
latent = make_latent(N_UNIQUE)

# Out-of-window responses (pilot test in Feb, late submissions in July)
for k, i in enumerate(rng.choice(np.arange(40, N_UNIQUE), size=4, replace=False)):
    latent[int(i)]["date"] = dt.date(2026, 2, 20 + k) if k < 2 else dt.date(2026, 7, 3 + k)

# Decoys: genuinely different people whose cleaned profile matches someone else's,
# but submitted > 48 hours later -> must NOT be flagged as duplicates.
for i in range(N_DECOY):
    src = latent[i * 7 + 2]
    d = dict(src)
    d["date"] = min(SURVEY_END, src["date"] + dt.timedelta(days=int(rng.integers(6, 20))))
    d["hour"] = int(rng.integers(7, 23))
    d["contribution"], d["pledge"], d["volunteer"] = contribution(src["freq"]), pledge(), volunteer_hours()
    d["comment"] = comment_for(d)
    d["is_decoy_of"] = id(src)
    latent.append(d)

# True duplicates: same person re-submitting within 48 hours (often a double-click
# or paper + online). Same answers; rendering noise is re-drawn independently.
dup_sources = rng.choice(np.arange(10, N_UNIQUE), size=N_DUP, replace=False)
for j in dup_sources:
    src = latent[int(j)]
    d = dict(src)
    hours = int(rng.integers(0, 40))
    d["date"] = src["date"] + dt.timedelta(days=(src["hour"] + hours) // 24)
    d["hour"] = (src["hour"] + hours) % 24
    d["channel"] = pick([src["channel"], "online"])
    d["true_dup_of"] = id(src)
    latent.append(d)

# Assign respondent IDs in submission order
latent.sort(key=lambda r: (r["date"], r["hour"]))
id_by_obj = {}
for n, r in enumerate(latent, start=1):
    r["respondent_id"] = f"R{n:04d}"
    id_by_obj[id(r)] = r["respondent_id"]


def render_survey_row(r: dict) -> dict:
    # date
    date_txt = fmt_date(r["date"])
    # consent
    consent_txt = variant(["TRUE", "Yes", "Y", "yes", "1", "True"], 0.5) if r["consent"] \
        else variant(["FALSE", "No", "N", "0"], 0.5)
    # age / household
    if r["age_missing"] == "blank":
        age_txt = ""
    elif r["age_missing"] == "pnts":
        age_txt = variant(["prefer not to say", "Prefer not to say"])
    else:
        age_txt = r["age"].replace("-", " - ") if rng.random() < 0.05 else r["age"]
    if r["hh_missing"]:
        hh_txt = ""
    else:
        hh_txt = {"3-4": variant(["3-4", "3 to 4"], 0.8), "5+": variant(["5+", "5 or more"], 0.8)}.get(r["hh"], r["hh"])
    # programs: aliases, case noise, inconsistent separators
    labels = [case_noise(pick(ALIASES[c]), 0.3) for c in r["top"]]
    sep = pick([";", "; ", " ;"])
    progs_txt = sep.join(labels)
    # frequency / day / time
    freq_txt = variant(FREQ_VARIANTS[r["freq"]], 0.5)
    day_txt = "" if r["day_missing"] else variant(DAY_VARIANTS[r["day"]], 0.55)
    time_txt = "" if r["day_missing"] else variant(TIME_VARIANTS[r["time"]], 0.6)
    # travel
    if r["travel_missing"]:
        travel_txt = ""
    elif rng.random() < 0.12:
        travel_txt = f"{r['travel']} {pick(['min', 'mins', 'minutes'])}"
    else:
        travel_txt = str(r["travel"])
    # money
    if r["contribution"] is None:
        contrib_txt = variant(["", "N/A", "-", "prefer not to say", "unknown"], 0.5)
    else:
        contrib_txt = fmt_money(r["contribution"])
    pledge_txt = "" if r["pledge"] is None else fmt_money(r["pledge"], p_dollar=0.3)
    if r["volunteer"] is None:
        vol_txt = ""
    else:
        vol_txt = pick([str(r["volunteer"]), f" {r['volunteer']}", f"{r['volunteer']}.0", f"{r['volunteer']} hrs"],
                       p=[0.75, 0.08, 0.10, 0.07])
    # barriers
    bar_txt = pick([";", "; "]).join(case_noise(pick(BARRIER_VARIANTS[b]), 0.2) for b in r["barriers"])
    # comment whitespace
    c = r["comment"]
    if c is not None and rng.random() < 0.15:
        c = pick([f"  {c}", f"{c}   ", f" {c} "])
    channel_txt = "" if r["channel_missing"] else case_noise(variant(
        {"online": ["online", "Online"], "paper": ["paper", "Paper "],
         "event_kiosk": ["event_kiosk", "kiosk", "Event kiosk"]}[r["channel"]], 0.6), 0.15)
    return {
        "respondent_id": r["respondent_id"],
        "response_date": date_txt,
        "response_channel": channel_txt,
        "consent_flag": consent_txt,
        "age_group": age_txt,
        "household_size_range": hh_txt,
        "preferred_programs": progs_txt,
        "attendance_frequency": freq_txt,
        "preferred_day": day_txt,
        "preferred_time": time_txt,
        "max_travel_minutes": travel_txt,
        "monthly_contribution_stated": contrib_txt,
        "one_time_pledge_stated": pledge_txt,
        "volunteer_hours_month": vol_txt,
        "main_barriers": bar_txt,
        "comment_text": c if c is not None else "",
        "data_status": status_label(),
        "source_id": "SRC001",
    }


survey = pd.DataFrame([render_survey_row(r) for r in latent])

# --- Targeted, documented anomalies (small in number, deliberately placed) ---
def rid(n):  # row index for respondent number n
    return survey.index[survey["respondent_id"] == f"R{n:04d}"][0]

linked = {r.get("true_dup_of") for r in latent} | {r.get("is_decoy_of") for r in latent}
non_dup_ids = [r["respondent_id"] for r in latent
               if "true_dup_of" not in r and "is_decoy_of" not in r and id(r) not in linked]
anomaly_ids = list(rng.choice(non_dup_ids[20:], size=16, replace=False))

# invalid / unparseable dates
survey.loc[survey.respondent_id == anomaly_ids[0], "response_date"] = "04/31/2026"
survey.loc[survey.respondent_id == anomaly_ids[1], "response_date"] = "TBD"
# out-of-range travel minutes
survey.loc[survey.respondent_id == anomaly_ids[2], "max_travel_minutes"] = "300"
survey.loc[survey.respondent_id == anomaly_ids[3], "max_travel_minutes"] = "-5"
survey.loc[survey.respondent_id == anomaly_ids[4], "max_travel_minutes"] = "999"
# implausible pledge and volunteer hours
survey.loc[survey.respondent_id == anomaly_ids[5], "one_time_pledge_stated"] = "250000"
survey.loc[survey.respondent_id == anomaly_ids[6], "volunteer_hours_month"] = "120"
# required field blank
survey.loc[survey.respondent_id == anomaly_ids[7], "attendance_frequency"] = ""
survey.loc[survey.respondent_id == anomaly_ids[8], "attendance_frequency"] = ""
# contradictory barriers ("None" plus a real barrier)
for a in anomaly_ids[9:12]:
    survey.loc[survey.respondent_id == a, "main_barriers"] = pick(["None; Parking", "no barriers;Travel distance", "None;Cost"])
# same program category listed twice under different labels
for a in anomaly_ids[12:16]:
    row = survey.loc[survey.respondent_id == a].iloc[0]
    first = row["preferred_programs"].split(";")[0].strip().lower()
    code = alias_df.loc[alias_df.alias_text == first, "category_code"]
    if len(code):
        other = [x for x in ALIASES[code.iloc[0]] if x != first]
        if other:
            survey.loc[survey.respondent_id == a, "preferred_programs"] = row["preferred_programs"] + ";" + pick(other).title()

survey.to_csv(OUT / "community_survey.csv", index=False)

# ---------------------------------------------------------------------------
# 2. Program preferences (child of survey; duplicates re-submit their ratings too)
# ---------------------------------------------------------------------------
FREQ_BY_CAT = {
    "DAILY_PUJA": (["daily", "weekly", "occasional"], [0.45, 0.45, 0.10]),
    "WEEKLY_SATSANG": (["weekly", "biweekly", "monthly"], [0.65, 0.20, 0.15]),
    "FESTIVALS": (["occasional", "monthly"], [0.85, 0.15]),
    "SAMSKARA": (["occasional"], [1.0]),
    "SCRIPTURE": (["weekly", "biweekly", "monthly"], [0.5, 0.3, 0.2]),
    "CHILD_EDU": (["weekly", "biweekly"], [0.8, 0.2]),
    "LANGUAGE": (["weekly", "biweekly"], [0.75, 0.25]),
    "YOGA_MED": (["weekly", "daily", "biweekly"], [0.6, 0.2, 0.2]),
    "MUSIC_DANCE": (["weekly", "biweekly"], [0.7, 0.3]),
    "SENIOR": (["weekly", "biweekly", "monthly"], [0.5, 0.25, 0.25]),
    "SEVA": (["monthly", "occasional", "biweekly"], [0.6, 0.3, 0.1]),
}
PFREQ_VARIANTS = {
    "daily": ["daily", "Daily", "every day"],
    "weekly": ["weekly", "Weekly", "once a week"],
    "biweekly": ["biweekly", "Bi-weekly", "every two weeks", "fortnightly"],
    "monthly": ["monthly", "Monthly"],
    "occasional": ["occasional", "Occasionally", "as needed"],
}

ratings_by_person: dict[int, list[tuple]] = {}
pref_rows = []


def person_ratings(r) -> list[tuple]:
    rated = []
    for rank, c in enumerate(r["top"], start=1):
        if rank == 1:
            score = pick([5, 4, 3], p=[0.60, 0.35, 0.05])
        else:
            score = pick([5, 4, 3], p=[0.40, 0.48, 0.12])
        rated.append((c, score))
    extra_n = 1 if len(r["top"]) < 3 else int(rng.integers(0, 2))
    others = [c for c in CATEGORIES if c not in r["top"]]
    for c in rng.choice(others, size=min(extra_n, len(others)), replace=False):
        rated.append((c, pick([1, 2, 3, 4, 5], p=[0.12, 0.20, 0.30, 0.23, 0.15])))
    out = []
    for c, s in rated:
        opts, p = FREQ_BY_CAT[c]
        f = pick(opts, p=p) if rng.random() > 0.10 else None
        out.append((c, s, f))
    return out


for r in latent:
    src_key = r.get("true_dup_of")
    if src_key is not None and src_key in ratings_by_person:
        ratings = ratings_by_person[src_key]
    else:
        ratings = person_ratings(r)
        ratings_by_person[id(r)] = ratings
    for c, s, f in ratings:
        pref_rows.append([r["respondent_id"], c, s, f])

# originals may sort after their duplicates? No - duplicates are always later in time,
# but ratings for a duplicate are looked up from its original, so fill any misses:
pref = pd.DataFrame(pref_rows, columns=["respondent_id", "category_code", "rating", "freq"])


def render_rating(s: int) -> str:
    r = rng.random()
    if r < 0.88:
        return str(s)
    if r < 0.95:
        return f" {s}"
    return {1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}[s]


pref["program_category"] = [case_noise(pick(ALIASES[c]), 0.3) for c in pref["category_code"]]
pref["interest_rating"] = [render_rating(s) for s in pref["rating"]]
pref["preferred_frequency"] = ["" if not isinstance(f, str) else variant(PFREQ_VARIANTS[f], 0.6) for f in pref["freq"]]

# invalid ratings and blanks
bad_idx = rng.choice(pref.index, size=7, replace=False)
for i, v in zip(bad_idx, ["0", "7", "", "6", "0", "", "10"]):
    pref.loc[i, "interest_rating"] = v

# same respondent, same category under a different label (conflicting ratings)
extra = []
for i in rng.choice(pref.index, size=8, replace=False):
    row = pref.loc[i]
    alts = [a for a in ALIASES[row.category_code] if a.lower() != str(row.program_category).strip().lower()]
    if alts:
        extra.append({"respondent_id": row.respondent_id, "category_code": row.category_code,
                      "program_category": pick(alts).title(),
                      "interest_rating": str(int(np.clip(row.rating + pick([-2, -1, 1]), 1, 5))),
                      "preferred_frequency": row.preferred_frequency})
# orphans (respondent IDs that don't exist in the survey)
for k in range(5):
    c = pick(CATEGORIES)
    extra.append({"respondent_id": f"R{901 + k:04d}", "category_code": c,
                  "program_category": pick(ALIASES[c]), "interest_rating": str(pick([3, 4, 5])),
                  "preferred_frequency": ""})
pref = pd.concat([pref, pd.DataFrame(extra)], ignore_index=True)
pref = pref.sample(frac=1, random_state=SEED).sort_values("respondent_id", kind="stable").reset_index(drop=True)
pref.insert(0, "preference_id", [f"P{n:05d}" for n in range(1, len(pref) + 1)])
pref["data_status"] = [status_label() for _ in range(len(pref))]
pref["source_id"] = "SRC001"
pref[["preference_id", "respondent_id", "program_category", "interest_rating",
      "preferred_frequency", "data_status", "source_id"]].to_csv(OUT / "program_preferences.csv", index=False)

# ---------------------------------------------------------------------------
# 3. Program options (small, mostly clean, a few formatting issues)
# ---------------------------------------------------------------------------
programs = [
    # id, code, name, audience, launch, monthly, vol_h, paid_h, area, flame, kitchen, permanent, note
    ("PG01", "DAILY_PUJA", "Daily darshan & aarti", "all_ages", 2500, 450, 40, 80, 800, True, False, True,
     "Assumes part-time officiant; ritual items beyond startup altar set"),
    ("PG02", "WEEKLY_SATSANG", "Weekly bhajan & satsang", "all_ages", 1200, 150, 24, 0, 1500, False, False, False,
     "Harmonium/tabla/sound; electric diyas in rented venues"),
    ("PG03", "FESTIVALS", "Major festival celebrations (4 per year)", "families", 2500, 900, 40, 8, 3000, True, True, False,
     "Monthly figure is annual cost / 12 incl. decorations and prasad"),
    ("PG04", "SAMSKARA", "Life-cycle ceremonies on request", "families", 800, 100, 4, 8, 600, True, False, False,
     "Largely fee-for-service; cost shown net of typical offerings"),
    ("PG05", "SCRIPTURE", "Gita study circle", "adults", 200, 30, 8, 0, 400, False, False, False,
     "Books and printed material"),
    ("PG06", "CHILD_EDU", "Bal Vihar Sunday classes", "children", 1500, 250, 48, 0, 1200, False, False, False,
     "Volunteer teachers; curriculum materials"),
    ("PG07", "LANGUAGE", "Indian language classes", "families", 800, 150, 32, 0, 600, False, False, False,
     "Volunteer teachers; workbooks"),
    ("PG08", "YOGA_MED", "Yoga & meditation", "adults", 1000, 160, 8, 8, 1000, False, False, False,
     "Mats; stipend for certified instructor"),
    ("PG09", "MUSIC_DANCE", "Classical music & dance", "youth", 1500, 320, 8, 16, 1200, False, False, False,
     "Paid teacher stipend; partly offset by class fees (not modeled)"),
    ("PG10", "SENIOR", "Weekday senior gathering", "seniors", 300, 80, 12, 0, 600, False, True, False,
     "Tea/snacks; accessibility critical"),
    ("PG11", "SEVA", "Monthly food drive & seva", "all_ages", 300, 150, 20, 0, 400, False, False, False,
     "Partnership with local food bank (to be confirmed)"),
    ("PG12", "FESTIVALS", "Annual Diwali community fair", "all_ages", 4000, 350, 60, 0, 5000, False, True, False,
     "Large outdoor/indoor event; venue hire separate"),
    ("PG13", "CHILD_EDU", "Youth leadership group", "youth", 400, 60, 12, 0, 600, False, False, False,
     "Volunteer mentors"),
    ("PG14", "WEEKLY_SATSANG", "Weekend havan (fire ritual)", "all_ages", 1500, 120, 8, 8, 600, True, False, True,
     "Requires ventilation & fire-safety approval; not feasible in most rented halls"),
]
prog = pd.DataFrame(programs, columns=[
    "program_id", "category_code", "program_name", "intended_audience", "est_launch_cost", "est_monthly_cost",
    "volunteer_hours_month", "paid_hours_month", "min_area_sqft", "requires_open_flame", "requires_kitchen",
    "requires_permanent_space", "evidence_note"])
bool_txt = lambda b: variant(["TRUE", "Yes", "true"] if b else ["FALSE", "No", "false"], 0.6)
for col in ["requires_open_flame", "requires_kitchen", "requires_permanent_space"]:
    prog[col] = prog[col].map(bool_txt)
prog["est_launch_cost"] = prog["est_launch_cost"].map(lambda x: fmt_money(x, p_dollar=0.3))
prog["est_monthly_cost"] = prog["est_monthly_cost"].map(lambda x: fmt_money(x, p_dollar=0.2))
prog.loc[prog.program_id == "PG06", "category_code"] = "Bal Vihar"       # label instead of code
prog.loc[prog.program_id == "PG08", "intended_audience"] = "Adults "
prog["min_area_sqft"] = prog["min_area_sqft"].astype(str)
prog.loc[prog.program_id == "PG13", "min_area_sqft"] = ""
prog["verification_status"] = "synthetic_placeholder"
prog["data_status"] = [status_label() for _ in range(len(prog))]
prog["source_id"] = "SRC003"
prog.to_csv(OUT / "program_options.csv", index=False)

# ---------------------------------------------------------------------------
# 4. Candidate properties - ALL SIMULATED. Generic area labels, no addresses.
# ---------------------------------------------------------------------------
props = [
    dict(property_id="SIM-P01", area_label="Simulated Area - Central Civic", jurisdiction="city_tracy",
         property_type="community_hall", tenure_offered="hourly_rental", floor_area_sqft="4200", lot_area_acres="",
         hourly_rate="125", asking_monthly_rent="", asking_price="", parking_spaces="~80",
         current_use="Community hall (rental)", building_condition="good", zoning_label="Public/Institutional (listing)",
         zoning_verification="listing_claim", date_verified="2026-05-02"),
    dict(property_id="SIM-P02", area_label="Simulated Area - West Residential", jurisdiction="City of Tracy",
         property_type="Community_Hall", tenure_offered="hourly_rental", floor_area_sqft="2,600 sq ft",
         lot_area_acres="", hourly_rate="$95/hr", asking_monthly_rent="", asking_price="", parking_spaces="shared",
         current_use="Clubhouse (rental)", building_condition="fair", zoning_label="Residential (listing)",
         zoning_verification="not_checked", date_verified="05/14/2026"),
    dict(property_id="SIM-P03", area_label="Simulated Area - South Schools", jurisdiction="city_tracy",
         property_type="school_facility", tenure_offered="hourly_rental", floor_area_sqft="3800", lot_area_acres="",
         hourly_rate="$140", asking_monthly_rent="", asking_price="", parking_spaces="120",
         current_use="School multipurpose room (weekend rental)", building_condition="good",
         zoning_label="Public/Institutional (listing)", zoning_verification="listing_claim", date_verified="18-May-2026"),
    dict(property_id="SIM-P04", area_label="Simulated Area - East Rural Edge", jurisdiction="County",
         property_type="community_hall", tenure_offered="hourly_rental", floor_area_sqft="3000", lot_area_acres="1.2",
         hourly_rate="85", asking_monthly_rent="", asking_price="", parking_spaces="60",
         current_use="Grange-style hall (rental)", building_condition="fair", zoning_label="",
         zoning_verification="not_checked", date_verified=""),
    dict(property_id="SIM-P05", area_label="Simulated Area - North Commercial", jurisdiction="City of Tracy",
         property_type="retail_unit", tenure_offered="lease", floor_area_sqft="5,200 sq ft", lot_area_acres="",
         hourly_rate="", asking_monthly_rent="$8,840", asking_price="", parking_spaces="shared (center)",
         current_use="Vacant retail (former furniture store)", building_condition="fair",
         zoning_label="General Commercial (listing)", zoning_verification="listing_claim", date_verified="2026-06-01"),
    dict(property_id="SIM-P06", area_label="Simulated Area - Business Park", jurisdiction="city_tracy",
         property_type="office_unit", tenure_offered="lease", floor_area_sqft="3600", lot_area_acres="",
         hourly_rate="", asking_monthly_rent="7560", asking_price="", parking_spaces="45",
         current_use="Vacant office suite", building_condition="good", zoning_label="Office (listing)",
         zoning_verification="not_checked", date_verified="06/03/2026"),
    dict(property_id="SIM-P07", area_label="Simulated Area - Industrial East", jurisdiction="city_tracy",
         property_type="light_industrial", tenure_offered="lease", floor_area_sqft="8000", lot_area_acres="",
         hourly_rate="", asking_monthly_rent="8400", asking_price="", parking_spaces="30",
         current_use="Warehouse/flex", building_condition="fair", zoning_label="Industrial (listing)",
         zoning_verification="not_permitted", date_verified="2026-06-10"),
    dict(property_id="SIM-P08", area_label="Simulated Area - Industrial East", jurisdiction="unknown",
         property_type="light_industrial", tenure_offered="lease", floor_area_sqft="6500", lot_area_acres="",
         hourly_rate="", asking_monthly_rent="TBD", asking_price="", parking_spaces="unknown",
         current_use="Flex unit", building_condition="poor", zoning_label="",
         zoning_verification="not_checked", date_verified=""),
    dict(property_id="SIM-P09", area_label="Simulated Area - South Retail", jurisdiction="city_tracy",
         property_type="Retail Unit", tenure_offered="lease", floor_area_sqft="4400", lot_area_acres="",
         hourly_rate="", asking_monthly_rent="", asking_price="$7,480", parking_spaces="50",
         current_use="Vacant retail", building_condition="good", zoning_label="General Commercial (listing)",
         zoning_verification="listing_claim", date_verified="12-Jun-2026"),
    dict(property_id="SIM-P10", area_label="Simulated Area - Old Town", jurisdiction="city_tracy",
         property_type="former_church", tenure_offered="sale", floor_area_sqft="9000", lot_area_acres="1.8",
         hourly_rate="", asking_monthly_rent="", asking_price="$2,450,000", parking_spaces="95",
         current_use="Former church (vacant)", building_condition="fair",
         zoning_label="Public/Institutional (listing)", zoning_verification="listing_claim", date_verified="2026-06-15"),
    dict(property_id="SIM-P11", area_label="Simulated Area - Southwest Agricultural", jurisdiction="sj_county",
         property_type="agricultural_building", tenure_offered="sale", floor_area_sqft="5000", lot_area_acres="5",
         hourly_rate="", asking_monthly_rent="", asking_price="1650000", parking_spaces="unknown",
         current_use="Agricultural barn/office", building_condition="fair", zoning_label="Agricultural (listing)",
         zoning_verification="not_checked", date_verified="06/20/2026"),
    dict(property_id="SIM-P12", area_label="Simulated Area - Southwest Agricultural", jurisdiction="county",
         property_type="vacant_land", tenure_offered="sale", floor_area_sqft="", lot_area_acres="3.2",
         hourly_rate="", asking_monthly_rent="", asking_price="call for pricing", parking_spaces="0",
         current_use="Vacant land", building_condition="", zoning_label="Agricultural (listing)",
         zoning_verification="not_checked", date_verified="2026-06-20"),
]
prop = pd.DataFrame(props)
prop["is_simulated"] = [variant(["TRUE", "Yes", "true"], 0.6) for _ in range(len(prop))]
prop["data_status"] = [status_label() for _ in range(len(prop))]
prop["source_id"] = "SRC002"
prop.loc[prop.property_id == "SIM-P06", "area_label"] = "  Simulated Area - Business Park "
prop.to_csv(OUT / "candidate_properties.csv", index=False)

# ---------------------------------------------------------------------------
# 5. Property due diligence (long format: property x review area)
# ---------------------------------------------------------------------------
AREA_CODE = {"zoning": "ZON", "building_use": "BLD", "parking": "PRK", "accessibility": "ACC", "fire_life_safety": "FIR"}
AREA_TXT = {
    "zoning": ["Zoning", "zoning"],
    "building_use": ["Building Use", "building use", "Building-use"],
    "parking": ["Parking", "parking "],
    "accessibility": ["Accessibility", "ADA"],
    "fire_life_safety": ["Fire/Life Safety", "fire & life safety", "Fire"],
}
STATUS_TXT = {
    "not_started": ["Not Started", "not started", "not_started"],
    "in_progress": ["In Progress", "pending", "in-progress"],
    "issue_found": ["Issue found", "issue", "Issue Found"],
    "verified_ok": ["Verified", "OK", "verified_ok"],
    "failed": ["Failed", "FAILED"],
    "not_applicable": ["N/A", "not applicable"],
}
# (status, est_cost_to_resolve, next_action, owner_role, last_updated)
DD = {
    "SIM-P01": {"zoning": ("verified_ok", None, "Venue already operates as rental assembly hall; keep rental agreement on file", "facilities lead", "2026-05-02"),
                "building_use": ("verified_ok", None, "Confirm posted occupant load covers expected attendance", "facilities lead", "2026-05-02"),
                "parking": ("verified_ok", None, "None", "facilities lead", "2026-05-02"),
                "accessibility": ("in_progress", None, "Walk accessible route and restrooms with checklist", "volunteer coordinator", "2026-05-20"),
                "fire_life_safety": ("issue_found", 0, "Venue policy bans open flame - confirm electric diyas acceptable; ask about incense", "facilities lead", "2026-05-20")},
    "SIM-P02": {"zoning": ("in_progress", None, "Ask HOA/management whether recurring religious gatherings are allowed", "facilities lead", "05/14/2026"),
                "building_use": ("in_progress", None, "Request occupant load from management", "facilities lead", "05/14/2026"),
                "parking": ("issue_found", None, "Shared lot with residents; limited weekend availability", "facilities lead", "05/30/2026"),
                "accessibility": ("not_started", None, "", "", ""),
                "fire_life_safety": ("not_started", None, "", "", "")},
    "SIM-P03": {"zoning": ("verified_ok", None, "District facility-use agreement covers community groups", "facilities lead", "18-May-2026"),
                "building_use": ("verified_ok", None, "None", "facilities lead", "18-May-2026"),
                "parking": ("verified_ok", None, "None", "facilities lead", "18-May-2026"),
                "accessibility": ("verified_ok", None, "None", "facilities lead", "18-May-2026"),
                "fire_life_safety": ("issue_found", 1500, "No open flame; district requires extra insurance rider and custodian fee", "treasurer", "2026-06-02")},
    "SIM-P04": {"zoning": ("in_progress", None, "Confirm county allows recurring religious events at the hall", "facilities lead", "2026-06-05"),
                "building_use": ("not_started", None, "", "", ""),
                "parking": ("verified_ok", None, "Gravel lot ~60 spaces", "facilities lead", "2026-06-05"),
                "accessibility": ("issue_found", "unknown", "Entrance has steps; ramp availability unclear", "facilities lead", "2026-06-05"),
                "fire_life_safety": ("not_started", None, "", "", "")},
    "SIM-P05": {"zoning": ("in_progress", 8000, "Pre-application meeting: is a CUP required for religious assembly in this zone?", "facilities lead", "2026-06-01"),
                "building_use": ("not_started", None, "Architect review of change to assembly occupancy", "architect", ""),
                "parking": ("issue_found", 2500, "Shared center parking; explore joint-use agreement with daytime tenants", "facilities lead", "2026-05-10"),
                "accessibility": ("not_started", None, "", "", ""),
                "fire_life_safety": ("not_started", None, "Fire district consult on sprinklers and occupant load", "architect", "")},
    "SIM-P06": {"zoning": ("in_progress", 8000, "Confirm whether assembly use allowed in office zone and permit type", "facilities lead", "06/03/2026"),
                "building_use": ("issue_found", 45000, "Restroom count likely insufficient for assembly occupancy", "architect", "06/10/2026"),
                "parking": ("in_progress", None, "Count stalls vs. assembly ratio; weekend availability", "facilities lead", "06/10/2026"),
                "accessibility": ("not_started", None, "", "", ""),
                "fire_life_safety": ("not_started", None, "", "", "")},
    "SIM-P07": {"zoning": ("failed", None, "Simulated scenario: assembly not permitted in this zone - drop unless rezoning considered", "facilities lead", "2026-06-10"),
                "building_use": ("not_started", None, "", "", ""),
                "parking": ("not_started", None, "", "", ""),
                "accessibility": ("not_started", None, "", "", ""),
                "fire_life_safety": ("not_started", None, "", "", "")},
    "SIM-P08": {"zoning": ("not_started", None, "Confirm jurisdiction (city or county) via parcel lookup", "facilities lead", ""),
                "building_use": ("not_started", None, "", "", ""),
                "parking": ("not_started", None, "", "", ""),
                "accessibility": (None, None, "", "", ""),       # blank status
                "fire_life_safety": ("not_started", None, "", "", "")},
    "SIM-P09": {"zoning": ("in_progress", 8000, "Pre-application meeting on CUP requirement", "facilities lead", "12-Jun-2026"),
                "building_use": ("issue_found", 30000, "Single restroom; upgrades needed for assembly use", "architect", "2026-06-18"),
                "parking": ("in_progress", None, "Verify 50 stalls are dedicated, not shared", "facilities lead", "2026-06-18"),
                "accessibility": ("not_started", None, "", "", ""),
                "fire_life_safety": ("not_started", None, "", "", "")},
    "SIM-P10": {"zoning": ("in_progress", 5000, "Confirm whether prior church entitlement transfers or new CUP needed", "attorney", "2026-06-15"),
                "building_use": ("in_progress", None, "Architect walk-through of structure and roof", "architect", "2026-06-22"),
                "parking": ("verified_ok", None, "Simulated: on-site lot appears adequate - confirm against code ratio", "facilities lead", "2026-06-22"),
                "accessibility": ("issue_found", 60000, "Older building; restrooms and entrance need upgrades", "architect", "2026-06-22"),
                "fire_life_safety": ("issue_found", "$120,000", "No sprinkler system; fire district consultation needed", "architect", "2026-06-22")},
    "SIM-P11": {"zoning": ("in_progress", 15000, "County CUP for religious assembly likely required; pre-application meeting", "facilities lead", "06/20/2026"),
                "building_use": ("issue_found", "unknown", "Change of occupancy from agricultural to assembly", "architect", "06/20/2026"),
                "parking": ("not_started", None, "", "", ""),
                # accessibility row intentionally missing
                "fire_life_safety": ("not_started", None, "Rural fire district - water supply for fire flow?", "architect", "")},
    "SIM-P12": {"zoning": ("not_started", None, "", "", ""),
                "building_use": ("not_applicable", None, "No building - new construction out of scope for phase 1", "", "2026-06-20"),
                "parking": ("not_started", None, "", "", ""),
                "accessibility": ("not_applicable", None, "", "", "2026-06-20"),
                "fire_life_safety": ("not_started", None, "", "", "")},
}
dd_rows = []
for pid, areas in DD.items():
    for area, (status, cost, action, owner, updated) in areas.items():
        dd_rows.append({
            "dd_id": f"DD-{pid[4:]}-{AREA_CODE[area]}",
            "property_id": pid,
            "review_area": variant(AREA_TXT[area], 0.5),
            "status": "" if status is None else variant(STATUS_TXT[status], 0.4),
            "est_cost_to_resolve": "" if cost is None else (cost if isinstance(cost, str) else fmt_money(cost, p_dollar=0.3)),
            "next_action": action,
            "owner_role": owner,
            "last_updated": updated,
        })
# a stale earlier version of one record (same dd_id) - only the later one is current
dd_rows.append({"dd_id": "DD-P05-PRK", "property_id": "SIM-P05", "review_area": "parking", "status": "In Progress",
                "est_cost_to_resolve": "", "next_action": "Count shared stalls on a Sunday morning",
                "owner_role": "facilities lead", "last_updated": "04/28/2026"})
dd = pd.DataFrame(dd_rows)
dd["data_status"] = [status_label() for _ in range(len(dd))]
dd["source_id"] = "SRC002"
dd.to_csv(OUT / "property_due_diligence.csv", index=False)

# ---------------------------------------------------------------------------
# 6. Startup cost estimates (synthetic placeholder magnitudes)
# ---------------------------------------------------------------------------
SC = [
    # model, category, description, low, base, high, basis
    ("OM_RENT_EVENT", "RITUAL_SETUP", "Portable altar, murtis and puja items", 3000, 6000, 12000, "Placeholder; ask vendors"),
    ("OM_RENT_EVENT", "FURNITURE_AV", "Portable sound system and storage cases", 1500, 3000, 5000, "Placeholder"),
    ("OM_RENT_EVENT", "LEASE_DEPOSIT", "Venue booking deposits", 500, 1000, 2000, "Placeholder; venue-specific"),
    ("OM_RENT_EVENT", "PROFESSIONAL", "Attorney/insurance review of venue contracts", 500, 1500, 3000, "Placeholder"),
    ("OM_RENT_EVENT", "ORG_FORMATION", "Nonprofit incorporation and filings", 1000, 2500, 5000, "Placeholder; confirm with attorney/CPA"),
    ("OM_LEASE_DEDICATED", "LEASE_DEPOSIT", "Security deposit and first month", 15000, 20000, 30000, "~2-3 months of synthetic rent"),
    ("OM_LEASE_DEDICATED", "PERMITS_FEES", "CUP application, plan check, building permits", 5000, 12000, 25000, "Placeholder; obtain fee schedule"),
    ("OM_LEASE_DEDICATED", "PROFESSIONAL", "Architect and engineer", 12000, 25000, 45000, "Placeholder"),
    ("OM_LEASE_DEDICATED", "PROFESSIONAL", "Attorney (lease review, entitlement)", 3000, 7000, 12000, "Placeholder"),
    ("OM_LEASE_DEDICATED", "PROFESSIONAL", "Accessibility (CASp) inspection", 1000, 2500, 4000, "Placeholder"),
    ("OM_LEASE_DEDICATED", "RENOVATION", "Tenant improvements for assembly use", 60000, 150000, 300000, "Placeholder; highly property-specific"),
    ("OM_LEASE_DEDICATED", "ACCESSIBILITY", "Accessible restrooms, entrance, parking", 10000, 35000, 80000, "Placeholder"),
    ("OM_LEASE_DEDICATED", "FIRE_LIFE_SAFETY", "Sprinklers, alarms, exits (if required)", 15000, 50000, 150000, "Placeholder; depends on fire district"),
    ("OM_LEASE_DEDICATED", "RITUAL_SETUP", "Sanctum, murtis and installation", 15000, 40000, 90000, "Placeholder; community decision"),
    ("OM_LEASE_DEDICATED", "FURNITURE_AV", "Seating, sound system, storage", 8000, 15000, 30000, "Placeholder"),
    ("OM_LEASE_DEDICATED", "KITCHEN", "Prasad kitchen equipment", 5000, 15000, 40000, "Placeholder; health permit needed"),
    ("OM_LEASE_DEDICATED", "SECURITY", "Cameras, alarm, lighting", 3000, 8000, 15000, "Placeholder"),
    ("OM_LEASE_DEDICATED", "ORG_FORMATION", "Nonprofit incorporation and filings", 1000, 2500, 5000, "Placeholder"),
    ("OM_PURCHASE_ADAPT", "ACQUISITION", "Down payment and closing costs", 400000, 500000, 650000, "~25% of synthetic ~$1.8M price plus closing"),
    ("OM_PURCHASE_ADAPT", "PERMITS_FEES", "CUP, plan check, building permits", 10000, 25000, 50000, "Placeholder"),
    ("OM_PURCHASE_ADAPT", "PROFESSIONAL", "Architect and engineer", 25000, 50000, 85000, "Placeholder"),
    ("OM_PURCHASE_ADAPT", "PROFESSIONAL", "Attorney (purchase, entitlement)", 5000, 10000, 20000, "Placeholder"),
    ("OM_PURCHASE_ADAPT", "PROFESSIONAL", "Inspections and environmental review", 3000, 8000, 15000, "Placeholder"),
    ("OM_PURCHASE_ADAPT", "RENOVATION", "Renovation for assembly use", 150000, 350000, 700000, "Placeholder"),
    ("OM_PURCHASE_ADAPT", "ACCESSIBILITY", "Accessibility upgrades", 20000, 60000, 120000, "Placeholder"),
    ("OM_PURCHASE_ADAPT", "FIRE_LIFE_SAFETY", "Sprinklers, alarms, exits", 30000, 90000, 200000, "Placeholder"),
    ("OM_PURCHASE_ADAPT", "RITUAL_SETUP", "Sanctum, murtis and installation", 25000, 60000, 150000, "Placeholder"),
    ("OM_PURCHASE_ADAPT", "FURNITURE_AV", "Seating, sound system, storage", 10000, 20000, 40000, "Placeholder"),
    ("OM_PURCHASE_ADAPT", "KITCHEN", "Prasad kitchen equipment", 10000, 30000, 60000, "Placeholder"),
    ("OM_PURCHASE_ADAPT", "SECURITY", "Cameras, alarm, lighting", 5000, 10000, 20000, "Placeholder"),
    ("OM_PURCHASE_ADAPT", "ORG_FORMATION", "Nonprofit incorporation and filings", 1000, 2500, 5000, "Placeholder"),
]
MODEL_TXT = {
    "OM_RENT_EVENT": ["OM_RENT_EVENT", "Rent", "rent event", "OM_RENT_EVENT "],
    "OM_LEASE_DEDICATED": ["OM_LEASE_DEDICATED", "Lease", "lease dedicated", "OM_LEASE_DEDICATED "],
    "OM_PURCHASE_ADAPT": ["OM_PURCHASE_ADAPT", "Purchase", "purchase & adapt"],
}
cc = pd.read_csv(REF / "cost_category.csv")
CC_NAME = dict(zip(cc.cost_category_code, cc.category_name))


def render_cost_rows(rows, id_prefix, cols):
    out = []
    for n, (m, c, desc, lo, ba, hi, basis) in enumerate(rows, start=1):
        out.append({
            cols[0]: f"{id_prefix}{n:03d}",
            "operating_model": variant(MODEL_TXT[m], 0.75),
            "cost_category": c if rng.random() < 0.8 else CC_NAME[c],
            "line_description": desc,
            cols[1]: fmt_money(lo), cols[2]: fmt_money(ba), cols[3]: fmt_money(hi),
            "estimate_basis": basis,
            "verification_status": variant(["synthetic_placeholder", "Synthetic placeholder", "placeholder"], 0.8),
            "data_status": status_label(),
            "source_id": "SRC003",
        })
    return pd.DataFrame(out)


sc = render_cost_rows(SC, "SC", ["cost_id", "low_estimate", "base_estimate", "high_estimate"])
# one row with low and high swapped
sc.loc[sc.cost_id == "SC013", ["low_estimate", "high_estimate"]] = sc.loc[sc.cost_id == "SC013", ["high_estimate", "low_estimate"]].values
sc.to_csv(OUT / "startup_cost_estimates.csv", index=False)

# ---------------------------------------------------------------------------
# 7. Operating cost estimates (monthly)
# ---------------------------------------------------------------------------
OC = [
    ("OM_RENT_EVENT", "RENT", "Hall hire ~40 hrs/month (2 weekly sessions + 1 festival)", 2800, 4400, 6500, "40 hrs x synthetic $70-160/hr"),
    ("OM_RENT_EVENT", "INSURANCE", "Event liability coverage", 150, 250, 400, "Placeholder; broker quote needed"),
    ("OM_RENT_EVENT", "STAFF", "Priest honorarium per session", 800, 1500, 2500, "Placeholder"),
    ("OM_RENT_EVENT", "PROGRAMS", "Program supplies and prasad", 300, 600, 1000, "Placeholder"),
    ("OM_RENT_EVENT", "ADMIN", "Accounting, software, bank fees", 100, 200, 350, "Placeholder"),
    ("OM_RENT_EVENT", "MAINTENANCE", "Storage unit for altar and equipment", 100, 150, 250, "Placeholder"),
    ("OM_LEASE_DEDICATED", "RENT", "Base rent (synthetic ~5,000 sq ft)", 7000, 9000, 12000, "Synthetic $1.40-2.40/sq ft/month"),
    ("OM_LEASE_DEDICATED", "UTILITIES", "Electricity, gas, water, waste", 800, 1200, 1800, "Placeholder"),
    ("OM_LEASE_DEDICATED", "INSURANCE", "Liability, property, D&O", 500, 800, 1300, "Placeholder"),
    ("OM_LEASE_DEDICATED", "MAINTENANCE", "Janitorial, CAM charges, repairs", 900, 1500, 2500, "Placeholder"),
    ("OM_LEASE_DEDICATED", "STAFF", "Part-time priest stipend and admin", 3000, 4500, 6500, "Placeholder"),
    ("OM_LEASE_DEDICATED", "PROGRAMS", "Program supplies and prasad", 500, 900, 1500, "Placeholder"),
    ("OM_LEASE_DEDICATED", "ADMIN", "Accounting, software, bank fees", 200, 350, 600, "Placeholder"),
    ("OM_LEASE_DEDICATED", "RESERVE_CONTRIB", "Capital reserve set-aside", 300, 500, 1000, "Policy choice"),
    ("OM_PURCHASE_ADAPT", "MORTGAGE", "Debt service on ~$1.35M loan", 8000, 9500, 11500, "Placeholder; depends on rate and term"),
    ("OM_PURCHASE_ADAPT", "UTILITIES", "Electricity, gas, water, waste", 1200, 1800, 2600, "Placeholder"),
    ("OM_PURCHASE_ADAPT", "INSURANCE", "Liability, property, D&O", 900, 1400, 2200, "Placeholder"),
    ("OM_PURCHASE_ADAPT", "MAINTENANCE", "Janitorial, repairs, landscaping", 1500, 2500, 4000, "Placeholder"),
    ("OM_PURCHASE_ADAPT", "STAFF", "Part-time priest stipend and admin", 3000, 4500, 6500, "Placeholder"),
    ("OM_PURCHASE_ADAPT", "PROGRAMS", "Program supplies and prasad", 500, 900, 1500, "Placeholder"),
    ("OM_PURCHASE_ADAPT", "ADMIN", "Accounting, software, bank fees", 200, 350, 600, "Placeholder"),
    ("OM_PURCHASE_ADAPT", "PROPERTY_TAX", "Property tax before any exemption", 0, 1500, 2100, "Low case assumes exemption obtained"),
    ("OM_PURCHASE_ADAPT", "RESERVE_CONTRIB", "Capital reserve set-aside", 500, 1000, 2000, "Policy choice"),
]
oc = render_cost_rows(OC, "OC", ["op_cost_id", "monthly_low", "monthly_base", "monthly_high"])
# low above base on one row
oc.loc[oc.op_cost_id == "OC009", "monthly_low"] = "1100"
# exact duplicate line re-keyed (copy/paste error in the estimate sheet)
dup_line = oc.loc[oc.op_cost_id == "OC012"].copy()
dup_line["op_cost_id"] = "OC024"
oc = pd.concat([oc, dup_line], ignore_index=True)
oc.to_csv(OUT / "operating_cost_estimates.csv", index=False)

# ---------------------------------------------------------------------------
# 8. Funding scenarios (hypothetical, realized amounts - NOT pledged amounts)
# ---------------------------------------------------------------------------
fs = pd.DataFrame([
    ["FS01", "Pessimistic", "40000", "2500", 12, "0.20", "5000", "0", "0.30", "low",
     "Few large donors; pledges mostly unrealized; slow ramp-up."],
    ["FS02", "Conservative", "$90,000", "4500", 9, "0.30", "10000", "0", "0.40", "low",
     "Recommended planning case: realization below survey intent."],
    ["FS03", "Base", "150000", "$7,000", 6, "35%", "18000", "0", "0.50", "medium",
     "Midpoint assumptions; still unvalidated until a pilot period."],
    ["FS04", "Optimistic", "250000", "11000", 4, "0.50", "30000", "0", "0.70", "low",
     "Requires strong early participation; treat as upside only."],
    ["FS05", "Base + secular program grant", "150000", "7000", 6, "0.35", "18000", "15000", "0.50", "low",
     "Grant only for non-worship programs (e.g., seva/food drive); eligibility unverified."],
], columns=["scenario_id", "scenario_name", "initial_funds_assumed", "monthly_recurring_assumed", "ramp_months",
            "pledge_realization_rate", "annual_event_fundraising_net", "grant_amount_assumed", "attendance_discount",
            "confidence_level", "assumptions_text"])
fs["data_status"] = "unverified_assumption"
fs["source_id"] = "SRC004"
fs.to_csv(OUT / "funding_scenarios.csv", index=False)

# ---------------------------------------------------------------------------
# 9. Model assumptions (every constant used later lives here)
# ---------------------------------------------------------------------------
MA = [
    ("attendance_intent_discount", 0.30, 0.50, 0.70, "ratio", "all", "Stated intent overstates behaviour; replace with pilot-event data"),
    ("pledge_realization_rate", 0.20, 0.35, 0.50, "ratio", "all", "Share of stated giving that becomes cash; validate with 6 months of records"),
    ("attending_share_of_household", 0.50, 0.65, 0.80, "ratio", "all", "Not every household member attends every visit"),
    ("visits_per_month_multiple_weekly", 8, 10, 12, "visits_per_month", "all", "Interpretation of survey category"),
    ("visits_per_month_weekly", 3, 4, 4.3, "visits_per_month", "all", "Interpretation of survey category"),
    ("visits_per_month_monthly", 0.8, 1, 1.2, "visits_per_month", "all", "Interpretation of survey category"),
    ("visits_per_month_festivals_only", 0.25, 0.33, 0.5, "visits_per_month", "all", "3-6 festivals per year"),
    ("visits_per_month_rarely", 0, 0.1, 0.2, "visits_per_month", "all", "Interpretation of survey category"),
    ("visits_per_month_unsure", 0, 0.25, 0.5, "visits_per_month", "all", "Wide range by design"),
    ("assembly_sqft_per_person", 7, 12, 15, "sqft_per_person", "all", "Floor seating to chairs/tables; confirm occupant-load factors with architect"),
    ("support_space_factor", 1.4, 1.6, 1.8, "ratio", "all", "Gross area / assembly area (lobby, restrooms, kitchen, storage)"),
    ("persons_per_parking_space", 3, 3.5, 4, "persons_per_space", "all", "Confirm actual code ratio with planning staff"),
    ("peak_session_share", 0.40, 0.50, 0.60, "ratio", "all", "Share of weekly attendees present at the busiest session"),
    ("festival_peak_multiplier", 2, 3, 4, "ratio", "all", "Festival attendance relative to regular peak"),
    ("contingency_rate_rent", 0.05, 0.10, 0.15, "ratio", "OM_RENT_EVENT", "BRL-08"),
    ("contingency_rate_lease", 0.10, 0.15, 0.20, "ratio", "OM_LEASE_DEDICATED", "BRL-08"),
    ("contingency_rate_purchase", 0.15, 0.20, 0.25, "ratio", "OM_PURCHASE_ADAPT", "BRL-08"),
    ("operating_reserve_months", 3, 6, 9, "months", "all", "BRL-09"),
    ("volunteer_hours_realization", 0.30, 0.50, 0.70, "ratio", "all", "Share of stated volunteer hours actually given"),
    ("startup_amortization_years", 5, 5, 5, "years", "all", "For cost-per-visit comparison only"),
    ("cost_inflation_annual", 0.02, 0.03, 0.05, "ratio", "all", "Applied to operating costs in years 2-3"),
]
ma = pd.DataFrame(MA, columns=["assumption_name", "value_low", "value_base", "value_high", "unit", "applies_to", "rationale"])
ma.insert(0, "assumption_id", [f"MA{n:02d}" for n in range(1, len(ma) + 1)])
ma["verification_status"] = "analyst_estimate"
ma["data_status"] = "unverified_assumption"
ma["source_id"] = "SRC004"
ma.to_csv(OUT / "model_assumptions.csv", index=False)

# ---------------------------------------------------------------------------
# 10. Data sources (copy of the reference registry)
# ---------------------------------------------------------------------------
pd.read_csv(REF / "data_source.csv").to_csv(OUT / "data_sources.csv", index=False)

# ---------------------------------------------------------------------------
summary = {f.name: sum(1 for _ in open(f)) - 1 for f in sorted(OUT.glob("*.csv"))}
total = 0
for k, v in summary.items():
    print(f"{k:32s} {v:5d} rows")
    total += v
print(f"{'TOTAL':32s} {total:5d} rows  (all synthetic / hypothetical)")
