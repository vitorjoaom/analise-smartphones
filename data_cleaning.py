"""
Smartphones Dataset — Data Treatment & Cleaning
================================================
Shared cleaning module used by both analise_smartphones.py (EDA) and
analise_preditiva.py (predictive modeling), so every downstream chart and
model is trained on the exact same validated, deduplicated dataset.

Steps performed (in order):
  1. Load the raw CSV and record its shape.
  2. Normalize text columns (trim whitespace, collapse casing).
  3. Validate dtypes / coerce numeric columns.
  4. Drop exact duplicate rows and duplicate ids.
  5. Sanity-check numeric ranges (price, ram, storage, battery, screen
     size, weight, thickness, refresh rate, release year) and drop rows
     with physically impossible values.
  6. Impute any remaining missing values (median for numeric, mode for
     categorical) — defensive, in case future data isn't as clean as the
     current snapshot.
  7. Flag and cap extreme price outliers (IQR method, 3x multiplier) so a
     handful of extreme values can't distort the regression trendlines.
  8. Save the cleaned dataset to smartphones_clean.csv and a JSON report
     of every change made to outputs/kpis_cleaning.json.
"""

import json
import os

import numpy as np
import pandas as pd

RAW_PATH = "smartphones.csv"
CLEAN_PATH = "smartphones_clean.csv"
REPORT_PATH = os.path.join("outputs", "kpis_cleaning.json")

TEXT_COLUMNS = [
    "brand_name", "model", "operating_system", "body_material", "chipset",
    "gpu", "dual_sim", "network_support", "wifi_version", "usb_type",
    "fingerprint_sensor",
]

NUMERIC_RANGES = {
    "price": (1, None),
    "screen_size": (3.0, 10.0),
    "battery_capacity": (500, 10000),
    "ram": (1, 64),
    "storage": (1, 2048),
    "camera_mp": (1, 300),
    "front_camera_mp": (1, 300),
    "refresh_rate": (30, 300),
    "weight": (50, 500),
    "thickness": (3.0, 20.0),
    "fast_charging": (0, 300),
    "release_year": (2000, 2026),
}


def load_and_clean(raw_path=RAW_PATH, verbose=True):
    report = {}

    df = pd.read_csv(raw_path)
    report["rows_raw"] = int(len(df))
    report["columns_raw"] = int(df.shape[1])

    # ── 2. Normalize text columns ────────────────────────────────────────
    for col in TEXT_COLUMNS:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # ── 3. Validate / coerce dtypes ──────────────────────────────────────
    numeric_cols = list(NUMERIC_RANGES.keys())
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # ── 4. Drop exact duplicate rows and duplicate ids ───────────────────
    dup_rows = int(df.duplicated().sum())
    df = df.drop_duplicates()

    dup_ids = 0
    if "id" in df.columns:
        dup_ids = int(df.duplicated(subset="id").sum())
        df = df.drop_duplicates(subset="id", keep="first")

    report["duplicate_rows_removed"] = dup_rows
    report["duplicate_ids_removed"] = dup_ids

    # ── 5. Sanity-check numeric ranges ───────────────────────────────────
    invalid_mask = pd.Series(False, index=df.index)
    for col, (lo, hi) in NUMERIC_RANGES.items():
        if col not in df.columns:
            continue
        col_mask = df[col].isna()
        if lo is not None:
            col_mask |= df[col] < lo
        if hi is not None:
            col_mask |= df[col] > hi
        invalid_mask |= col_mask

    rows_invalid = int(invalid_mask.sum())
    df = df.loc[~invalid_mask].copy()
    report["rows_dropped_invalid_range"] = rows_invalid

    # ── 6. Impute any remaining missing values ───────────────────────────
    missing_before = df.isna().sum()
    missing_cols = missing_before[missing_before > 0]
    imputed = {}
    for col in missing_cols.index:
        if pd.api.types.is_numeric_dtype(df[col]):
            fill = df[col].median()
        else:
            fill = df[col].mode().iloc[0] if not df[col].mode().empty else "Unknown"
        imputed[col] = {"count": int(missing_cols[col]), "fill_value": str(fill)}
        df[col] = df[col].fillna(fill)
    report["missing_values_imputed"] = imputed

    # ── 7. Flag and cap extreme price outliers (IQR method) ──────────────
    q1, q3 = df["price"].quantile([0.25, 0.75])
    iqr = q3 - q1
    lower, upper = q1 - 3 * iqr, q3 + 3 * iqr
    outlier_mask = (df["price"] < lower) | (df["price"] > upper)
    report["price_outliers_detected"] = int(outlier_mask.sum())
    report["price_outlier_bounds"] = {"lower": round(float(lower), 2), "upper": round(float(upper), 2)}
    df["price"] = df["price"].clip(lower=lower, upper=upper)

    report["rows_clean"] = int(len(df))
    report["columns_clean"] = int(df.shape[1])
    report["rows_removed_total"] = report["rows_raw"] - report["rows_clean"]

    os.makedirs("outputs", exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    df.to_csv(CLEAN_PATH, index=False)

    if verbose:
        print("=" * 60)
        print("DATA TREATMENT & CLEANING")
        print("=" * 60)
        print(f"Raw rows            : {report['rows_raw']:,}")
        print(f"Duplicate rows removed   : {dup_rows}")
        print(f"Duplicate ids removed    : {dup_ids}")
        print(f"Rows dropped (invalid range): {rows_invalid}")
        print(f"Missing values imputed   : {sum(v['count'] for v in imputed.values())}")
        print(f"Price outliers detected/capped (IQR x3): {report['price_outliers_detected']}")
        print(f"Clean rows          : {report['rows_clean']:,}")
        print(f"[Saved] {CLEAN_PATH}")
        print(f"[Saved] {REPORT_PATH}")

    return df


if __name__ == "__main__":
    load_and_clean()
