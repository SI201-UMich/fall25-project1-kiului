# SI 201: Project 1 — Data Analysis (Penguins)
# Name: Hong Kiu Lui
# Student ID: TBD # <-- replace with your UM ID to satisfy rubric
# Email: ok
# Collaborators: None
# GenAI usage: Used ChatGPT (GPT-5 Thinking) for planning, code review, and diagram generation.


import csv
import math

#cleaning data

def load_penguins(csv_file):
    """
    Read CSV and return a list of dictionaries (one dict per row).
    Also normalizes types and strings using _coerce_types().
    """
    rows = []
    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(_coerce_types(row))
    return rows

def _coerce_types(row):
    """
    Helper: clean strings and convert numbers.
    - Blank strings or 'na'/'nan'/'none' become None.
    - body_mass_g, flipper_length_mm -> int (if possible)
    - bill_length_mm, bill_depth_mm -> float (if possible)
    - species, island, sex -> title-case strings for consistency
    """
    clean = {}

    # 1) normalize blanks / NA-like strings
    for k, v in row.items():
        if isinstance(v, str):
            v = v.strip()
            if v == "" or v.lower() in ("na", "nan", "none"):
                v = None
        clean[k] = v

    # 2) convert numbers (best effort)
    int_fields = ["body_mass_g", "flipper_length_mm"]
    float_fields = ["bill_length_mm", "bill_depth_mm"]

    for fld in int_fields:
        if fld in clean:
            try:
                clean[fld] = int(clean[fld]) if clean[fld] is not None else None
            except Exception:
                clean[fld] = None

    for fld in float_fields:
        if fld in clean:
            try:
                clean[fld] = float(clean[fld]) if clean[fld] is not None else None
            except Exception:
                clean[fld] = None

    for fld in ["species", "island", "sex"]:
        if fld in clean and isinstance(clean[fld], str):
            clean[fld] = clean[fld].title()

    return clean

def filter_valid_rows(rows):
    """
    Keep only rows that have all the fields we need for BOTH calculations:
    species, island, sex, body_mass_g
    """
    required = ["species", "island", "sex", "body_mass_g"]
    clean_rows = []
    for r in rows:
        ok = True
        for col in required:
            if r.get(col) is None:
                ok = False
                break
        if ok:
            clean_rows.append(r)
    return clean_rows

#helper functions


def _group_by_species_sex(rows):
    """
    Build a dictionary: (species, sex) -> list of body_mass_g values
    """
    groups = {}
    for r in rows:
        sp = r.get("species")
        sx = r.get("sex")
        bm = r.get("body_mass_g")
        if sp is None or sx is None or bm is None:
            continue
        key = (sp, sx)
        if key not in groups:
            groups[key] = []
        groups[key].append(bm)
    return groups


def _group_by_island_species(rows):
    """
    Build a nested dictionary: island -> species -> list of body_mass_g values
    """
    nested = {}
    for r in rows:
        isl = r.get("island")
        sp = r.get("species")
        bm = r.get("body_mass_g")
        if isl is None or sp is None or bm is None:
            continue
        if isl not in nested:
            nested[isl] = {}
        if sp not in nested[isl]:
            nested[isl][sp] = []
        nested[isl][sp].append(bm)
    return nested

#calculations
def calc_avg_mass_by_species_sex(rows):
    """
    Return a list of dictionaries with:
      species, sex, avg_body_mass_g. 
    One result per (species, sex).
    """
    groups = _group_by_species_sex(rows)
    results = []

    # Sort keys so output is stable and easy to read
    keys = list(groups.keys())
    keys.sort()

    for key in keys:
        masses = groups[key]
        if len(masses) == 0:
            continue
        avg = sum(masses) / float(len(masses))
        result_row = {
            "species": key[0],
            "sex": key[1],
            "avg_body_mass_g": round(avg, 2),
            "n": len(masses)
        }
        results.append(result_row)

    return results

