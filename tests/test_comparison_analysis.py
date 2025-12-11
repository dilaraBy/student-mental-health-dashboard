# Tests for Comparison Explorer functionality
import pytest
import pandas as pd
import matplotlib.figure
from unittest.mock import Mock, patch

from services.comparison_analysis import ComparisonAnalysisService, InsightGenerator
from db.repository import StudentMentalHealthRepository


class TestComparisonAnalysisService:
    """Test class for ComparisonAnalysisService following TDD approach."""

    @pytest.fixture
    def sample_repository(self):
        """Create a mock repository with sample data for testing."""
        # Create diverse sample data for comparison testing
        sample_data = pd.DataFrame({
            'gender': ['Male', 'Female', 'Male', 'Female', 'Male', 'Female'],
            'division': ['Dhaka', 'Sylhet', 'Khulna', 'Chattogram', 'Rajshahi', 'Rangpur'],
            'university': ['Uni A', 'Uni A', 'Uni B', 'Uni B', 'Uni A', 'Uni B'],
            'course': ['Computer Science', 'Psychology', 'Engineering', 'Medicine', 'Business', 'Agriculture'],
            'year_of_study': ['1st Year', '2nd Year', '1st Year', '3rd Year', '2nd Year', '1st Year'],
            'financial_stress_level': ['Low', 'High', 'Medium', 'Low', 'High', 'Medium'],
            'depression': ['Yes', 'No', 'Yes', 'Yes', 'No', 'Yes'],
            'anxiety': ['No', 'Yes', 'No', 'Yes', 'Yes', 'No'],
            'panic_attack': ['Yes', 'No', 'No', 'Yes', 'No', 'Yes'],
            'sought_specialist_treatment': ['Yes', 'No', 'No', 'Yes', 'Yes', 'No'],
            'cgpa': [3.5, 3.8, 3.2, 3.9, 3.6, 3.4],
            'family_history_mental_illness': ['Yes', 'No', 'Yes', 'No', 'Yes', 'No']
        })
        
        # Create a mock repository
        mock_repo = Mock(spec=StudentMentalHealthRepository)
        mock_repo.get_all_data.return_value = sample_data
        return mock_repo

    @pytest.fixture
    def comparison_service(self, sample_repository):
        """Create ComparisonAnalysisService with sample repository."""
        return ComparisonAnalysisService(sample_repository)

    def test_get_available_x_axis_options(self, comparison_service):
        """Test that service returns correct X-axis options."""
        options = comparison_service.get_available_x_axis_options()
        
        expected_options = [
            'gender', 'division', 'university', 'course', 'year_of_study', 
            'financial_stress_level', 'family_history_mental_illness'
        ]
        
        assert isinstance(options, list)
        for option in expected_options:
            assert option in options

    def test_get_available_y_metrics(self, comparison_service):
        """Test that service returns correct Y-metric options."""
        metrics = comparison_service.get_available_y_metrics()
        
        expected_metrics = [
            'depression_prevalence', 'anxiety_prevalence', 
            'panic_attack_prevalence', 'help_seeking_proportion'
        ]
        
        assert isinstance(metrics, dict)
        for metric in expected_metrics:
            assert metric in metrics
            assert isinstance(metrics[metric], str)  # Display name

    def test_compute_comparison_data_depression_by_gender(self, comparison_service):
        """Test computing depression prevalence by gender."""
        result = comparison_service.compute_comparison_data(
            x_axis='gender',
            y_metric='depression_prevalence'
        )
        
        assert isinstance(result, pd.DataFrame)
        assert 'gender' in result.columns
        assert 'depression_prevalence' in result.columns
        assert len(result) == 2  # Male and Female
        
        # Check values are percentages (0-100)
        assert all(0 <= val <= 100 for val in result['depression_prevalence'])

    def test_compute_comparison_data_anxiety_by_division(self, comparison_service):
        """Test computing anxiety prevalence by division."""
        result = comparison_service.compute_comparison_data(
            x_axis='division',
            y_metric='anxiety_prevalence'
        )
        
        assert isinstance(result, pd.DataFrame)
        assert 'division' in result.columns
        assert 'anxiety_prevalence' in result.columns
        assert len(result) >= 2  # Multiple divisions

    def test_compute_comparison_data_with_filters(self, comparison_service):
        """Test computing comparison data with additional filters."""
        filters = {'gender': 'Female'}
        
        result = comparison_service.compute_comparison_data(
            x_axis='division',
            y_metric='depression_prevalence',
            filters=filters
        )
        
        assert isinstance(result, pd.DataFrame)
        # Should only include data for females
        assert len(result) >= 1

    def test_compute_comparison_data_help_seeking(self, comparison_service):
        """Test computing help-seeking proportion."""
        result = comparison_service.compute_comparison_data(
            x_axis='gender',
            y_metric='help_seeking_proportion'
        )
        
        assert isinstance(result, pd.DataFrame)
        assert 'help_seeking_proportion' in result.columns

    def test_compute_comparison_data_invalid_x_axis(self, comparison_service):
        """Test error handling for invalid X-axis."""
        with pytest.raises(ValueError, match="Invalid x_axis"):
            comparison_service.compute_comparison_data(
                x_axis='invalid_column',
                y_metric='depression_prevalence'
            )

    def test_compute_comparison_data_invalid_y_metric(self, comparison_service):
        """Test error handling for invalid Y-metric."""
        with pytest.raises(ValueError, match="Invalid y_metric"):
            comparison_service.compute_comparison_data(
                x_axis='gender',
                y_metric='invalid_metric'
            )

    def test_create_comparison_chart_bar(self, comparison_service):
        """Test creating bar chart for comparison."""
        data = comparison_service.compute_comparison_data(
            x_axis='gender',
            y_metric='depression_prevalence'
        )
        
        chart = comparison_service.create_comparison_chart(
            data=data,
            x_axis='gender',
            y_metric='depression_prevalence',
            chart_type='bar'
        )
        
        assert isinstance(chart, matplotlib.figure.Figure)

    def test_create_comparison_chart_line(self, comparison_service):
        """Test creating line chart for temporal data."""
        data = comparison_service.compute_comparison_data(
            x_axis='year_of_study',
            y_metric='depression_prevalence'
        )
        
        chart = comparison_service.create_comparison_chart(
            data=data,
            x_axis='year_of_study',
            y_metric='depression_prevalence',
            chart_type='line'
        )
        
        assert isinstance(chart, matplotlib.figure.Figure)

    def test_create_comparison_chart_empty_data(self, comparison_service):
        """Test chart creation with empty data."""
        empty_data = pd.DataFrame()
        
        chart = comparison_service.create_comparison_chart(
            data=empty_data,
            x_axis='gender',
            y_metric='depression_prevalence',
            chart_type='bar'
        )
        
        assert isinstance(chart, matplotlib.figure.Figure)

    def test_create_interactive_comparison_chart_bar(self, comparison_service):
        """Test creating interactive bar chart for comparison."""
        data = comparison_service.compute_comparison_data(
            x_axis='gender',
            y_metric='depression_prevalence'
        )
        
        chart = comparison_service.create_interactive_comparison_chart(
            data=data,
            x_axis='gender',
            y_metric='depression_prevalence',
            chart_type='bar'
        )
        
        # Import plotly here to avoid issues if not installed
        import plotly.graph_objects as go
        assert isinstance(chart, go.Figure)

    def test_create_interactive_comparison_chart_line(self, comparison_service):
        """Test creating interactive line chart for comparison."""
        data = comparison_service.compute_comparison_data(
            x_axis='year_of_study',
            y_metric='anxiety_prevalence'
        )
        
        chart = comparison_service.create_interactive_comparison_chart(
            data=data,
            x_axis='year_of_study',
            y_metric='anxiety_prevalence',
            chart_type='line'
        )
        
        import plotly.graph_objects as go
        assert isinstance(chart, go.Figure)

    def test_create_interactive_comparison_chart_empty_data(self, comparison_service):
        """Test interactive chart creation with empty data."""
        empty_data = pd.DataFrame()
        
        chart = comparison_service.create_interactive_comparison_chart(
            data=empty_data,
            x_axis='gender',
            y_metric='depression_prevalence',
            chart_type='bar'
        )
        
        import plotly.graph_objects as go
        assert isinstance(chart, go.Figure)

    def test_create_comparison_dashboard(self, comparison_service):
        """Test creating comprehensive comparison dashboard."""
        data = comparison_service.compute_comparison_data(
            x_axis='gender',
            y_metric='depression_prevalence'
        )
        
        dashboard = comparison_service.create_comparison_dashboard(
            data=data,
            x_axis='gender',
            y_metric='depression_prevalence'
        )
        
        import plotly.graph_objects as go
        assert isinstance(dashboard, go.Figure)

    def test_create_comparison_dashboard_empty_data(self, comparison_service):
        """Test dashboard creation with empty data."""
        empty_data = pd.DataFrame()
        
        dashboard = comparison_service.create_comparison_dashboard(
            data=empty_data,
            x_axis='gender',
            y_metric='depression_prevalence'
        )
        
        import plotly.graph_objects as go
        assert isinstance(dashboard, go.Figure)

    def test_create_multi_metric_comparison(self, comparison_service):
        """Test creating multi-metric comparison chart."""
        multi_chart = comparison_service.create_multi_metric_comparison(
            x_axis='gender'
        )
        
        import plotly.graph_objects as go
        assert isinstance(multi_chart, go.Figure)

    def test_create_multi_metric_comparison_with_filters(self, comparison_service):
        """Test creating multi-metric comparison with filters."""
        filters = {'division': 'Dhaka'}
        
        multi_chart = comparison_service.create_multi_metric_comparison(
            x_axis='gender',
            filters=filters
        )
        
        import plotly.graph_objects as go
        assert isinstance(multi_chart, go.Figure)

    def test_get_chart_type_recommendation(self, comparison_service):
        """Test automatic chart type recommendation."""
        # Categorical X-axis should recommend bar chart
        chart_type = comparison_service.get_chart_type_recommendation('gender')
        assert chart_type == 'bar'
        
        # Temporal X-axis should recommend line chart
        chart_type = comparison_service.get_chart_type_recommendation('year_of_study')
        assert chart_type == 'line'


