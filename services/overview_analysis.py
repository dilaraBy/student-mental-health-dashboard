# Overview analysis functions for KPIs and summary statistics
import pandas as pd
from typing import Dict, Union, Any
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from utils.logger import get_logger

logger = get_logger(__name__)


def compute_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute key performance indicators from mental health survey data.
    
    Args:
        df: DataFrame with mental health survey responses
        
    Returns:
        Dictionary containing:
        - total_students: Total number of students
        - pct_depressed: Percentage with depression 
        - pct_anxious: Percentage with anxiety
        - pct_panic: Percentage with panic attacks
        - pct_sought_help: Percentage who sought treatment
    """
    logger.debug("Computing KPIs from DataFrame with shape: %s", df.shape)
    
    # Handle empty DataFrame
    if df.empty:
        logger.info("Empty DataFrame provided, returning zero values")
        return {
            'total_students': 0,
            'pct_depressed': 0.0,
            'pct_anxious': 0.0,
            'pct_panic': 0.0,
            'pct_sought_help': 0.0
        }
    
    # Work on a copy to avoid mutating input
    df_copy = df.copy()
    
    # Calculate total students
    total_students = len(df_copy)
    logger.debug("Total students: %d", total_students)
    
    # Initialize results
    kpis = {'total_students': total_students}
    
    # Define column mappings and their corresponding KPI names
    column_mappings = {
        'depression': 'pct_depressed',
        'anxiety': 'pct_anxious', 
        'panic_attack': 'pct_panic',
        'sought_specialist_treatment': 'pct_sought_help'
    }
    
    # Calculate percentages for each condition
    for col_name, kpi_name in column_mappings.items():
        if col_name in df_copy.columns:
            # Count "Yes" responses
            yes_count = (df_copy[col_name] == 'Yes').sum()
            percentage = (yes_count / total_students) * 100 if total_students > 0 else 0.0
            kpis[kpi_name] = round(percentage, 2)
            logger.debug("%s: %d/%d = %.2f%%", col_name, yes_count, total_students, percentage)
        else:
            # Column missing - treat as 0%
            kpis[kpi_name] = 0.0
            logger.debug("Column '%s' missing, setting %s to 0%%", col_name, kpi_name)
    
    logger.info("Computed KPIs: %s", kpis)
    return kpis


def compute_demographic_breakdown(df: pd.DataFrame, group_col: str = "gender") -> Dict[str, Dict[str, float]]:
    """
    Compute KPIs broken down by demographic groups.
    
    Args:
        df: DataFrame with mental health survey responses
        group_col: Column to group by (e.g., 'gender', 'division', 'year_of_study')
        
    Returns:
        Dictionary with group names as keys, KPIs as values
    """
    logger.debug("Computing demographic breakdown by '%s'", group_col)
    
    if df.empty or group_col not in df.columns:
        logger.warning("Empty DataFrame or missing group column '%s'", group_col)
        return {}
    
    breakdown = {}
    
    # Get unique groups
    groups = df[group_col].unique()
    logger.debug("Found %d groups: %s", len(groups), list(groups))
    
    # Compute KPIs for each group
    for group in groups:
        group_df = df[df[group_col] == group]
        group_kpis = compute_kpis(group_df)
        breakdown[str(group)] = group_kpis
        logger.debug("Group '%s' KPIs: %s", group, group_kpis)
    
    return breakdown


def compute_trend_metrics(df: pd.DataFrame) -> Dict[str, float]:
    """
    Compute trend-related metrics from timestamp data.
    
    Args:
        df: DataFrame with timestamp column
        
    Returns:
        Dictionary with trend metrics
    """
    logger.debug("Computing trend metrics from DataFrame")
    
    if df.empty or 'timestamp' not in df.columns:
        logger.warning("Empty DataFrame or missing timestamp column")
        return {
            'total_months': 0,
            'avg_monthly_responses': 0.0,
            'peak_month_responses': 0,
            'data_coverage_months': 0
        }
    
    # Work on copy with valid timestamps
    df_copy = df.copy()
    
    try:
        # Ensure timestamp is datetime
        df_copy['timestamp'] = pd.to_datetime(df_copy['timestamp'], errors='coerce')
        
        # Remove rows with invalid timestamps
        valid_df = df_copy.dropna(subset=['timestamp'])
        
        if valid_df.empty:
            logger.warning("No valid timestamps found")
            return {
                'total_months': 0,
                'avg_monthly_responses': 0.0,
                'peak_month_responses': 0,
                'data_coverage_months': 0
            }
        
        # Extract month-year combinations
        valid_df['month_year'] = valid_df['timestamp'].dt.to_period('M')
        
        # Calculate metrics
        monthly_counts = valid_df.groupby('month_year').size()
        
        metrics = {
            'total_months': len(monthly_counts),
            'avg_monthly_responses': round(monthly_counts.mean(), 2),
            'peak_month_responses': int(monthly_counts.max()),
            'data_coverage_months': len(monthly_counts)
        }
        
        logger.info("Trend metrics: %s", metrics)
        return metrics
        
    except Exception as e:
        logger.error("Error computing trend metrics: %s", e)
        return {
            'total_months': 0,
            'avg_monthly_responses': 0.0,
            'peak_month_responses': 0,
            'data_coverage_months': 0
        }


# Overview-specific visualization functions
def plot_overall_depression(df: pd.DataFrame) -> Figure:
    """
    Plot overall depression prevalence as a bar chart.
    
    Args:
        df: DataFrame with 'depression' column containing Yes/No values
        
    Returns:
        matplotlib.figure.Figure: The generated plot figure
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Check if required column exists
    if 'depression' not in df.columns:
        logger.warning("Column 'depression' not found in DataFrame for plot_overall_depression")
        ax.text(0.5, 0.5, 'No depression data available', 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Overall Depression - No Data')
        return fig
    
    # Handle empty DataFrame
    if df.empty:
        logger.warning("Empty DataFrame provided to plot_overall_depression")
        ax.text(0.5, 0.5, 'No data available', 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Overall Depression - No Data')
        return fig
    
    # Count depression values
    depression_counts = df['depression'].value_counts()
    
    if depression_counts.empty:
        ax.text(0.5, 0.5, 'No depression data available', 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Overall Depression - No Data')
        return fig
    
    # Create bar chart
    colors = ['#66b3ff', '#ff9999']
    bars = ax.bar(depression_counts.index, depression_counts.values, color=colors)
    
    # Add percentage labels on bars
    total = depression_counts.sum()
    for i, bar in enumerate(bars):
        height = bar.get_height()
        percentage = (height / total) * 100
        ax.text(bar.get_x() + bar.get_width()/2., height + total*0.01,
                f'{height}\n({percentage:.1f}%)', ha='center', va='bottom')
    
    ax.set_title('Overall Depression Prevalence', fontsize=14, fontweight='bold')
    ax.set_xlabel('Depression Status', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    
    plt.tight_layout()
    return fig


def plot_depression_by_gender_pie(df: pd.DataFrame) -> Figure:
    """
    Plot depression prevalence by gender as a pie chart.
    
    Args:
        df: DataFrame with 'depression' and 'gender' columns
        
    Returns:
        matplotlib.figure.Figure: The generated plot figure
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Check if required columns exist
    required_cols = ['depression', 'gender']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        logger.warning(f"Columns {missing_cols} not found in DataFrame for plot_depression_by_gender_pie")
        ax.text(0.5, 0.5, f'Missing columns: {", ".join(missing_cols)}', 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Depression by Gender (Pie) - Missing Data')
        return fig
    
    # Handle empty DataFrame
    if df.empty:
        logger.warning("Empty DataFrame provided to plot_depression_by_gender_pie")
        ax.text(0.5, 0.5, 'No data available', 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Depression by Gender (Pie) - No Data')
        return fig
    
    # Calculate depression percentage by gender
    gender_depression = df[df['depression'] == 'Yes'].groupby('gender').size()
    gender_total = df.groupby('gender').size()
    gender_pct = (gender_depression / gender_total * 100).fillna(0)
    
    if gender_pct.empty:
        ax.text(0.5, 0.5, 'No data to display', 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Depression by Gender (Pie) - No Data')
        return fig
    
    # Create pie chart
    colors = plt.cm.Set3(range(len(gender_pct)))
    labels = [f'{gender}\n({pct:.1f}%)' for gender, pct in gender_pct.items()]
    
    wedges, texts = ax.pie(gender_pct.values, labels=labels, colors=colors, startangle=90)
    
    ax.set_title('Depression Rate by Gender', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    return fig


def plot_depression_by_division_bar(df: pd.DataFrame) -> Figure:
    """
    Plot depression prevalence by division as a horizontal bar chart.
    
    Args:
        df: DataFrame with 'depression' and 'division' columns
        
    Returns:
        matplotlib.figure.Figure: The generated plot figure
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Check if required columns exist
    required_cols = ['depression', 'division']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        logger.warning(f"Columns {missing_cols} not found in DataFrame for plot_depression_by_division_bar")
        ax.text(0.5, 0.5, f'Missing columns: {", ".join(missing_cols)}', 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Depression by Division - Missing Data')
        return fig
    
    # Handle empty DataFrame
    if df.empty:
        logger.warning("Empty DataFrame provided to plot_depression_by_division_bar")
        ax.text(0.5, 0.5, 'No data available', 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Depression by Division - No Data')
        return fig
    
    # Calculate depression percentage by division
    division_depression = df[df['depression'] == 'Yes'].groupby('division').size()
    division_total = df.groupby('division').size()
    division_pct = (division_depression / division_total * 100).fillna(0).sort_values(ascending=True)
    
    if division_pct.empty:
        ax.text(0.5, 0.5, 'No data to display', 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Depression by Division - No Data')
        return fig
    
    # Create horizontal bar chart
    bars = ax.barh(division_pct.index, division_pct.values, color='#ff7f7f')
    
    # Add percentage labels
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width + 1, bar.get_y() + bar.get_height()/2,
                f'{width:.1f}%', ha='left', va='center')
    
    ax.set_title('Depression Rate by Division', fontsize=14, fontweight='bold')
    ax.set_xlabel('Depression Rate (%)', fontsize=12)
    ax.set_ylabel('Division', fontsize=12)
    ax.set_xlim(0, max(100, division_pct.max() * 1.1))
    
    plt.tight_layout()
    return fig


def plot_risk_profile_radar(df: pd.DataFrame) -> Figure:
    """
    Plot risk profile as a radar chart showing multiple mental health indicators.
    
    Args:
        df: DataFrame with mental health columns
        
    Returns:
        matplotlib.figure.Figure: The generated plot figure
    """
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    # Handle empty DataFrame
    if df.empty:
        logger.warning("Empty DataFrame provided to plot_risk_profile_radar")
        ax.text(0.5, 0.5, 'No data available', 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Risk Profile Radar - No Data')
        return fig
    
    # Define risk factors and their columns
    risk_factors = {
        'Depression': 'depression',
        'Anxiety': 'anxiety', 
        'Panic Attacks': 'panic_attack',
        'Financial Stress': 'financial_stress_level',
        'Help Seeking': 'sought_specialist_treatment'
    }
    
    categories = []
    values = []
    
    total_students = len(df)
    
    for factor, col in risk_factors.items():
        if col in df.columns:
            if col == 'financial_stress_level':
                # Convert string stress levels to numeric and calculate percentage
                stress_mapping = {'Low': 1, 'Medium': 2, 'High': 3, 'Unknown': 2}  # Unknown = Medium
                numeric_stress = df[col].map(stress_mapping)
                if numeric_stress.notna().sum() > 0:
                    avg_stress = numeric_stress.mean()
                    normalized_stress = (avg_stress - 1) / 2 * 100  # Convert to 0-100 percentage
                    values.append(normalized_stress)
                else:
                    values.append(0)
            elif col == 'sought_specialist_treatment':
                # Invert help seeking (higher = less help seeking = higher risk)
                help_rate = (df[col] == 'Yes').sum() / total_students * 100
                risk_rate = 100 - help_rate  # Invert for risk profile
                values.append(risk_rate)
            else:
                # Yes/No columns - calculate percentage
                yes_rate = (df[col] == 'Yes').sum() / total_students * 100
                values.append(yes_rate)
            
            categories.append(factor)
        else:
            logger.debug(f"Column '{col}' not found, skipping {factor}")
    
    if not categories:
        ax.text(0.5, 0.5, 'No risk factor data available', 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Risk Profile Radar - No Data')
        return fig
    
    # Add first value at end to close the radar chart
    values += values[:1]
    
    # Calculate angles for each category
    angles = [n / len(categories) * 2 * 3.14159 for n in range(len(categories))]
    angles += angles[:1]
    
    # Plot the radar chart
    ax.plot(angles, values, 'o-', linewidth=2, color='#ff6b6b')
    ax.fill(angles, values, alpha=0.25, color='#ff6b6b')
    
    # Add category labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    
    # Set y-axis limits and labels
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'])
    
    ax.set_title('Mental Health Risk Profile', fontsize=16, fontweight='bold', pad=20)
    ax.grid(True)
    
    return fig