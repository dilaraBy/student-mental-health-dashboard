import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Iterable, List
import pandas as pd
import numpy as np
from utils.logger import get_logger
from utils.config import RAW_DATA_PATH


logger = get_logger(__name__)

def handle_missing_target_variable(df: pd.DataFrame, target_column: str = 'depression') -> pd.DataFrame:
    """
    Drop rows where the target variable (depression) is missing.
    Never impute this column as it's our target variable.
    
    Args:
        df: Input DataFrame
        target_column: Name of the target column (default: 'depression')
        
    Returns:
        DataFrame with rows containing missing target values dropped
    """
    out = df.copy()
    
    if target_column not in out.columns:
        logger.warning(f"Target column '{target_column}' not found in DataFrame")
        return out
    
    initial_rows = len(out)
    out = out.dropna(subset=[target_column])
    dropped_rows = initial_rows - len(out)
    
    if dropped_rows > 0:
        logger.info(f"Dropped {dropped_rows} rows with missing {target_column} values")
    
    return out


def impute_yes_no_columns(df: pd.DataFrame, yes_no_columns: List[str]) -> pd.DataFrame:
    """
    Impute missing values in Yes/No columns with the mode (most frequent value).
    For ties, prefer 'Yes' over 'No' as it's often the positive response.
    
    Args:
        df: Input DataFrame
        yes_no_columns: List of column names that contain Yes/No values
        
    Returns:
        DataFrame with Yes/No columns imputed with mode
    """
    out = df.copy()
    
    for col in yes_no_columns:
        if col not in out.columns:
            logger.debug(f"Column '{col}' not found in DataFrame, skipping")
            continue
            
        missing_count = out[col].isna().sum()
        if missing_count == 0:
            continue
            
        # Calculate value counts
        value_counts = out[col].value_counts()
        if len(value_counts) > 0:
            # Check if there's a tie between Yes and No
            max_count = value_counts.max()
            tied_values = value_counts[value_counts == max_count].index.tolist()
            
            # For ties in Yes/No columns, prefer 'Yes'
            if 'Yes' in tied_values:
                mode_value = 'Yes'
            else:
                mode_value = value_counts.index[0]  # Most frequent value
                
            out[col] = out[col].fillna(mode_value)
            logger.info(f"Imputed {missing_count} missing values in '{col}' with mode: '{mode_value}'")
        else:
            logger.warning(f"Could not determine mode for column '{col}', no imputation performed")
    
    return out


def fill_low_cardinality_categorical(df: pd.DataFrame, categorical_columns: List[str]) -> pd.DataFrame:
    """
    Fill missing values in low-cardinality categorical columns with 'Unknown'.
    
    Args:
        df: Input DataFrame
        categorical_columns: List of categorical column names
        
    Returns:
        DataFrame with low-cardinality categoricals filled with 'Unknown'
    """
    out = df.copy()
    
    for col in categorical_columns:
        if col not in out.columns:
            logger.debug(f"Column '{col}' not found in DataFrame, skipping")
            continue
            
        missing_count = out[col].isna().sum()
        if missing_count == 0:
            continue
            
        # Fill with 'Unknown'
        out[col] = out[col].fillna('Unknown')
        logger.info(f"Filled {missing_count} missing values in '{col}' with 'Unknown'")
    
    return out


def fill_high_cardinality_categorical(df: pd.DataFrame, categorical_columns: List[str]) -> pd.DataFrame:
    """
    Fill missing values in high-cardinality categorical columns with 'Unknown'.
    For high-cardinality columns, we avoid mode imputation to prevent distribution distortion.
    
    Args:
        df: Input DataFrame  
        categorical_columns: List of high-cardinality categorical column names
        
    Returns:
        DataFrame with high-cardinality categoricals filled with 'Unknown'
    """
    out = df.copy()
    
    for col in categorical_columns:
        if col not in out.columns:
            logger.debug(f"Column '{col}' not found in DataFrame, skipping")
            continue
            
        missing_count = out[col].isna().sum()
        if missing_count == 0:
            continue
            
        # Fill with 'Unknown' instead of mode to avoid distribution distortion
        out[col] = out[col].fillna('Unknown')
        unique_count = out[col].nunique()
        logger.info(f"Filled {missing_count} missing values in high-cardinality column '{col}' with 'Unknown' ({unique_count} unique values)")
    
    return out


