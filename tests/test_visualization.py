# Test file for visualization functions
import pandas as pd
import pytest
import matplotlib.figure
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from services.visualization import (
    plot_depression_prevalence,
    plot_depression_by_gender,
    plot_depression_by_division,
    plot_depression_by_year_of_study,
    plot_monthly_depression_trend
)


class TestVisualizationFunctions:
    """Test class for all visualization functions."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample DataFrame with correct standardized column names."""
        data = {
            'depression': ['Yes', 'No', 'Yes', 'No', 'Yes', 'Yes', 'No', 'Yes'],
            'gender': ['Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female'],
            'division': ['Dhaka', 'Chittagong', 'Dhaka', 'Sylhet', 'Chittagong', 'Dhaka', 'Sylhet', 'Dhaka'],
            'year_of_study': [1, 2, 3, 4, 1, 2, 3, 4],
            'timestamp': pd.to_datetime([
                '2023-01-15 10:30:00',
                '2023-02-20 14:45:00',
                '2023-03-10 09:15:00',
                '2023-04-25 16:20:00',
                '2023-05-30 11:10:00',
                '2023-06-15 13:40:00',
                '2023-07-22 08:30:00',
                '2023-08-18 15:25:00'
            ])
        }
        return pd.DataFrame(data)
    
    @pytest.fixture
    def empty_data(self):
        """Create empty DataFrame with correct column structure."""
        return pd.DataFrame(columns=['depression', 'gender', 'division', 'year_of_study', 'timestamp'])
    
    @pytest.fixture
    def missing_columns_data(self):
        """Create DataFrame with missing required columns."""
        data = {
            'depression': ['Yes', 'No', 'Yes'],
            'gender': ['Male', 'Female', 'Male']
            # Missing division, year_of_study, timestamp
        }
        return pd.DataFrame(data)

    def test_plot_depression_prevalence_returns_figure(self, sample_data):
        """Test that plot_depression_prevalence returns a matplotlib Figure."""
        result = plot_depression_prevalence(sample_data)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_depression_prevalence_empty_data(self, empty_data):
        """Test that plot_depression_prevalence handles empty DataFrame."""
        result = plot_depression_prevalence(empty_data)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_depression_prevalence_missing_columns(self, missing_columns_data):
        """Test that plot_depression_prevalence handles missing columns."""
        result = plot_depression_prevalence(missing_columns_data)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_depression_prevalence_doesnt_mutate_input(self, sample_data):
        """Test that plot_depression_prevalence doesn't mutate input DataFrame."""
        original_shape = sample_data.shape
        original_columns = sample_data.columns.tolist()
        plot_depression_prevalence(sample_data)
        assert sample_data.shape == original_shape
        assert sample_data.columns.tolist() == original_columns

    def test_plot_depression_by_gender_returns_figure(self, sample_data):
        """Test that plot_depression_by_gender returns a matplotlib Figure."""
        result = plot_depression_by_gender(sample_data)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_depression_by_gender_empty_data(self, empty_data):
        """Test that plot_depression_by_gender handles empty DataFrame."""
        result = plot_depression_by_gender(empty_data)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_depression_by_gender_missing_columns(self, missing_columns_data):
        """Test that plot_depression_by_gender handles missing columns."""
        # Remove gender column to test missing required column
        df_no_gender = missing_columns_data.drop('gender', axis=1)
        result = plot_depression_by_gender(df_no_gender)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_depression_by_gender_doesnt_mutate_input(self, sample_data):
        """Test that plot_depression_by_gender doesn't mutate input DataFrame."""
        original_shape = sample_data.shape
        original_columns = sample_data.columns.tolist()
        plot_depression_by_gender(sample_data)
        assert sample_data.shape == original_shape
        assert sample_data.columns.tolist() == original_columns

    def test_plot_depression_by_division_returns_figure(self, sample_data):
        """Test that plot_depression_by_division returns a matplotlib Figure."""
        result = plot_depression_by_division(sample_data)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_depression_by_division_empty_data(self, empty_data):
        """Test that plot_depression_by_division handles empty DataFrame."""
        result = plot_depression_by_division(empty_data)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_depression_by_division_missing_columns(self, missing_columns_data):
        """Test that plot_depression_by_division handles missing columns."""
        result = plot_depression_by_division(missing_columns_data)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_depression_by_division_doesnt_mutate_input(self, sample_data):
        """Test that plot_depression_by_division doesn't mutate input DataFrame."""
        original_shape = sample_data.shape
        original_columns = sample_data.columns.tolist()
        plot_depression_by_division(sample_data)
        assert sample_data.shape == original_shape
        assert sample_data.columns.tolist() == original_columns

    def test_plot_depression_by_year_of_study_returns_figure(self, sample_data):
        """Test that plot_depression_by_year_of_study returns a matplotlib Figure."""
        result = plot_depression_by_year_of_study(sample_data)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_depression_by_year_of_study_empty_data(self, empty_data):
        """Test that plot_depression_by_year_of_study handles empty DataFrame."""
        result = plot_depression_by_year_of_study(empty_data)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_depression_by_year_of_study_missing_columns(self, missing_columns_data):
        """Test that plot_depression_by_year_of_study handles missing columns."""
        result = plot_depression_by_year_of_study(missing_columns_data)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_depression_by_year_of_study_doesnt_mutate_input(self, sample_data):
        """Test that plot_depression_by_year_of_study doesn't mutate input DataFrame."""
        original_shape = sample_data.shape
        original_columns = sample_data.columns.tolist()
        plot_depression_by_year_of_study(sample_data)
        assert sample_data.shape == original_shape
        assert sample_data.columns.tolist() == original_columns

    def test_plot_monthly_depression_trend_returns_figure(self, sample_data):
        """Test that plot_monthly_depression_trend returns a matplotlib Figure."""
        result = plot_monthly_depression_trend(sample_data)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_monthly_depression_trend_empty_data(self, empty_data):
        """Test that plot_monthly_depression_trend handles empty DataFrame."""
        result = plot_monthly_depression_trend(empty_data)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_monthly_depression_trend_missing_columns(self, missing_columns_data):
        """Test that plot_monthly_depression_trend handles missing columns."""
        result = plot_monthly_depression_trend(missing_columns_data)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_monthly_depression_trend_doesnt_mutate_input(self, sample_data):
        """Test that plot_monthly_depression_trend doesn't mutate input DataFrame."""
        original_shape = sample_data.shape
        original_columns = sample_data.columns.tolist()
        plot_monthly_depression_trend(sample_data)
        assert sample_data.shape == original_shape
        assert sample_data.columns.tolist() == original_columns
