# Data View & CRUD Page - Raw Data Exploration and Management
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from typing import Dict, List, Any

from db.repository import StudentMentalHealthRepository
from services.data_management import DataManagementService, RecordFormHandler
from utils.config import DB_PATH
from utils.logger import get_logger

logger = get_logger(__name__)

# Initialize services
@st.cache_resource
def get_services():
    """Initialize and cache repository and service instances."""
    repository = StudentMentalHealthRepository(str(DB_PATH))
    data_service = DataManagementService(repository)
    return repository, data_service

repository, data_service = get_services()

# Page configuration
st.title("📋 Data View & CRUD")
st.markdown("*Manage and explore the student mental health dataset with advanced filtering and CRUD operations.*")

# Initialize session state for form management
if 'show_create_form' not in st.session_state:
    st.session_state.show_create_form = False
if 'show_update_form' not in st.session_state:
    st.session_state.show_update_form = False
if 'selected_record_id' not in st.session_state:
    st.session_state.selected_record_id = None
if 'refresh_data' not in st.session_state:
    st.session_state.refresh_data = False

# Helper functions for UI state management
def reset_forms():
    """Reset all form states."""
    st.session_state.show_create_form = False
    st.session_state.show_update_form = False
    st.session_state.selected_record_id = None

def refresh_data():
    """Trigger data refresh."""
    st.session_state.refresh_data = True


# ========================================
# 1. DATA FILTERING SECTION
# ========================================
st.markdown("---")
st.subheader("🔍 Data Filters")

with st.container():
    # Get filter options
    filter_options = data_service.get_filter_options()
    
    if not filter_options:
        st.warning("⚠️ No data available for filtering. Please ensure the database is initialized.")
        st.stop()
    
    # Create filter controls in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        gender_filter = st.multiselect(
            "Gender", 
            options=filter_options.get('gender', []),
            key="gender_filter"
        )
        
        depression_filter = st.selectbox(
            "Depression Status",
            options=['All'] + filter_options.get('depression', []),
            key="depression_filter"
        )
    
    with col2:
        division_filter = st.multiselect(
            "Division",
            options=filter_options.get('division', []),
            key="division_filter"
        )
        
        anxiety_filter = st.selectbox(
            "Anxiety Status",
            options=['All'] + filter_options.get('anxiety', []),
            key="anxiety_filter"
        )
    
    with col3:
        year_filter = st.multiselect(
            "Year of Study",
            options=filter_options.get('year_of_study', []),
            key="year_filter"
        )
        
        stress_filter = st.selectbox(
            "Financial Stress Level",
            options=['All'] + filter_options.get('financial_stress_level', []),
            key="stress_filter"
        )
    
    # Date range filter
    st.markdown("**Date Range Filter**")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=date.today() - timedelta(days=365),
            key="start_date"
        )
    with col2:
        end_date = st.date_input(
            "End Date", 
            value=date.today(),
            key="end_date"
        )
    
    # Build filters dictionary
    filters = {}
    if gender_filter:
        filters['gender'] = gender_filter
    if division_filter:
        filters['division'] = division_filter
    if year_filter:
        filters['year_of_study'] = year_filter
    if depression_filter != 'All':
        filters['depression'] = depression_filter
    if anxiety_filter != 'All':
        filters['anxiety'] = anxiety_filter
    if stress_filter != 'All':
        filters['financial_stress_level'] = stress_filter
    if start_date and end_date:
        filters['date_range'] = (start_date, end_date)
    
    # Apply filters button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Apply Filters", key="apply_filters"):
            logger.info(f"User applied filters: {filters}")
            st.session_state.refresh_data = True

# ========================================
# 2. DATA TABLE SECTION  
# ========================================
st.markdown("---")
st.subheader("📊 Filtered Data Table")

# Get filtered data
with st.spinner("Loading data..."):
    try:
        filtered_df = data_service.apply_filters(filters)
        
        if filtered_df.empty:
            st.warning("No data matches the current filters.")
        else:
            # Display data table with configuration
            st.markdown(f"**Showing {len(filtered_df)} records**")
            
            # Configure dataframe display
            column_config = {
                'rowid': st.column_config.NumberColumn(
                    'ID',
                    help='Record ID for editing/deletion',
                    width='small'
                ),
                'timestamp': st.column_config.DatetimeColumn(
                    'Date',
                    width='medium'
                ),
                'gender': st.column_config.TextColumn('Gender', width='small'),
                'division': st.column_config.TextColumn('Division', width='medium'),
                'depression': st.column_config.TextColumn('Depression', width='small'),
                'anxiety': st.column_config.TextColumn('Anxiety', width='small'),
                'panic_attack': st.column_config.TextColumn('Panic Attack', width='small'),
                'financial_stress_level': st.column_config.TextColumn('Stress Level', width='medium'),
                'sought_specialist_treatment': st.column_config.TextColumn('Sought Help', width='medium')
            }
            
            # Display interactive dataframe
            st.dataframe(
                filtered_df,
                column_config=column_config,
                hide_index=True,
                use_container_width=True,
                height=400
            )
            
    except Exception as e:
        logger.error(f"Error loading filtered data: {e}")
        st.error(f"Error loading data: {e}")
        filtered_df = pd.DataFrame()

