# Tests for data management functionality
import pytest
import pandas as pd
import tempfile
import os
import io
from unittest.mock import Mock, patch

from db.repository import StudentMentalHealthRepository
from services.data_management import DataManagementService, RecordFormHandler


class TestDataManagementService:
    """Test class for DataManagementService."""

    @pytest.fixture
    def sample_repository(self):
        """Create a repository with sample data."""
        # Use in-memory database for testing
        repo = StudentMentalHealthRepository(':memory:')
        repo.init_tables()
        
        # Insert sample data
        sample_data = pd.DataFrame({
            'gender': ['Male', 'Female', 'Male', 'Female'],
            'division': ['Science', 'Arts', 'Science', 'Arts'],
            'depression': ['Yes', 'No', 'Yes', 'No'],
            'anxiety': ['No', 'Yes', 'No', 'Yes'],
            'financial_stress_level': ['Low', 'High', 'Medium', 'Low']
        })
        repo.insert_data(sample_data)
        return repo

    @pytest.fixture
    def data_service(self, sample_repository):
        """Create DataManagementService with sample repository."""
        return DataManagementService(sample_repository)

    def test_get_filter_options(self, data_service):
        """Test filter options generation."""
        options = data_service.get_filter_options()
        
        assert isinstance(options, dict)
        assert 'gender' in options
        assert 'division' in options
        assert set(options['gender']) == {'Male', 'Female'}
        assert set(options['division']) == {'Arts', 'Science'}

    def test_apply_filters_no_filters(self, data_service):
        """Test applying no filters returns all data."""
        result = data_service.apply_filters({})
        
        assert len(result) == 4
        assert 'rowid' in result.columns

    def test_apply_filters_single_filter(self, data_service):
        """Test applying single filter."""
        filters = {'gender': 'Male'}
        result = data_service.apply_filters(filters)
        
        assert len(result) == 2
        assert all(result['gender'] == 'Male')

    def test_apply_filters_multiple_filters(self, data_service):
        """Test applying multiple filters."""
        filters = {'gender': 'Male', 'division': 'Science'}
        result = data_service.apply_filters(filters)
        
        assert len(result) == 2
        assert all(result['gender'] == 'Male')
        assert all(result['division'] == 'Science')

    def test_get_data_statistics_empty_df(self, data_service):
        """Test statistics with empty DataFrame."""
        empty_df = pd.DataFrame()
        stats = data_service.get_data_statistics(empty_df)
        
        assert stats['total_records'] == 0
        assert stats['missing_data'] == {}

    def test_get_data_statistics_with_data(self, data_service):
        """Test statistics with real data."""
        df = data_service.apply_filters({})
        stats = data_service.get_data_statistics(df)
        
        assert stats['total_records'] == 4
        assert 'missing_data' in stats
        assert 'data_types' in stats
        assert 'categorical_distributions' in stats

    def test_validate_record_data_valid(self, data_service):
        """Test validation with valid record data."""
        valid_data = {
            'gender': 'Male',
            'division': 'Science',
            'depression': 'Yes',
            'anxiety': 'No',
            'financial_stress_level': 'Medium'
        }
        
        is_valid, errors = data_service.validate_record_data(valid_data)
        
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_record_data_missing_required(self, data_service):
        """Test validation with missing required fields."""
        invalid_data = {
            'depression': 'Yes'
        }
        
        is_valid, errors = data_service.validate_record_data(invalid_data)
        
        assert is_valid is False
        assert len(errors) > 0
        assert any('gender' in error.lower() for error in errors)

    def test_validate_record_data_invalid_yes_no(self, data_service):
        """Test validation with invalid yes/no values."""
        invalid_data = {
            'gender': 'Male',
            'division': 'Science',
            'depression': 'Maybe'
        }
        
        is_valid, errors = data_service.validate_record_data(invalid_data)
        
        assert is_valid is False
        assert any('depression' in error.lower() for error in errors)

    def test_validate_record_data_invalid_stress_level(self, data_service):
        """Test validation with invalid stress level."""
        invalid_data = {
            'gender': 'Male',
            'division': 'Science',
            'financial_stress_level': 'Extreme'
        }
        
        is_valid, errors = data_service.validate_record_data(invalid_data)
        
        assert is_valid is False
        assert any('financial stress' in error.lower() for error in errors)

    def test_process_uploaded_csv_valid(self, data_service):
        """Test processing valid CSV file using real StringIO instead of mocking."""
        # Create real CSV content using StringIO
        csv_content = """gender,division,depression
Male,Science,Yes
Female,Arts,No"""
        
        # Use StringIO to simulate file upload without mocking pandas
        csv_file = io.StringIO(csv_content)
        csv_file.name = "test.csv"  # Add name attribute for logging
        
        success, message, df = data_service.process_uploaded_csv(csv_file)
        
        assert success is True
        assert 'Successfully processed' in message
        assert df is not None
        assert len(df) == 2
        assert 'Male' in df['gender'].values
        assert 'Female' in df['gender'].values

    def test_process_uploaded_csv_empty(self, data_service):
        """Test processing empty CSV file using real empty StringIO."""
        # Create empty CSV content
        empty_csv = io.StringIO("")
        empty_csv.name = "empty.csv"
        
        success, message, df = data_service.process_uploaded_csv(empty_csv)
        
        assert success is False
        assert 'empty' in message.lower()
        assert df is None

    def test_process_uploaded_csv_missing_columns(self, data_service):
        """Test processing CSV with missing required columns using real CSV."""
        # Create CSV with wrong columns
        invalid_csv_content = """name,age
John,20
Jane,21"""
        
        invalid_csv = io.StringIO(invalid_csv_content)
        invalid_csv.name = "invalid.csv"
        
        success, message, df = data_service.process_uploaded_csv(invalid_csv)
        
        assert success is False
        assert 'Missing required columns' in message
        assert df is None

    def test_export_to_csv(self, data_service):
        """Test CSV export functionality."""
        df = data_service.apply_filters({})
        csv_bytes = data_service.export_to_csv(df)
        
        assert isinstance(csv_bytes, bytes)
        assert len(csv_bytes) > 0
        
        # Verify CSV content
        csv_string = csv_bytes.decode('utf-8')
        assert 'gender' in csv_string
        assert 'division' in csv_string


