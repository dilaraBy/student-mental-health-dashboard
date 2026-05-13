"""
Bootstrap script: downloads the Bangladesh GeoJSON used by the
geographic-analysis page, then initialises the SQLite database from
the bundled raw CSV.

Run once after cloning:
    python -m scripts.setup_data
"""

from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.config import DB_PATH, GEOJSON_PATH, RAW_DATA_PATH  # noqa: E402

GEOJSON_URL = (
    "https://raw.githubusercontent.com/strativ-dev/"
    "technical-test-data/main/bangladesh_geojson_adm1_8_divisions_bibhags.json"
)


def download_geojson() -> None:
    if GEOJSON_PATH.exists():
        print(f"[skip] GeoJSON already present: {GEOJSON_PATH}")
        return
    GEOJSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    print(f"[download] {GEOJSON_URL}")
    urllib.request.urlretrieve(GEOJSON_URL, GEOJSON_PATH)
    print(f"[ok] saved to {GEOJSON_PATH}")


def init_database() -> None:
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Raw CSV not found at {RAW_DATA_PATH}. The CSV ships with the repo;"
            " re-clone or restore from git history if it is missing."
        )

    import pandas as pd
    from db.repository import StudentMentalHealthRepository

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    repo = StudentMentalHealthRepository(str(DB_PATH))
    print(f"[init] creating SQLite DB at {DB_PATH}")
    repo.init_tables()
    df = pd.read_csv(RAW_DATA_PATH)
    inserted = repo.insert_data(df, if_exists="replace")
    print(f"[ok] inserted {inserted} rows into {DB_PATH}")


if __name__ == "__main__":
    download_geojson()
    init_database()
