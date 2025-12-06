from typing import Iterable
import pandas as pd
from pathlib import Path
from utils.logger import get_logger
from utils.config import RAW_DATA_PATH

logger = get_logger(__name__)


def load_data(filepath: str = None) -> pd.DataFrame:
	"""Load CSV data from the specified filepath or default raw data path.

	Args:
		filepath: Path to CSV file. If None, uses RAW_DATA_PATH from config.

	Returns:
		Loaded DataFrame.

	Raises:
		FileNotFoundError: If the file does not exist.
	"""
	if filepath is None:
		filepath = RAW_DATA_PATH
	else:
		filepath = Path(filepath)

	if not Path(filepath).exists():
		logger.error(f"Data file not found: {filepath}")
		raise FileNotFoundError(f"Data file not found: {filepath}")

	try:
		logger.info(f"Loading data from: {filepath}")
		df = pd.read_csv(filepath)
		logger.info(f"Successfully loaded {len(df)} rows and {len(df.columns)} columns.")
		return df
	except Exception as e:
		logger.error(f"Error loading CSV file {filepath}: {e}")
		raise


def convert_timestamps(df: pd.DataFrame, column: str = "Timestamp") -> pd.DataFrame:
	"""Convert the specified timestamp column to datetime, coercing errors to NaT.

	Returns a new DataFrame with the converted column.
	"""
	logger.debug(f"Converting column '{column}' to datetime.")
	out = df.copy()
	out[column] = pd.to_datetime(out[column], errors="coerce")
	nat_count = out[column].isna().sum()
	if nat_count > 0:
		logger.warning(f"Converted {nat_count} invalid timestamp(s) to NaT.")
	logger.info(f"Successfully converted '{column}' to datetime.")
	return out


def _map_to_yes_no(value: object) -> object:
	if pd.isna(value):
		return value
	s = str(value).strip().lower()
	yes_values = {"yes", "y", "true", "t", "1", "yes."}
	no_values = {"no", "n", "false", "f", "0", "no."}
	if s in yes_values:
		return "Yes"
	if s in no_values:
		return "No"
	return value


def normalize_yes_no(df: pd.DataFrame, columns: Iterable[str] = None) -> pd.DataFrame:
	"""Normalize columns containing yes/no-like values to 'Yes'/'No'.

	If `columns` is None, applies to all object (string-like) columns.
	"""
	out = df.copy()
	if columns is None:
		columns = [c for c, t in out.dtypes.items() if t == object]
		logger.debug(f"Auto-detected object columns: {columns}")
	else:
		logger.debug(f"Normalizing specified columns: {columns}")

	for col in columns:
		try:
			out[col] = out[col].apply(_map_to_yes_no)
			logger.debug(f"Normalized yes/no values in column: {col}")
		except Exception as e:
			logger.error(f"Error normalizing column '{col}': {e}")
			raise

	logger.info(f"Successfully normalized yes/no columns.")
	return out


def add_temporal_columns(df: pd.DataFrame, column: str = "Timestamp") -> pd.DataFrame:
	"""Add `year`, `month`, and `day_of_week` columns derived from a datetime column.

	Expects the `column` to be datetime dtype. Returns a new DataFrame.
	"""
	logger.debug(f"Adding temporal columns from '{column}'.")
	out = df.copy()
	if not pd.api.types.is_datetime64_any_dtype(out[column]):
		logger.warning(f"Column '{column}' is not datetime dtype; converting now.")
		out[column] = pd.to_datetime(out[column], errors="coerce")

	out["year"] = out[column].dt.year
	out["month"] = out[column].dt.month
	out["day_of_week"] = out[column].dt.day_name()
	logger.info(f"Added temporal columns: year, month, day_of_week.")
	return out


def fill_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    - Drop rows where 'Do you have Depression?' is missing
    - For all other columns, fill missing values with 'Unknown'
    """
    out = df.copy()

    # 1. Drop rows where depression is missing
    if "Do you have Depression?" in out.columns:
        before = len(out)
        out = out.dropna(subset=["Do you have Depression?"])
        dropped = before - len(out)
        if dropped > 0:
            logger.info(f"Dropped {dropped} rows with missing depression value.")

    # 2. Fill missing values for all other columns
    for col in out.columns:
        if col == "Do you have Depression?":
            continue  # already handled
        missing_before = out[col].isna().sum()
        if missing_before > 0:
            out[col] = out[col].fillna("Unknown")
            logger.debug(f"Filled {missing_before} missing values in column: {col}")

    return out
