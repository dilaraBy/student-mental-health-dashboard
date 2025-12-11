# Geographic Analysis Service - Business logic for geographic data processing
import pandas as pd
import json
from typing import Dict, Any, List
from utils.logger import get_logger
from utils.config import GEOJSON_PATH

logger = get_logger(__name__)


class GeographicAnalysisService:
    """Service class for geographic data analysis and processing."""
    
    def __init__(self):
        """Initialize the geographic analysis service."""
        self._geojson_cache = None
    
    def load_bangladesh_geojson(self) -> Dict[str, Any]:
        """
        Load Bangladesh divisions GeoJSON data from file with caching.
        
        Returns:
            Dict containing GeoJSON data, empty dict if file not found
        """
        if self._geojson_cache is not None:
            return self._geojson_cache
            
        try:
            with open(GEOJSON_PATH, 'r', encoding='utf-8') as f:
                geojson_data = json.load(f)
            self._geojson_cache = geojson_data
            logger.info(f"Successfully loaded GeoJSON data with {len(geojson_data['features'])} divisions")
            return geojson_data
        except FileNotFoundError:
            logger.error(f"GeoJSON file not found at {GEOJSON_PATH}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format in GeoJSON file: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error loading GeoJSON data: {e}")
            return {}
    
    def normalize_division_name(self, division_name: str) -> str:
        """
        Normalize division names to match GeoJSON property names.
        
        Args:
            division_name: Raw division name from survey data
            
        Returns:
            Normalized division name matching GeoJSON ADM1_EN property
        """
        if pd.isna(division_name):
            return None
        
        # Create mapping for common variations
        division_mapping = {
            # Common variations to GeoJSON standard names
            'chattogram': 'Chittagong',
            'barishal': 'Barisal',
            'dhaka': 'Dhaka',
            'khulna': 'Khulna', 
            'mymensingh': 'Mymensingh',
            'rajshahi': 'Rajshahi',
            'rangpur': 'Rangpur',
            'sylhet': 'Sylhet',
            # Handle exact matches (case-insensitive)
            'chittagong': 'Chittagong',
            'barisal': 'Barisal'
        }
        
        # Normalize to lowercase for lookup
        normalized = str(division_name).strip().lower()
        
        # Return mapped name or original if no mapping found
        mapped_name = division_mapping.get(normalized)
        if mapped_name:
            logger.debug(f"Mapped division '{division_name}' -> '{mapped_name}'")
            return mapped_name
        
        # If no mapping found, try title case of original
        title_case = str(division_name).strip().title()
        return title_case
    
    def calculate_division_depression_rates(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate depression rates by division from survey data.
        
        Args:
            df: DataFrame with 'division' and 'depression' columns
            
        Returns:
            Dict mapping division names to depression rates (0-100)
        """
        if df.empty or 'division' not in df.columns or 'depression' not in df.columns:
            logger.warning("Missing required columns for depression rate calculation")
            return {}
        
        # Work on a copy to avoid mutating input
        df_copy = df.copy()
        
        # Remove rows with missing division or depression data
        df_copy = df_copy.dropna(subset=['division', 'depression'])
        
        if df_copy.empty:
            logger.info("No valid data after removing missing values")
            return {}
        
        # Calculate depression rates by division with name normalization
        division_counts = {}  # Track total and depression counts per normalized division
        
        for division in df_copy['division'].unique():
            if pd.isna(division):
                continue
                
            # Normalize division name to match GeoJSON
            normalized_division = self.normalize_division_name(division)
            if not normalized_division:
                continue
                
            division_data = df_copy[df_copy['division'] == division]
            total_count = len(division_data)
            
            if total_count == 0:
                continue
                
            # Count students with depression
            depression_count = (division_data['depression'] == 'Yes').sum()
            
            # Aggregate counts for normalized division name
            if normalized_division not in division_counts:
                division_counts[normalized_division] = {'total': 0, 'depression': 0}
            
            division_counts[normalized_division]['total'] += total_count
            division_counts[normalized_division]['depression'] += depression_count
            
            logger.debug(f"Division {division} -> {normalized_division}: {depression_count}/{total_count} students with depression")
        
        # Calculate final rates from aggregated counts
        division_rates = {}
        for normalized_division, counts in division_counts.items():
            if counts['total'] > 0:
                depression_rate = (counts['depression'] / counts['total']) * 100.0
                division_rates[normalized_division] = round(depression_rate, 1)
                logger.debug(f"Final rate for {normalized_division}: {depression_rate:.1f}% ({counts['depression']}/{counts['total']} students)")
        
        logger.info(f"Calculated depression rates for {len(division_rates)} divisions after normalization")
        return division_rates
    
    def get_division_names_from_geojson(self) -> List[str]:
        """
        Extract division names from loaded GeoJSON data.
        
        Returns:
            List of division names from GeoJSON ADM1_EN property
        """
        geojson_data = self.load_bangladesh_geojson()
        if not geojson_data:
            return []
        
        division_names = []
        for feature in geojson_data.get('features', []):
            division_name = feature['properties']['ADM1_EN']
            division_names.append(division_name)
        
        return division_names