# Plotting and visualization functions
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.figure
from typing import Dict, Any, Optional
import plotly.express as px
import plotly.graph_objects as go
from utils.logger import get_logger
from services.geographic_analysis import GeographicAnalysisService

logger = get_logger(__name__)


def plot_depression_prevalence(df: pd.DataFrame) -> matplotlib.figure.Figure:
    """
    Plot overall depression prevalence as a pie chart.
    
    Args:
        df: DataFrame with 'depression' column containing Yes/No values
        
    Returns:
        matplotlib.figure.Figure: The generated plot figure
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Check if required column exists
    if 'depression' not in df.columns:
        logger.warning("Column 'depression' not found in DataFrame for plot_depression_prevalence")
        ax.text(0.5, 0.5, 'No depression data available', 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Depression Prevalence - No Data')
        return fig
    
    # Handle empty DataFrame
    if df.empty:
        logger.warning("Empty DataFrame provided to plot_depression_prevalence")
        ax.text(0.5, 0.5, 'No data available', 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Depression Prevalence - No Data')
        return fig
    
    # Count depression values
    depression_counts = df['depression'].value_counts()
    
    if depression_counts.empty:
        ax.text(0.5, 0.5, 'No depression data available', 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Depression Prevalence - No Data')
        return fig
    
    # Create pie chart
    colors = ['#ff9999', '#66b3ff']
    pie_result = ax.pie(list(depression_counts.values), 
                       labels=list(depression_counts.index),
                       autopct='%1.1f%%',
                       colors=colors,
                       startangle=90)
    
    ax.set_title('Depression Prevalence', fontsize=14, fontweight='bold')
    
    return fig


def plot_depression_by_gender(df: pd.DataFrame) -> matplotlib.figure.Figure:
    """
    Plot depression prevalence by gender as a grouped bar chart.
    
    Args:
        df: DataFrame with 'depression' and 'gender' columns
        
    Returns:
        matplotlib.figure.Figure: The generated plot figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Check if required columns exist
    required_cols = ['depression', 'gender']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        logger.warning(f"Columns {missing_cols} not found in DataFrame for plot_depression_by_gender")
        ax.text(0.5, 0.5, f'Missing columns: {", ".join(missing_cols)}', 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Depression by Gender - Missing Data')
        return fig
    
    # Handle empty DataFrame
    if df.empty:
        logger.warning("Empty DataFrame provided to plot_depression_by_gender")
        ax.text(0.5, 0.5, 'No data available', 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Depression by Gender - No Data')
        return fig
    
    # Group by gender and depression, count occurrences
    grouped = df.groupby(['gender', 'depression']).size().unstack(fill_value=0)
    
    if grouped.empty:
        ax.text(0.5, 0.5, 'No data to display', 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Depression by Gender - No Data')
        return fig
    
    # Create grouped bar chart
    grouped.plot(kind='bar', ax=ax, color=['#66b3ff', '#ff9999'], width=0.7)
    
    ax.set_title('Depression Prevalence by Gender', fontsize=14, fontweight='bold')
    ax.set_xlabel('Gender', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    ax.legend(title='Depression', loc='upper right')
    ax.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    return fig


def plot_depression_by_division(df: pd.DataFrame) -> matplotlib.figure.Figure:
    """
    Plot depression prevalence by division as a grouped bar chart.
    
    Args:
        df: DataFrame with 'depression' and 'division' columns
        
    Returns:
        matplotlib.figure.Figure: The generated plot figure
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Check if required columns exist
    required_cols = ['depression', 'division']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        logger.warning(f"Columns {missing_cols} not found in DataFrame for plot_depression_by_division")
        ax.text(0.5, 0.5, f'Missing columns: {", ".join(missing_cols)}', 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Depression by Division - Missing Data')
        return fig
    
    # Handle empty DataFrame
    if df.empty:
        logger.warning("Empty DataFrame provided to plot_depression_by_division")
        ax.text(0.5, 0.5, 'No data available', 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Depression by Division - No Data')
        return fig
    
    # Group by division and depression, count occurrences
    grouped = df.groupby(['division', 'depression']).size().unstack(fill_value=0)
    
    if grouped.empty:
        ax.text(0.5, 0.5, 'No data to display', 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Depression by Division - No Data')
        return fig
    
    # Create grouped bar chart
    grouped.plot(kind='bar', ax=ax, color=['#66b3ff', '#ff9999'], width=0.7)
    
    ax.set_title('Depression Prevalence by Division', fontsize=14, fontweight='bold')
    ax.set_xlabel('Division', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    ax.legend(title='Depression', loc='upper right')
    ax.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    return fig


def plot_depression_by_year_of_study(df: pd.DataFrame) -> matplotlib.figure.Figure:
    """
    Plot depression prevalence by year of study as a grouped bar chart.
    
    Args:
        df: DataFrame with 'depression' and 'year_of_study' columns
        
    Returns:
        matplotlib.figure.Figure: The generated plot figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Check if required columns exist
    required_cols = ['depression', 'year_of_study']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        logger.warning(f"Columns {missing_cols} not found in DataFrame for plot_depression_by_year_of_study")
        ax.text(0.5, 0.5, f'Missing columns: {", ".join(missing_cols)}', 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Depression by Year of Study - Missing Data')
        return fig
    
    # Handle empty DataFrame
    if df.empty:
        logger.warning("Empty DataFrame provided to plot_depression_by_year_of_study")
        ax.text(0.5, 0.5, 'No data available', 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Depression by Year of Study - No Data')
        return fig
    
    # Group by year of study and depression, count occurrences
    grouped = df.groupby(['year_of_study', 'depression']).size().unstack(fill_value=0)
    
    if grouped.empty:
        ax.text(0.5, 0.5, 'No data to display', 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Depression by Year of Study - No Data')
        return fig
    
    # Create grouped bar chart
    grouped.plot(kind='bar', ax=ax, color=['#66b3ff', '#ff9999'], width=0.7)
    
    ax.set_title('Depression Prevalence by Year of Study', fontsize=14, fontweight='bold')
    ax.set_xlabel('Year of Study', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    ax.legend(title='Depression', loc='upper right')
    ax.tick_params(axis='x', rotation=0)
    
    plt.tight_layout()
    return fig


def plot_monthly_depression_trend(df: pd.DataFrame) -> matplotlib.figure.Figure:
    """
    Plot monthly depression trend over time as a line chart.
    Groups by year+month from timestamp column and shows percentage of "Yes" responses.
    
    Args:
        df: DataFrame with 'depression' and 'timestamp' columns
        
    Returns:
        matplotlib.figure.Figure: The generated plot figure
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Check if required columns exist
    required_cols = ['depression', 'timestamp']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        logger.warning(f"Columns {missing_cols} not found in DataFrame for plot_monthly_depression_trend")
        ax.text(0.5, 0.5, f'Missing columns: {", ".join(missing_cols)}', 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Monthly Depression Trend - Missing Data')
        return fig
    
    # Handle empty DataFrame
    if df.empty:
        logger.warning("Empty DataFrame provided to plot_monthly_depression_trend")
        ax.text(0.5, 0.5, 'No data available', 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Monthly Depression Trend - No Data')
        return fig
    
    # Create a copy to avoid mutating input DataFrame
    df_copy = df.copy()
    
    # Ensure timestamp is datetime
    try:
        df_copy['timestamp'] = pd.to_datetime(df_copy['timestamp'])
    except Exception as e:
        logger.warning(f"Error converting timestamp to datetime: {e}")
        ax.text(0.5, 0.5, 'Invalid timestamp data', 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Monthly Depression Trend - Invalid Data')
        return fig
    
    # Extract year-month from timestamp
    df_copy['year_month'] = df_copy['timestamp'].dt.strftime('%Y-%m')  # type: ignore
    
    # Group by year-month and calculate depression percentage
    monthly_data = df_copy.groupby('year_month')['depression'].agg([
        lambda x: (x == 'Yes').sum(),  # Count of "Yes"
        'count'  # Total count
    ]).rename(columns={'<lambda_0>': 'yes_count', 'count': 'total_count'})
    
    if monthly_data.empty:
        ax.text(0.5, 0.5, 'No data to display', 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Monthly Depression Trend - No Data')
        return fig
    
    # Calculate percentage
    monthly_data['yes_percentage'] = (monthly_data['yes_count'] / monthly_data['total_count']) * 100
    
    # Plot the trend
    x_vals = range(len(monthly_data))
    ax.plot(x_vals, monthly_data['yes_percentage'], marker='o', linewidth=2, markersize=6, color='#ff6b6b')
    
    # Format x-axis labels
    ax.set_xticks(x_vals)
    ax.set_xticklabels([str(period) for period in monthly_data.index], rotation=45)
    
    ax.set_title('Monthly Depression Trend', fontsize=14, fontweight='bold')
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Depression Rate (%)', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 100)
    
    plt.tight_layout()
    return fig





def plot_depression_choropleth(df: pd.DataFrame) -> Optional[go.Figure]:
    """
    Create a choropleth map showing depression rates by Bangladesh division.
    
    Args:
        df: DataFrame with mental health survey data including 'division' and 'depression' columns
        
    Returns:
        plotly.graph_objects.Figure: Interactive choropleth map visualization
    """
    logger.info("Creating Bangladesh choropleth map for depression rates")
    
    # Initialize geographic analysis service
    geo_service = GeographicAnalysisService()
    
    # Load GeoJSON data
    geojson_data = geo_service.load_bangladesh_geojson()
    
    if not geojson_data:
        logger.error("Could not load GeoJSON data - creating empty map")
        fig = go.Figure()
        fig.update_layout(
            title="Bangladesh Depression Rates Map - Data Not Available",
            annotations=[
                dict(
                    text="GeoJSON data could not be loaded",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, xanchor='center', yanchor='middle',
                    showarrow=False, font=dict(size=16)
                )
            ]
        )
        return fig
    
    # Calculate depression rates by division
    division_rates = geo_service.calculate_division_depression_rates(df)
    
    # Prepare data for choropleth map
    division_names = []
    depression_rates = []
    
    # Extract division names from GeoJSON and match with calculated rates
    for feature in geojson_data.get('features', []):
        division_name = feature['properties']['ADM1_EN']
        division_names.append(division_name)
        
        # Get depression rate for this division, default to 0 if no data
        rate = division_rates.get(division_name, 0.0)
        depression_rates.append(rate)
    
    # Create DataFrame for choropleth
    choropleth_df = pd.DataFrame({
        'division': division_names,
        'depression_rate': depression_rates
    })
    
    # Create choropleth map using plotly express
    try:
        fig = px.choropleth_map(
            choropleth_df,
            geojson=geojson_data,
            locations='division',
            color='depression_rate',
            featureidkey="properties.ADM1_EN",
            color_continuous_scale='RdYlBu_r',  # Red for high depression, Blue for low
            range_color=(0, max(depression_rates) if depression_rates else 100),
            labels={'depression_rate': 'Depression Rate (%)', 'division': 'Division'},
            title='Depression Rates by Division in Bangladesh'
        )
        
        # Update layout for better appearance
        fig.update_layout(
            title_x=0.5,
            title_font_size=20,
            title_font_color='#2c3e50',
            font=dict(size=12),
            height=600,
            margin=dict(l=0, r=0, t=50, b=0)
        )
        
        # Update color bar
        fig.update_coloraxes(
            colorbar_title_text="Depression Rate (%)",
            colorbar_title_side="right",
            colorbar_thickness=20
        )
        
        logger.info(f"Created choropleth map with {len(division_names)} divisions")
        return fig
        
    except Exception as e:
        logger.error(f"Error creating choropleth map: {e}")
        # Return simple fallback figure that doesn't use problematic Plotly features
        try:
            # Create a simple scatter plot as fallback
            fig = go.Figure()
            
            # Add scatter trace for each division
            for i, (division, rate) in enumerate(zip(division_names, depression_rates)):
                fig.add_trace(go.Scatter(
                    x=[i],
                    y=[rate],
                    mode='markers+text',
                    marker=dict(size=20, color=rate, colorscale='RdYlBu_r', cmax=100, cmin=0),
                    text=[division],
                    textposition='middle center',
                    name=division,
                    showlegend=False
                ))
            
            fig.update_layout(
                title="Depression Rates by Division (Fallback View)",
                xaxis=dict(title="Division Index", showticklabels=False),
                yaxis=dict(title="Depression Rate (%)"),
                height=400
            )
            
            logger.info("Created fallback scatter plot for choropleth map")
            return fig
            
        except Exception as fallback_error:
            logger.error(f"Error creating fallback figure: {fallback_error}")
            # Ultimate fallback - create a minimal figure manually
            try:
                # Create the most basic figure possible
                fig = go.Figure(data=[], layout={})
                logger.info("Created minimal empty figure as ultimate fallback")
                return fig
            except Exception as ultimate_error:
                # If even that fails, return None to indicate failure
                logger.error(f"Could not create any Plotly figure: {ultimate_error}")
                return None