class TestInsightGenerator:
    """Test class for InsightGenerator following TDD approach."""

    @pytest.fixture
    def sample_comparison_data(self):
        """Create sample comparison data for testing."""
        return pd.DataFrame({
            'gender': ['Male', 'Female'],
            'depression_prevalence': [45.5, 58.0]
        })

    def test_generate_insight_depression_by_gender(self, sample_comparison_data):
        """Test generating insight for depression by gender."""
        insight = InsightGenerator.generate_insight(
            data=sample_comparison_data,
            x_axis='gender',
            y_metric='depression_prevalence'
        )
        
        assert isinstance(insight, str)
        assert len(insight) > 0
        assert 'Female' in insight
        assert 'Male' in insight
        assert '12.5%' in insight or '12.5' in insight  # Difference

    def test_generate_insight_highest_lowest(self):
        """Test insight generation identifies highest and lowest values."""
        data = pd.DataFrame({
            'division': ['Arts', 'Science', 'Engineering'],
            'anxiety_prevalence': [30.0, 55.0, 42.0]
        })
        
        insight = InsightGenerator.generate_insight(
            data=data,
            x_axis='division',
            y_metric='anxiety_prevalence'
        )
        
        assert 'Science' in insight  # Highest
        assert 'Arts' in insight    # Lowest
        assert '55' in insight or '55.0' in insight

    def test_generate_insight_empty_data(self):
        """Test insight generation with empty data."""
        empty_data = pd.DataFrame()
        
        insight = InsightGenerator.generate_insight(
            data=empty_data,
            x_axis='gender',
            y_metric='depression_prevalence'
        )
        
        assert isinstance(insight, str)
        assert 'no data' in insight.lower() or 'insufficient' in insight.lower()

    def test_generate_insight_single_category(self):
        """Test insight generation with single category."""
        single_data = pd.DataFrame({
            'gender': ['Male'],
            'depression_prevalence': [45.5]
        })
        
        insight = InsightGenerator.generate_insight(
            data=single_data,
            x_axis='gender',
            y_metric='depression_prevalence'
        )
        
        assert isinstance(insight, str)
        assert 'Male' in insight
        assert '45.5' in insight

    def test_generate_insight_help_seeking_metric(self):
        """Test insight generation for help-seeking metric."""
        data = pd.DataFrame({
            'university': ['Uni A', 'Uni B'],
            'help_seeking_proportion': [35.0, 48.0]
        })
        
        insight = InsightGenerator.generate_insight(
            data=data,
            x_axis='university',
            y_metric='help_seeking_proportion'
        )
        
        assert isinstance(insight, str)
        assert 'Uni B' in insight  # Higher help-seeking
        assert 'Uni A' in insight

    def test_format_metric_name(self):
        """Test metric name formatting for insights."""
        assert InsightGenerator.format_metric_name('depression_prevalence') == 'depression prevalence'
        assert InsightGenerator.format_metric_name('anxiety_prevalence') == 'anxiety prevalence'
        assert InsightGenerator.format_metric_name('help_seeking_proportion') == 'help-seeking rate'

    def test_calculate_percentage_difference(self):
        """Test percentage difference calculation."""
        diff = InsightGenerator.calculate_percentage_difference(45.5, 58.0)
        assert abs(diff - 12.5) < 0.1  # Should be approximately 12.5%

    def test_get_comparison_summary(self):
        """Test getting summary statistics for comparison data."""
        data = pd.DataFrame({
            'division': ['Arts', 'Science', 'Engineering'],
            'depression_prevalence': [30.0, 55.0, 42.0]
        })
        
        summary = InsightGenerator.get_comparison_summary(
            data=data,
            x_axis='division',
            y_metric='depression_prevalence'
        )
        
        assert isinstance(summary, dict)
        assert 'highest' in summary
        assert 'lowest' in summary
        assert 'average' in summary
        assert 'range' in summary
        
        assert summary['highest']['category'] == 'Science'
        assert summary['lowest']['category'] == 'Arts'


