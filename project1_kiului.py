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





