"""
Comparison Analysis Service for Student Mental Health Dashboard.

This module provides functionality for flexible X vs Y comparisons,
allowing researchers to explore relationships between different variables
and mental health metrics.
"""

import logging
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.figure
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Any, Tuple, Union
from db.repository import StudentMentalHealthRepository

# Configure logging
logger = logging.getLogger(__name__)


class ComparisonAnalysisService:
    """Service for handling comparison analysis between different variables and metrics."""
    
    def __init__(self, repository: StudentMentalHealthRepository):
        """Initialize the comparison analysis service.
        
        Args:
            repository: Database repository for accessing student data
        """
        self.repository = repository
        logger.info("ComparisonAnalysisService initialized")
    
    def get_available_x_axis_options(self) -> List[str]:
        """Get available options for X-axis variables.
        
        Returns:
            List of available X-axis variable names
        """
        options = [
            'gender',
            'division',
            'university', 
            'course',
            'year_of_study',
            'financial_stress_level',
            'family_history_mental_illness'
        ]
        logger.debug(f"Available X-axis options: {options}")
        return options
    
    def get_available_y_metrics(self) -> Dict[str, str]:
        """Get available Y-axis metrics with display names.
        
        Returns:
            Dictionary mapping metric keys to display names
        """
        metrics = {
            'depression_prevalence': 'Depression Prevalence (%)',
            'anxiety_prevalence': 'Anxiety Prevalence (%)',
            'panic_attack_prevalence': 'Panic Attack Prevalence (%)',
            'help_seeking_proportion': 'Help-Seeking Rate (%)'
        }
        logger.debug(f"Available Y-metrics: {list(metrics.keys())}")
        return metrics
    
    def compute_comparison_data(self, x_axis: str, y_metric: str, 
                              filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """Compute comparison data for given X-axis and Y-metric.
        
        Args:
            x_axis: Variable to use for X-axis grouping
            y_metric: Metric to calculate for Y-axis
            filters: Optional additional filters to apply
            
        Returns:
            DataFrame with comparison data
            
        Raises:
            ValueError: If invalid x_axis or y_metric provided
        """
        logger.info(f"Computing comparison data: {x_axis} vs {y_metric}")
        
        # Validate inputs
        if x_axis not in self.get_available_x_axis_options():
            raise ValueError(f"Invalid x_axis: {x_axis}")
        
        if y_metric not in self.get_available_y_metrics():
            raise ValueError(f"Invalid y_metric: {y_metric}")
        
        # Get data from repository
        df = self.repository.get_all_data()
        logger.debug(f"Retrieved {len(df)} records from repository")
        
        # Apply filters if provided
        if filters:
            for filter_col, filter_val in filters.items():
                if filter_col in df.columns:
                    df = df[df[filter_col] == filter_val]
                    logger.debug(f"Applied filter: {filter_col} = {filter_val}, remaining records: {len(df)}")
        
        if df.empty:
            logger.warning("No data remaining after applying filters")
            return pd.DataFrame()
        
        # Group by X-axis variable and calculate metric
        grouped_data = []
        for category in df[x_axis].unique():
            category_data = df[df[x_axis] == category]
            metric_value = self._calculate_metric(category_data, y_metric)
            
            grouped_data.append({
                x_axis: category,
                y_metric: metric_value
            })
        
        result_df = pd.DataFrame(grouped_data)
        logger.info(f"Computed comparison data with {len(result_df)} categories")
        
        return result_df
    
    def _calculate_metric(self, data: pd.DataFrame, metric: str) -> float:
        """Calculate the specified metric for a subset of data.
        
        Args:
            data: Subset of data to calculate metric for
            metric: Metric to calculate
            
        Returns:
            Calculated metric value as percentage
        """
        if data.empty:
            return 0.0
        
        total_count = len(data)
        
        if metric == 'depression_prevalence':
            positive_count = len(data[data['depression'] == 'Yes'])
        elif metric == 'anxiety_prevalence':
            positive_count = len(data[data['anxiety'] == 'Yes'])
        elif metric == 'panic_attack_prevalence':
            positive_count = len(data[data['panic_attack'] == 'Yes'])
        elif metric == 'help_seeking_proportion':
            positive_count = len(data[data['sought_specialist_treatment'] == 'Yes'])
        else:
            logger.error(f"Unknown metric: {metric}")
            return 0.0
        
        percentage = (positive_count / total_count) * 100
        logger.debug(f"Calculated {metric}: {positive_count}/{total_count} = {percentage:.1f}%")
        
        return round(percentage, 1)
    
    def get_chart_type_recommendation(self, x_axis: str) -> str:
        """Recommend chart type based on X-axis variable.
        
        Args:
            x_axis: X-axis variable name
            
        Returns:
            Recommended chart type ('bar' or 'line')
        """
        # Temporal variables work better with line charts
        temporal_variables = ['year_of_study']
        
        if x_axis in temporal_variables:
            return 'line'
        else:
            return 'bar'
    
    def create_comparison_chart(self, data: pd.DataFrame, x_axis: str, 
                              y_metric: str, chart_type: str = 'bar') -> matplotlib.figure.Figure:
        """Create comparison chart from data.
        
        Args:
            data: Comparison data
            x_axis: X-axis variable name
            y_metric: Y-metric name
            chart_type: Type of chart ('bar' or 'line')
            
        Returns:
            Matplotlib figure object
        """
        logger.info(f"Creating {chart_type} chart for {x_axis} vs {y_metric}")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if data.empty:
            ax.text(0.5, 0.5, 'No data available for the selected filters', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title(f"{self.get_available_y_metrics().get(y_metric, y_metric)} by {x_axis.replace('_', ' ').title()}")
            return fig
        
        # Set color palette
        colors = sns.color_palette("husl", len(data))
        
        if chart_type == 'bar':
            bars = ax.bar(data[x_axis], data[y_metric], color=colors)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}%',
                       ha='center', va='bottom')
        
        elif chart_type == 'line':
            ax.plot(data[x_axis], data[y_metric], marker='o', linewidth=2, markersize=8)
            
            # Add value labels on points
            for i, (x, y) in enumerate(zip(data[x_axis], data[y_metric])):
                ax.annotate(f'{y:.1f}%', (x, y), textcoords="offset points", 
                           xytext=(0,10), ha='center')
        
        # Customize chart
        ax.set_xlabel(x_axis.replace('_', ' ').title())
        ax.set_ylabel(self.get_available_y_metrics().get(y_metric, y_metric))
        ax.set_title(f"{self.get_available_y_metrics().get(y_metric, y_metric)} by {x_axis.replace('_', ' ').title()}")
        
        # Rotate x-axis labels if needed
        if len(data) > 4:
            plt.xticks(rotation=45, ha='right')
        
        # Set y-axis to percentage scale
        ax.set_ylim(0, max(100, data[y_metric].max() * 1.1) if not data.empty else 100)
        
        plt.tight_layout()
        
        logger.info("Chart created successfully")
        return fig
    
    def create_interactive_comparison_chart(self, data: pd.DataFrame, x_axis: str, 
                                           y_metric: str, chart_type: str = 'bar') -> go.Figure:
        """Create interactive comparison chart using Plotly.
        
        Args:
            data: Comparison data
            x_axis: X-axis variable name
            y_metric: Y-metric name
            chart_type: Type of chart ('bar' or 'line')
            
        Returns:
            Plotly figure object
        """
        logger.info(f"Creating interactive {chart_type} chart for {x_axis} vs {y_metric}")
        
        if data.empty:
            fig = go.Figure()
            fig.add_annotation(
                x=0.5, y=0.5,
                text="No data available for the selected filters",
                showarrow=False,
                xref="paper", yref="paper",
                font=dict(size=16, color="gray")
            )
            fig.update_layout(
                title=f"{self.get_available_y_metrics().get(y_metric, y_metric)} by {x_axis.replace('_', ' ').title()}",
                height=400
            )
            return fig
        
        # Sort data for better visualization
        data_sorted = data.sort_values(y_metric, ascending=False)
        
        # Create color scale based on values
        colors = px.colors.qualitative.Set3[:len(data_sorted)]
        
        if chart_type == 'bar':
            fig = go.Figure()
            
            # Add bar chart with hover information
            fig.add_trace(go.Bar(
                x=data_sorted[x_axis],
                y=data_sorted[y_metric],
                marker_color=colors,
                text=[f"{val:.1f}%" for val in data_sorted[y_metric]],
                textposition='outside',
                hovertemplate=(
                    f"<b>%{{x}}</b><br>"
                    f"{self.get_available_y_metrics().get(y_metric, y_metric)}: %{{y:.1f}}%<br>"
                    "<extra></extra>"
                ),
                name=self.get_available_y_metrics().get(y_metric, y_metric)
            ))
            
        elif chart_type == 'line':
            fig = go.Figure()
            
            # Add line chart with markers
            fig.add_trace(go.Scatter(
                x=data_sorted[x_axis],
                y=data_sorted[y_metric],
                mode='lines+markers+text',
                line=dict(width=3, color='#1f77b4'),
                marker=dict(size=10, color='#1f77b4'),
                text=[f"{val:.1f}%" for val in data_sorted[y_metric]],
                textposition='top center',
                hovertemplate=(
                    f"<b>%{{x}}</b><br>"
                    f"{self.get_available_y_metrics().get(y_metric, y_metric)}: %{{y:.1f}}%<br>"
                    "<extra></extra>"
                ),
                name=self.get_available_y_metrics().get(y_metric, y_metric)
            ))
        
        # Update layout with professional styling
        fig.update_layout(
            title={
                'text': f"{self.get_available_y_metrics().get(y_metric, y_metric)} by {x_axis.replace('_', ' ').title()}",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'family': 'Arial, sans-serif'}
            },
            xaxis={
                'title': x_axis.replace('_', ' ').title(),
                'tickangle': -45 if len(data_sorted) > 4 else 0,
                'title_font': {'size': 14},
                'tickfont': {'size': 12}
            },
            yaxis={
                'title': self.get_available_y_metrics().get(y_metric, y_metric),
                'range': [0, max(100, data_sorted[y_metric].max() * 1.1) if not data_sorted.empty else 100],
                'title_font': {'size': 14},
                'tickfont': {'size': 12}
            },
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=500,
            margin=dict(t=80, b=100, l=80, r=40),
            showlegend=False,
            hovermode='x unified' if chart_type == 'line' else 'closest'
        )
        
        # Add grid lines
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        
        logger.info("Interactive chart created successfully")
        return fig
    
    def create_comparison_dashboard(self, data: pd.DataFrame, x_axis: str, y_metric: str) -> go.Figure:
        """Create comprehensive interactive dashboard with multiple views.
        
        Args:
            data: Comparison data
            x_axis: X-axis variable name
            y_metric: Y-metric name
            
        Returns:
            Plotly figure with subplots
        """
        logger.info(f"Creating comparison dashboard for {x_axis} vs {y_metric}")
        
        if data.empty:
            fig = go.Figure()
            fig.add_annotation(
                x=0.5, y=0.5,
                text="No data available for comprehensive dashboard",
                showarrow=False,
                xref="paper", yref="paper",
                font=dict(size=16, color="gray")
            )
            return fig
        
        # Create subplots: main chart + summary stats
        fig = make_subplots(
            rows=2, cols=2,
            specs=[[{"colspan": 2}, None],
                   [{}, {}]],
            subplot_titles=(
                f"{self.get_available_y_metrics().get(y_metric, y_metric)} by {x_axis.replace('_', ' ').title()}",
                "Distribution Overview",
                "Top vs Bottom Categories"
            ),
            row_heights=[0.7, 0.3],
            vertical_spacing=0.15
        )
        
        # Sort data for visualization
        data_sorted = data.sort_values(y_metric, ascending=False)
        
        # Main comparison chart (top row)
        colors = px.colors.qualitative.Set3[:len(data_sorted)]
        fig.add_trace(
            go.Bar(
                x=data_sorted[x_axis],
                y=data_sorted[y_metric],
                marker_color=colors,
                text=[f"{val:.1f}%" for val in data_sorted[y_metric]],
                textposition='outside',
                hovertemplate=(
                    f"<b>%{{x}}</b><br>"
                    f"{self.get_available_y_metrics().get(y_metric, y_metric)}: %{{y:.1f}}%<br>"
                    "<extra></extra>"
                ),
                showlegend=False
            ),
            row=1, col=1
        )
        
        # Distribution histogram (bottom left)
        fig.add_trace(
            go.Histogram(
                x=data_sorted[y_metric],
                nbinsx=min(10, len(data_sorted)),
                marker_color='lightblue',
                opacity=0.7,
                name='Distribution',
                showlegend=False
            ),
            row=2, col=1
        )
        
        # Top vs Bottom comparison (bottom right)
        if len(data_sorted) >= 2:
            top_category = data_sorted.iloc[0]
            bottom_category = data_sorted.iloc[-1]
            
            fig.add_trace(
                go.Bar(
                    x=["Highest", "Lowest"],
                    y=[top_category[y_metric], bottom_category[y_metric]],
                    marker_color=['green', 'red'],
                    text=[f"{top_category[x_axis]}<br>{top_category[y_metric]:.1f}%", 
                          f"{bottom_category[x_axis]}<br>{bottom_category[y_metric]:.1f}%"],
                    textposition='inside',
                    showlegend=False
                ),
                row=2, col=2
            )
        
        # Update layout
        fig.update_layout(
            title={
                'text': f"Comprehensive Analysis: {self.get_available_y_metrics().get(y_metric, y_metric)}",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'family': 'Arial, sans-serif'}
            },
            height=700,
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(t=100, b=60, l=60, r=60)
        )
        
        # Update individual subplot axes
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        
        logger.info("Comparison dashboard created successfully")
        return fig
    
    def create_multi_metric_comparison(self, x_axis: str, 
                                     filters: Optional[Dict[str, Any]] = None) -> go.Figure:
        """Create comparison chart showing all metrics for selected X-axis.
        
        Args:
            x_axis: Variable to use for X-axis grouping
            filters: Optional additional filters to apply
            
        Returns:
            Plotly figure with multiple metrics
        """
        logger.info(f"Creating multi-metric comparison for {x_axis}")
        
        # Get data for all metrics
        metrics = self.get_available_y_metrics()
        all_data = []
        
        for metric_key in metrics.keys():
            try:
                metric_data = self.compute_comparison_data(x_axis, metric_key, filters)
                if not metric_data.empty:
                    metric_data['metric'] = metrics[metric_key]
                    metric_data['metric_key'] = metric_key
                    all_data.append(metric_data)
            except Exception as e:
                logger.warning(f"Could not compute data for {metric_key}: {e}")
        
        if not all_data:
            fig = go.Figure()
            fig.add_annotation(
                x=0.5, y=0.5,
                text="No data available for multi-metric comparison",
                showarrow=False,
                xref="paper", yref="paper",
                font=dict(size=16, color="gray")
            )
            return fig
        
        # Create subplot grid
        n_metrics = len(all_data)
        cols = 2 if n_metrics > 1 else 1
        rows = (n_metrics + cols - 1) // cols
        
        fig = make_subplots(
            rows=rows, cols=cols,
            subplot_titles=[data['metric'].iloc[0] for data in all_data],
            vertical_spacing=0.1,
            horizontal_spacing=0.1
        )
        
        # Add traces for each metric
        colors = px.colors.qualitative.Set1
        for i, metric_data in enumerate(all_data):
            row = (i // cols) + 1
            col = (i % cols) + 1
            
            data_sorted = metric_data.sort_values(metric_data['metric_key'].iloc[0], ascending=False)
            
            fig.add_trace(
                go.Bar(
                    x=data_sorted[x_axis],
                    y=data_sorted[metric_data['metric_key'].iloc[0]],
                    marker_color=colors[i % len(colors)],
                    name=metric_data['metric'].iloc[0],
                    text=[f"{val:.1f}%" for val in data_sorted[metric_data['metric_key'].iloc[0]]],
                    textposition='outside',
                    showlegend=False
                ),
                row=row, col=col
            )
        
        # Update layout
        fig.update_layout(
            title={
                'text': f"Multi-Metric Mental Health Analysis by {x_axis.replace('_', ' ').title()}",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'family': 'Arial, sans-serif'}
            },
            height=300 * rows + 100,
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(t=100, b=60, l=60, r=60)
        )
        
        # Update axes for all subplots
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray', range=[0, 100])
        
        logger.info("Multi-metric comparison created successfully")
        return fig


