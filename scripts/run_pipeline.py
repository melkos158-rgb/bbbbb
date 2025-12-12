from __future__ import annotations

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

# Allow imports from src/ when running as a script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config import RAW_PATH, PROCESSED_PATH  # noqa: E402
from src.utils import check_columns, basic_clean, quick_report  # noqa: E402


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def save_fig(path: str) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()


def main() -> None:
    print("=== Warsaw Rent Pipeline ===")
    print("RAW:", RAW_PATH)
    print("PROCESSED:", PROCESSED_PATH)

    # folders for outputs
    ensure_dir("figures")
    ensure_dir(os.path.dirname(PROCESSED_PATH) or "data/processed")

    # 1) load
    if not os.path.exists(RAW_PATH):
        raise FileNotFoundError(
            f"Raw dataset not found: {RAW_PATH}\n"
            f"Put your CSV file here: data/raw/rents.csv"
        )

    df = pd.read_csv(RAW_PATH)
    print("Loaded rows:", len(df))

    # 2) validate + clean
    check_columns(df)
    df = basic_clean(df)
    print("After clean:", quick_report(df))

    # 3) save processed
    df.to_csv(PROCESSED_PATH, index=False)
    print("Saved processed:", PROCESSED_PATH)

    # 4) quick charts
    # Price histogram
    plt.figure()
    df["price_pln"].hist(bins=30)
    plt.title("Price distribution (PLN)")
    plt.xlabel("price_pln")
    plt.ylabel("count")
    save_fig("figures/price_distribution.png")
    print("Saved: figures/price_distribution.png")

    # Area vs price scatter
    plt.figure()
    plt.scatter(df["area_m2"], df["price_pln"])
    plt.title("Area (m²) vs Price (PLN)")
    plt.xlabel("area_m2")
    plt.ylabel("price_pln")
    save_fig("figures/area_vs_price.png")
    print("Saved: figures/area_vs_price.png")

    # Avg price by district (top 15)
    top = (
        df.groupby("district")["price_pln"]
        .mean()
        .sort_values(ascending=False)
        .head(15)
        .sort_values()
    )

    plt.figure()
    top.plot(kind="barh")
    plt.title("Average price by district (Top 15)")
    plt.xlabel("avg price (PLN)")
    plt.ylabel("district")
    save_fig("figures/avg_price_by_district_top15.png")
    print("Saved: figures/avg_price_by_district_top15.png")

    print("✅ Done.")


if __name__ == "__main__":
    main()
