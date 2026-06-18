"""
week1.py — RiseBoro Yardi work-order ETL pipeline

Steps executed in sequence:
  1. Load + normalize three raw Yardi xlsx exports into a single combined dataset
  2. Canonicalize category labels (collapse near-duplicate strings)
  3. Subcategorize Plumbing & Extermination rows with ordered anchor classifiers
  4. Infer tier-1 category for originally-blank rows; subcategorize if applicable
   5. Merge all enrichment into one final analytic dataset
  6. Write subcategory distribution summaries & export to a single Excel file

Outputs
  work_orders_enriched_final.xlsx   — Excel workbook with sheets: Enriched Work Orders, Plumbing Subcategories, and Extermination Subcategories

Anchor patterns live in anchors.py — edit them there to tune subcategory rules.
"""

import os
import re

import pandas as pd

from anchors import ANCHOR_MAP, ADDRESS_ONLY_RE, TIER1_ANCHORS

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCEL_DIR = os.path.join(BASE_DIR, "data", "raw")

OUTPUT_EXCEL = os.path.join(BASE_DIR, "data", "processed", "work_orders_enriched_final.xlsx")

STANDARD_COLS = [
    "wo_number", "prop_unit", "status", "category", "brief_desc",
    "tenant", "call_date", "schedule_date", "complete_date", "vendor", "amount",
]

CATEGORY_CANONICAL = {
    "Inspections":   "Inspection",
    "Exterminating": "Extermination",
}


# =============================================================================
# Classification helpers
# =============================================================================

def classify(desc, anchors):
    """Return (subcat_primary, subcat_secondary). First anchor match = primary."""
    if pd.isna(desc) or str(desc).strip() == "":
        return "Blank/No Desc", ""
    norm = str(desc).strip().lower()
    matched = []
    for label, pattern in anchors:
        if pattern.search(norm) and label not in matched:
            matched.append(label)
    if matched:
        return matched[0], "; ".join(matched[1:])
    if ADDRESS_ONLY_RE.match(norm):
        return "Address-Only (No Work Desc)", ""
    return "Other", ""


def infer_tier1(desc):
    """Infer tier-1 category for a blank-category row."""
    if pd.isna(desc) or str(desc).strip() == "":
        return "Blank/No Desc"
    norm = str(desc).strip().lower()
    for label, pattern in TIER1_ANCHORS:
        if pattern.search(norm):
            return label
    if ADDRESS_ONLY_RE.match(norm):
        return "Address-Only"
    return "Uncategorized"



def _subcat_report(subset, cat, threshold):
    """Print a subcategory breakdown and flag if Other% exceeds threshold."""
    n = len(subset)
    counts = subset["subcat_primary"].value_counts()
    print(f"  {cat.upper()} — {n:,} rows")
    print(f"  {'Subcategory':<30} {'N':>6}  {'%':>5}")
    print(f"  {'-'*44}")
    for label, cnt in counts.items():
        print(f"  {label:<30} {cnt:>6,}  {cnt/n*100:>4.1f}%")
    other_pct = counts.get("Other", 0) / n * 100
    if other_pct > threshold:
        print(f"\n  *** FLAG: Other = {other_pct:.1f}% > {threshold}% threshold ***")
        unmatched = (subset[subset["subcat_primary"] == "Other"]["brief_desc"]
                     .dropna().unique())
        print(f"  Unmatched descs ({len(unmatched)}):")
        for d in sorted(unmatched, key=str.lower):
            print(f"    {repr(d)}")
    sec_n = (subset["subcat_secondary"].notna() & (subset["subcat_secondary"] != "")).sum()
    print(f"\n  Rows with subcat_secondary: {sec_n:,}  ({sec_n/n*100:.1f}%)\n")





# =============================================================================
# Loader helpers
# =============================================================================

def load_work_order_directory(path):
    """2-row header; drops the pre-calculated days col at index 9."""
    df = pd.read_excel(path, header=None, skiprows=2)
    df = df.dropna(subset=[0])
    df = df.drop(columns=[9])
    df.columns = STANDARD_COLS
    return df


def load_yardi_file(path):
    """7-row Yardi header block, 11 cols, data starts at row 7."""
    df = pd.read_excel(path, header=None, skiprows=7)
    df = df.dropna(subset=[0])
    df.columns = STANDARD_COLS
    return df


# =============================================================================
# STEP 1 — Load + normalize
# =============================================================================

wod = load_work_order_directory(
    os.path.join(EXCEL_DIR, "WorkOrderDirectory06_01_2026.xlsx")
)
gp = load_yardi_file(os.path.join(EXCEL_DIR, "Gates Plaza (1245 Gates Avenue).xlsx"))
wb = load_yardi_file(os.path.join(EXCEL_DIR, "wb203k.xlsx"))

combined = pd.concat([wod, gp, wb], ignore_index=True)
_EXPECTED_ROWS = len(combined)

combined["source_property"] = (
    combined["prop_unit"].astype(str).str.split("-").str[0]
)
for col in ("call_date", "complete_date"):
    combined[col] = pd.to_datetime(combined[col], errors="coerce")
combined["wo_number"] = (
    pd.to_numeric(combined["wo_number"], errors="coerce").astype("Int64")
)
combined = combined[[
    "source_property", "wo_number", "prop_unit", "status", "category",
    "brief_desc", "tenant", "call_date", "complete_date",
    "vendor",
]]

print("=" * 64)
print("  STEP 1 — Load & normalize")
print("=" * 64)
print(f"  Rows: {len(combined):,}   Columns: {combined.shape[1]}")
for prop, n in combined["source_property"].value_counts().items():
    print(f"    {prop:<12} {n:>6,}")
print()


