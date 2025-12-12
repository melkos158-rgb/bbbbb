from pathlib import Path

# Project root directory
BASE_DIR = Path(__file__).resolve().parents[1]

# Data paths
RAW_PATH = BASE_DIR / "data" / "raw" / "rents.csv"
PROCESSED_PATH = BASE_DIR / "data" / "processed" / "rents_processed.csv"
