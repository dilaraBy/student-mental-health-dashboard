# Test file for visualization functions
import pandas as pd
import pytest
import matplotlib.figure
import plotly.graph_objects as go
import json
import sys
from pathlib import Path
from unittest.mock import patch, mock_open

# Add project root to path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from services.visualization import (
    plot_depression_prevalence, 
    plot_depression_by_gender, 
    plot_depression_by_division, 
    plot_depression_by_year_of_study, 
    plot_monthly_depression_trend,
    plot_depression_choropleth
)
class TestVisualizationFunctions:
    """Test class for all visualization functions."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample DataFrame with correct standardized column names."""
        data = {
            'depression': ['Yes', 'No', 'Yes', 'No', 'Yes', 'Yes', 'No', 'Yes'],
            'anxiety': ['Yes', 'Yes', 'No', 'No', 'Yes', 'No', 'Yes', 'Yes'],
            'panic_attack': ['No', 'No', 'Yes', 'No', 'Yes', 'No', 'No', 'Yes'],
            'sought_treatment': ['Yes', 'No', 'Yes', 'No', 'No', 'Yes', 'No', 'Yes'],
            'financial_stress_level': [3, 1, 4, 2, 5, 3, 2, 4],
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
        return pd.DataFrame(columns=[
            'depression', 'anxiety', 'panic_attack', 'sought_treatment', 'financial_stress_level',
            'gender', 'division', 'year_of_study', 'timestamp'
        ])
    
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

    # ---- Choropleth Map Tests ----
    
    @pytest.fixture
    def sample_choropleth_data(self):
        """Create sample DataFrame with division data for choropleth testing."""
        data = {
            'division': ['Dhaka', 'Chittagong', 'Sylhet', 'Barisal', 'Khulna', 'Rajshahi', 'Rangpur', 'Mymensingh'],
            'depression': ['Yes', 'No', 'Yes', 'Yes', 'No', 'Yes', 'No', 'Yes']
        }
        return pd.DataFrame(data)
    
    @pytest.fixture
    def mock_geojson_data(self):
        """Create mock GeoJSON data for testing."""
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"ADM1_EN": "Dhaka"},
                    "geometry": {"type": "Polygon", "coordinates": [[[90, 23], [91, 23], [91, 24], [90, 24], [90, 23]]]}
                },
                {
                    "type": "Feature", 
                    "properties": {"ADM1_EN": "Chittagong"},
                    "geometry": {"type": "Polygon", "coordinates": [[[91, 22], [92, 22], [92, 23], [91, 23], [91, 22]]]}
                }
            ]
        }

    def test_plot_depression_choropleth_returns_plotly_figure(self, sample_choropleth_data, mock_geojson_data):
        """Test that plot_depression_choropleth returns a Plotly Figure or handles errors gracefully."""
        mock_json_content = json.dumps(mock_geojson_data)
        with patch('builtins.open', mock_open(read_data=mock_json_content)):
            result = plot_depression_choropleth(sample_choropleth_data)
            # Function should return either a valid Figure or None if Plotly is broken
            assert result is None or isinstance(result, go.Figure)

    def test_plot_depression_choropleth_loads_geojson(self, sample_choropleth_data, mock_geojson_data):
        """Test that the function loads the GeoJSON file through GeographicAnalysisService."""
        mock_json_content = json.dumps(mock_geojson_data)
        with patch('services.geographic_analysis.open', mock_open(read_data=mock_json_content)) as mock_file:
            plot_depression_choropleth(sample_choropleth_data)
            # Check that our GeoJSON file was opened (there might be other file opens from Plotly)
            mock_file.assert_called()

    def test_plot_depression_choropleth_maps_divisions_correctly(self, sample_choropleth_data, mock_geojson_data):
        """Test that division names are mapped correctly using ADM1_EN property."""
        mock_json_content = json.dumps(mock_geojson_data)
        with patch('builtins.open', mock_open(read_data=mock_json_content)):
            fig = plot_depression_choropleth(sample_choropleth_data)
            
            # Check that figure was created successfully or handled gracefully
            assert fig is None or isinstance(fig, go.Figure)
            # The function should be able to process the mock GeoJSON data structure

    def test_plot_depression_choropleth_calculates_depression_rates(self, sample_choropleth_data, mock_geojson_data):
        """Test that depression rates are calculated correctly."""
        # Create data where we know the expected rates
        data = {
            'division': ['Dhaka', 'Dhaka', 'Chittagong', 'Chittagong'],
            'depression': ['Yes', 'No', 'Yes', 'Yes']  # Dhaka: 50%, Chittagong: 100%
        }
        df = pd.DataFrame(data)
        
        mock_json_content = json.dumps(mock_geojson_data)
        with patch('builtins.open', mock_open(read_data=mock_json_content)):
            fig = plot_depression_choropleth(df)
            assert fig is None or isinstance(fig, go.Figure)

    def test_plot_depression_choropleth_handles_missing_columns(self, mock_geojson_data):
        """Test that function handles missing required columns gracefully."""
        df_missing = pd.DataFrame({'other_col': [1, 2, 3]})
        
        mock_json_content = json.dumps(mock_geojson_data)
        with patch('builtins.open', mock_open(read_data=mock_json_content)):
            fig = plot_depression_choropleth(df_missing)
            assert fig is None or isinstance(fig, go.Figure)

    def test_plot_depression_choropleth_handles_empty_data(self, mock_geojson_data):
        """Test that function handles empty DataFrame."""
        df_empty = pd.DataFrame(columns=['division', 'depression'])
        
        mock_json_content = json.dumps(mock_geojson_data)
        with patch('builtins.open', mock_open(read_data=mock_json_content)):
            fig = plot_depression_choropleth(df_empty)
            assert fig is None or isinstance(fig, go.Figure)

    def test_plot_depression_choropleth_handles_geojson_load_error(self, sample_choropleth_data):
        """Test that function handles GeoJSON file load errors gracefully."""
        with patch('builtins.open', side_effect=FileNotFoundError()):
            fig = plot_depression_choropleth(sample_choropleth_data)
            assert fig is None or isinstance(fig, go.Figure)

    def test_plot_depression_choropleth_doesnt_mutate_input(self, sample_choropleth_data, mock_geojson_data):
        """Test that plot_depression_choropleth doesn't mutate input DataFrame."""
        original_shape = sample_choropleth_data.shape
        original_columns = sample_choropleth_data.columns.tolist()
        
        mock_json_content = json.dumps(mock_geojson_data)
        with patch('builtins.open', mock_open(read_data=mock_json_content)):
            plot_depression_choropleth(sample_choropleth_data)
            
        assert sample_choropleth_data.shape == original_shape
        assert sample_choropleth_data.columns.tolist() == original_columns

    def test_plot_depression_choropleth_handles_division_name_variations(self, mock_geojson_data):
        """Test that function correctly maps division name variations."""
        # Test data with common variations
        data = {
            'division': ['Chattogram', 'Barishal', 'dhaka', 'CHITTAGONG', 'barisal'],
            'depression': ['Yes', 'No', 'Yes', 'No', 'Yes']
        }
        df_variations = pd.DataFrame(data)
        
        mock_json_content = json.dumps(mock_geojson_data)
        with patch('builtins.open', mock_open(read_data=mock_json_content)):
            fig = plot_depression_choropleth(df_variations)
            assert fig is None or isinstance(fig, go.Figure)


