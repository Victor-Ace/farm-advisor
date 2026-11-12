"""
Farm Implement Advisor
----------------------
Tells a farmer which implement to use for a job, based on simple things
that are easy to know without measuring: the job, how wet the soil is,
the soil type, the crop, and the tractor size (horsepower).

Run it:      python farm_implement_advisor.py
Quick demo:  python farm_implement_advisor.py --demo

Use it inside another program:
    from farm_implement_advisor import recommend
    result = recommend("ridging", "moist", "loam", 60)
    print(result["implement"])
"""

import sys
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# 1. The choices the farmer can pick from
# ---------------------------------------------------------------------------

OPERATIONS = {
    "ploughing": "Ploughing (first breaking of the land)",
    "harrowing": "Harrowing (breaking clods, making soil fine)",
    "ridging": "Ridging / making beds or bunds",
    "cultivating": "Cultivating (weeding between rows)",
    "planting": "Planting / sowing",
    "harvesting": "Harvesting",
}

SOIL_CONDITIONS = {
    "dry": "Dry - dusty or hard, cracks on top, does not stick to boots",
    "moist": "In-between - squeeze a handful, it forms a ball that breaks easily",
    "muddy": "Muddy - sticky, water shows when squeezed, boots sink in",
}

SOIL_TYPES = {
    "sandy": "Sandy - loose, feels gritty, does not hold together",
    "loam": "Loam - soft, crumbly, not too sticky (most farm soils)",
    "clay": "Clay - heavy and sticky when wet, very hard when dry",
}

CROPS = {
    "rowcrop": "Row crops - maize, beans, soybean, sorghum, groundnut",
    "smallgrain": "Small grains - wheat, millet, barley",
    "rice": "Rice",
    "roots": "Roots and tubers - cassava, yam, potato",
    "forage": "Grass or fodder crops",
}

DRIVES = {
    "2wd": "2WD - power only on the back wheels",
    "4wd": "4WD - power on all four wheels",
}

# If the farmer does not know the horsepower, they can pick a size.
SIZE_TO_HP = {"s": 30, "m": 55, "l": 90, "x": 130}


# ---------------------------------------------------------------------------
# 2. The list of implements and when each one works best
# ---------------------------------------------------------------------------

@dataclass
class Implement:
    name: str
    conditions: tuple      # soil conditions it works well in
    best_soils: tuple      # soil types it suits best
    hp_min: int            # smallest tractor that can pull it
    hp_max: int            # above this, the tractor is too big for it
    why: str               # one-line reason shown to the farmer
    crops: tuple = ("any",)  # crops it is made for ("any" = all)


ALL_SOILS = ("sandy", "loam", "clay")

