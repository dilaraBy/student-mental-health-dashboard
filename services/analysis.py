# Analysis functions: prevalence, trends, group comparisons

import pandas as pd
from utils.logger import get_logger

logger = get_logger(__name__)

def compute_prevalence(df: pd.DataFrame, column: str) -> dict:
    """
    Compute prevalence of 'Yes'/'No' values in a given column.
    Assumes values are already normalized to 'Yes'/'No'.
    """
    if column not in df.columns:
        logger.warning(f"Column {column} not in DataFrame")
        return {"yes_count": 0, "no_count": 0, "total": 0,
                "yes_percentage": 0.0, "no_percentage": 0.0}

    series = df[column].dropna()

    yes_count = (series == "Yes").sum()
    no_count = (series == "No").sum()
    total = len(series)

    if total == 0:
        yes_pct = no_pct = 0.0
    else:
        yes_pct = yes_count / total * 100
        no_pct = no_count / total * 100

    result = {
        "yes_count": yes_count,
        "no_count": no_count,
        "total": total,
        "yes_percentage": round(yes_pct, 2),
        "no_percentage": round(no_pct, 2),
    }

    logger.debug(f"Prevalence for {column}: {result}")
    return result


def compute_all_prevalence(df: pd.DataFrame, columns: list[str]) -> dict:
    """
    Compute prevalence for multiple yes/no columns.
    Returns a dict: {column_name: prevalence_dict}
    """
    results: dict[str, dict] = {}

    for col in columns:
        results[col] = compute_prevalence(df, col)

    logger.info(f"Computed prevalence for columns: {columns}")
    return results

def group_comparison(df: pd.DataFrame, group_by: str, condition: str) -> pd.DataFrame:
    """
    For each value in `group_by`, compute prevalence of 'Yes' in `condition`.
    Returns a DataFrame with columns:
    [group_by, yes_count, no_count, total, yes_percentage]
    """
    if group_by not in df.columns or condition not in df.columns:
        logger.warning(f"Columns {group_by} or {condition} not in DataFrame")
        return pd.DataFrame()

    grouped = df.dropna(subset=[group_by, condition]).groupby(group_by)

    rows = []
    for group_value, group_df in grouped:
        prev = compute_prevalence(group_df, condition)
        row = {
            group_by: group_value,
            "yes_count": prev["yes_count"],
            "no_count": prev["no_count"],
            "total": prev["total"],
            "yes_percentage": prev["yes_percentage"],
        }
        rows.append(row)

    result = pd.DataFrame(rows)
    logger.info(f"Computed group comparison for {condition} by {group_by}")
    return result


# Detailed Analysis Functions for Depression Correlations

