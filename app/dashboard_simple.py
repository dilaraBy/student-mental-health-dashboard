"""Simple Streamlit dashboard using project utilities.

Run with:
    streamlit run app/dashboard_simple.py

This is a lightweight page that uses existing functions in
`services.data_processing`, `db.repository`, and `services.analysis`.
"""

import sys
from pathlib import Path
import pandas as pd

# Add project root to sys.path so imports work when run via streamlit
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.config import RAW_DATA_PATH, DB_PATH
from utils.logger import get_logger
from services.data_processing import (
    load_data,
    convert_timestamps,
    normalize_yes_no,
    add_temporal_columns,
    fill_missing_values,
)
from db.repository import StudentMentalHealthRepository
from services.analysis import compute_prevalence

logger = get_logger(__name__)


def load_and_clean_into_db():
    repo = StudentMentalHealthRepository(str(DB_PATH))
    repo.init_tables()

    df = load_data(str(RAW_DATA_PATH))

    # apply minimal cleaning steps (safe-wrapped)
    for fn in (convert_timestamps, normalize_yes_no, add_temporal_columns, fill_missing_values):
        try:
            df = fn(df)
        except Exception:
            logger.debug(f"Cleaning step {fn.__name__} failed; continuing.")

    count = repo.insert_data(df, if_exists="replace")
    logger.info(f"Loaded {count} rows into DB")
    return count


def get_data_from_db() -> pd.DataFrame:
    repo = StudentMentalHealthRepository(str(DB_PATH))
    return repo.get_all_data()


def main():
    try:
        import streamlit as st
    except Exception as e:
        logger.error("Streamlit not installed or failed to import: %s", e)
        raise

    st.set_page_config(page_title="Student Mental Health Dashboard", layout="wide")
    st.title("Student Mental Health Dashboard")

    st.sidebar.header("Data")
    if st.sidebar.button("Load & Clean Data into DB"):
        try:
            rows = load_and_clean_into_db()
            st.success(f"Loaded {rows} rows into DB")
        except Exception as e:
            st.error(f"Load failed: {e}")

    st.sidebar.markdown("---")

    try:
        df = get_data_from_db()
    except Exception as e:
        st.warning("No data available. Load data using the sidebar.")
        logger.warning("Failed to fetch data from DB: %s", e)
        return

    if df.empty:
        st.info("Database empty — load data using the sidebar.")
        return

    st.subheader("Overview")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total responses", len(df))
    c2.metric("Unique genders", df["Gender"].nunique() if "Gender" in df.columns else 0)
    c3.metric("Unique divisions", df["Division"].nunique() if "Division" in df.columns else 0)

    if "Do you have Depression?" in df.columns:
        prev = compute_prevalence(df, "Do you have Depression?")
        st.subheader("Depression prevalence")
        st.write(f"Yes: {prev['yes_percentage']}% ({prev['yes_count']})")
        st.write(f"No: {prev['no_percentage']}% ({prev['no_count']})")

    st.subheader("Raw data")
    st.dataframe(df)


if __name__ == "__main__":
    main()