CATALOG = {
    "ploughing": [
        Implement("Disc plough", ("dry",), ("clay", "loam"), 45, 120,
                  "Cuts through hard, dry ground and handles stones and old crop trash."),
        Implement("Chisel plough", ("dry", "moist"), ("clay", "loam"), 60, 150,
                  "Breaks hard ground deep without turning it over; saves fuel and moisture."),
        Implement("Mouldboard plough", ("moist",), ("loam", "clay"), 35, 100,
                  "Turns the soil over cleanly when it is damp, and buries weeds."),
        Implement("Rotary tiller (rotavator)", ("dry", "moist"), ("sandy", "loam"), 35, 90,
                  "Chops and mixes loose soil in one pass, leaving a fine bed."),
        Implement("Rotary puddler", ("muddy",), ALL_SOILS, 30, 100,
                  "Made for wet land; mixes the mud into a smooth paste, good for rice."),
    ],
    "harrowing": [
        Implement("Disc harrow", ("dry", "moist"), ("clay", "loam"), 45, 130,
                  "Breaks hard clods and cuts through crop leftovers."),
        Implement("Spike-tooth harrow", ("dry", "moist"), ("sandy", "loam"), 20, 60,
                  "Light and cheap; good for loose soil and small tractors."),
        Implement("Power harrow", ("moist",), ALL_SOILS, 65, 150,
                  "Gives a very fine seedbed in one pass when the soil is damp."),
        Implement("Levelling board (planker)", ("muddy",), ALL_SOILS, 25, 90,
                  "Drags wet soil flat and even after puddling."),
    ],
    "ridging": [
        Implement("Disc ridger (hiller)", ("dry", "moist"), ("clay", "loam"), 35, 90,
                  "Throws up firm ridges even in hard or heavy soil."),
        Implement("Mouldboard ridger", ("moist",), ("sandy", "loam"), 30, 80,
                  "Builds neat ridges in soft, damp soil."),
        Implement("Rotary ridger / bed former", ("moist", "dry"), ("sandy", "loam"), 55, 120,
                  "Mixes and shapes loose soil into raised beds in one pass."),
        Implement("Bund former", ("muddy",), ALL_SOILS, 25, 80,
                  "Makes mud walls (bunds) to hold water in wet fields."),
    ],
    "cultivating": [
        Implement("Tine row cultivator", ("dry", "moist"), ("clay", "loam"), 35, 90,
                  "Pulls up weeds between rows and loosens the crust."),
        Implement("Rotary inter-row cultivator", ("dry", "moist"), ("sandy", "loam"), 20, 60,
                  "Light weeding between rows; works well on soft soil."),
    ],
    "planting": [
        Implement("Row planter (maize/bean planter)", ("dry", "moist"), ALL_SOILS, 35, 100,
                  "Drops seeds at an even spacing in rows.", crops=("rowcrop",)),
        Implement("Seed drill", ("dry", "moist"), ("sandy", "loam"), 45, 110,
                  "Sows small seeds in tight, even lines.", crops=("smallgrain", "forage")),
        Implement("Root and tuber planter", ("dry", "moist"), ("sandy", "loam"), 45, 100,
                  "Plants cassava stems or potato seed pieces at set spacing.", crops=("roots",)),
        Implement("Rice transplanter", ("muddy",), ALL_SOILS, 0, 999,
                  "Plants rice seedlings in puddled mud; it has its own engine.", crops=("rice",)),
        Implement("Seed drill (rice direct sowing)", ("dry", "moist"), ALL_SOILS, 45, 110,
                  "Sows rice seed straight into dry or damp land.", crops=("rice",)),
    ],
    "harvesting": [
        Implement("Combine harvester", ("dry", "moist"), ALL_SOILS, 90, 300,
                  "Cuts, threshes and cleans grain in one pass.",
                  crops=("rowcrop", "smallgrain", "rice")),
        Implement("Tracked combine harvester", ("muddy",), ALL_SOILS, 70, 300,
                  "Rubber tracks stop it sinking in wet fields.",
                  crops=("rice", "smallgrain", "rowcrop")),
        Implement("Reaper / reaper-binder", ("dry", "moist"), ALL_SOILS, 20, 89,
                  "Cuts and ties grain stalks; suits medium tractors.",
                  crops=("smallgrain", "rice", "rowcrop")),
        Implement("Walk-behind power reaper", ("muddy", "dry", "moist"), ALL_SOILS, 0, 999,
                  "Small self-powered cutter; light enough for soft ground.",
                  crops=("rice", "smallgrain")),
        Implement("Root and tuber digger (lifter)", ("dry", "moist"), ("sandy", "loam"), 40, 120,
                  "Lifts cassava, yam or potato out of the ground without damage.",
                  crops=("roots",)),
        Implement("Mower (disc or drum)", ("dry", "moist"), ALL_SOILS, 30, 99,
                  "Cuts grass and fodder for hay.", crops=("forage",)),
        Implement("Forage harvester", ("dry", "moist"), ALL_SOILS, 100, 300,
                  "Cuts and chops fodder in one pass for silage.", crops=("forage",)),
    ],
}

# Which questions each job needs answered
NEEDS_CROP = {"planting", "harvesting"}


# ---------------------------------------------------------------------------
# 3. The decision logic
# ---------------------------------------------------------------------------

def _score(item, soil, hp):
    """Higher score = better match. Easy to read and easy to change."""
    score = 3                                   # it already matches the soil condition
    if soil in item.best_soils:
        score += 2                              # it suits this soil type
    if hp >= item.hp_min + 15:
        score += 1                              # tractor has comfortable power
    if hp > item.hp_max:
        score -= 2                              # tractor is much bigger than needed
    return score


def recommend(operation, condition, soil, hp, crop=None, drive="4wd"):
    """Return the best implement for the situation.

    Returns a dict with: implement, why, alternative, warnings.
    """
    warnings = []
    pool = CATALOG[operation]

    # Step 1: keep only implements made for this crop
    if operation in NEEDS_CROP and crop:
        pool = [i for i in pool if "any" in i.crops or crop in i.crops]

    # Step 2: keep only implements that work in this soil condition
    by_condition = [i for i in pool if condition in i.conditions]
    if not by_condition:
        by_condition = pool
        warnings.append(
            "The soil is too " + ("wet" if condition == "muddy" else condition)
            + " for this job. If you can, wait a few days for better soil."
        )

    # Step 3: keep only implements the tractor can pull
    by_power = [i for i in by_condition if hp >= i.hp_min]
    if not by_power:
        by_power = sorted(by_condition, key=lambda i: i.hp_min)
        warnings.append(
            "Your tractor is smaller than recommended for this job. "
            "Hire a bigger tractor or use a smaller version of the implement."
        )

    # Step 4: score what is left and pick the best (ties keep list order)
    ranked = sorted(by_power, key=lambda i: -_score(i, soil, hp))
    best = ranked[0]
    alternative = ranked[1].name if len(ranked) > 1 else None

    # Extra advice
    if condition == "muddy" and drive == "2wd":
        warnings.append("A 2WD tractor can get stuck in mud. Use cage wheels or add weight.")
    if hp > best.hp_max and best.hp_max < 999:
        warnings.append("Your tractor is bigger than needed for this implement. "
                        "A larger implement would save time.")

    return {
        "implement": best.name,
        "why": best.why,
        "alternative": alternative,
        "warnings": warnings,
    }


