# TDD Tests for Enhanced Missing Value Handling Pipeline
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
import pytest
from services import data_processing as dp


class TestMissingValueHandlingTDD:
    """Test-Driven Development tests for missing value handling functions."""
    
    def test_missing_depression_rows_are_dropped(self):
        """Test that rows with missing depression values are dropped entirely."""
        df = pd.DataFrame({
            'depression': ['Yes', np.nan, 'No', None, 'Yes'],
            'age': [20, 22, 24, 26, 28],
            'gender': ['Male', 'Female', 'Male', 'Female', 'Male']
        })
        
        result = dp.handle_missing_target_variable(df)
        
        # Should keep only rows with non-null depression values
        assert len(result) == 3
        assert result['depression'].tolist() == ['Yes', 'No', 'Yes']
        assert result['age'].tolist() == [20, 24, 28]
    
    def test_yes_no_imputation_mode_vs_unknown(self):
        """Test that Yes/No columns are imputed with mode, not 'Unknown'."""
        df = pd.DataFrame({
            'depression': ['Yes', 'No', 'Yes', 'Yes'],  # mode = 'Yes'
            'anxiety': ['Yes', np.nan, 'No', np.nan],   # mode = 'Yes' (tie, should pick first)
            'panic_attack': ['No', 'No', np.nan, 'No'],  # mode = 'No'
            'family_history_mental_illness': [np.nan, 'Yes', np.nan, np.nan],  # mode = 'Yes'
            'sought_treatment': ['No', np.nan, np.nan, np.nan]  # mode = 'No'
        })
        
        yes_no_columns = ['depression', 'anxiety', 'panic_attack', 'family_history_mental_illness', 'sought_treatment']
        result = dp.impute_yes_no_columns(df, yes_no_columns)
        
        # Check mode imputation
        assert result['anxiety'].tolist() == ['Yes', 'Yes', 'No', 'Yes']  # NaNs filled with mode 'Yes'
        assert result['panic_attack'].tolist() == ['No', 'No', 'No', 'No']  # NaN filled with mode 'No'
        assert result['family_history_mental_illness'].tolist() == ['Yes', 'Yes', 'Yes', 'Yes']  # NaNs filled with mode 'Yes'
        assert result['sought_treatment'].tolist() == ['No', 'No', 'No', 'No']  # NaNs filled with mode 'No'
    
    def test_low_cardinality_filled_with_unknown(self):
        """Test that low-cardinality categorical variables are filled with 'Unknown'."""
        df = pd.DataFrame({
            'gender': ['Male', 'Female', np.nan, 'Male'],  # 2 unique values
            'division': ['Dhaka', np.nan, 'Chittagong', np.nan],  # 2 unique values  
            'marital_status': ['Single', 'Married', np.nan, 'Single'],  # 2 unique values
            'living_situation': ['Home', np.nan, 'Hostel', 'Home']  # 2 unique values
        })
        
        low_cardinality_columns = ['gender', 'division', 'marital_status', 'living_situation']
        result = dp.fill_low_cardinality_categorical(df, low_cardinality_columns)
        
        # All NaN values should be filled with 'Unknown'
        assert result['gender'].tolist() == ['Male', 'Female', 'Unknown', 'Male']
        assert result['division'].tolist() == ['Dhaka', 'Unknown', 'Chittagong', 'Unknown']
        assert result['marital_status'].tolist() == ['Single', 'Married', 'Unknown', 'Single']
        assert result['living_situation'].tolist() == ['Home', 'Unknown', 'Hostel', 'Home']
    
    def test_high_cardinality_filled_with_unknown(self):
        """Test that high-cardinality categorical variables are filled with 'Unknown' instead of mode."""
        df = pd.DataFrame({
            'course': ['CSE', 'EEE', np.nan, 'CSE', 'BBA', np.nan, 'CSE', 'Physics', 'Chemistry'],  # 6 unique, mode='CSE'
            'university': ['DU', 'BUET', np.nan, 'DU', 'NSU', np.nan, 'DU', 'CUET', 'RU']  # 6 unique, mode='DU'
        })
        
        high_cardinality_columns = ['course', 'university']
        result = dp.fill_high_cardinality_categorical(df, high_cardinality_columns)
        
        # NaN values should be filled with 'Unknown', not mode
        assert result['course'].tolist() == ['CSE', 'EEE', 'Unknown', 'CSE', 'BBA', 'Unknown', 'CSE', 'Physics', 'Chemistry']
        assert result['university'].tolist() == ['DU', 'BUET', 'Unknown', 'DU', 'NSU', 'Unknown', 'DU', 'CUET', 'RU']
    
    def test_numeric_median_imputation(self):
        """Test that numeric columns are imputed with median."""
        df = pd.DataFrame({
            'age': [18, 20, np.nan, 24, 26, np.nan, 30],  # median = 24
            'some_score': [1.5, 2.0, np.nan, 3.5, 4.0, np.nan, 5.0]   # median = 3.5
        })
        
        numeric_columns = ['age', 'some_score']
        result = dp.impute_numeric_columns(df, numeric_columns)
        
        # NaN values should be filled with median
        expected_age = [18, 20, 24, 24, 26, 24, 30]  # median=24
        expected_score = [1.5, 2.0, 3.5, 3.5, 4.0, 3.5, 5.0]  # median=3.5
        
        assert result['age'].tolist() == expected_age
        assert result['some_score'].tolist() == expected_score
    
    def test_cgpa_interval_handling(self):
        """Test that CGPA is treated as ordered categorical, not numeric."""
        df = pd.DataFrame({
            'cgpa': ['3.00-3.49', '2.50-2.99', np.nan, '3.50-4.00', np.nan, '2.00-2.49']
        })
        
        result = dp.handle_cgpa_categorical(df, column='cgpa')
        
        # Should be treated as categorical, missing filled with 'Unknown' or mode
        assert result['cgpa'].dtype == 'object'  # Should remain as object/categorical
        
        # Check that missing values are filled appropriately (mode or Unknown)
        non_null_values = result['cgpa'][result['cgpa'].notna()]
        assert len(non_null_values) == len(result)  # All should be non-null after handling
        
        # Should not have any numeric conversion artifacts
        assert all(isinstance(val, str) for val in result['cgpa'])
    
    def test_timestamp_conversion_and_invalid_drop(self):
        """Test timestamp conversion and dropping rows with invalid timestamps."""
        df = pd.DataFrame({
            'timestamp': ['2023-01-05 14:30:00', 'invalid_date', '2023-12-15 09:15:00', ''],
            'depression': ['Yes', 'No', 'Yes', 'No'],
            'age': [20, 22, 24, 26]
        })
        
        result = dp.handle_timestamp_and_drop_invalid(df, column='timestamp')
        
        # Should drop rows with invalid timestamps  
        assert len(result) == 2  # Only 2 valid timestamps
        assert pd.api.types.is_datetime64_any_dtype(result['timestamp'])
        assert result['depression'].tolist() == ['Yes', 'Yes']
        assert result['age'].tolist() == [20, 24]
    
    def test_year_of_study_drop_missing(self):
        """Test that rows with missing year of study are dropped."""
        df = pd.DataFrame({
            'year_of_study': ['Year 1', np.nan, 'Year 2', None, 'Year 3'],
            'depression': ['Yes', 'No', 'Yes', 'No', 'Yes'],
            'age': [18, 20, 22, 24, 26]
        })
        
        result = dp.handle_year_of_study_drop_missing(df, column='year_of_study')
        
        # Should drop rows where year_of_study is missing
        assert len(result) == 3
        assert result['year_of_study'].tolist() == ['Year 1', 'Year 2', 'Year 3']
        assert result['depression'].tolist() == ['Yes', 'Yes', 'Yes']
        assert result['age'].tolist() == [18, 22, 26]
    
    def test_comprehensive_missing_value_pipeline(self):
        """Test the complete missing value handling pipeline."""
        df = pd.DataFrame({
            'timestamp': ['2023-01-05 14:30:00', '2023-12-15 09:15:00', 'invalid', '2023-06-20 16:45:00'],
            'depression': ['Yes', np.nan, 'No', 'Yes'],  # Row 1 should be dropped
            'anxiety': ['Yes', 'No', np.nan, 'Yes'],
            'gender': ['Male', 'Female', np.nan, 'Male'],
            'course': ['CSE', 'EEE', np.nan, 'CSE'],
            'cgpa': ['3.00-3.49', np.nan, '2.50-2.99', '3.50-4.00'],
            'age': [20, 22, np.nan, 26],
            'year_of_study': ['Year 1', 'Year 2', np.nan, 'Year 4']  # Row 2 should be dropped
        })
        
        result = dp.comprehensive_missing_value_pipeline(df)
        
        # After all processing:
        # - Row 1 dropped (depression missing)  
        # - Row 2 dropped (year_of_study missing)
        # - Rows 0 and 3 remain (valid timestamps and required fields)
        assert len(result) == 2
        assert result['depression'].tolist() == ['Yes', 'Yes']
        assert result['gender'].tolist() == ['Male', 'Male']
        
        # Age values should be preserved and imputed as needed
        assert result['age'].tolist() == [20.0, 26.0]
        
        # Anxiety should be present
        assert result['anxiety'].notna().all()
        
        # CGPA should be handled as categorical
        assert result['cgpa'].dtype == 'object'
    
    def test_pipeline_preserves_data_types(self):
        """Test that the pipeline preserves correct data types."""
        df = pd.DataFrame({
            'timestamp': ['01.05.2023 14:30', '15.12.2023 09:15'],
            'depression': ['Yes', 'No'],
            'anxiety': ['Yes', 'No'], 
            'gender': ['Male', 'Female'],
            'cgpa': ['3.00-3.49', '2.50-2.99'],
            'age': [20, 22],
            'year_of_study': ['Year 1', 'Year 2']
        })
        
        result = dp.comprehensive_missing_value_pipeline(df)
        
        # Check data types
        assert pd.api.types.is_datetime64_any_dtype(result['timestamp'])
        assert result['depression'].dtype == 'object'  # String
        assert result['anxiety'].dtype == 'object'     # String
        assert result['gender'].dtype == 'object'      # String  
        assert result['cgpa'].dtype == 'object'        # Categorical string
        assert pd.api.types.is_numeric_dtype(result['age'])  # Numeric
        assert result['year_of_study'].dtype == 'object'     # String
    
    def test_pipeline_logging(self, caplog):
        """Test that pipeline logs missing value handling steps."""
        df = pd.DataFrame({
            'depression': ['Yes', np.nan, 'No'],
            'age': [20, np.nan, 24]
        })
        
        result = dp.comprehensive_missing_value_pipeline(df)
        
        # Should log various steps
        log_messages = [record.message for record in caplog.records]
        assert any('missing' in msg.lower() for msg in log_messages)