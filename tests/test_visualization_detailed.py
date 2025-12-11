# Tests for Detailed Analysis Visualization functions - TDD approach
import pytest
import pandas as pd
import matplotlib.figure
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from services.detailed_analysis import (
    plot_cgpa_boxplot,
    plot_depression_by_year_bar,
    plot_depression_by_financial_stress_bar,
    plot_depression_by_family_history_bar,
    plot_depression_by_condition_grouped_bar,
    plot_correlation_heatmap
)


class TestDetailedAnalysisVisualizationFunctions:
    """Test suite for detailed analysis visualization functions - TDD approach."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Sample data mimicking analysis function outputs
        self.sample_cgpa_data = pd.DataFrame({
            'depression_label': ['Depressed', 'Not Depressed', 'Depressed', 'Not Depressed'],
            'cgpa': [3.2, 3.8, 2.9, 3.5]
        })
        
        self.sample_year_data = pd.DataFrame({
            'year_of_study': ['Year 1', 'Year 2', 'Year 3', 'Year 4'],
            'depression_pct': [75.0, 50.0, 25.0, 60.0]
        })
        
        self.sample_financial_data = pd.DataFrame({
            'financial_stress_level': ['Low', 'Medium', 'High'],
            'depression_pct': [20.0, 40.0, 80.0]
        })
        
        self.sample_family_data = pd.DataFrame({
            'family_history': ['No', 'Yes'],
            'depression_pct': [30.0, 70.0]
        })
        
        self.sample_condition_data = pd.DataFrame({
            'condition_value': ['No', 'Yes'],
            'depression_pct': [25.0, 75.0]
        })
        
        # Sample correlation matrix
        self.sample_correlation_data = pd.DataFrame({
            'depression': [1.0, 0.6, 0.3, -0.2],
            'anxiety': [0.6, 1.0, 0.4, -0.1],
            'panic_attack': [0.3, 0.4, 1.0, 0.0],
            'cgpa': [-0.2, -0.1, 0.0, 1.0]
        }, index=['depression', 'anxiety', 'panic_attack', 'cgpa'])
    
    def test_plot_cgpa_boxplot_returns_figure(self):
        """Test that plot_cgpa_boxplot returns matplotlib figure."""
        result = plot_cgpa_boxplot(self.sample_cgpa_data)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_cgpa_boxplot_empty_data(self):
        """Test plot_cgpa_boxplot with empty DataFrame."""
        empty_df = pd.DataFrame(columns=['depression_label', 'cgpa'])
        result = plot_cgpa_boxplot(empty_df)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_cgpa_boxplot_missing_columns(self):
        """Test plot_cgpa_boxplot with missing columns."""
        df_missing = pd.DataFrame({'other_col': [1, 2, 3]})
        result = plot_cgpa_boxplot(df_missing)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_depression_by_year_bar_returns_figure(self):
        """Test that plot_depression_by_year_bar returns matplotlib figure."""
        result = plot_depression_by_year_bar(self.sample_year_data)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_depression_by_year_bar_empty_data(self):
        """Test plot_depression_by_year_bar with empty DataFrame."""
        empty_df = pd.DataFrame(columns=['year_of_study', 'depression_pct'])
        result = plot_depression_by_year_bar(empty_df)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_depression_by_year_bar_missing_columns(self):
        """Test plot_depression_by_year_bar with missing columns."""
        df_missing = pd.DataFrame({'other_col': [1, 2, 3]})
        result = plot_depression_by_year_bar(df_missing)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_depression_by_financial_stress_bar_returns_figure(self):
        """Test that plot_depression_by_financial_stress_bar returns matplotlib figure."""
        result = plot_depression_by_financial_stress_bar(self.sample_financial_data)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_depression_by_financial_stress_bar_empty_data(self):
        """Test plot_depression_by_financial_stress_bar with empty DataFrame."""
        empty_df = pd.DataFrame(columns=['financial_stress_level', 'depression_pct'])
        result = plot_depression_by_financial_stress_bar(empty_df)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_depression_by_financial_stress_bar_missing_columns(self):
        """Test plot_depression_by_financial_stress_bar with missing columns."""
        df_missing = pd.DataFrame({'other_col': [1, 2, 3]})
        result = plot_depression_by_financial_stress_bar(df_missing)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_depression_by_family_history_bar_returns_figure(self):
        """Test that plot_depression_by_family_history_bar returns matplotlib figure."""
        result = plot_depression_by_family_history_bar(self.sample_family_data)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_depression_by_family_history_bar_empty_data(self):
        """Test plot_depression_by_family_history_bar with empty DataFrame."""
        empty_df = pd.DataFrame(columns=['family_history', 'depression_pct'])
        result = plot_depression_by_family_history_bar(empty_df)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_depression_by_family_history_bar_missing_columns(self):
        """Test plot_depression_by_family_history_bar with missing columns."""
        df_missing = pd.DataFrame({'other_col': [1, 2, 3]})
        result = plot_depression_by_family_history_bar(df_missing)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_depression_by_condition_grouped_bar_returns_figure(self):
        """Test that plot_depression_by_condition_grouped_bar returns matplotlib figure."""
        result = plot_depression_by_condition_grouped_bar(self.sample_condition_data, 'Anxiety')
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_depression_by_condition_grouped_bar_different_condition_names(self):
        """Test plot_depression_by_condition_grouped_bar with different condition names."""
        result1 = plot_depression_by_condition_grouped_bar(self.sample_condition_data, 'Anxiety')
        result2 = plot_depression_by_condition_grouped_bar(self.sample_condition_data, 'Panic Attack')
        
        assert isinstance(result1, matplotlib.figure.Figure)
        assert isinstance(result2, matplotlib.figure.Figure)
    
    def test_plot_depression_by_condition_grouped_bar_empty_data(self):
        """Test plot_depression_by_condition_grouped_bar with empty DataFrame."""
        empty_df = pd.DataFrame(columns=['condition_value', 'depression_pct'])
        result = plot_depression_by_condition_grouped_bar(empty_df, 'Anxiety')
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_depression_by_condition_grouped_bar_missing_columns(self):
        """Test plot_depression_by_condition_grouped_bar with missing columns."""
        df_missing = pd.DataFrame({'other_col': [1, 2, 3]})
        result = plot_depression_by_condition_grouped_bar(df_missing, 'Anxiety')
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_correlation_heatmap_returns_figure(self):
        """Test that plot_correlation_heatmap returns matplotlib figure."""
        result = plot_correlation_heatmap(self.sample_correlation_data)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_correlation_heatmap_square_matrix(self):
        """Test plot_correlation_heatmap with square correlation matrix."""
        # Ensure we have a proper square correlation matrix
        assert self.sample_correlation_data.shape[0] == self.sample_correlation_data.shape[1]
        
        result = plot_correlation_heatmap(self.sample_correlation_data)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_correlation_heatmap_empty_data(self):
        """Test plot_correlation_heatmap with empty DataFrame."""
        empty_df = pd.DataFrame()
        result = plot_correlation_heatmap(empty_df)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_plot_correlation_heatmap_single_column(self):
        """Test plot_correlation_heatmap with single column matrix."""
        single_col_df = pd.DataFrame({'depression': [1.0]}, index=['depression'])
        result = plot_correlation_heatmap(single_col_df)
        assert isinstance(result, matplotlib.figure.Figure)
    
    def test_functions_dont_mutate_input_data(self):
        """Test that all plotting functions don't mutate the input DataFrame."""
        # Store original data
        original_cgpa = self.sample_cgpa_data.copy()
        original_year = self.sample_year_data.copy()
        original_financial = self.sample_financial_data.copy()
        original_family = self.sample_family_data.copy()
        original_condition = self.sample_condition_data.copy()
        original_correlation = self.sample_correlation_data.copy()
        
        # Test all plotting functions
        plot_cgpa_boxplot(self.sample_cgpa_data)
        plot_depression_by_year_bar(self.sample_year_data)
        plot_depression_by_financial_stress_bar(self.sample_financial_data)
        plot_depression_by_family_history_bar(self.sample_family_data)
        plot_depression_by_condition_grouped_bar(self.sample_condition_data, 'Anxiety')
        plot_correlation_heatmap(self.sample_correlation_data)
        
        # Check data wasn't mutated
        pd.testing.assert_frame_equal(self.sample_cgpa_data, original_cgpa)
        pd.testing.assert_frame_equal(self.sample_year_data, original_year)
        pd.testing.assert_frame_equal(self.sample_financial_data, original_financial)
        pd.testing.assert_frame_equal(self.sample_family_data, original_family)
        pd.testing.assert_frame_equal(self.sample_condition_data, original_condition)
        pd.testing.assert_frame_equal(self.sample_correlation_data, original_correlation)