class TestCRUDMethods:
    """Test class for repository CRUD methods."""

    @pytest.fixture
    def test_repository(self):
        """Create a test repository with sample data."""
        repo = StudentMentalHealthRepository(':memory:')
        repo.init_tables()
        
        # Insert initial sample data
        sample_data = pd.DataFrame({
            'gender': ['Male', 'Female'],
            'division': ['Science', 'Arts'],
            'depression': ['Yes', 'No']
        })
        repo.insert_data(sample_data)
        return repo

    def test_create_record_success(self, test_repository):
        """Test successful record creation."""
        record_data = {
            'gender': 'Male',
            'division': 'Engineering',
            'depression': 'No',
            'anxiety': 'Yes'
        }
        
        success = test_repository.create_record(record_data)
        assert success is True
        
        # Verify record was created
        df = test_repository.get_all_data()
        assert len(df) == 3
        assert 'Engineering' in df['division'].values

    def test_create_record_invalid_columns(self, test_repository):
        """Test record creation with invalid columns."""
        record_data = {
            'invalid_column': 'value',
            'another_invalid': 'value'
        }
        
        success = test_repository.create_record(record_data)
        assert success is False

    def test_update_record_success(self, test_repository):
        """Test successful record update."""
        # Get existing record
        df = test_repository.get_all_data_with_ids()
        first_rowid = df.iloc[0]['rowid']
        
        update_data = {
            'division': 'Engineering',
            'depression': 'No'
        }
        
        success = test_repository.update_record(first_rowid, update_data)
        assert success is True
        
        # Verify update
        updated_record = test_repository.get_record_by_id(first_rowid)
        assert updated_record['division'] == 'Engineering'

    def test_update_record_not_found(self, test_repository):
        """Test update of non-existent record."""
        update_data = {'division': 'Engineering'}
        
        success = test_repository.update_record(999, update_data)
        assert success is False

    def test_delete_record_success(self, test_repository):
        """Test successful record deletion."""
        # Get existing record
        df = test_repository.get_all_data_with_ids()
        initial_count = len(df)
        first_rowid = df.iloc[0]['rowid']
        
        success = test_repository.delete_record(first_rowid)
        assert success is True
        
        # Verify deletion
        df_after = test_repository.get_all_data()
        assert len(df_after) == initial_count - 1

    def test_delete_record_not_found(self, test_repository):
        """Test deletion of non-existent record."""
        success = test_repository.delete_record(999)
        assert success is False

    def test_get_record_by_id_success(self, test_repository):
        """Test successful record retrieval by ID."""
        # Get existing record
        df = test_repository.get_all_data_with_ids()
        first_rowid = df.iloc[0]['rowid']
        
        record = test_repository.get_record_by_id(first_rowid)
        
        assert record is not None
        assert isinstance(record, dict)
        assert 'gender' in record
        assert 'division' in record

    def test_get_record_by_id_not_found(self, test_repository):
        """Test retrieval of non-existent record."""
        record = test_repository.get_record_by_id(999)
        assert record is None

    def test_get_all_data_with_ids(self, test_repository):
        """Test getting all data with row IDs."""
        df = test_repository.get_all_data_with_ids()
        
        assert 'rowid' in df.columns
        assert len(df) == 2  # Initial sample data
        assert all(df['rowid'] > 0)


