# StudentMentalHealthRepository class
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
    
import sqlite3
import pandas as pd
from typing import Optional
from utils.logger import get_logger

logger = get_logger(__name__)


class StudentMentalHealthRepository:
    """Repository for database operations on student mental health survey data."""

    def __init__(self, db_path: str):
        """
        Initialize repository with database path.

        Args:
            db_path: Path to SQLite database file, or ':memory:' for tests.
        """
        self.db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        """Create and return a new database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # so we can get dict-like rows if needed
        return conn

    def init_tables(self) -> None:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS survey_responses (
                    Timestamp TEXT,
                    Gender TEXT,
                    Division TEXT,
                    "Do you have Depression?" TEXT
                );
                """
            )
            conn.commit()
            logger.info("Created survey_responses table (if not exists).")
        finally:
            conn.close()

    def insert_data(self, df: pd.DataFrame, if_exists: str = "replace") -> int:
        """
        Insert a DataFrame into the survey_responses table.

        - Converts datetime columns to ISO strings so sqlite3 can store them.
        """
        conn = self.get_connection()
        try:
            df_to_store = df.copy()

            # Convert any datetime/timestamp columns to string (ISO format)
            # Check both datetime64 dtypes and object columns containing pandas.Timestamp
            for col in df_to_store.columns:
                if pd.api.types.is_datetime64_any_dtype(df_to_store[col]):
                    logger.debug(f"Converting datetime column '{col}' to ISO string")
                    df_to_store[col] = df_to_store[col].astype(str)
                elif df_to_store[col].dtype == object:
                    # Check if this column contains pandas Timestamp objects
                    non_null = df_to_store[col].dropna()
                    if not non_null.empty and isinstance(non_null.iloc[0], pd.Timestamp):
                        logger.debug(f"Converting Timestamp column '{col}' to ISO string")
                        df_to_store[col] = df_to_store[col].astype(str)

            df_to_store.to_sql(
                "survey_responses",
                conn,
                if_exists=if_exists,
                index=False,
            )
            conn.commit()

            cursor = conn.execute("SELECT COUNT(*) FROM survey_responses")
            (count,) = cursor.fetchone()
            logger.info(f"Inserted data into survey_responses; total rows = {count}")
            return count
        finally:
            conn.close()


    def get_all_data(self) -> pd.DataFrame:
        """
        Retrieve all data from the survey_responses table as a DataFrame.
        """
        conn = self.get_connection()
        try:
            df = pd.read_sql_query("SELECT * FROM survey_responses", conn)
            logger.info(f"Retrieved {len(df)} rows from survey_responses.")
            return df
        finally:
            conn.close()