def impute_numeric_columns(df: pd.DataFrame, numeric_columns: List[str]) -> pd.DataFrame:
    """
    Impute missing values in numeric columns with the median.
    
    Args:
        df: Input DataFrame
        numeric_columns: List of numeric column names
        
    Returns:
        DataFrame with numeric columns imputed with median
    """
    out = df.copy()
    
    for col in numeric_columns:
        if col not in out.columns:
            logger.debug(f"Column '{col}' not found in DataFrame, skipping")
            continue
            
        missing_count = out[col].isna().sum()
        if missing_count == 0:
            continue
            
        # Calculate median and impute
        median_value = out[col].median()
        if not pd.isna(median_value):
            out[col] = out[col].fillna(median_value)
            logger.info(f"Imputed {missing_count} missing values in '{col}' with median: {median_value}")
        else:
            logger.warning(f"Could not calculate median for column '{col}', no imputation performed")
    
    return out


def handle_cgpa_categorical(df: pd.DataFrame, column: str = 'cgpa') -> pd.DataFrame:
    """
    Handle CGPA as an ordered categorical variable, not numeric.
    CGPA values are intervals like '3.00-3.49' and should be treated as categorical.
    
    Args:
        df: Input DataFrame
        column: CGPA column name (default: 'cgpa')
        
    Returns:
        DataFrame with CGPA handled as categorical
    """
    out = df.copy()
    
    if column not in out.columns:
        logger.debug(f"Column '{column}' not found in DataFrame, returning unchanged")
        return out
        
    missing_count = out[column].isna().sum()
    
    if missing_count > 0:
        # For CGPA intervals, we can either use mode or 'Unknown'
        # Using mode might make sense for academic data
        mode_values = out[column].mode()
        if len(mode_values) > 0:
            mode_value = mode_values.iloc[0]
            out[column] = out[column].fillna(mode_value)
            logger.info(f"Filled {missing_count} missing CGPA values with mode: '{mode_value}'")
        else:
            out[column] = out[column].fillna('Unknown')
            logger.info(f"Filled {missing_count} missing CGPA values with 'Unknown'")
    
    # Ensure it remains as object/categorical type
    out[column] = out[column].astype('object')
    logger.debug(f"CGPA column '{column}' treated as categorical (dtype: object)")
    
    return out


def handle_timestamp_and_drop_invalid(df: pd.DataFrame, column: str = 'timestamp') -> pd.DataFrame:
    """
    Convert timestamp column to datetime and drop rows with invalid timestamps.
    
    Args:
        df: Input DataFrame
        column: Timestamp column name (default: 'timestamp')
        
    Returns:
        DataFrame with valid timestamps converted and invalid rows dropped
    """
    out = df.copy()
    
    if column not in out.columns:
        logger.debug(f"Column '{column}' not found in DataFrame, returning unchanged")
        return out
        
    initial_rows = len(out)
    
    # Convert to datetime - try standard ISO format first, then infer others
    out[column] = pd.to_datetime(out[column], errors='coerce')
    
    # Drop rows with invalid timestamps (NaT)
    out = out.dropna(subset=[column])
    
    dropped_rows = initial_rows - len(out)
    if dropped_rows > 0:
        logger.info(f"Dropped {dropped_rows} rows with invalid timestamps")
    
    logger.info(f"Successfully converted '{column}' to datetime format")
    return out