class TestRecordFormHandler:
    """Test class for RecordFormHandler.
    
    Note: These tests require mocking Streamlit components because:
    1. Streamlit components need an active app context to function
    2. We want to test the form logic without running a full Streamlit app
    3. UI components are external dependencies that should be mocked in unit tests
    """

    def test_create_record_form_structure(self):
        """Test record form creation structure with mocked Streamlit components."""
        columns = ['gender', 'division', 'depression', 'anxiety']
        
        # NECESSARY MOCKING: Streamlit components require app context
        with patch('streamlit.selectbox') as mock_selectbox, \
             patch('streamlit.text_input') as mock_text_input:
            
            mock_selectbox.return_value = 'Male'
            mock_text_input.return_value = 'Test'
            
            form_data = RecordFormHandler.create_record_form(columns)
            
            assert isinstance(form_data, dict)
            assert 'timestamp' in form_data  # Auto-added for new records

    def test_create_record_form_with_existing_data(self):
        """Test record form with pre-existing data and mocked Streamlit components."""
        columns = ['gender', 'division']
        existing_data = {'gender': 'Female', 'division': 'Arts'}
        
        # NECESSARY MOCKING: Streamlit components require app context
        with patch('streamlit.selectbox') as mock_selectbox:
            mock_selectbox.return_value = 'Female'
            
            form_data = RecordFormHandler.create_record_form(columns, existing_data)
            
            assert isinstance(form_data, dict)
            # Should not auto-add timestamp for existing records
            assert 'timestamp' not in form_data


class TestDataManagementWithoutMocks:
    """Additional tests that don't require mocking - testing core business logic."""

    @pytest.fixture
    def clean_repository(self):
        """Create a clean in-memory repository for testing."""
        repo = StudentMentalHealthRepository(':memory:')
        repo.init_tables()
        return repo

    def test_validation_logic_without_mocks(self, clean_repository):
        """Test validation logic directly without any mocks."""
        service = DataManagementService(clean_repository)
        
        # Test completely valid data
        valid_data = {
            'gender': 'Male',
            'division': 'Science',
            'depression': 'Yes',
            'anxiety': 'No',
            'panic_attack': 'Yes',
            'sought_specialist_treatment': 'No',
            'financial_stress_level': 'Medium'
        }
        
        is_valid, errors = service.validate_record_data(valid_data)
        assert is_valid is True
        assert len(errors) == 0

    def test_csv_export_without_mocks(self, clean_repository):
        """Test CSV export using real DataFrame without mocking."""
        service = DataManagementService(clean_repository)
        
        # Create real test DataFrame
        test_df = pd.DataFrame({
            'rowid': [1, 2, 3],
            'gender': ['Male', 'Female', 'Male'],
            'division': ['Science', 'Arts', 'Engineering'],
            'depression': ['Yes', 'No', 'Yes']
        })
        
        csv_bytes = service.export_to_csv(test_df)
        
        assert isinstance(csv_bytes, bytes)
        assert len(csv_bytes) > 0
        
        # Verify CSV content without mocking
        csv_string = csv_bytes.decode('utf-8')
        assert 'gender,division,depression' in csv_string  # Headers (rowid removed)
        assert 'Male,Science,Yes' in csv_string  # First row
        assert 'Female,Arts,No' in csv_string  # Second row

    def test_statistics_calculation_without_mocks(self, clean_repository):
        """Test statistics calculation with real DataFrame."""
        service = DataManagementService(clean_repository)
        
        # Create test DataFrame with realistic data
        test_df = pd.DataFrame({
            'gender': ['Male', 'Female', 'Male', None, 'Female'],
            'division': ['Science', 'Arts', 'Science', 'Arts', None],
            'age': [20, 21, 22, 23, 24],
            'depression': ['Yes', 'No', 'Yes', 'No', 'Yes']
        })
        
        stats = service.get_data_statistics(test_df)
        
        assert stats['total_records'] == 5
        assert stats['total_columns'] == 4
        assert stats['missing_data']['gender'] == 1  # One None value
        assert stats['missing_data']['division'] == 1  # One None value
        assert 'categorical_distributions' in stats