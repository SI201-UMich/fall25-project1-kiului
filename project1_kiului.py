# SI 201: Project 1 — Data Analysis (Penguins)
# Name: Hong Kiu Lui
# Student ID: 3212 6869
# Email: kiului@umich.edu
# Collaborators: None
# GenAI usage: Used ChatGPT for planning code logic and diagram generation.


import csv

#Cleaning data

def load_penguins(csv_file):
    """
    Read CSV and return a list of dictionaries (one dict per row).
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
    """
    clean = {}

    # Normalize blanks / NA strings
    for k, v in row.items():
        if isinstance(v, str):
            v = v.strip()
            if v == "" or v.lower() in ("na", "nan", "none"):
                v = None
        clean[k] = v

    # Convert numbers (best effort)
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
    Keep only rows that have all the fields we need for both calculations:
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

#Helper functions


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

#Calculations
def calc_avg_mass_by_species_sex(rows):
    """
    Return a list of dictionaries with:
      species, sex, avg_body_mass_g. 
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

#Write into csv

def write_avg_mass_csv(results, out_path):
    """
    Write species-sex averages to CSV:
      species,sex,avg_body_mass_g,n
    """
    fields = ["species", "sex", "avg_body_mass_g", "n"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in results:
            w.writerow(row)


def write_heaviest_csv(results, out_path):
    """
    Write heaviest species per island to CSV:
      island,species,avg_body_mass_g,n
    """
    fields = ["island", "species", "avg_body_mass_g", "n"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in results:
            w.writerow(row)


def write_summary_txt(avg_results, heavy_results, out_path):
   
    lines = []
    lines.append("Penguins Project — Summary")
    lines.append("")
    lines.append("Average body mass by (species, sex):")
    for r in avg_results:
        lines.append("- " + r["species"] + " (" + r["sex"] + "): " +
                     str(r["avg_body_mass_g"]) + " g (n=" + str(r["n"]) + ")")
    lines.append("")
    lines.append("Heaviest species per island (by average mass):")
    for r in heavy_results:
        lines.append("- " + r["island"] + ": " + r["species"] +
                     " — " + str(r["avg_body_mass_g"]) + " g (n=" + str(r["n"]) + ")")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))




#Test cases

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
    # Use only rows that have a sex and body mass for this test
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

def main():
    
    #csv_path = "/Users/hongkiului/Desktop/si201/fall25-project1-kiului/penguins.csv"
    #the comment above is hardcoded, since simple doing csv_path= 'penguins.csv' did not work for me, but to avoid hardcoding i used an input function instead so instructors can also run the code
    csv_path = input("Enter the full path to your penguins.csv file: ").strip()


    rows = load_penguins(csv_path)
    clean = filter_valid_rows(rows)

    avg = calc_avg_mass_by_species_sex(clean)
    heavy = calc_heaviest_species_per_island(clean)

    write_avg_mass_csv(avg, "results_avg_mass.csv")
    write_heaviest_csv(heavy, "results_heaviest.csv")
    write_summary_txt(avg, heavy, "results_summary.txt")

    print("Done! Files written and tests passed.")

if __name__ == "__main__":
    main()