def depression_vs_cgpa(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare data for depression vs CGPA boxplot analysis.
    
    Args:
        df: DataFrame with 'depression' and 'cgpa' columns
        
    Returns:
        DataFrame with 'depression_label' and 'cgpa' columns suitable for boxplot
    """
    # Handle missing data or empty DataFrame
    if df.empty or 'depression' not in df.columns or 'cgpa' not in df.columns:
        return pd.DataFrame(columns=['depression_label', 'cgpa'])
    
    # Work with copy to avoid mutation
    df_copy = df[['depression', 'cgpa']].copy()
    df_copy = df_copy.dropna()
    
    if df_copy.empty:
        return pd.DataFrame(columns=['depression_label', 'cgpa'])
    
    # Convert CGPA ranges to numeric values
    def convert_cgpa_to_numeric(cgpa_value):
        """Convert CGPA ranges to numeric midpoint values."""
        if pd.isna(cgpa_value):
            return None
        
        # If already numeric, return as is
        try:
            return float(cgpa_value)
        except (ValueError, TypeError):
            pass
        
        # Handle string ranges like "3.0 - 3.49"
        cgpa_str = str(cgpa_value).strip()
        cgpa_mapping = {
            # Standard format
            '3.5 - 4.0': 3.75, '3.50 - 4.00': 3.75,
            '3.0 - 3.49': 3.25, '3.00 - 3.49': 3.25,
            '2.5 - 2.99': 2.75, '2.50 - 2.99': 2.75,
            '2.0 - 2.49': 2.25, '2.00 - 2.49': 2.25,
            '1.5 - 1.99': 1.75, '1.50 - 1.99': 1.75,
            '1.0 - 1.49': 1.25, '1.00 - 1.49': 1.25,
            '0.0 - 0.99': 0.5, '0.00 - 0.99': 0.5,
            # Variations without decimal places
            '0 - 1.99': 1.0, '0 - 0.99': 0.5,
            '1 - 1.49': 1.25, '1 - 1.99': 1.5,
            '2 - 2.49': 2.25, '2 - 2.99': 2.5,
            '3 - 3.49': 3.25, '3 - 3.99': 3.5,
            '3.5 - 4': 3.75, '4.0': 4.0
        }
        
        return cgpa_mapping.get(cgpa_str, 2.5)  # Default to middle value
    
    # Convert CGPA to numeric
    df_copy['cgpa'] = df_copy['cgpa'].apply(convert_cgpa_to_numeric)
    
    # Convert depression to readable labels
    df_copy['depression_label'] = df_copy['depression'].map({
        'Yes': 'Depressed',
        'No': 'Not Depressed'
    })
    
    # Remove any rows that couldn't be mapped or have invalid CGPA
    df_copy = df_copy.dropna(subset=['depression_label', 'cgpa'])
    
    return df_copy[['depression_label', 'cgpa']]


def depression_rate_by_year(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate depression percentage by year of study.
    
    Args:
        df: DataFrame with 'year_of_study' and 'depression' columns
        
    Returns:
        DataFrame with 'year_of_study' and 'depression_pct' columns, sorted by year
    """
    # Handle missing data or empty DataFrame
    if df.empty or 'year_of_study' not in df.columns or 'depression' not in df.columns:
        return pd.DataFrame(columns=['year_of_study', 'depression_pct'])
    
    # Work with copy to avoid mutation
    df_copy = df[['year_of_study', 'depression']].copy()
    df_copy = df_copy.dropna()
    
    if df_copy.empty:
        return pd.DataFrame(columns=['year_of_study', 'depression_pct'])
    
    # Calculate depression rate by year
    year_stats = df_copy.groupby('year_of_study')['depression'].apply(
        lambda x: (x == 'Yes').sum() / len(x) * 100
    ).round(1).reset_index()
    year_stats.columns = ['year_of_study', 'depression_pct']
    
    # Sort by year order
    year_order = ['Year 1', 'Year 2', 'Year 3', 'Year 4']
    year_stats['year_sort'] = year_stats['year_of_study'].apply(
        lambda x: year_order.index(x) if x in year_order else 999
    )
    year_stats = year_stats.sort_values('year_sort').drop('year_sort', axis=1)
    
    return year_stats


def depression_rate_by_financial_stress(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate depression percentage by financial stress level.
    
    Args:
        df: DataFrame with 'financial_stress_level' and 'depression' columns
        
    Returns:
        DataFrame with 'financial_stress_level' and 'depression_pct' columns
    """
    # Handle missing data or empty DataFrame
    if df.empty or 'financial_stress_level' not in df.columns or 'depression' not in df.columns:
        return pd.DataFrame(columns=['financial_stress_level', 'depression_pct'])
    
    # Work with copy to avoid mutation
    df_copy = df[['financial_stress_level', 'depression']].copy()
    df_copy = df_copy.dropna()
    
    if df_copy.empty:
        return pd.DataFrame(columns=['financial_stress_level', 'depression_pct'])
    
    # Calculate depression rate by financial stress level
    stress_stats = df_copy.groupby('financial_stress_level')['depression'].apply(
        lambda x: (x == 'Yes').sum() / len(x) * 100
    ).round(1).reset_index()
    stress_stats.columns = ['financial_stress_level', 'depression_pct']
    
    return stress_stats


def depression_rate_by_family_history(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate depression percentage by family history of mental illness.
    
    Args:
        df: DataFrame with 'family_history_mental_illness' and 'depression' columns
        
    Returns:
        DataFrame with 'family_history' and 'depression_pct' columns
    """
    # Handle missing data or empty DataFrame
    if df.empty or 'family_history_mental_illness' not in df.columns or 'depression' not in df.columns:
        return pd.DataFrame(columns=['family_history', 'depression_pct'])
    
    # Work with copy to avoid mutation
    df_copy = df[['family_history_mental_illness', 'depression']].copy()
    df_copy = df_copy.dropna()
    
    if df_copy.empty:
        return pd.DataFrame(columns=['family_history', 'depression_pct'])
    
    # Calculate depression rate by family history
    family_stats = df_copy.groupby('family_history_mental_illness')['depression'].apply(
        lambda x: (x == 'Yes').sum() / len(x) * 100
    ).round(1).reset_index()
    family_stats.columns = ['family_history', 'depression_pct']
    
    return family_stats


def depression_rate_by_condition(df: pd.DataFrame, condition_col: str) -> pd.DataFrame:
    """
    Generic helper to calculate depression rates by any condition (anxiety, panic_attack, etc).
    
    Args:
        df: DataFrame with condition column and 'depression' column
        condition_col: Name of the condition column to group by
        
    Returns:
        DataFrame with 'condition_value' and 'depression_pct' columns
    """
    # Handle missing data or empty DataFrame
    if df.empty or condition_col not in df.columns or 'depression' not in df.columns:
        return pd.DataFrame(columns=['condition_value', 'depression_pct'])
    
    # Work with copy to avoid mutation
    df_copy = df[[condition_col, 'depression']].copy()
    df_copy = df_copy.dropna()
    
    if df_copy.empty:
        return pd.DataFrame(columns=['condition_value', 'depression_pct'])
    
    # Calculate depression rate by condition
    condition_stats = df_copy.groupby(condition_col)['depression'].apply(
        lambda x: (x == 'Yes').sum() / len(x) * 100
    ).round(1).reset_index()
    condition_stats.columns = ['condition_value', 'depression_pct']
    
    return condition_stats


def build_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build correlation matrix for numeric/coded mental health variables.
    
    Args:
        df: DataFrame with mental health survey data
        
    Returns:
        pandas DataFrame correlation matrix (square, symmetric)
    """
    if df.empty:
        return pd.DataFrame()
    
    # Work with copy to avoid mutation
    df_numeric = pd.DataFrame()
    
    # Binary conversions (Yes/No -> 1/0)
    binary_cols = ['depression', 'anxiety', 'panic_attack', 'family_history_mental_illness']
    for col in binary_cols:
        if col in df.columns:
            df_numeric[col.replace('_mental_illness', '')] = (df[col] == 'Yes').astype(int)
    
    # Financial stress level conversion (Low=1, Medium=2, High=3, Unknown=2 as neutral)
    if 'financial_stress_level' in df.columns:
        stress_mapping = {'Low': 1, 'Medium': 2, 'High': 3, 'Unknown': 2}
        df_numeric['financial_stress_level'] = df['financial_stress_level'].map(stress_mapping)
    
    # Year of study conversion (Year 1=1, Year 2=2, etc.)
    if 'year_of_study' in df.columns:
        year_mapping = {'Year 1': 1, 'Year 2': 2, 'Year 3': 3, 'Year 4': 4}
        df_numeric['year_of_study'] = df['year_of_study'].map(year_mapping)
    
    # CGPA conversion (handle both numeric and range strings)
    if 'cgpa' in df.columns:
        def convert_cgpa_to_numeric(cgpa_value):
            """Convert CGPA ranges to numeric midpoint values."""
            if pd.isna(cgpa_value):
                return None
            
            # If already numeric, return as is
            try:
                return float(cgpa_value)
            except (ValueError, TypeError):
                pass
            
            # Handle string ranges like "3.0 - 3.49"
            cgpa_str = str(cgpa_value).strip()
            cgpa_mapping = {
                # Standard format
                '3.5 - 4.0': 3.75, '3.50 - 4.00': 3.75,
                '3.0 - 3.49': 3.25, '3.00 - 3.49': 3.25,
                '2.5 - 2.99': 2.75, '2.50 - 2.99': 2.75,
                '2.0 - 2.49': 2.25, '2.00 - 2.49': 2.25,
                '1.5 - 1.99': 1.75, '1.50 - 1.99': 1.75,
                '1.0 - 1.49': 1.25, '1.00 - 1.49': 1.25,
                '0.0 - 0.99': 0.5, '0.00 - 0.99': 0.5,
                # Variations without decimal places
                '0 - 1.99': 1.0, '0 - 0.99': 0.5,
                '1 - 1.49': 1.25, '1 - 1.99': 1.5,
                '2 - 2.49': 2.25, '2 - 2.99': 2.5,
                '3 - 3.49': 3.25, '3 - 3.99': 3.5,
                '3.5 - 4': 3.75, '4.0': 4.0
            }
            
            return cgpa_mapping.get(cgpa_str, 2.5)  # Default to middle value
        
        df_numeric['cgpa'] = df['cgpa'].apply(convert_cgpa_to_numeric)
    
    # Age (if available and numeric)
    if 'age' in df.columns:
        try:
            df_numeric['age'] = pd.to_numeric(df['age'], errors='coerce')
        except:
            pass
    
    # Remove rows with missing values for clean correlation
    df_numeric = df_numeric.dropna()
    
    if df_numeric.empty or len(df_numeric.columns) < 2:
        return pd.DataFrame()
    
    # Calculate correlation matrix
    correlation_matrix = df_numeric.corr()
    
    return correlation_matrix