# =============================================================================
# STEP 2 — Canonicalize category labels
# =============================================================================

combined["category"] = combined["category"].replace(CATEGORY_CANONICAL)

print("=" * 64)
print("  STEP 2 — Canonicalize categories")
print("=" * 64)
for variant, canonical in CATEGORY_CANONICAL.items():
    print(f"  '{variant}' → '{canonical}'")
print()


# =============================================================================
# STEP 3 — Subcategorize Plumbing & Extermination
# =============================================================================

target = combined[combined["category"].isin(["Plumbing", "Extermination"])].copy()

# Optimization: Avoid row-by-row apply overhead with a list comprehension
results = [
    classify(desc, ANCHOR_MAP[cat])
    for desc, cat in zip(target["brief_desc"], target["category"])
]
target["subcat_primary"] = [r[0] for r in results]
target["subcat_secondary"] = [r[1] for r in results]

print("=" * 64)
print("  STEP 3 — Subcategorize Plumbing & Extermination")
print("=" * 64)
for cat, threshold in [("Plumbing", 6.0), ("Extermination", 4.0)]:
    _subcat_report(target[target["category"] == cat], cat, threshold)


# =============================================================================
# STEP 4 — Infer categories for blank rows; subcategorize if applicable
# =============================================================================

no_cat = combined[combined["category"].isna()].copy()
no_cat["category_inferred"] = no_cat["brief_desc"].apply(infer_tier1)
no_cat["inference_source"]  = "inferred_from_desc"

# Optimization: Avoid row-by-row apply overhead with a list comprehension
inferred_subcats = []
for desc, cat in zip(no_cat["brief_desc"], no_cat["category_inferred"]):
    if cat in ANCHOR_MAP:
        inferred_subcats.append(classify(desc, ANCHOR_MAP[cat]))
    else:
        inferred_subcats.append((pd.NA, pd.NA))

no_cat["subcat_primary"]   = [r[0] for r in inferred_subcats]
no_cat["subcat_secondary"] = [r[1] for r in inferred_subcats]

print("=" * 64)
print("  STEP 4 — Infer categories for blank rows")
print("=" * 64)
_nc_total  = len(no_cat)
inf_counts = no_cat["category_inferred"].value_counts(dropna=False)
print(f"  Total no-category rows: {_nc_total:,}\n")
print(f"  {'category_inferred':<30} {'N':>6}  {'%':>5}")
print(f"  {'-'*44}")
for label, n in inf_counts.items():
    print(f"  {label:<30} {n:>6,}  {n/_nc_total*100:>4.1f}%")
print()


# =============================================================================
# STEP 5 — Merge all enrichment into one final analytic dataset
# =============================================================================

combined["subcat_primary"]    = pd.NA
combined["subcat_secondary"]  = pd.NA

# Step 3 subcategories (Plumbing / Extermination rows — indices preserved)
combined.loc[target.index, "subcat_primary"]   = target["subcat_primary"]
combined.loc[target.index, "subcat_secondary"] = target["subcat_secondary"]

# Step 4 enrichment (originally-NaN rows — indices preserved, no overlap with above)
combined.loc[no_cat.index, "subcat_primary"]    = no_cat["subcat_primary"]
combined.loc[no_cat.index, "subcat_secondary"]  = no_cat["subcat_secondary"]

# category_final: use original category where present, else inferred
combined["category_final"] = combined["category"].where(
    combined["category"].notna(), no_cat["category_inferred"]
)

assert len(combined) == _EXPECTED_ROWS, (
    f"Row count mismatch after merge: {len(combined):,} ≠ {_EXPECTED_ROWS:,}"
)


# =============================================================================
# STEP 6 — Subcategory distribution summaries & single Excel export
# =============================================================================

plumb  = combined[combined["category_final"] == "Plumbing"].copy()
exterm = combined[combined["category_final"] == "Extermination"].copy()

print("=" * 64)
print("  STEP 6 — Subcategory distribution & Excel export")
print("=" * 64)

# Create tables
plumb_tbl = plumb["subcat_primary"].value_counts(dropna=False).reset_index()
plumb_tbl.columns = ["subcat_primary", "count"]
plumb_tbl["pct_of_category"] = (plumb_tbl["count"] / len(plumb) * 100).round(1)

exterm_tbl = exterm["subcat_primary"].value_counts(dropna=False).reset_index()
exterm_tbl.columns = ["subcat_primary", "count"]
exterm_tbl["pct_of_category"] = (exterm_tbl["count"] / len(exterm) * 100).round(1)

# Print distribution to terminal
for tbl, cat_name in [(plumb_tbl, "Plumbing"), (exterm_tbl, "Extermination")]:
    n_total = len(plumb) if cat_name == "Plumbing" else len(exterm)
    print(f"\n  {cat_name.upper()} (n={n_total:,})")
    print(f"  {'Subcategory':<30} {'N':>6}  {'%':>5}")
    print(f"  {'-'*44}")
    for _, row in tbl.iterrows():
        print(f"  {str(row.subcat_primary):<30} {row['count']:>6,}  {row.pct_of_category:>4.1f}%")

# Save all sheets into a single Excel file
with pd.ExcelWriter(OUTPUT_EXCEL, engine="openpyxl") as writer:
    combined.to_excel(writer, sheet_name="Enriched Work Orders", index=False)
    plumb_tbl.to_excel(writer, sheet_name="Plumbing Subcategories", index=False)
    exterm_tbl.to_excel(writer, sheet_name="Extermination Subcategories", index=False)

print()
print(f"  Wrote single Excel file to {OUTPUT_EXCEL} with sheets:")
print(f"    - Enriched Work Orders")
print(f"    - Plumbing Subcategories")
print(f"    - Extermination Subcategories")
print()