# ========================================
# 3. DATA STATISTICS SECTION
# ========================================
st.markdown("---") 
st.subheader("📈 Data Statistics")

if not filtered_df.empty:
    stats = data_service.get_data_statistics(filtered_df)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Records", stats.get('total_records', 0))
        st.metric("Total Columns", stats.get('total_columns', 0))
        
        # Missing data summary
        if stats.get('missing_data'):
            st.markdown("**Missing Data Summary**")
            missing_data = stats['missing_data']
            for col, count in list(missing_data.items())[:5]:
                if count > 0:
                    st.text(f"• {col}: {count} missing")
    
    with col2:
        st.metric("Memory Usage", stats.get('memory_usage', 'N/A'))
        
        # Distribution summary  
        if stats.get('categorical_distributions'):
            st.markdown("**Top Categories**")
            for col, dist in list(stats['categorical_distributions'].items())[:3]:
                if dist:
                    top_value = max(dist, key=dist.get)
                    st.text(f"• {col}: {top_value} ({dist[top_value]})")

# ========================================
# 4. IMPORT CSV SECTION
# ========================================
st.markdown("---")
st.subheader("📥 Import CSV Data")

with st.expander("Upload CSV File", expanded=False):
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload a CSV file with student mental health data. Required columns: gender, division"
    )
    
    if uploaded_file is not None:
        success, message, new_df = data_service.process_uploaded_csv(uploaded_file)
        
        if success and new_df is not None:
            st.success(message)
            
            # Preview uploaded data
            st.markdown("**Preview of uploaded data:**")
            st.dataframe(new_df.head(10), use_container_width=True)
            
            # Import options
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Import Data (Replace)", key="import_replace"):
                    try:
                        count = repository.insert_data(new_df, if_exists="replace")
                        logger.info(f"CSV import (replace): imported {count} records from {uploaded_file.name}")
                        st.success(f"✅ Successfully imported {count} records (replaced existing data)")
                        refresh_data()
                    except Exception as e:
                        logger.error(f"CSV import (replace) failed: {e}")
                        st.error(f"Import failed: {e}")
            
            with col2:
                if st.button("➕ Import Data (Append)", key="import_append"):
                    try:
                        count = repository.insert_data(new_df, if_exists="append")
                        logger.info(f"CSV import (append): imported {count} records from {uploaded_file.name}")
                        st.success(f"✅ Successfully imported {count} records (appended to existing data)")
                        refresh_data()
                    except Exception as e:
                        logger.error(f"CSV import (append) failed: {e}")
                        st.error(f"Import failed: {e}")
        else:
            st.error(message)

# ========================================
# 5. CRUD OPERATIONS SECTION  
# ========================================
st.markdown("---")
st.subheader("⚙️ CRUD Operations")

# Operation buttons
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("➕ Create Record", key="create_btn"):
        st.session_state.show_create_form = True
        st.session_state.show_update_form = False

with col2:
    if st.button("✏️ Update Record", key="update_btn"):
        st.session_state.show_update_form = True
        st.session_state.show_create_form = False

with col3:
    if st.button("🗑️ Delete Record", key="delete_btn"):
        st.session_state.show_delete_form = True

with col4:
    if st.button("🔄 Refresh", key="refresh_btn"):
        refresh_data()
        reset_forms()
        st.rerun()

# Create Record Form
if st.session_state.show_create_form:
    st.markdown("---")
    st.subheader("➕ Create New Record")
    
    with st.form("create_record_form"):
        st.markdown("**Enter new record details:**")
        
        # Get column names for form
        sample_data = repository.get_all_data()
        if not sample_data.empty:
            columns = [col for col in sample_data.columns if col not in ['rowid']]
            form_data = RecordFormHandler.create_record_form(columns)
            
            submitted = st.form_submit_button("✅ Create Record")
            
            if submitted:
                # Validate data
                is_valid, errors = data_service.validate_record_data(form_data)
                
                if is_valid:
                    # Remove empty values
                    clean_data = {k: v for k, v in form_data.items() if v and v.strip()}
                    
                    # Create record
                    success = repository.create_record(clean_data)
                    
                    if success:
                        logger.info(f"Successfully created new record with data: {clean_data}")
                        st.success("✅ Record created successfully!")
                        reset_forms()
                        refresh_data()
                        st.rerun()
                    else:
                        logger.error(f"Failed to create record with data: {clean_data}")
                        st.error("❌ Failed to create record.")
                else:
                    st.error("❌ Validation errors:")
                    for error in errors:
                        st.error(f"• {error}")