class InsightGenerator:
    """Generate text insights from comparison data."""
    
    @staticmethod
    def generate_insight(data: pd.DataFrame, x_axis: str, y_metric: str) -> str:
        """Generate text insight from comparison data.
        
        Args:
            data: Comparison data
            x_axis: X-axis variable name
            y_metric: Y-metric name
            
        Returns:
            Generated insight text
        """
        logger.info(f"Generating insight for {x_axis} vs {y_metric}")
        
        if data.empty:
            return "No data available for the selected filters to generate insights."
        
        if len(data) == 1:
            row = data.iloc[0]
            metric_name = InsightGenerator.format_metric_name(y_metric)
            return (f"{row[x_axis]} shows a {metric_name} rate of {row[y_metric]:.1f}% "
                   f"in the filtered dataset.")
        
        # Get summary statistics
        summary = InsightGenerator.get_comparison_summary(data, x_axis, y_metric)
        metric_name = InsightGenerator.format_metric_name(y_metric)
        
        # Generate insight based on comparison
        insights = []
        
        # Highest and lowest
        insights.append(
            f"{summary['highest']['category']} has the highest {metric_name} rate "
            f"at {summary['highest']['value']:.1f}%."
        )
        
        insights.append(
            f"{summary['lowest']['category']} has the lowest {metric_name} rate "
            f"at {summary['lowest']['value']:.1f}%."
        )
        
        # Difference between highest and lowest
        if len(data) >= 2:
            diff = summary['highest']['value'] - summary['lowest']['value']
            insights.append(
                f"This represents a {diff:.1f} percentage point difference "
                f"between the highest and lowest categories."
            )
        
        # Average insight
        insights.append(
            f"The average {metric_name} rate across all {x_axis.replace('_', ' ')} "
            f"categories is {summary['average']:.1f}%."
        )
        
        result = " ".join(insights)
        logger.info("Insight generated successfully")
        
        return result
    
    @staticmethod
    def format_metric_name(metric: str) -> str:
        """Format metric name for display in insights.
        
        Args:
            metric: Metric key name
            
        Returns:
            Formatted metric name
        """
        format_map = {
            'depression_prevalence': 'depression prevalence',
            'anxiety_prevalence': 'anxiety prevalence', 
            'panic_attack_prevalence': 'panic attack prevalence',
            'help_seeking_proportion': 'help-seeking rate'
        }
        return format_map.get(metric, metric.replace('_', ' '))
    
    @staticmethod
    def calculate_percentage_difference(value1: float, value2: float) -> float:
        """Calculate percentage point difference between two values.
        
        Args:
            value1: First value
            value2: Second value
            
        Returns:
            Absolute difference in percentage points
        """
        return abs(value1 - value2)
    
    @staticmethod
    def get_comparison_summary(data: pd.DataFrame, x_axis: str, y_metric: str) -> Dict[str, Any]:
        """Get summary statistics for comparison data.
        
        Args:
            data: Comparison data
            x_axis: X-axis variable name
            y_metric: Y-metric name
            
        Returns:
            Dictionary with summary statistics
        """
        if data.empty:
            return {}
        
        max_row = data.loc[data[y_metric].idxmax()]
        min_row = data.loc[data[y_metric].idxmin()]
        
        summary = {
            'highest': {
                'category': max_row[x_axis],
                'value': max_row[y_metric]
            },
            'lowest': {
                'category': min_row[x_axis],
                'value': min_row[y_metric]
            },
            'average': data[y_metric].mean(),
            'range': data[y_metric].max() - data[y_metric].min()
        }
        
        return summary