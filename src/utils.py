from __future__ import annotations

import re
import pandas as pd

REQUIRED_COLS = ["price_pln", "district", "area_m2", "rooms"]


def check_columns(df: pd.DataFrame) -> None:
    """Raise clear error if required columns are missing."""
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(
            f"Missing columns: {missing}. Found columns: {list(df.columns)}\n"
            f"Expected at least: {REQUIRED_COLS}"
        )


def _clean_text(x: object) -> str:
    """Normalize text fields: strip, collapse spaces, lowercase."""
    if pd.isna(x):
        return ""
    s = str(x).strip()
    s = re.sub(r"\s+", " ", s)
    return s


def normalize_district(series: pd.Series) -> pd.Series:
    """
    Standardize district names:
    - strip
    - collapse spaces
    - title-case (Warszawa Śródmieście style)
    """
    s = series.astype(str).map(_clean_text)
    s = s.str.replace("-", " ", regex=False)
    s = s.str.replace("_", " ", regex=False)
    s = s.str.strip()
    # Title case but keep Polish characters OK
    s = s.str.title()
    return s


def to_numeric(series: pd.Series) -> pd.Series:
    """Convert messy numeric strings to float: '3 500', '3500 PLN', '3,5' etc."""
    s = series.astype(str).map(_clean_text)

    # keep digits, dot, comma
    s = s.str.replace(r"[^0-9\.,]", "", regex=True)

    # handle comma decimals: 3,5 -> 3.5
    s = s.str.replace(",", ".", regex=False)

    # remove extra dots (rare), keep first
    s = s.str.replace(r"(\..*)\.", r"\1", regex=True)

    return pd.to_numeric(s, errors="coerce")


def basic_clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean dataset to a consistent, analysis-ready format.
    Adds:
    - price_per_m2
    """
    df = df.copy()

    # keep only required columns (+ keep other columns if present)
    check_columns(df)

    # normalize
    df["district"] = normalize_district(df["district"])
    df["price_pln"] = to_numeric(df["price_pln"])
    df["area_m2"] = to_numeric(df["area_m2"])
    df["rooms"] = to_numeric(df["rooms"])

    # drop missing core fields
    df = df.dropna(subset=["price_pln", "district", "area_m2", "rooms"])

    # sanity filters
    df = df[df["price_pln"] > 0]
    df = df[df["area_m2"] > 0]
    df = df[df["rooms"] > 0]

    # optional: remove extreme outliers (safe defaults)
    # You can tweak these later based on the dataset distribution.
    df = df[df["price_pln"].between(500, 30000)]
    df = df[df["area_m2"].between(10, 300)]
    df = df[df["rooms"].between(1, 10)]

    # derived feature
    df["price_per_m2"] = df["price_pln"] / df["area_m2"]

    # clean district empty strings
    df = df[df["district"].str.len() > 0]

    # final ordering: put core columns first
    core = ["price_pln", "area_m2", "rooms", "district", "price_per_m2"]
    rest = [c for c in df.columns if c not in core]
    df = df[core + rest]

    return df


def quick_report(df: pd.DataFrame) -> str:
    """Return a short human-readable summary for logs/README."""
    lines = []
    lines.append(f"rows: {len(df)}")
    lines.append(f"districts: {df['district'].nunique()}")
    lines.append(f"price_pln: min={df['price_pln'].min():.0f}, "
                 f"median={df['price_pln'].median():.0f}, max={df['price_pln'].max():.0f}")
    lines.append(f"area_m2: min={df['area_m2'].min():.0f}, "
                 f"median={df['area_m2'].median():.0f}, max={df['area_m2'].max():.0f}")
    return " | ".join(lines)