# Update Record Form  
if st.session_state.show_update_form:
    st.markdown("---")
    st.subheader("✏️ Update Record")
    
    # Record selection
    if not filtered_df.empty:
        record_options = {f"ID {row['rowid']}: {row.get('gender', 'N/A')} - {row.get('division', 'N/A')}": row['rowid'] 
                         for _, row in filtered_df.iterrows()}
        
        selected_record = st.selectbox(
            "Select record to update:",
            options=list(record_options.keys()),
            key="record_selector"
        )
        
        if selected_record:
            record_id = record_options[selected_record]
            existing_record = repository.get_record_by_id(record_id)
            
            if existing_record:
                with st.form("update_record_form"):
                    st.markdown(f"**Updating record ID: {record_id}**")
                    
                    # Pre-populate form with existing data
                    columns = [col for col in existing_record.keys() if col not in ['rowid']]
                    form_data = RecordFormHandler.create_record_form(columns, existing_record)
                    
                    submitted = st.form_submit_button("✅ Update Record")
                    
                    if submitted:
                        # Validate data
                        is_valid, errors = data_service.validate_record_data(form_data)
                        
                        if is_valid:
                            # Remove empty values
                            clean_data = {k: v for k, v in form_data.items() if v and v.strip()}
                            
                            # Update record
                            success = repository.update_record(record_id, clean_data)
                            
                            if success:
                                logger.info(f"Successfully updated record ID {record_id} with data: {clean_data}")
                                st.success("✅ Record updated successfully!")
                                reset_forms()
                                refresh_data()
                                st.rerun()
                            else:
                                logger.error(f"Failed to update record ID {record_id} with data: {clean_data}")
                                st.error("❌ Failed to update record.")
                        else:
                            st.error("❌ Validation errors:")
                            for error in errors:
                                st.error(f"• {error}")

# Delete Record Form
if st.session_state.get('show_delete_form', False):
    st.markdown("---")
    st.subheader("🗑️ Delete Record")
    
    if not filtered_df.empty:
        record_options = {f"ID {row['rowid']}: {row.get('gender', 'N/A')} - {row.get('division', 'N/A')}": row['rowid'] 
                         for _, row in filtered_df.iterrows()}
        
        selected_record = st.selectbox(
            "Select record to delete:",
            options=list(record_options.keys()),
            key="delete_selector"
        )
        
        if selected_record:
            record_id = record_options[selected_record]
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Confirm Delete", key="confirm_delete", type="primary"):
                    success = repository.delete_record(record_id)
                    
                    if success:
                        logger.info(f"Successfully deleted record ID {record_id}")
                        st.success("✅ Record deleted successfully!")
                        st.session_state.show_delete_form = False
                        refresh_data()
                        st.rerun()
                    else:
                        logger.error(f"Failed to delete record ID {record_id}")
                        st.error("❌ Failed to delete record.")
            
            with col2:
                if st.button("❌ Cancel", key="cancel_delete"):
                    st.session_state.show_delete_form = False
                    st.rerun()

# ========================================
# 6. EXPORT OPTIONS SECTION
# ========================================
st.markdown("---")
st.subheader("📤 Export Options")

if not filtered_df.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV Export
        csv_data = data_service.export_to_csv(filtered_df)
        
        st.download_button(
            label="📄 Download as CSV",
            data=csv_data,
            file_name=f"student_mental_health_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key="download_csv"
        )
    
    with col2:
        # Statistics summary export
        if 'stats' in locals():
            stats_text = f"""Student Mental Health Data Statistics
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Total Records: {stats.get('total_records', 0)}
Total Columns: {stats.get('total_columns', 0)}
Memory Usage: {stats.get('memory_usage', 'N/A')}

Applied Filters:
{chr(10).join([f"• {k}: {v}" for k, v in filters.items()]) if filters else "No filters applied"}
"""
            
            st.download_button(
                label="📊 Download Statistics",
                data=stats_text,
                file_name=f"data_statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                key="download_stats"
            )
else:
    st.info("💡 Apply filters or load data to enable export options.")

# Auto-refresh handling
if st.session_state.refresh_data:
    st.session_state.refresh_data = False
    st.rerun()