def handle_year_of_study_drop_missing(df: pd.DataFrame, column: str = 'year_of_study') -> pd.DataFrame:
    """
    Drop rows where year_of_study is missing, as it's critical for academic analysis.
    
    Args:
        df: Input DataFrame
        column: Year of study column name (default: 'year_of_study')
        
    Returns:
        DataFrame with rows containing missing year_of_study dropped
    """
    out = df.copy()
    
    if column not in out.columns:
        logger.debug(f"Column '{column}' not found in DataFrame, returning unchanged")
        return out
        
    initial_rows = len(out)
    out = out.dropna(subset=[column])
    dropped_rows = initial_rows - len(out)
    
    if dropped_rows > 0:
        logger.info(f"Dropped {dropped_rows} rows with missing {column} values (critical for analysis)")
    
    return out


def comprehensive_missing_value_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """
    Complete missing value handling pipeline following best practices.
    
    Processing order:
    1. Handle target variable (depression) - drop missing rows
    2. Handle critical variables (year_of_study) - drop missing rows  
    3. Handle timestamps - convert and drop invalid
    4. Impute Yes/No columns with mode
    5. Fill low-cardinality categoricals with 'Unknown'
    6. Fill high-cardinality categoricals with 'Unknown'
    7. Handle CGPA as categorical
    8. Impute numeric columns with median
    
    Args:
        df: Input DataFrame
        
    Returns:
        Fully cleaned DataFrame
    """
    logger.info("Starting comprehensive missing value handling pipeline")
    out = df.copy()
    initial_rows = len(out)
    
    # 1. Handle target variable - never impute, always drop
    out = handle_missing_target_variable(out, 'depression')
    
    # 2. Handle critical academic variable - drop missing
    out = handle_year_of_study_drop_missing(out, 'year_of_study')
    
    # 3. Handle timestamps - convert and drop invalid
    if 'timestamp' in out.columns:
        out = handle_timestamp_and_drop_invalid(out, 'timestamp')
    
    # 4. Impute Yes/No columns with mode
    yes_no_columns = ['anxiety', 'panic_attack', 'family_history_mental_illness', 'sought_treatment']
    existing_yes_no = [col for col in yes_no_columns if col in out.columns]
    if existing_yes_no:
        out = impute_yes_no_columns(out, existing_yes_no)
    
    # 5. Fill low-cardinality categoricals with 'Unknown'
    low_cardinality_columns = ['gender', 'division', 'marital_status', 'living_situation']
    existing_low_cardinality = [col for col in low_cardinality_columns if col in out.columns]
    if existing_low_cardinality:
        out = fill_low_cardinality_categorical(out, existing_low_cardinality)
    
    # 6. Fill high-cardinality categoricals with 'Unknown'
    high_cardinality_columns = ['course', 'university']
    existing_high_cardinality = [col for col in high_cardinality_columns if col in out.columns]
    if existing_high_cardinality:
        out = fill_high_cardinality_categorical(out, existing_high_cardinality)
    
    # 7. Handle CGPA as categorical
    if 'cgpa' in out.columns:
        out = handle_cgpa_categorical(out, 'cgpa')
    
    # 8. Impute numeric columns with median  
    numeric_columns = ['age']
    existing_numeric = [col for col in numeric_columns if col in out.columns]
    if existing_numeric:
        out = impute_numeric_columns(out, existing_numeric)
    
    final_rows = len(out)
    logger.info(f"Missing value pipeline complete: {initial_rows} -> {final_rows} rows ({initial_rows - final_rows} dropped)")
    
    return out



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
	"""Convert the specified timestamp column to datetime, handling European date format.
	
	Expected format in raw data: 'dd.mm.yyyy hh:mm' (e.g., '8.05.2023 22:26')
	Output format: datetime64[ns]

	Returns a new DataFrame with the converted column.
	"""
	logger.debug(f"Converting column '{column}' to datetime.")
	out = df.copy()
	
	# Try to parse European date format first (dd.mm.yyyy hh:mm)
	try:
		out[column] = pd.to_datetime(out[column], format='%d.%m.%Y %H:%M', errors='coerce')
		nat_count_european = out[column].isna().sum()
		
		# If still have many NaT values, try other common formats
		if nat_count_european > 0:
			# For rows that failed European format, try standard ISO/American formats
			mask_na = out[column].isna()
			if mask_na.any():
				logger.debug(f"Trying alternative formats for {mask_na.sum()} timestamps")
				# Try standard pandas parsing as fallback
				out.loc[mask_na, column] = pd.to_datetime(df.loc[mask_na, column], errors='coerce')
		
		final_nat_count = out[column].isna().sum()
		
		if final_nat_count > 0:
			logger.warning(f"Converted {final_nat_count} invalid timestamp(s) to NaT.")
		
		successful_count = len(out) - final_nat_count
		logger.info(f"Successfully converted {successful_count} timestamps to datetime (European format: dd.mm.yyyy hh:mm).")
		
	except Exception as e:
		logger.warning(f"European format parsing failed: {e}. Falling back to standard parsing.")
		# Fallback to standard pandas parsing
		out[column] = pd.to_datetime(out[column], errors="coerce")
		nat_count = out[column].isna().sum()
		if nat_count > 0:
			logger.warning(f"Converted {nat_count} invalid timestamp(s) to NaT.")
		logger.info(f"Successfully converted '{column}' to datetime using standard parsing.")
	
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


