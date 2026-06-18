"""
anchors.py — Ordered anchor-pattern classifiers for week1.py

Each list is ordered most-specific first so the first match wins.
Edit this file to tune subcategory rules; week1.py imports everything from here.
"""

import re

# =============================================================================
# Plumbing subcategory anchors — problem type first, bare fixture last
# =============================================================================
PLUMBING_ANCHORS = [
    ("Sewer/Backup",
     r"sewer|sewage|basement back|back ?up in basement|toilet bowl back"),
    ("Clog/Drain",
     # added: back ?up / backed ?up / backin\.? ?up
     r"clog|cloog|cloged|overflow|backing up|backup|back ?up|backed ?up"
     r"|backin\.? ?up|\bdrain\b|not flushing|stoppage|snake"),
    ("Leak",
     # added: \blesk\b (misspelling)
     r"leak|leek|drip|water damage|leaky|\blesk\b"),
    ("Hot Water/Supply",
     r"hot water|no water|water heater|expansion tank|storage tank"
     r"|water booster|domestic|no heat|hw supply"),
    ("Toilet Internal Parts",
     # added: running water|water running — running-toilet descriptions;
     # Leak sits above and catches genuine "water running down the wall" phrases
     # that also contain leak/drip keywords before reaching this rule.
     r"flapper|wax ?ring|waxring|waxing|fill ?valve|fluid ?master|fluidmaster"
     r"|fluid-master|fludmaster|fluidvalve|\bfloat\b|flushmate|toilet tank"
     r"|speedy valve|tip ?toe|toilet.*running|running.*toilet|toilet.*pump"
     r"|running water|water running"
     r"|screws? (?:in|inside).*tank|supply line.*tank|tank.*supply line"
     r"|washes.*tank"),
    ("Faucet/Fixture Hardware",
     # added: back ?flow (widens "backflow" → "Back Flow Preventer")
     r"faucet|shower ?head|shower ?body|cartridge|shower handle|water handle"
     r"|water stopper|strainer|sump pump|backflow|back ?flow|grab bar|soap dish"
     r"|diverter|spout|push ?pop|pop ?up|\bknob\b|\bhandle\b|seat"),
    # NEW — heat/steam risers; intercepts before Valve/Pressure
    ("Heating-Adjacent (Review)",
     r"heat riser|heat valve|\briser\b|steam"),
    # NEW — valve mechanisms, pumps, pressure issues
    ("Valve/Pressure",
     r"\bvalve\b|\bvlave\b|\bpump\b|pressure|water main|water cut"
     r"|\bmeter\b|flushometer|flushometor"),
    ("Pipe Repair",
     r"\bpipe\b|pipes|waste ?bend|waste ?line|wasteline|waist been|weastben"),
    ("Caulking/Sealing",
     # added: chaulk, cualking (phonetic misspellings)
     r"caulk|calk|chaulk|cualking|cork|\bseal\b|mold|mildew"),
    # NEW — administrative/regulatory driver
    ("Violation-Driven",
     r"violation|\bhpd\b|court order|section 8|abate"),
    ("Plumbing Inspection",  r"inspection"),
    ("Toilet (General)",     r"toilet|toliet"),
    ("Bathtub (General)",    r"bathtub|bath tub|\btub\b"),
    ("Kitchen Sink (General)",  r"kitchen sink|kitchen"),
    ("Bathroom Sink (General)", r"bathroom sink|\blav\b"),
    ("Bathroom (General)",   r"bathroom|bath ?room|shower"),
    ("Basement (General)",   r"basement"),
]

# =============================================================================
# Extermination subcategory anchors
# =============================================================================
EXTERMINATION_ANCHORS = [
    ("Bedbugs",
     # widened: bed ?bugs? → bed ?bu[gd]s?; bedbgs → bedb[gu]+s
     r"bed ?bu[gd]s?|bedb[gu]+s|begs bugs|bed  bug"),
    ("Rodents",
     r"\bmice\b|\bmouse\b|mices|\brat\b|\brats\b|rodent|raccoon|racoon"),
    ("Roaches",
     r"roach|roahes|roches"),
    ("Other Pest",
     r"\bant\b|\bants\b|termite|maggot|moth|hornet|\bfly\b|flies|flying"
     r"|\bnats\b|gnat|worm|wasp|fungus"),
    ("Violation-Driven",
     # added: \bdoh\b (Dept of Health)
     r"violation|\bhpd\b|\bdoh\b|court order|abate|nycha"),
    ("General/Unspecified",
     # added: infectation|infections? (misspellings of "infestation")
     r"exterminat|exermination|extermaination|\bpest\b|infestation|infested"
     r"|infectation|infections?\b|sanitiz|spray|treat|\bhole"),
]

