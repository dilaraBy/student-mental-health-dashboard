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

            # Convert columns to SQLite-compatible types
            for col in df_to_store.columns:
                # Convert datetime columns to ISO strings
                if pd.api.types.is_datetime64_any_dtype(df_to_store[col]):
                    logger.debug(f"Converting datetime column '{col}' to ISO string")
                    df_to_store[col] = df_to_store[col].astype(str)
                # Convert nullable integers (Int64) to regular integers for SQLite
                elif str(df_to_store[col].dtype) == 'Int64':
                    logger.debug(f"Converting nullable integer column '{col}' to float (for SQLite)")
                    # Convert to float to preserve NaN values (SQLite doesn't have nullable integers)
                    df_to_store[col] = df_to_store[col].astype('float64')
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

    def get_row_count(self) -> int:
        """
        Get the total number of rows in the survey_responses table.
        
        Returns:
            Number of rows in the table.
        """
        conn = self.get_connection()
        try:
            cursor = conn.execute("SELECT COUNT(*) FROM survey_responses")
            (count,) = cursor.fetchone()
            logger.debug(f"Total rows in survey_responses: {count}")
            return count
        finally:
            conn.close()

    def get_unique_values(self, column: str) -> list:
        """
        Get unique values from a specific column.
        
        Args:
            column: Column name to get unique values from.
            
        Returns:
            List of unique values (excludes NULL values).
        """
        conn = self.get_connection()
        try:
            # Check if column exists first
            cursor = conn.execute("PRAGMA table_info(survey_responses)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if column not in columns:
                logger.warning(f"Column '{column}' does not exist in survey_responses table")
                return []
            
            # Get unique values, excluding NULLs - use safe parameterized query
            query = "SELECT DISTINCT [" + column + "] FROM survey_responses WHERE [" + column + "] IS NOT NULL ORDER BY [" + column + "]"
            cursor = conn.execute(query)
            values = [row[0] for row in cursor.fetchall()]
            
            logger.debug(f"Found {len(values)} unique values in column '{column}'")
            return values
        except Exception as e:
            logger.error(f"Error getting unique values from column '{column}': {e}")
            return []
        finally:
            conn.close()

    def filter_by_multiple(self, filters: dict) -> pd.DataFrame:
        """
        Filter data by multiple conditions using AND logic with safe parameterized queries.
        
        Args:
            filters: Dictionary where keys are column names and values are filter values.
                    e.g., {"gender": "Male", "division": "Dhaka"}
                    
        Returns:
            Filtered DataFrame.
        """
        if not filters:
            return self.get_all_data()
        
        conn = self.get_connection()
        try:
            # Check if all columns exist to prevent SQL injection
            cursor = conn.execute("PRAGMA table_info(survey_responses)")
            existing_columns = [row[1] for row in cursor.fetchall()]
            
            # Start with base query - using WHERE 1=1 for easy AND chaining
            query = "SELECT * FROM survey_responses WHERE 1=1"
            params = []
            
            valid_filter_count = 0
            for col, value in filters.items():
                if col in existing_columns:
                    # Use parameterized query to prevent SQL injection
                    query += " AND [" + col + "] = ?"
                    params.append(value)
                    valid_filter_count += 1
                else:
                    logger.warning(f"Column '{col}' does not exist, skipping filter")
            
            if valid_filter_count == 0:
                logger.warning("No valid filters found, returning empty DataFrame")
                return pd.DataFrame()
            
            # Execute safe parameterized query
            df = pd.read_sql_query(query, conn, params=params)
            logger.debug(f"Filter returned {len(df)} rows with {valid_filter_count} conditions")
            return df
            
        except Exception as e:
            logger.error(f"Error filtering data: {e}")
            return pd.DataFrame()
        finally:
            conn.close()

    def get_column_stats(self, column: str) -> dict:
        """
        Get basic statistics for a numeric column.
        
        Args:
            column: Column name to get statistics for.
            
        Returns:
            Dictionary with count, min, max, mean statistics.
        """
        conn = self.get_connection()
        try:
            # Check if column exists
            cursor = conn.execute("PRAGMA table_info(survey_responses)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if column not in columns:
                logger.warning(f"Column '{column}' does not exist")
                return {}
            
            # Get statistics (excluding NULL values) - use safe SQL construction
            query = (
                "SELECT "
                "COUNT([" + column + "]) as count, "
                "MIN([" + column + "]) as min, "
                "MAX([" + column + "]) as max, "
                "AVG([" + column + "]) as mean "
                "FROM survey_responses "
                "WHERE [" + column + "] IS NOT NULL"
            )
            
            cursor = conn.execute(query)
            result = cursor.fetchone()
            
            stats = {
                "count": result[0],
                "min": result[1],
                "max": result[2],
                "mean": result[3]
            }
            
            logger.debug(f"Column '{column}' statistics: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting statistics for column '{column}': {e}")
            return {}
        finally:
            conn.close()

    def get_value_counts(self, column: str) -> dict:
        """
        Get value counts for a categorical column.
        
        Args:
            column: Column name to get value counts for.
            
        Returns:
            Dictionary with values as keys and counts as values.
        """
        conn = self.get_connection()
        try:
            # Check if column exists
            cursor = conn.execute("PRAGMA table_info(survey_responses)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if column not in columns:
                logger.warning(f"Column '{column}' does not exist")
                return {}
            
            # Get value counts - use safe SQL construction
            query = (
                "SELECT [" + column + "], COUNT(*) as count "
                "FROM survey_responses "
                "WHERE [" + column + "] IS NOT NULL "
                "GROUP BY [" + column + "] "
                "ORDER BY count DESC"
            )
            
            cursor = conn.execute(query)
            results = cursor.fetchall()
            
            counts = {row[0]: row[1] for row in results}
            
            logger.debug(f"Column '{column}' value counts: {len(counts)} unique values")
            return counts
            
        except Exception as e:
            logger.error(f"Error getting value counts for column '{column}': {e}")
            return {}
        finally:
            conn.close()

    def search_by_text(self, column: str, search_text: str) -> pd.DataFrame:
        """
        Search for rows where a column contains specific text (case-insensitive).
        
        Args:
            column: Column name to search in.
            search_text: Text to search for.
            
        Returns:
            DataFrame with matching rows.
        """
        conn = self.get_connection()
        try:
            # Check if column exists
            cursor = conn.execute("PRAGMA table_info(survey_responses)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if column not in columns:
                logger.warning(f"Column '{column}' does not exist")
                return pd.DataFrame()
            
            # Search using LIKE with wildcards (case-insensitive) - safe parameterized query
            query = "SELECT * FROM survey_responses WHERE [" + column + "] LIKE ? COLLATE NOCASE"
            search_pattern = "%" + search_text + "%"
            
            df = pd.read_sql_query(query, conn, params=[search_pattern])
            
            logger.debug(f"Text search in '{column}' for '{search_text}' returned {len(df)} rows")
            return df
            
        except Exception as e:
            logger.error(f"Error searching text in column '{column}': {e}")
            return pd.DataFrame()
        finally:
            conn.close()