def normalize_year_of_study(df: pd.DataFrame, column: str = "year_of_study") -> pd.DataFrame:
	"""Normalize year of study values to consistent 'Year X' format.
	
	Handles various formats:
	- "year 1", "Year 1", "YEAR 2" -> "Year 1", "Year 2"
	- "1st year", "2nd year" -> "Year 1", "Year 2" 
	- "first year", "second year" -> "Year 1", "Year 2"
	- "1", "2", "3", "4" -> "Year 1", "Year 2", etc.
	- Invalid/missing values -> "Unknown"
	
	Args:
		df: DataFrame to process
		column: Column name containing year of study data
		
	Returns:
		DataFrame with normalized year of study values
	"""
	if column not in df.columns:
		logger.debug(f"Column '{column}' not found in DataFrame, returning unchanged.")
		return df.copy()
	
	logger.debug(f"Normalizing year of study values in column '{column}'.")
	out = df.copy()
	
	def _normalize_year_value(value):
		"""Helper function to normalize individual year values."""
		if pd.isna(value) or str(value).strip() == "":
			return "Unknown"
		
		# Convert to lowercase string for processing
		val_str = str(value).lower().strip()
		
		# Direct year formats: "year 1", "year 2", etc.
		if "year" in val_str:
			if "1" in val_str:
				return "Year 1"
			elif "2" in val_str:
				return "Year 2" 
			elif "3" in val_str:
				return "Year 3"
			elif "4" in val_str:
				return "Year 4"
		
		# Ordinal formats: "1st year", "2nd year", etc.
		if any(ord_num in val_str for ord_num in ["1st", "2nd", "3rd", "4th"]):
			if "1st" in val_str:
				return "Year 1"
			elif "2nd" in val_str:
				return "Year 2"
			elif "3rd" in val_str:
				return "Year 3"
			elif "4th" in val_str:
				return "Year 4"
		
		# Written formats: "first year", "second year", etc.
		written_years = {
			"first": "Year 1",
			"second": "Year 2", 
			"third": "Year 3",
			"fourth": "Year 4"
		}
		for written, standard in written_years.items():
			if written in val_str:
				return standard
		
		# Simple number formats: "1", "2", "3", "4"
		if val_str in ["1", "2", "3", "4"]:
			return f"Year {val_str}"
		
		# If none of the patterns match, return Unknown
		logger.debug(f"Could not normalize year value: '{value}' -> 'Unknown'")
		return "Unknown"
	
	try:
		out[column] = out[column].apply(_normalize_year_value)
		
		# Log the normalization results
		unique_values = out[column].unique()
		logger.info(f"Normalized year of study values. Unique values: {sorted(unique_values)}")
		
	except Exception as e:
		logger.error(f"Error normalizing year of study column '{column}': {e}")
		raise
	
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


