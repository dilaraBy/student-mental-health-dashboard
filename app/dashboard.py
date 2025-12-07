# Streamlit UI for Student Mental Health Dashboard
import pandas as pd
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from utils.config import RAW_DATA_PATH, DB_PATH
from utils.logger import get_logger
from services.data_processing import clean_data
from db.repository import StudentMentalHealthRepository
from services.analysis import compute_prevalence

logger = get_logger(__name__)


def load_and_clean_into_db():
    """Load raw CSV, perform complete cleaning, and load into the main SQLite DB."""
    repo = StudentMentalHealthRepository(str(DB_PATH))
    repo.init_tables()

    # Use the main clean_data pipeline
    df = clean_data(str(RAW_DATA_PATH))

    count = repo.insert_data(df, if_exists="replace")

    logger.info(f"Loaded {count} cleaned rows into DB from Streamlit.")
    return count


def get_data_from_db() -> pd.DataFrame:
    """Fetch all data from the DB."""
    repo = StudentMentalHealthRepository(str(DB_PATH))
    return repo.get_all_data()


def main():
    try:
        import streamlit as st
    except Exception as e:
        logger.error(f"Streamlit is required to run the dashboard: {e}")
        raise

    st.set_page_config(page_title="Student Mental Health Dashboard", layout="wide")

    st.title("📊 Student Mental Health Dashboard")

    st.sidebar.header("Data Management")

    # --- Load & Clean Data Button ---
    if st.sidebar.button("Load & Clean Data into DB"):
        try:
            count = load_and_clean_into_db()
            st.success(f"Successfully loaded {count} rows into the database.")
        except Exception as e:
            st.error(f"Error loading data: {e}")
            logger.error(f"Error in Streamlit load button: {e}")

    st.sidebar.markdown("---")

    # --- Fetch & Display Data ---
    try:
        df = get_data_from_db()
    except Exception as e:
        st.warning("Could not read data from database yet. "
                   "Click 'Load & Clean Data into DB' in the sidebar.")
        logger.warning(f"Could not fetch data from DB: {e}")
        return

    if df.empty:
        st.warning("Database is empty. Load data first from the sidebar.")
        return

    # ---- Overview Metrics ----
    st.subheader("Overview")

    col1, col2, col3 = st.columns(3)

    total_students = len(df)
    unique_genders = df["Gender"].nunique() if "Gender" in df.columns else 0
    unique_divisions = df["Division"].nunique() if "Division" in df.columns else 0

    col1.metric("Total Responses", total_students)
    col2.metric("Unique Genders", unique_genders)
    col3.metric("Unique Divisions", unique_divisions)

    # ---- Simple Depression Prevalence ----
    if "Do you have Depression?" in df.columns:
        prev = compute_prevalence(df, "Do you have Depression?")
        st.subheader("Depression Prevalence")
        st.write(f"**Yes:** {prev['yes_percentage']}% ({prev['yes_count']} students)")
        st.write(f"**No:** {prev['no_percentage']}% ({prev['no_count']} students)")
    else:
        st.info("Depression column not found in data.")

    # ---- Raw Data Table ----
    st.subheader("Raw Data")
    st.dataframe(df)


if __name__ == "__main__":
    main()