def calc_heaviest_species_per_island(rows):
    """
    For each island, find the species with the highest average body mass.
    Returns a list of dicts: island, species, avg_body_mass_g. 
      - If two species have the same average, choose the one with larger n.
      - If still tied, choose the species name that is alphabetically earlier.
    """
    nested = _group_by_island_species(rows)
    results = []

    islands = list(nested.keys())
    islands.sort()

    for island in islands:
        best_species = None
        best_avg = -float("inf")
        best_n = 0

        species_list = list(nested[island].keys())
        species_list.sort()

        for species in species_list:
            masses = nested[island][species]
            if len(masses) == 0:
                continue
            avg = sum(masses) / float(len(masses))

            # Compare to current best using the tie-break rule
            replace = False
            if avg > best_avg:
                replace = True
            elif abs(avg - best_avg) < 1e-9:
                if len(masses) > best_n:
                    replace = True
                elif len(masses) == best_n and best_species is not None and species < best_species:
                    replace = True

            if replace:
                best_species = species
                best_avg = avg
                best_n = len(masses)

        if best_species is not None:
            results.append({
                "island": island,
                "species": best_species,
                "avg_body_mass_g": round(best_avg, 2),
                "n": best_n
            })

    return results











#test cases

TEST_SAMPLE = [
    {"species": "Adelie",   "island": "Torgersen", "sex": "Male",   "body_mass_g": 3700},
    {"species": "Adelie",   "island": "Torgersen", "sex": "Female", "body_mass_g": 3400},
    {"species": "Adelie",   "island": "Torgersen", "sex": "Female", "body_mass_g": None},   # NA
    {"species": "Gentoo",   "island": "Biscoe",    "sex": "Male",   "body_mass_g": 5200},
    {"species": "Gentoo",   "island": "Biscoe",    "sex": "Male",   "body_mass_g": 5000},
    {"species": "Gentoo",   "island": "Biscoe",    "sex": "Female", "body_mass_g": 4700},
    {"species": "Chinstrap","island": "Dream",     "sex": "Male",   "body_mass_g": 3600},
    {"species": "Chinstrap","island": "Dream",     "sex": "Female", "body_mass_g": 3800},
    {"species": "Chinstrap","island": "Dream",     "sex": None,     "body_mass_g": 3700},   # NA sex
]


def test_calc_avg_mass_by_species_sex():
    # Use only rows that have a sex AND body mass for this test
    rows = []
    for r in TEST_SAMPLE:
        if r["sex"] is not None and r["body_mass_g"] is not None:
            rows.append(r)

    res = calc_avg_mass_by_species_sex(rows)

    # General cases
    # Adelie Male avg = 3700
    ok1 = False
    for r in res:
        if r["species"] == "Adelie" and r["sex"] == "Male" and r["avg_body_mass_g"] == 3700:
            ok1 = True
    assert ok1

    # Gentoo Male avg = (5200+5000)/2 = 5100
    ok2 = False
    for r in res:
        if r["species"] == "Gentoo" and r["sex"] == "Male" and r["avg_body_mass_g"] == 5100:
            ok2 = True
    assert ok2

    # Edge cases
    # Gentoo Female avg = 4700 (single value works)
    ok3 = False
    for r in res:
        if r["species"] == "Gentoo" and r["sex"] == "Female" and r["avg_body_mass_g"] == 4700:
            ok3 = True
    assert ok3

    # No rows with missing sex should appear
    for r in res:
        assert r["sex"] is not None


def test_calc_heaviest_species_per_island():
    # Only rows that have body mass
    rows = []
    for r in TEST_SAMPLE:
        if r["body_mass_g"] is not None:
            rows.append(r)

    res = calc_heaviest_species_per_island(rows)

    # General cases
    ok1 = False
    for r in res:
        if r["island"] == "Biscoe" and r["species"] == "Gentoo" and r["avg_body_mass_g"] == 5100:
            ok1 = True
    assert ok1

    ok2 = False
    for r in res:
        if r["island"] == "Dream" and r["species"] == "Chinstrap" and r["avg_body_mass_g"] == 3700:
            ok2 = True
    assert ok2

    ok3 = False
    for r in res:
        if r["island"] == "Torgersen" and r["species"] == "Adelie":
            ok3 = True
    assert ok3

    # All averages should be numbers
    for r in res:
        assert isinstance(r["avg_body_mass_g"], (int, float))





