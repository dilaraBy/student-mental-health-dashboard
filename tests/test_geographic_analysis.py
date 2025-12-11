# Tests for GeographicAnalysisService
import pytest
import pandas as pd
import json
from unittest.mock import patch, mock_open
from services.geographic_analysis import GeographicAnalysisService


class TestGeographicAnalysisService:
    """Test suite for GeographicAnalysisService class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.service = GeographicAnalysisService()
        
        # Sample GeoJSON data for testing
        self.sample_geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"ADM1_EN": "Dhaka"},
                    "geometry": {"type": "Polygon", "coordinates": []}
                },
                {
                    "type": "Feature", 
                    "properties": {"ADM1_EN": "Chittagong"},
                    "geometry": {"type": "Polygon", "coordinates": []}
                }
            ]
        }
        
        # Sample survey data for testing
        self.sample_data = pd.DataFrame({
            'division': ['Dhaka', 'Chattogram', 'Barishal', 'Dhaka', 'Chittagong'],
            'depression': ['Yes', 'No', 'Yes', 'No', 'Yes']
        })
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_load_bangladesh_geojson_success(self, mock_json_load, mock_file):
        """Test successful loading of GeoJSON data."""
        mock_json_load.return_value = self.sample_geojson
        
        result = self.service.load_bangladesh_geojson()
        
        assert result == self.sample_geojson
        assert len(result['features']) == 2
        mock_file.assert_called_once()
        mock_json_load.assert_called_once()
    
    @patch('builtins.open', side_effect=FileNotFoundError())
    def test_load_bangladesh_geojson_file_not_found(self, mock_file):
        """Test handling of missing GeoJSON file."""
        result = self.service.load_bangladesh_geojson()
        
        assert result == {}
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load', side_effect=json.JSONDecodeError("Invalid JSON", "", 0))
    def test_load_bangladesh_geojson_invalid_json(self, mock_json_load, mock_file):
        """Test handling of invalid JSON in GeoJSON file."""
        result = self.service.load_bangladesh_geojson()
        
        assert result == {}
    
    def test_normalize_division_name_chattogram_to_chittagong(self):
        """Test normalization of Chattogram to Chittagong."""
        result = self.service.normalize_division_name('Chattogram')
        assert result == 'Chittagong'
        
        result = self.service.normalize_division_name('chattogram')
        assert result == 'Chittagong'
    
    def test_normalize_division_name_barishal_to_barisal(self):
        """Test normalization of Barishal to Barisal."""
        result = self.service.normalize_division_name('Barishal')
        assert result == 'Barisal'
        
        result = self.service.normalize_division_name('barishal')
        assert result == 'Barisal'
    
    def test_normalize_division_name_unchanged(self):
        """Test that already correct names remain unchanged."""
        result = self.service.normalize_division_name('Dhaka')
        assert result == 'Dhaka'
        
        result = self.service.normalize_division_name('Sylhet')
        assert result == 'Sylhet'
    
    def test_normalize_division_name_none_input(self):
        """Test handling of None input."""
        result = self.service.normalize_division_name(None)
        assert result is None
        
        result = self.service.normalize_division_name(pd.NA)
        assert result is None
    
    def test_calculate_division_depression_rates_basic(self):
        """Test basic depression rate calculation."""
        result = self.service.calculate_division_depression_rates(self.sample_data)
        
        # Expected: Dhaka 1/2=50%, Chittagong (Chattogram+Chittagong) 1/2=50%, Barisal (Barishal) 1/1=100%
        assert 'Dhaka' in result
        assert 'Chittagong' in result  # Both Chattogram and Chittagong should be normalized to this
        assert 'Barisal' in result     # Barishal should be normalized to this
        
        assert result['Dhaka'] == 50.0
        assert result['Chittagong'] == 50.0  # 1 depression case out of 2 (Chattogram + Chittagong)
        assert result['Barisal'] == 100.0
    
    def test_calculate_division_depression_rates_empty_df(self):
        """Test handling of empty DataFrame."""
        empty_df = pd.DataFrame()
        result = self.service.calculate_division_depression_rates(empty_df)
        
        assert result == {}
    
    def test_calculate_division_depression_rates_missing_columns(self):
        """Test handling of DataFrame with missing required columns."""
        df_missing_cols = pd.DataFrame({'other_col': [1, 2, 3]})
        result = self.service.calculate_division_depression_rates(df_missing_cols)
        
        assert result == {}
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_get_division_names_from_geojson(self, mock_json_load, mock_file):
        """Test extraction of division names from GeoJSON."""
        mock_json_load.return_value = self.sample_geojson
        
        result = self.service.get_division_names_from_geojson()
        
        expected = ['Dhaka', 'Chittagong']
        assert result == expected
    
    @patch('builtins.open', side_effect=FileNotFoundError())
    def test_get_division_names_from_geojson_no_file(self, mock_file):
        """Test handling when GeoJSON file is not available."""
        result = self.service.get_division_names_from_geojson()
        
        assert result == []
    
    def test_geojson_caching(self):
        """Test that GeoJSON data is cached after first load."""
        # Mock the file operations for first call
        with patch('builtins.open', new_callable=mock_open) as mock_file, \
             patch('json.load', return_value=self.sample_geojson) as mock_json_load:
            
            # First call should load from file
            result1 = self.service.load_bangladesh_geojson()
            assert mock_file.call_count == 1
            assert mock_json_load.call_count == 1
            
            # Second call should use cache
            result2 = self.service.load_bangladesh_geojson()
            assert mock_file.call_count == 1  # No additional file access
            assert mock_json_load.call_count == 1  # No additional JSON loading
            
            # Results should be identical
            assert result1 == result2 == self.sample_geojson