def convert_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
	"""Convert appropriate columns to numeric types.
	
	Converts age, year, and month columns to numeric, keeping NaN for missing values.
	Leaves other columns as strings/objects.
	"""
	out = df.copy()
	
	# Define columns that should be numeric
	numeric_columns = {
		'age': 'float64',      # Age can be decimal
		'year': 'Int64',       # Year as integer (nullable)  
		'month': 'Int64',      # Month as integer (nullable)
	}
	
	for col, target_dtype in numeric_columns.items():
		if col in out.columns:
			# Replace "Unknown" with NaN first for numeric conversion
			if out[col].dtype == 'object':
				out[col] = out[col].replace('Unknown', pd.NA)
				
			# Convert to numeric, coercing errors to NaN
			try:
				if target_dtype == 'float64':
					out[col] = pd.to_numeric(out[col], errors='coerce')
				elif target_dtype == 'Int64':
					# Use nullable integer type
					out[col] = pd.to_numeric(out[col], errors='coerce').astype('Int64')
				
				logger.debug(f"Converted {col} to {target_dtype}")
			except Exception as e:
				logger.warning(f"Failed to convert {col} to numeric: {e}")
	
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
	8. Convert numeric columns to proper types
	9. Normalize year of study values
	
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
	
	# Step 7: Fill missing values using TDD-validated comprehensive pipeline
	try:
		df = comprehensive_missing_value_pipeline(df)
		logger.debug(f"Step 7: Applied comprehensive missing value handling pipeline")
	except Exception as e:
		logger.warning(f"Comprehensive missing value handling failed: {e}; continuing")
	
	# Step 8: Convert numeric columns to proper types
	try:
		df = convert_numeric_columns(df)
		logger.debug(f"Step 8: Converted numeric columns to proper types")
	except Exception as e:
		logger.warning(f"Numeric conversion failed: {e}; continuing")
	
	# Step 9: Normalize year of study values
	try:
		df = normalize_year_of_study(df)
		logger.debug(f"Step 9: Normalized year of study values")
	except Exception as e:
		logger.warning(f"Year of study normalization failed: {e}; continuing")
	
	logger.info(f"Data cleaning complete. Final shape: {df.shape}")
	return df


if __name__ == "__main__":
	"""Run data processing pipeline when script is executed directly."""
	from db.repository import StudentMentalHealthRepository
	from utils.config import DB_PATH
	logger.info("STUDENT MENTAL HEALTH DATA PROCESSING PIPELINE")
	
	try:
		# Step 1: Process the data
		logger.info("Step 1: Processing raw data...")
		df = clean_data()
		logger.info("Data processing complete!")
		logger.info(f"Final shape: {df.shape}")
		
		# Show year_of_study results
		if "year_of_study" in df.columns:
			unique_years = sorted(df["year_of_study"].unique())
			logger.info(f"Year of study values: {unique_years}")
			
			year_counts = df["year_of_study"].value_counts().sort_index()
			logger.info("Year of Study Distribution:")
			for year, count in year_counts.items():
				logger.info(f"• {year}: {count} students")
		
		# Step 2: Update database
		logger.info(f"\nStep 2: Updating database at {DB_PATH}")
		repo = StudentMentalHealthRepository(str(DB_PATH))
		repo.init_tables()
		
		count = repo.insert_data(df, if_exists="replace")
		logger.info(f"Successfully updated database with {count} rows")
		
		# Step 3: Verify database update
		logger.info("\nStep 3: Verifying database update...")
		db_df = repo.get_all_data()
		logger.info(f"Database now contains {len(db_df)} rows")
		
		if "year_of_study" in db_df.columns:
			db_unique_years = sorted(db_df["year_of_study"].unique())
			logger.info(f"Database year_of_study values: {db_unique_years}")
		
		logger.info("\n" + "=" * 60)
		logger.info("SUCCESS! Database updated with normalized year_of_study values")
		logger.info("You can now run the Streamlit dashboard with updated data")
		logger.info("=" * 60)
		
	except Exception as e:
		logger.error(f"Pipeline failed: {e}")
		raise
