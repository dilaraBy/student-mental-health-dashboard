# Tests for overview analysis functions
import pandas as pd
import pytest
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from services.overview_analysis import (
    compute_kpis,
    plot_overall_depression,
    plot_depression_by_gender_pie,
    plot_depression_by_division_bar,
    plot_risk_profile_radar
)
import matplotlib


class TestOverviewAnalysis:
    """Test class for overview analysis functions."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample DataFrame for testing."""
        data = {
            'depression': ['Yes', 'No', 'Yes', 'No', 'Yes', 'Yes', 'No', 'Yes'],
            'anxiety': ['Yes', 'Yes', 'No', 'No', 'Yes', 'No', 'Yes', 'Yes'],
            'panic_attack': ['No', 'No', 'Yes', 'No', 'Yes', 'No', 'No', 'Yes'],
            'sought_specialist_treatment': ['Yes', 'No', 'Yes', 'No', 'No', 'Yes', 'No', 'Yes'],
            'gender': ['Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female']
        }
        return pd.DataFrame(data)
    
    @pytest.fixture
    def empty_data(self):
        """Create empty DataFrame with correct column structure."""
        return pd.DataFrame(columns=['depression', 'anxiety', 'panic_attack', 'sought_specialist_treatment', 'gender'])
    
    @pytest.fixture
    def missing_columns_data(self):
        """Create DataFrame with some missing columns."""
        data = {
            'depression': ['Yes', 'No', 'Yes'],
            'gender': ['Male', 'Female', 'Male']
            # Missing anxiety, panic_attack, sought_specialist_treatment
        }
        return pd.DataFrame(data)

    def test_compute_kpis_basic_functionality(self, sample_data):
        """Test that compute_kpis returns correct KPIs for sample data."""
        result = compute_kpis(sample_data)
        
        # Check structure
        assert isinstance(result, dict)
        expected_keys = {'total_students', 'pct_depressed', 'pct_anxious', 'pct_panic', 'pct_sought_help'}
        assert set(result.keys()) == expected_keys
        
        # Check values - 8 total students
        assert result['total_students'] == 8
        
        # Depression: 5 out of 8 = 62.5%
        assert result['pct_depressed'] == pytest.approx(62.5, rel=1e-2)
        
        # Anxiety: 5 out of 8 = 62.5%
        assert result['pct_anxious'] == pytest.approx(62.5, rel=1e-2)
        
        # Panic: 3 out of 8 = 37.5%
        assert result['pct_panic'] == pytest.approx(37.5, rel=1e-2)
        
        # Sought help: 4 out of 8 = 50.0%
        assert result['pct_sought_help'] == pytest.approx(50.0, rel=1e-2)
    
    def test_compute_kpis_empty_dataframe(self, empty_data):
        """Test that compute_kpis handles empty DataFrame without crashing."""
        result = compute_kpis(empty_data)
        
        # Should return dict with zeros, not crash
        assert isinstance(result, dict)
        expected_keys = {'total_students', 'pct_depressed', 'pct_anxious', 'pct_panic', 'pct_sought_help'}
        assert set(result.keys()) == expected_keys
        
        # All values should be 0
        assert result['total_students'] == 0
        assert result['pct_depressed'] == 0.0
        assert result['pct_anxious'] == 0.0
        assert result['pct_panic'] == 0.0
        assert result['pct_sought_help'] == 0.0
    
    def test_compute_kpis_missing_columns(self, missing_columns_data):
        """Test that compute_kpis handles missing columns gracefully."""
        result = compute_kpis(missing_columns_data)
        
        # Should return dict without crashing
        assert isinstance(result, dict)
        expected_keys = {'total_students', 'pct_depressed', 'pct_anxious', 'pct_panic', 'pct_sought_help'}
        assert set(result.keys()) == expected_keys
        
        # Should have correct total
        assert result['total_students'] == 3
        
        # Should have depression data (2 out of 3 = 66.67%)
        assert result['pct_depressed'] == pytest.approx(66.67, rel=1e-2)
        
        # Missing columns should be treated as 0%
        assert result['pct_anxious'] == 0.0
        assert result['pct_panic'] == 0.0
        assert result['pct_sought_help'] == 0.0
    
    def test_compute_kpis_doesnt_mutate_input(self, sample_data):
        """Test that compute_kpis doesn't mutate the input DataFrame."""
        original_shape = sample_data.shape
        original_columns = sample_data.columns.tolist()
        original_values = sample_data.copy()
        
        compute_kpis(sample_data)
        
        # DataFrame should be unchanged
        assert sample_data.shape == original_shape
        assert sample_data.columns.tolist() == original_columns
        assert sample_data.equals(original_values)
    
    def test_compute_kpis_all_yes_values(self):
        """Test compute_kpis when all values are Yes."""
        data = {
            'depression': ['Yes', 'Yes', 'Yes'],
            'anxiety': ['Yes', 'Yes', 'Yes'],
            'panic_attack': ['Yes', 'Yes', 'Yes'],
            'sought_specialist_treatment': ['Yes', 'Yes', 'Yes']
        }
        df = pd.DataFrame(data)
        
        result = compute_kpis(df)
        
        assert result['total_students'] == 3
        assert result['pct_depressed'] == pytest.approx(100.0, rel=1e-2)
        assert result['pct_anxious'] == pytest.approx(100.0, rel=1e-2)
        assert result['pct_panic'] == pytest.approx(100.0, rel=1e-2)
        assert result['pct_sought_help'] == pytest.approx(100.0, rel=1e-2)
    
    def test_compute_kpis_all_no_values(self):
        """Test compute_kpis when all values are No."""
        data = {
            'depression': ['No', 'No', 'No'],
            'anxiety': ['No', 'No', 'No'],
            'panic_attack': ['No', 'No', 'No'],
            'sought_specialist_treatment': ['No', 'No', 'No']
        }
        df = pd.DataFrame(data)
        
        result = compute_kpis(df)
        
        assert result['total_students'] == 3
        assert result['pct_depressed'] == pytest.approx(0.0, rel=1e-2)
        assert result['pct_anxious'] == pytest.approx(0.0, rel=1e-2)
        assert result['pct_panic'] == pytest.approx(0.0, rel=1e-2)
        assert result['pct_sought_help'] == pytest.approx(0.0, rel=1e-2)

    # Tests for overview visualization functions
    
    def test_plot_overall_depression_returns_figure(self, sample_data):
        """Test that plot_overall_depression returns a matplotlib Figure."""
        result = plot_overall_depression(sample_data)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_overall_depression_empty_data(self, empty_data):
        """Test that plot_overall_depression handles empty DataFrame."""
        result = plot_overall_depression(empty_data)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_overall_depression_doesnt_mutate_input(self, sample_data):
        """Test that plot_overall_depression doesn't mutate input DataFrame."""
        original_shape = sample_data.shape
        original_columns = sample_data.columns.tolist()
        plot_overall_depression(sample_data)
        assert sample_data.shape == original_shape
        assert sample_data.columns.tolist() == original_columns

    def test_plot_depression_by_gender_pie_returns_figure(self, sample_data):
        """Test that plot_depression_by_gender_pie returns a matplotlib Figure."""
        result = plot_depression_by_gender_pie(sample_data)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_depression_by_gender_pie_empty_data(self, empty_data):
        """Test that plot_depression_by_gender_pie handles empty DataFrame."""
        result = plot_depression_by_gender_pie(empty_data)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_depression_by_gender_pie_doesnt_mutate_input(self, sample_data):
        """Test that plot_depression_by_gender_pie doesn't mutate input DataFrame."""
        original_shape = sample_data.shape
        original_columns = sample_data.columns.tolist()
        plot_depression_by_gender_pie(sample_data)
        assert sample_data.shape == original_shape
        assert sample_data.columns.tolist() == original_columns

    def test_plot_depression_by_division_bar_returns_figure(self, sample_data):
        """Test that plot_depression_by_division_bar returns a matplotlib Figure."""
        # Add division column for this test
        sample_data_with_division = sample_data.copy()
        sample_data_with_division['division'] = ['Science', 'Arts', 'Science', 'Arts', 
                                                'Science', 'Arts', 'Science', 'Arts']
        result = plot_depression_by_division_bar(sample_data_with_division)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_depression_by_division_bar_empty_data(self, empty_data):
        """Test that plot_depression_by_division_bar handles empty DataFrame."""
        result = plot_depression_by_division_bar(empty_data)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_depression_by_division_bar_doesnt_mutate_input(self, sample_data):
        """Test that plot_depression_by_division_bar doesn't mutate input DataFrame."""
        # Add division column for this test
        sample_data_with_division = sample_data.copy()
        sample_data_with_division['division'] = ['Science', 'Arts', 'Science', 'Arts', 
                                                'Science', 'Arts', 'Science', 'Arts']
        original_shape = sample_data_with_division.shape
        original_columns = sample_data_with_division.columns.tolist()
        plot_depression_by_division_bar(sample_data_with_division)
        assert sample_data_with_division.shape == original_shape
        assert sample_data_with_division.columns.tolist() == original_columns

    def test_plot_risk_profile_radar_returns_figure(self, sample_data):
        """Test that plot_risk_profile_radar returns a matplotlib Figure."""
        # Add required columns for radar chart
        sample_data_enhanced = sample_data.copy()
        sample_data_enhanced['financial_stress_level'] = [3, 2, 4, 1, 5, 3, 2, 4]
        result = plot_risk_profile_radar(sample_data_enhanced)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_risk_profile_radar_empty_data(self, empty_data):
        """Test that plot_risk_profile_radar handles empty DataFrame."""
        result = plot_risk_profile_radar(empty_data)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_risk_profile_radar_doesnt_mutate_input(self, sample_data):
        """Test that plot_risk_profile_radar doesn't mutate input DataFrame."""
        # Add required columns for radar chart
        sample_data_enhanced = sample_data.copy()
        sample_data_enhanced['financial_stress_level'] = [3, 2, 4, 1, 5, 3, 2, 4]
        original_shape = sample_data_enhanced.shape
        original_columns = sample_data_enhanced.columns.tolist()
        plot_risk_profile_radar(sample_data_enhanced)
        assert sample_data_enhanced.shape == original_shape
        assert sample_data_enhanced.columns.tolist() == original_columns