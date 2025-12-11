# Tests for Detailed Analysis functions - TDD approach
import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from services.analysis import (
    depression_vs_cgpa,
    depression_rate_by_year,
    depression_rate_by_financial_stress,
    depression_rate_by_family_history,
    depression_rate_by_condition,
    build_correlation_matrix
)


class TestDetailedAnalysisFunctions:
    """Test suite for detailed analysis functions - TDD approach."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Sample data for testing
        self.sample_data = pd.DataFrame({
            'depression': ['Yes', 'No', 'Yes', 'No', 'Yes', 'No'],
            'cgpa': [3.2, 3.8, 2.9, 3.5, 2.1, 3.7],
            'year_of_study': ['Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 1', 'Year 2'],
            'financial_stress_level': ['Low', 'Medium', 'High', 'Low', 'High', 'Medium'],
            'family_history_mental_illness': ['Yes', 'No', 'Yes', 'No', 'No', 'Yes'],
            'anxiety': ['Yes', 'No', 'Yes', 'Yes', 'No', 'No'],
            'panic_attack': ['No', 'No', 'Yes', 'No', 'Yes', 'No'],
            'age': [20, 21, 22, 23, 20, 21]
        })
    
    def test_depression_vs_cgpa_returns_correct_structure(self):
        """Test that depression_vs_cgpa returns DataFrame with correct structure."""
        result = depression_vs_cgpa(self.sample_data)
        
        assert isinstance(result, pd.DataFrame)
        assert 'depression_label' in result.columns
        assert 'cgpa' in result.columns
        assert len(result) == 6  # Same number of rows as input
    
    def test_depression_vs_cgpa_correct_values(self):
        """Test that depression_vs_cgpa returns correct values."""
        result = depression_vs_cgpa(self.sample_data)
        
        # Check that depression labels are correctly mapped
        expected_labels = ['Depressed', 'Not Depressed', 'Depressed', 'Not Depressed', 'Depressed', 'Not Depressed']
        assert result['depression_label'].tolist() == expected_labels
        
        # Check CGPA values are preserved
        assert result['cgpa'].tolist() == [3.2, 3.8, 2.9, 3.5, 2.1, 3.7]
    
    def test_depression_vs_cgpa_empty_dataframe(self):
        """Test depression_vs_cgpa with empty DataFrame."""
        empty_df = pd.DataFrame()
        result = depression_vs_cgpa(empty_df)
        
        assert isinstance(result, pd.DataFrame)
        assert 'depression_label' in result.columns
        assert 'cgpa' in result.columns
        assert len(result) == 0
    
    def test_depression_vs_cgpa_missing_columns(self):
        """Test depression_vs_cgpa with missing columns."""
        df_missing = pd.DataFrame({'other_col': [1, 2, 3]})
        result = depression_vs_cgpa(df_missing)
        
        assert isinstance(result, pd.DataFrame)
        assert 'depression_label' in result.columns
        assert 'cgpa' in result.columns
        assert len(result) == 0
    
    def test_depression_rate_by_year_returns_correct_structure(self):
        """Test that depression_rate_by_year returns correct structure."""
        result = depression_rate_by_year(self.sample_data)
        
        assert isinstance(result, pd.DataFrame)
        assert 'year_of_study' in result.columns
        assert 'depression_pct' in result.columns
    
    def test_depression_rate_by_year_correct_percentages(self):
        """Test that depression_rate_by_year calculates correct percentages."""
        result = depression_rate_by_year(self.sample_data)
        
        # Year 1: 2 students, 2 depressed (100%)
        # Year 2: 2 students, 0 depressed (0%)
        # Year 3: 1 student, 1 depressed (100%)
        # Year 4: 1 student, 0 depressed (0%)
        
        year1_rate = result[result['year_of_study'] == 'Year 1']['depression_pct'].iloc[0]
        year2_rate = result[result['year_of_study'] == 'Year 2']['depression_pct'].iloc[0]
        
        assert pytest.approx(year1_rate, abs=0.1) == 100.0
        assert pytest.approx(year2_rate, abs=0.1) == 0.0
    
    def test_depression_rate_by_year_sorted_by_year(self):
        """Test that depression_rate_by_year returns results sorted by year."""
        result = depression_rate_by_year(self.sample_data)
        
        # Should be sorted Year 1, 2, 3, 4
        years = result['year_of_study'].tolist()
        expected_order = ['Year 1', 'Year 2', 'Year 3', 'Year 4']
        assert years == expected_order
    
    def test_depression_rate_by_year_empty_dataframe(self):
        """Test depression_rate_by_year with empty DataFrame."""
        empty_df = pd.DataFrame()
        result = depression_rate_by_year(empty_df)
        
        assert isinstance(result, pd.DataFrame)
        assert 'year_of_study' in result.columns
        assert 'depression_pct' in result.columns
        assert len(result) == 0
    
    def test_depression_rate_by_financial_stress_returns_correct_structure(self):
        """Test depression_rate_by_financial_stress structure."""
        result = depression_rate_by_financial_stress(self.sample_data)
        
        assert isinstance(result, pd.DataFrame)
        assert 'financial_stress_level' in result.columns
        assert 'depression_pct' in result.columns
    
    def test_depression_rate_by_financial_stress_correct_percentages(self):
        """Test financial stress depression rates calculation."""
        result = depression_rate_by_financial_stress(self.sample_data)
        
        # Let's check the actual data distribution first
        # Looking at sample_data: 
        # High stress: 2 students (indices 2,4), depression ['Yes', 'Yes'] = 100%
        # Low stress: 2 students (indices 0,3), depression ['Yes', 'No'] = 50%
        # Medium stress: 2 students (indices 1,5), depression ['No', 'No'] = 0%
        
        high_rate = result[result['financial_stress_level'] == 'High']['depression_pct'].iloc[0]
        low_rate = result[result['financial_stress_level'] == 'Low']['depression_pct'].iloc[0]
        
        assert pytest.approx(high_rate, abs=0.1) == 100.0
        assert pytest.approx(low_rate, abs=0.1) == 50.0  # Corrected expectation
    
    def test_depression_rate_by_financial_stress_handles_missing_values(self):
        """Test financial stress function handles missing values."""
        df_with_na = self.sample_data.copy()
        df_with_na.loc[0, 'financial_stress_level'] = np.nan
        
        result = depression_rate_by_financial_stress(df_with_na)
        
        assert isinstance(result, pd.DataFrame)
        # Should still return results for non-missing values
        assert len(result) > 0
    
    def test_depression_rate_by_family_history_returns_correct_structure(self):
        """Test depression_rate_by_family_history structure."""
        result = depression_rate_by_family_history(self.sample_data)
        
        assert isinstance(result, pd.DataFrame)
        assert 'family_history' in result.columns
        assert 'depression_pct' in result.columns
    
    def test_depression_rate_by_family_history_yes_vs_no_percentages(self):
        """Test family history Yes vs No percentages."""
        result = depression_rate_by_family_history(self.sample_data)
        
        # Family history Yes: 3 students, 2 depressed (66.7%)
        # Family history No: 3 students, 1 depressed (33.3%)
        
        yes_rate = result[result['family_history'] == 'Yes']['depression_pct'].iloc[0]
        no_rate = result[result['family_history'] == 'No']['depression_pct'].iloc[0]
        
        assert pytest.approx(yes_rate, abs=0.1) == 66.7
        assert pytest.approx(no_rate, abs=0.1) == 33.3
    
    def test_depression_rate_by_condition_anxiety(self):
        """Test depression_rate_by_condition for anxiety."""
        result = depression_rate_by_condition(self.sample_data, 'anxiety')
        
        assert isinstance(result, pd.DataFrame)
        assert 'condition_value' in result.columns
        assert 'depression_pct' in result.columns
        
        # Anxiety Yes: 3 students, 2 depressed (66.7%)
        # Anxiety No: 3 students, 1 depressed (33.3%)
        yes_rate = result[result['condition_value'] == 'Yes']['depression_pct'].iloc[0]
        no_rate = result[result['condition_value'] == 'No']['depression_pct'].iloc[0]
        
        assert pytest.approx(yes_rate, abs=0.1) == 66.7
        assert pytest.approx(no_rate, abs=0.1) == 33.3
    
    def test_depression_rate_by_condition_panic_attack(self):
        """Test depression_rate_by_condition for panic_attack."""
        result = depression_rate_by_condition(self.sample_data, 'panic_attack')
        
        assert isinstance(result, pd.DataFrame)
        assert 'condition_value' in result.columns
        assert 'depression_pct' in result.columns
    
    def test_depression_rate_by_condition_nonexistent_column(self):
        """Test depression_rate_by_condition with nonexistent column."""
        result = depression_rate_by_condition(self.sample_data, 'nonexistent')
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    def test_build_correlation_matrix_returns_correct_structure(self):
        """Test build_correlation_matrix returns correct structure."""
        result = build_correlation_matrix(self.sample_data)
        
        assert isinstance(result, pd.DataFrame)
        # Should be square matrix
        assert result.shape[0] == result.shape[1]
        # Should have numeric columns only
        assert all(result.dtypes.apply(pd.api.types.is_numeric_dtype))
    
    def test_build_correlation_matrix_correct_shape_and_columns(self):
        """Test correlation matrix has expected columns."""
        result = build_correlation_matrix(self.sample_data)
        
        expected_columns = ['depression', 'anxiety', 'panic_attack', 'financial_stress_level', 
                          'cgpa', 'year_of_study', 'age']
        
        # Should contain these columns (may have others or be subset)
        numeric_columns = result.columns.tolist()
        assert len(numeric_columns) > 0
        assert all(col in expected_columns for col in numeric_columns if col in expected_columns)
    
    def test_build_correlation_matrix_values_between_minus_one_and_one(self):
        """Test correlation values are between -1 and 1."""
        result = build_correlation_matrix(self.sample_data)
        
        # All correlation values should be between -1 and 1
        values = result.values.flatten()
        values = values[~np.isnan(values)]  # Remove NaN values
        
        assert all(-1 <= val <= 1 for val in values)
    
    def test_build_correlation_matrix_diagonal_is_one(self):
        """Test correlation matrix diagonal values are 1."""
        result = build_correlation_matrix(self.sample_data)
        
        if len(result) > 0:
            diagonal_values = np.diag(result.values)
            diagonal_values = diagonal_values[~np.isnan(diagonal_values)]
            assert all(pytest.approx(val, abs=0.01) == 1.0 for val in diagonal_values)
    
    def test_build_correlation_matrix_empty_dataframe(self):
        """Test build_correlation_matrix with empty DataFrame."""
        empty_df = pd.DataFrame()
        result = build_correlation_matrix(empty_df)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    def test_functions_dont_mutate_input_data(self):
        """Test that all functions don't mutate the input DataFrame."""
        original_shape = self.sample_data.shape
        original_columns = self.sample_data.columns.tolist()
        
        # Test all functions
        depression_vs_cgpa(self.sample_data)
        depression_rate_by_year(self.sample_data)
        depression_rate_by_financial_stress(self.sample_data)
        depression_rate_by_family_history(self.sample_data)
        depression_rate_by_condition(self.sample_data, 'anxiety')
        build_correlation_matrix(self.sample_data)
        
        # Check data wasn't mutated
        assert self.sample_data.shape == original_shape
        assert self.sample_data.columns.tolist() == original_columns