# =============================================================================
# Tier-1 category anchors — used to infer category for blank rows (Step 4)
# =============================================================================
TIER1_ANCHORS = [
    ("Extermination",
     r"bed ?bug|bedbgs|\bmice\b|\bmouse\b|\brat\b|\brats\b|rodent|raccoon"
     r"|roach|roahes|exterminat|\bpest\b|infestation|infested|termite|maggot"),
    ("Elevator",      r"elevator|\blift\b"),
    ("Compactor",     r"compactor"),
    ("Boiler",        r"boiler"),
    ("Heating",       r"\bheat\b|radiator|thermostat|steam"),
    ("Fire Safety",
     r"smoke (?:detector|alarm)|fire (?:extinguish|alarm|safety)|co2"
     r"|carbon monoxide|sprinkler|standpipe|fdny|local law|self.?clos"
     r"|smoke alarm|smoke detector"),
    ("Plumbing",
     r"clog|cloog|leak|leek|toilet|toliet|faucet|sink|bathtub|\btub\b"
     r"|sewer|sewage|caulk|calk|flapper|wax ?ring|shower|\bpipe\b|\bdrain\b"
     r"|fluid ?master|fill ?valve|speedy valve|hot water|water heater|plumb|drip"),
    ("Electrical",
     r"electric|outlet|wiring|breaker|circuit|gfci|\bwire\b|sparking"),
    ("Lighting",
     r"\blight\b|lights|bulb|ballast|fluorescent|lamp"),
    ("Appliances",
     r"refrigerator|fridge|stove|oven|range|dishwasher|microwave|washer"
     r"|dryer|\bac\b|air condition|appliance|freezer"),
    ("Doors and Locks",
     r"\bdoor\b|\block\b|lockset|deadbolt|hinge|cylinder|\bkey\b|peephole"
     r"|intercom|closer"),
    ("Windows",
     r"window|\bsash\b|\bpane\b|glass|screen|\bguard\b|blind|shade"),
    ("Flooring",
     r"floor|tile|linoleum|vinyl|carpet|parquet|grout"),
    ("Painting and Plastering",
     r"paint|plaster|spackle|skim coat|sheetrock|drywall"),
    ("Carpentry",
     r"cabinet|counter|closet|shelf|shelv|molding|baseboard|trim|carpentr"
     r"|drawer|vanity|medicine cabinet"),
    ("Roofing",       r"roof|gutter|skylight|parapet"),
    ("HVAC",
     r"hvac|ventilation|exhaust fan|\bvent\b|air handler|condenser|make up air"),
    ("Landscaping",
     r"landscap|tree|shrub|garden|lawn|hedge|weed|grass|backyard|back yard"),
    ("Site Work",
     r"sidewalk|pavement|concrete|asphalt|\bfence\b|\bgate\b|curb|powerwash"),
    ("Security",
     r"security|camera|cctv|surveillance|alarm system"),
    ("Apt. Prep.",
     r"apartment prep|apt prep|vacant|make ready|turnover|paint vacant"),
]

# Compile all patterns dynamically at import time for optimal performance
PLUMBING_ANCHORS = [(label, re.compile(pat)) for label, pat in PLUMBING_ANCHORS]
EXTERMINATION_ANCHORS = [(label, re.compile(pat)) for label, pat in EXTERMINATION_ANCHORS]
TIER1_ANCHORS = [(label, re.compile(pat)) for label, pat in TIER1_ANCHORS]

# Convenience map used by week1.py classify() calls
ANCHOR_MAP = {"Plumbing": PLUMBING_ANCHORS, "Extermination": EXTERMINATION_ANCHORS}

# Matches descriptions that are just an address with no work detail
ADDRESS_ONLY_RE = re.compile(r"^\d{2,4}")

