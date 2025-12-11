# Detailed Analysis Visualization Functions - Matplotlib-based plotting
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.figure
import numpy as np
from typing import Optional
from utils.logger import get_logger

logger = get_logger(__name__)


def plot_cgpa_boxplot(df_cgpa: pd.DataFrame) -> matplotlib.figure.Figure:
    """
    Create boxplot showing CGPA distribution by depression status.
    
    Args:
        df_cgpa: DataFrame with 'depression_label' and 'cgpa' columns
        
    Returns:
        matplotlib.figure.Figure: Boxplot visualization
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Handle missing data or empty DataFrame
    if df_cgpa.empty or 'depression_label' not in df_cgpa.columns or 'cgpa' not in df_cgpa.columns:
        ax.text(0.5, 0.5, 'No data available for CGPA vs Depression analysis', 
               ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Depression vs CGPA - No Data Available')
        return fig
    
    # Work with copy to avoid mutation
    df_copy = df_cgpa.copy().dropna()
    
    if df_copy.empty:
        ax.text(0.5, 0.5, 'No valid data available', 
               ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Depression vs CGPA - No Valid Data')
        return fig
    
    # Create separate data for boxplot
    depressed_cgpa = df_copy[df_copy['depression_label'] == 'Depressed']['cgpa']
    not_depressed_cgpa = df_copy[df_copy['depression_label'] == 'Not Depressed']['cgpa']
    
    # Prepare data for boxplot
    box_data = []
    labels = []
    
    if len(not_depressed_cgpa) > 0:
        box_data.append(not_depressed_cgpa)
        labels.append('Not Depressed')
    
    if len(depressed_cgpa) > 0:
        box_data.append(depressed_cgpa)
        labels.append('Depressed')
    
    if box_data:
        bp = ax.boxplot(box_data, tick_labels=labels, patch_artist=True,
                       boxprops=dict(facecolor='lightblue', alpha=0.7),
                       medianprops=dict(color='red', linewidth=2))
    
    ax.set_title('CGPA Distribution by Depression Status', fontsize=14, pad=20)
    ax.set_xlabel('Depression Status', fontsize=12)
    ax.set_ylabel('CGPA', fontsize=12)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_depression_by_year_bar(df_year: pd.DataFrame) -> matplotlib.figure.Figure:
    """
    Create bar chart showing depression percentage by year of study.
    
    Args:
        df_year: DataFrame with 'year_of_study' and 'depression_pct' columns
        
    Returns:
        matplotlib.figure.Figure: Bar chart visualization
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Handle missing data or empty DataFrame
    if df_year.empty or 'year_of_study' not in df_year.columns or 'depression_pct' not in df_year.columns:
        ax.text(0.5, 0.5, 'No data available for Depression by Year analysis', 
               ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Depression by Year of Study - No Data Available')
        return fig
    
    # Work with copy to avoid mutation
    df_copy = df_year.copy()
    
    years = df_copy['year_of_study']
    rates = df_copy['depression_pct']
    colors = ['#3498db', '#e74c3c', '#f39c12', '#2ecc71'][:len(years)]
    
    # Create bar chart
    bars = ax.bar(years, rates, color=colors, alpha=0.7, edgecolor='black', linewidth=0.5)
    
    # Add value labels on bars
    for bar, rate in zip(bars, rates):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
               f'{rate:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_title('Depression Prevalence by Year of Study', fontsize=14, pad=20)
    ax.set_xlabel('Year of Study', fontsize=12)
    ax.set_ylabel('Depression Prevalence (%)', fontsize=12)
    ax.set_ylim(0, max(rates) * 1.2 if len(rates) > 0 else 100)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.xticks(rotation=0)
    plt.tight_layout()
    return fig


def plot_depression_by_financial_stress_bar(df_fin: pd.DataFrame) -> matplotlib.figure.Figure:
    """
    Create bar chart showing depression percentage by financial stress level.
    
    Args:
        df_fin: DataFrame with 'financial_stress_level' and 'depression_pct' columns
        
    Returns:
        matplotlib.figure.Figure: Bar chart visualization
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Handle missing data or empty DataFrame
    if df_fin.empty or 'financial_stress_level' not in df_fin.columns or 'depression_pct' not in df_fin.columns:
        ax.text(0.5, 0.5, 'No data available for Depression by Financial Stress analysis', 
               ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Depression by Financial Stress - No Data Available')
        return fig
    
    # Work with copy to avoid mutation
    df_copy = df_fin.copy()
    
    # Order stress levels logically
    stress_order = ['Low', 'Medium', 'High']
    df_sorted = df_copy.set_index('financial_stress_level').reindex(
        [level for level in stress_order if level in df_copy['financial_stress_level'].values]
    ).reset_index()
    
    if df_sorted.empty:
        df_sorted = df_copy  # Fallback to original if reindexing fails
    
    levels = df_sorted['financial_stress_level']
    rates = df_sorted['depression_pct']
    colors = ['#2ecc71', '#f39c12', '#e74c3c'][:len(levels)]
    
    # Create bar chart
    bars = ax.bar(levels, rates, color=colors, alpha=0.7, edgecolor='black', linewidth=0.5)
    
    # Add value labels on bars
    for bar, rate in zip(bars, rates):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
               f'{rate:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_title('Depression Prevalence by Financial Stress Level', fontsize=14, pad=20)
    ax.set_xlabel('Financial Stress Level', fontsize=12)
    ax.set_ylabel('Depression Prevalence (%)', fontsize=12)
    ax.set_ylim(0, max(rates) * 1.2 if len(rates) > 0 else 100)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    return fig


def plot_depression_by_family_history_bar(df_fam: pd.DataFrame) -> matplotlib.figure.Figure:
    """
    Create bar chart showing depression percentage by family history.
    
    Args:
        df_fam: DataFrame with 'family_history' and 'depression_pct' columns
        
    Returns:
        matplotlib.figure.Figure: Bar chart visualization
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Handle missing data or empty DataFrame
    if df_fam.empty or 'family_history' not in df_fam.columns or 'depression_pct' not in df_fam.columns:
        ax.text(0.5, 0.5, 'No data available for Depression by Family History analysis', 
               ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Depression by Family History - No Data Available')
        return fig
    
    # Work with copy to avoid mutation
    df_copy = df_fam.copy()
    
    # Order family history logically (No, Yes)
    history_order = ['No', 'Yes']
    df_sorted = df_copy.set_index('family_history').reindex(
        [status for status in history_order if status in df_copy['family_history'].values]
    ).reset_index()
    
    if df_sorted.empty:
        df_sorted = df_copy  # Fallback to original if reindexing fails
    
    statuses = df_sorted['family_history']
    rates = df_sorted['depression_pct']
    colors = ['#3498db', '#e74c3c'][:len(statuses)]
    
    # Create bar chart
    bars = ax.bar(statuses, rates, color=colors, alpha=0.7, edgecolor='black', linewidth=0.5)
    
    # Add value labels on bars
    for bar, rate in zip(bars, rates):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
               f'{rate:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_title('Depression Prevalence by Family History of Mental Health Issues', fontsize=14, pad=20)
    ax.set_xlabel('Family History of Mental Health Issues', fontsize=12)
    ax.set_ylabel('Depression Prevalence (%)', fontsize=12)
    ax.set_ylim(0, max(rates) * 1.2 if len(rates) > 0 else 100)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    return fig


def plot_depression_by_condition_grouped_bar(df_cond: pd.DataFrame, condition_name: str) -> matplotlib.figure.Figure:
    """
    Create grouped bar chart for depression vs condition (anxiety/panic).
    
    Args:
        df_cond: DataFrame with 'condition_value' and 'depression_pct' columns
        condition_name: Name of the condition for chart title
        
    Returns:
        matplotlib.figure.Figure: Grouped bar chart visualization
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Handle missing data or empty DataFrame
    if df_cond.empty or 'condition_value' not in df_cond.columns or 'depression_pct' not in df_cond.columns:
        ax.text(0.5, 0.5, f'No data available for Depression vs {condition_name} analysis', 
               ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title(f'Depression vs {condition_name} - No Data Available')
        return fig
    
    # Work with copy to avoid mutation
    df_copy = df_cond.copy()
    
    # Order condition values logically (No, Yes)
    condition_order = ['No', 'Yes']
    df_sorted = df_copy.set_index('condition_value').reindex(
        [status for status in condition_order if status in df_copy['condition_value'].values]
    ).reset_index()
    
    if df_sorted.empty:
        df_sorted = df_copy  # Fallback to original if reindexing fails
    
    conditions = df_sorted['condition_value']
    rates = df_sorted['depression_pct']
    colors = ['#3498db', '#e74c3c'][:len(conditions)]
    
    # Create bar chart
    bars = ax.bar(conditions, rates, color=colors, alpha=0.7, edgecolor='black', linewidth=0.5)
    
    # Add value labels on bars
    for bar, rate in zip(bars, rates):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
               f'{rate:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_title(f'Depression Prevalence by {condition_name} Status', fontsize=14, pad=20)
    ax.set_xlabel(f'Has {condition_name}', fontsize=12)
    ax.set_ylabel('Depression Prevalence (%)', fontsize=12)
    ax.set_ylim(0, max(rates) * 1.2 if len(rates) > 0 else 100)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    return fig


def plot_correlation_heatmap(corr_df: pd.DataFrame) -> matplotlib.figure.Figure:
    """
    Create correlation heatmap using matplotlib imshow.
    
    Args:
        corr_df: Correlation matrix DataFrame (square, symmetric)
        
    Returns:
        matplotlib.figure.Figure: Heatmap visualization
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Handle missing data or empty DataFrame
    if corr_df.empty:
        ax.text(0.5, 0.5, 'No data available for correlation analysis', 
               ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Correlation Heatmap - No Data Available')
        return fig
    
    # Work with copy to avoid mutation
    corr_matrix = corr_df.copy()
    
    # Create heatmap using imshow
    im = ax.imshow(corr_matrix.values, cmap='RdYlBu_r', aspect='auto', vmin=-1, vmax=1)
    
    # Set ticks and labels
    ax.set_xticks(np.arange(len(corr_matrix.columns)))
    ax.set_yticks(np.arange(len(corr_matrix.index)))
    ax.set_xticklabels(corr_matrix.columns, rotation=45, ha='right')
    ax.set_yticklabels(corr_matrix.index)
    
    # Add correlation values as text
    for i in range(len(corr_matrix.index)):
        for j in range(len(corr_matrix.columns)):
            value = corr_matrix.iloc[i, j]
            try:
                if not pd.isna(value) and isinstance(value, (int, float)):
                    text_color = 'white' if abs(float(value)) > 0.5 else 'black'
                    ax.text(j, i, f'{float(value):.2f}', ha='center', va='center', 
                           color=text_color, fontsize=10, fontweight='bold')
            except (TypeError, ValueError):
                # Skip non-numeric values
                continue
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Correlation Coefficient', rotation=270, labelpad=20, fontsize=12)
    
    ax.set_title('Mental Health Variables Correlation Matrix', fontsize=14, pad=20)
    
    plt.tight_layout()
    return fig