class TestComparisonFiltering:
    """Test class for comparison filtering functionality."""

    @pytest.fixture
    def sample_service_with_data(self):
        """Create service with more complex data for filtering tests."""
        # More complex data for filtering
        sample_data = pd.DataFrame({
            'gender': ['Male'] * 4 + ['Female'] * 4,
            'division': ['Dhaka', 'Sylhet'] * 4,
            'course': ['Computer Science', 'Medicine'] * 4,
            'depression': ['Yes', 'No', 'Yes', 'No'] * 2,
            'anxiety': ['Yes', 'Yes', 'No', 'No'] * 2,
            'university': ['Uni A'] * 6 + ['Uni B'] * 2,
            'year_of_study': ['1st Year'] * 2 + ['2nd Year'] * 2 + ['3rd Year'] * 4,
            'panic_attack': ['Yes', 'No'] * 4,
            'sought_specialist_treatment': ['Yes', 'No'] * 4,
            'financial_stress_level': ['Low', 'High'] * 4,
            'family_history_mental_illness': ['Yes', 'No'] * 4
        })
        
        # Create a mock repository
        mock_repo = Mock(spec=StudentMentalHealthRepository)
        mock_repo.get_all_data.return_value = sample_data
        return ComparisonAnalysisService(mock_repo)

    def test_apply_filters_gender_filter(self, sample_service_with_data):
        """Test applying gender filter to comparison data."""
        filters = {'gender': 'Female'}
        
        result = sample_service_with_data.compute_comparison_data(
            x_axis='division',
            y_metric='depression_prevalence',
            filters=filters
        )
        
        # Should only include female data
        assert len(result) >= 1

    def test_apply_filters_multiple_filters(self, sample_service_with_data):
        """Test applying multiple filters simultaneously."""
        filters = {
            'gender': 'Male',
            'university': 'Uni A'
        }
        
        result = sample_service_with_data.compute_comparison_data(
            x_axis='division',
            y_metric='anxiety_prevalence',
            filters=filters
        )
        
        assert isinstance(result, pd.DataFrame)

    def test_apply_filters_no_matching_data(self, sample_service_with_data):
        """Test behavior when filters result in no matching data."""
        filters = {
            'gender': 'Other',  # Non-existent value
            'university': 'Uni C'
        }
        
        result = sample_service_with_data.compute_comparison_data(
            x_axis='division',
            y_metric='depression_prevalence',
            filters=filters
        )
        
        # Should return empty DataFrame or handle gracefully
        assert isinstance(result, pd.DataFrame)