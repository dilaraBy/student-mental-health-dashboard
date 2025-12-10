# Data Management Service - Business logic for CRUD operations and data filtering
import pandas as pd
import streamlit as st
from typing import Dict, List, Optional, Any
from datetime import datetime
import io

from db.repository import StudentMentalHealthRepository
from utils.logger import get_logger

logger = get_logger(__name__)


class DataManagementService:
    """Service class for data management operations and filtering logic."""
    
    def __init__(self, repository: StudentMentalHealthRepository):
        """Initialize with repository dependency."""
        self.repository = repository
    
    def get_filter_options(self) -> Dict[str, List[str]]:
        """
        Get available filter options for each filterable column.
        
        Returns:
            Dictionary mapping column names to their unique values.
        """
        logger.debug("Getting filter options for data management")
        try:
            df = self.repository.get_all_data()
            if df.empty:
                return {}
            
            filter_columns = [
                'gender', 'division', 'university', 'year_of_study',
                'depression', 'anxiety', 'panic_attack', 
                'sought_specialist_treatment', 'financial_stress_level'
            ]
            
            options = {}
            for col in filter_columns:
                if col in df.columns:
                    unique_vals = df[col].dropna().unique().tolist()
                    # Sort values for better UX
                    if isinstance(unique_vals[0] if unique_vals else None, str):
                        unique_vals.sort()
                    options[col] = unique_vals
                    
            logger.debug(f"Generated filter options for {len(options)} columns")
            return options
            
        except Exception as e:
            logger.error(f"Error getting filter options: {e}")
            return {}
    
    def apply_filters(self, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply multiple filters to the dataset.
        
        Args:
            filters: Dictionary of column names and filter values.
            
        Returns:
            Filtered DataFrame.
        """
        logger.debug(f"Applying filters: {filters}")
        try:
            # Remove empty filters
            active_filters = {k: v for k, v in filters.items() 
                            if v is not None and v != [] and v != ""}
            
            if not active_filters:
                return self.repository.get_all_data_with_ids()
            
            # Use repository's filter method for basic filters
            basic_filters = {}
            date_range = None
            
            for col, value in active_filters.items():
                if col == 'date_range':
                    date_range = value
                elif isinstance(value, list) and len(value) == 1:
                    basic_filters[col] = value[0]
                elif not isinstance(value, list):
                    basic_filters[col] = value
            
            # Get filtered data with IDs
            if basic_filters:
                df = pd.read_sql_query(
                    self._build_filter_query(basic_filters), 
                    self.repository.get_connection()
                )
            else:
                df = self.repository.get_all_data_with_ids()
            
            # Apply date range filter if specified
            if date_range and 'timestamp' in df.columns:
                df = self._apply_date_filter(df, date_range)
            
            logger.info(f"Applied filters, returned {len(df)} rows")
            return df
            
        except Exception as e:
            logger.error(f"Error applying filters: {e}")
            return pd.DataFrame()
    
    def _build_filter_query(self, filters: Dict[str, str]) -> str:
        """Build SQL query with WHERE clauses for filters."""
        base_query = "SELECT rowid, * FROM survey_responses"
        
        if not filters:
            return base_query
        
        where_clauses = []
        for col, value in filters.items():
            where_clauses.append(f"[{col}] = '{value}'")
        
        return f"{base_query} WHERE {' AND '.join(where_clauses)}"
    
    def _apply_date_filter(self, df: pd.DataFrame, date_range: tuple) -> pd.DataFrame:
        """Apply date range filter to DataFrame."""
        try:
            df_copy = df.copy()
            df_copy['timestamp'] = pd.to_datetime(df_copy['timestamp'], errors='coerce')
            
            start_date, end_date = date_range
            mask = (df_copy['timestamp'] >= pd.to_datetime(start_date)) & \
                   (df_copy['timestamp'] <= pd.to_datetime(end_date))
            
            return df_copy[mask]
        except Exception as e:
            logger.error(f"Error applying date filter: {e}")
            return df
    
    def get_data_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate statistics for the given DataFrame.
        
        Args:
            df: DataFrame to analyze.
            
        Returns:
            Dictionary with various statistics.
        """
        try:
            if df.empty:
                return {
                    'total_records': 0,
                    'missing_data': {},
                    'data_types': {},
                    'categorical_distributions': {}
                }
            
            stats = {
                'total_records': len(df),
                'total_columns': len(df.columns),
                'missing_data': df.isnull().sum().to_dict(),
                'data_types': df.dtypes.astype(str).to_dict(),
                'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB"
            }
            
            # Calculate distributions for categorical columns
            categorical_cols = df.select_dtypes(include=['object']).columns
            distributions = {}
            for col in categorical_cols[:5]:  # Limit to first 5 to avoid clutter
                if col != 'rowid':
                    distributions[col] = df[col].value_counts().head(5).to_dict()
            
            stats['categorical_distributions'] = distributions
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return {}
    
    def validate_record_data(self, record_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate record data before create/update operations.
        
        Args:
            record_data: Dictionary with record field values.
            
        Returns:
            Tuple of (is_valid, list_of_error_messages).
        """
        logger.debug(f"Validating record data with {len(record_data)} fields")
        errors = []
        
        # Required fields validation
        required_fields = ['gender', 'division']
        for field in required_fields:
            if not record_data.get(field):
                errors.append(f"{field.replace('_', ' ').title()} is required")
        
        # Data type validations
        yes_no_fields = [
            'depression', 'anxiety', 'panic_attack', 
            'sought_specialist_treatment'
        ]
        for field in yes_no_fields:
            if field in record_data and record_data[field] not in ['Yes', 'No', '', None]:
                errors.append(f"{field.replace('_', ' ').title()} must be 'Yes' or 'No'")
        
        # Financial stress level validation
        if 'financial_stress_level' in record_data:
            valid_levels = ['Low', 'Medium', 'High', 'Unknown']
            if record_data['financial_stress_level'] not in valid_levels + ['', None]:
                errors.append("Financial Stress Level must be Low, Medium, High, or Unknown")
        
        is_valid = len(errors) == 0
        logger.debug(f"Validation result: {is_valid}, errors: {len(errors)}")
        if errors:
            logger.warning(f"Validation errors found: {errors}")
        return is_valid, errors
    
    def process_uploaded_csv(self, uploaded_file) -> tuple[bool, str, Optional[pd.DataFrame]]:
        """
        Process uploaded CSV file and validate its structure.
        
        Args:
            uploaded_file: Streamlit uploaded file object.
            
        Returns:
            Tuple of (success, message, dataframe).
        """
        logger.info(f"Processing uploaded CSV file: {uploaded_file.name if hasattr(uploaded_file, 'name') else 'unknown'}")
        try:
            # Read CSV
            df = pd.read_csv(uploaded_file)
            
            if df.empty:
                return False, "The uploaded CSV file is empty.", None
            
            # Basic validation - check for required columns
            required_cols = ['gender', 'division']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                return False, f"Missing required columns: {', '.join(missing_cols)}", None
            
            # Clean and validate data
            df = df.dropna(subset=required_cols)  # Remove rows with missing required data
            
            message = f"Successfully processed CSV with {len(df)} valid records."
            logger.info(message)
            return True, message, df
            
        except Exception as e:
            logger.error(f"Error processing CSV: {e}")
            return False, f"Error processing CSV file: {str(e)}", None
    
    def export_to_csv(self, df: pd.DataFrame) -> bytes:
        """
        Convert DataFrame to CSV bytes for download.
        
        Args:
            df: DataFrame to export.
            
        Returns:
            CSV data as bytes.
        """
        logger.debug(f"Exporting DataFrame with {len(df)} rows and {len(df.columns)} columns to CSV")
        try:
            # Remove rowid column if present for cleaner export
            export_df = df.drop('rowid', axis=1, errors='ignore')
            
            # Convert to CSV
            output = io.StringIO()
            export_df.to_csv(output, index=False)
            csv_data = output.getvalue().encode('utf-8')
            
            logger.info(f"Exported {len(export_df)} records to CSV")
            return csv_data
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return b""


class RecordFormHandler:
    """Handler for record creation and update forms."""
    
    @staticmethod
    def create_record_form(columns: List[str], existing_data: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        Create a form for record input with validation.
        
        Args:
            columns: List of column names to include in form.
            existing_data: Existing record data for update forms.
            
        Returns:
            Dictionary with form data if submitted, None otherwise.
        """
        logger.debug(f"Creating record form with {len(columns)} columns, existing_data: {existing_data is not None}")
        form_data = {}
        
        # Define field types and options
        yes_no_fields = [
            'depression', 'anxiety', 'panic_attack', 
            'sought_specialist_treatment'
        ]
        
        select_options = {
            'gender': ['Male', 'Female', 'Other'],
            'division': ['Arts', 'Science', 'Commerce', 'Engineering'],
            'university': ['University A', 'University B', 'University C'],
            'year_of_study': ['1st Year', '2nd Year', '3rd Year', '4th Year', 'Graduate'],
            'financial_stress_level': ['Low', 'Medium', 'High', 'Unknown']
        }
        
        # Create form fields
        for col in columns:
            if col in ['rowid', 'timestamp']:
                continue  # Skip system columns
                
            default_value = existing_data.get(col, '') if existing_data else ''
            
            if col in yes_no_fields:
                form_data[col] = st.selectbox(
                    col.replace('_', ' ').title(),
                    options=['', 'Yes', 'No'],
                    index=['', 'Yes', 'No'].index(default_value) if default_value in ['', 'Yes', 'No'] else 0,
                    key=f"form_{col}"
                )
            elif col in select_options:
                options = [''] + select_options[col]
                form_data[col] = st.selectbox(
                    col.replace('_', ' ').title(),
                    options=options,
                    index=options.index(default_value) if default_value in options else 0,
                    key=f"form_{col}"
                )
            else:
                form_data[col] = st.text_input(
                    col.replace('_', ' ').title(),
                    value=default_value,
                    key=f"form_{col}"
                )
        
        # Auto-set timestamp for new records
        if 'timestamp' not in form_data and not existing_data:
            form_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return form_data