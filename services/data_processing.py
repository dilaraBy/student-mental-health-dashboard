import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Iterable
import pandas as pd
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
    - Drop rows where 'depression' (or 'Do you have Depression?') is missing
    - For all other columns, fill missing values with 'Unknown'
    """
    out = df.copy()

    # Handle both original and standardized column names
    depression_col = None
    if "depression" in out.columns:
        depression_col = "depression"
    elif "Do you have Depression?" in out.columns:
        depression_col = "Do you have Depression?"
    
    # 1. Drop rows where depression is missing
    if depression_col:
        before = len(out)
        out = out.dropna(subset=[depression_col])
        dropped = before - len(out)
        if dropped > 0:
            logger.info(f"Dropped {dropped} rows with missing {depression_col} value.")

    # 2. Fill missing values for all other columns
    for col in out.columns:
        if depression_col and col == depression_col:
            continue  # already handled
        missing_before = out[col].isna().sum()
        if missing_before > 0:
            out[col] = out[col].fillna("Unknown")
            logger.debug(f"Filled {missing_before} missing values in column: {col}")

    return out


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
	"""Remove duplicate rows from the DataFrame.
	
	Returns a new DataFrame with duplicates removed, keeping first occurrence.
	"""
	out = df.copy()
	before = len(out)
	out = out.drop_duplicates(keep='first')
	after = len(out)
	removed = before - after
	
	if removed > 0:
		logger.info(f"Removed {removed} duplicate row(s).")
	else:
		logger.debug("No duplicates found.")
	
	return out


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
	"""Simplify column names by removing special characters and using lowercase.
	
	Examples:
		- 'Do you have Depression?' -> 'depression'
		- 'Choose your gender' -> 'gender'
		- 'Your current year of Study' -> 'year_of_study'
	"""
	out = df.copy()
	
	# Mapping of original column names to simplified names
	column_mapping = {
		"Do you have Depression?": "depression",
		"Do you have Anxiety?": "anxiety",
		"Do you have Panic attack?": "panic_attack",
		"Family History of Mental Illness": "family_history_mental_illness",
		"Did you seek any specialist for a treatment?": "sought_specialist_treatment",
		"Choose your gender": "gender",
		"Your current year of Study": "year_of_study",
		"What is your course?": "course",
		"What is your CGPA?": "cgpa",
		"Marital status": "marital_status",
		"Living Situation": "living_situation",
		"University": "university",
		"Financial Stress Level": "financial_stress_level",
		"Age": "age",
		"Division": "division",
		"Timestamp": "timestamp",
	}
	
	# Rename columns that exist in both mapping and dataframe
	rename_dict = {old: new for old, new in column_mapping.items() if old in out.columns}
	
	if rename_dict:
		out = out.rename(columns=rename_dict)
		logger.info(f"Standardized {len(rename_dict)} column name(s).")
	else:
		logger.debug("No columns matched standardization mapping.")
	
	return out


def clean_data(filepath: str = None) -> pd.DataFrame:
	"""Main data cleaning pipeline.
	
	Orchestrates all data processing steps:
	1. Load raw data
	2. Remove duplicates
	3. Standardize column names
	4. Convert timestamps to datetime
	5. Normalize yes/no columns
	6. Add temporal columns
	7. Fill missing values
	
	Args:
		filepath: Path to CSV file. If None, uses RAW_DATA_PATH from config.
	
	Returns:
		Cleaned DataFrame ready for analysis or storage.
	"""
	logger.info("Starting data cleaning pipeline...")
	
	# Step 1: Load
	df = load_data(filepath)
	logger.debug(f"Step 1: Loaded {len(df)} rows")
	
	# Step 2: Remove duplicates
	df = remove_duplicates(df)
	logger.debug(f"Step 2: After removing duplicates: {len(df)} rows")
	
	# Step 3: Standardize column names
	df = standardize_column_names(df)
	logger.debug(f"Step 3: Standardized column names")
	
	# Step 4: Convert timestamps (use 'timestamp' after standardization)
	try:
		df = convert_timestamps(df, column="timestamp")
	except Exception as e:
		logger.warning(f"Timestamp conversion failed: {e}; continuing with raw timestamps")
	
	# Step 5: Normalize yes/no columns
	df = normalize_yes_no(df)
	logger.debug(f"Step 5: Normalized yes/no columns")
	
	# Step 6: Add temporal columns
	try:
		df = add_temporal_columns(df, column="timestamp")
	except Exception as e:
		logger.warning(f"Adding temporal columns failed: {e}; continuing")
	
	# Step 7: Fill missing values (will now look for 'depression' column)
	try:
		df = fill_missing_values(df)
	except Exception as e:
		logger.warning(f"Filling missing values failed: {e}; continuing")
	
	logger.info(f"Data cleaning complete. Final shape: {df.shape}")
	return df