# ---------------------------------------------------------------------------
# 4. The screen the farmer sees
# ---------------------------------------------------------------------------

def ask_choice(title, options):
    print("\n" + title)
    keys = list(options)
    for n, key in enumerate(keys, 1):
        print(f"  {n}. {options[key]}")
    while True:
        raw = input("Type a number: ").strip().lower()
        if raw.isdigit() and 1 <= int(raw) <= len(keys):
            return keys[int(raw) - 1]
        if raw in keys:
            return raw
        print("Please type one of the numbers shown.")


def ask_horsepower():
    print("\nHow strong is your tractor?")
    print("  Type the horsepower (HP) if you know it, for example 60.")
    print("  If you do not know, type a letter:")
    print("    s = small (under 40 HP)    m = medium (40 to 75 HP)")
    print("    l = large (75 to 110 HP)   x = very large (over 110 HP)")
    while True:
        raw = input("HP or letter: ").strip().lower()
        if raw in SIZE_TO_HP:
            return SIZE_TO_HP[raw]
        try:
            value = float(raw)
            if 5 <= value <= 500:
                return value
        except ValueError:
            pass
        print("Please type a number like 60, or s / m / l / x.")


def show_result(result):
    print("\n" + "=" * 50)
    print("USE THIS:  " + result["implement"].upper())
    print("=" * 50)
    print("Why: " + result["why"])
    if result["alternative"]:
        print("Second choice: " + result["alternative"])
    for note in result["warnings"]:
        print("Note: " + note)


def main():
    print("FARM IMPLEMENT ADVISOR")
    print("Answer a few easy questions and get the right implement.")
    while True:
        op = ask_choice("What job do you want to do?", OPERATIONS)
        condition = ask_choice("How is the soil right now?", SOIL_CONDITIONS)
        soil = ask_choice("What type of soil is it?", SOIL_TYPES)
        crop = ask_choice("Which crop?", CROPS) if op in NEEDS_CROP else None
        hp = ask_horsepower()
        drive = ask_choice("Does the tractor drive all four wheels?", DRIVES)

        show_result(recommend(op, condition, soil, hp, crop, drive))

        again = input("\nCheck another job? (y/n): ").strip().lower()
        if again != "y":
            print("Good luck with the farm work!")
            break


# ---------------------------------------------------------------------------
# 5. Sample cases (run with --demo)
# ---------------------------------------------------------------------------

DEMO_CASES = [
    ("ploughing", "dry", "clay", 75, None, "4wd"),
    ("ploughing", "moist", "loam", 50, None, "4wd"),
    ("ploughing", "muddy", "clay", 45, None, "2wd"),
    ("harrowing", "dry", "sandy", 25, None, "2wd"),
    ("ridging", "moist", "sandy", 40, None, "2wd"),
    ("ridging", "dry", "clay", 70, None, "4wd"),
    ("cultivating", "moist", "loam", 30, None, "2wd"),
    ("planting", "moist", "loam", 55, "rowcrop", "4wd"),
    ("planting", "muddy", "clay", 50, "rice", "4wd"),
    ("harvesting", "dry", "loam", 130, "rowcrop", "4wd"),
    ("harvesting", "dry", "sandy", 55, "roots", "2wd"),
    ("harvesting", "muddy", "clay", 90, "rice", "4wd"),
    ("harvesting", "muddy", "loam", 55, "roots", "2wd"),
    ("harvesting", "dry", "loam", 30, "smallgrain", "2wd"),
]


def run_demo():
    for op, cond, soil, hp, crop, drive in DEMO_CASES:
        r = recommend(op, cond, soil, hp, crop, drive)
        crop_text = f", crop={crop}" if crop else ""
        print(f"{op}, {cond}, {soil}, {hp} HP, {drive}{crop_text}")
        print(f"   -> {r['implement']}")
        for note in r["warnings"]:
            print(f"      Note: {note}")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        run_demo()
    else:
        try:
            main()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
