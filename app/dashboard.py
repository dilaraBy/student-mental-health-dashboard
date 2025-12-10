# Streamlit UI for Student Mental Health Dashboard
import pandas as pd
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from utils.config import RAW_DATA_PATH, DB_PATH
from utils.logger import get_logger
from services.data_processing import clean_data
from db.repository import StudentMentalHealthRepository
from services.analysis import compute_prevalence
from services.visualization import (
    plot_depression_prevalence,
    plot_depression_by_gender,
    plot_depression_by_division,
    plot_depression_by_year_of_study,
    plot_monthly_depression_trend
)

logger = get_logger(__name__)


def get_data_from_db() -> pd.DataFrame:
    """Fetch all data from the DB."""
    repo = StudentMentalHealthRepository(str(DB_PATH))
    return repo.get_all_data()


def initialize_database() -> bool:
    """Initialize database with cleaned data. Returns True if successful."""
    try:
        logger.info("Initializing database with cleaned data...")
        
        # Step 1: Clean the data
        df = clean_data(str(RAW_DATA_PATH))
        logger.info(f"Cleaned data: {df.shape} rows")
        
        # Step 2: Initialize repository and tables
        repo = StudentMentalHealthRepository(str(DB_PATH))
        repo.init_tables()
        
        # Step 3: Insert cleaned data (replace existing)
        count = repo.insert_data(df, if_exists="replace")
        logger.info(f"Database initialized with {count} rows")
        
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False


def get_filtered_data(gender=None, division=None, year_of_study=None, depression=None) -> pd.DataFrame:
    """Get filtered data from the repository."""
    repo = StudentMentalHealthRepository(str(DB_PATH))
    
    # Build filters dictionary, excluding None values
    filters = {}
    if gender is not None:
        filters["gender"] = gender
    if division is not None:
        filters["division"] = division
    if year_of_study is not None:
        filters["year_of_study"] = year_of_study
    if depression is not None:
        filters["depression"] = depression
    
    return repo.filter_by_multiple(filters)


def main():
    try:
        import streamlit as st
    except Exception as e:
        logger.error(f"Streamlit is required to run the dashboard: {e}")
        raise

    st.set_page_config(page_title="Student Mental Health Dashboard", layout="wide")

    st.title("📊 Student Mental Health Dashboard")

    # --- Automatic Database Initialization ---
    if "db_initialized" not in st.session_state:
        with st.spinner("🔄 Initializing dashboard with fresh data..."):
            success = initialize_database()
            if success:
                st.session_state.db_initialized = True
                logger.info("Dashboard database initialization complete")
            else:
                st.error("❌ Failed to initialize database. Please check the logs.")
                st.stop()
    
    # Show initialization status
    if st.session_state.get("db_initialized", False):
        st.sidebar.success("✅ Database Ready")
    else:
        st.sidebar.error("❌ Database Not Ready")
        st.stop()

    # --- Filters Section ---
    st.sidebar.header("🔍 Filters")
    
    try:
        repo = StudentMentalHealthRepository(str(DB_PATH))
        
        # Get unique values from database
        unique_genders = repo.get_unique_values("gender")
        unique_divisions = repo.get_unique_values("division")
        unique_years = repo.get_unique_values("year_of_study")
        
        # Create filter dropdowns
        gender_options = ["All"] + unique_genders
        division_options = ["All"] + unique_divisions
        year_options = ["All"] + sorted(unique_years) if unique_years else ["All"]
        depression_options = ["All", "Yes", "No"]
        
        gender_filter = st.sidebar.selectbox("Gender", gender_options, index=0)
        division_filter = st.sidebar.selectbox("Division", division_options, index=0)
        year_filter = st.sidebar.selectbox("Year of Study", year_options, index=0)
        depression_filter = st.sidebar.selectbox("Depression", depression_options, index=0)
        
        # Convert "All" to None for repository filtering
        gender_param = None if gender_filter == "All" else gender_filter
        division_param = None if division_filter == "All" else division_filter
        year_param = None if year_filter == "All" else year_filter
        depression_param = None if depression_filter == "All" else depression_filter
        
    except Exception as e:
        st.error(f"Error setting up filters: {e}")
        logger.error(f"Error in filter setup: {e}")
        return

    # --- Get Filtered Data ---
    try:
        df = get_filtered_data(
            gender=gender_param,
            division=division_param,
            year_of_study=year_param,
            depression=depression_param,
        )
    except Exception as e:
        st.error(f"Error fetching filtered data: {e}")
        logger.error(f"Error fetching filtered data: {e}")
        return

    if df.empty:
        st.warning("No data matches the current filters.")
        return

    # ---- Overview Metrics ----
    st.subheader("Overview")

    col1, col2, col3 = st.columns(3)

    total_students = len(df)
    unique_genders = df["gender"].nunique() if "gender" in df.columns else 0
    unique_divisions = df["division"].nunique() if "division" in df.columns else 0

    col1.metric("Total Rows", total_students)
    col2.metric("Unique Genders", unique_genders)
    col3.metric("Unique Divisions", unique_divisions)

    # ---- Visualization Tabs ----
    st.subheader("📈 Mental Health Analytics")
    
    # Create tabs for different visualizations
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overall Prevalence",
        "👥 By Gender", 
        "🏢 By Division",
        "🎓 By Year of Study",
        "📅 Monthly Trend"
    ])
    
    with tab1:
        st.subheader("Depression Prevalence Overview")
        
        # Show text statistics
        if "depression" in df.columns:
            try:
                prev = compute_prevalence(df, "depression")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric(
                        "Depression Rate", 
                        f"{prev['yes_percentage']}%",
                        help="Percentage of students reporting depression"
                    )
                    st.metric(
                        "Students with Depression", 
                        prev['yes_count'],
                        help="Number of students reporting depression"
                    )
                
                with col2:
                    st.metric(
                        "No Depression Rate", 
                        f"{prev['no_percentage']}%",
                        help="Percentage of students not reporting depression"
                    )
                    st.metric(
                        "Students without Depression", 
                        prev['no_count'],
                        help="Number of students not reporting depression"
                    )
                
                # Show pie chart
                try:
                    fig = plot_depression_prevalence(df)
                    st.pyplot(fig)
                except Exception as e:
                    st.error(f"Error creating prevalence chart: {e}")
                    logger.error(f"Error in prevalence visualization: {e}")
                    
            except Exception as e:
                st.error(f"Error computing prevalence: {e}")
                logger.error(f"Error computing prevalence: {e}")
        else:
            st.info("Depression column not found in data.")
    
    with tab2:
        st.subheader("Depression Analysis by Gender")
        try:
            fig = plot_depression_by_gender(df)
            st.pyplot(fig)
            
            # Add summary statistics
            if "depression" in df.columns and "gender" in df.columns:
                gender_stats = df.groupby('gender')['depression'].apply(
                    lambda x: (x == 'Yes').sum() / len(x) * 100
                ).round(1)
                
                st.write("**Depression Rates by Gender:**")
                for gender, rate in gender_stats.items():
                    st.write(f"• {gender}: {rate}%")
                    
        except Exception as e:
            st.error(f"Error creating gender analysis: {e}")
            logger.error(f"Error in gender visualization: {e}")
    
    with tab3:
        st.subheader("Depression Analysis by Division")
        try:
            fig = plot_depression_by_division(df)
            st.pyplot(fig)
            
            # Add summary statistics
            if "depression" in df.columns and "division" in df.columns:
                division_stats = df.groupby('division')['depression'].apply(
                    lambda x: (x == 'Yes').sum() / len(x) * 100
                ).round(1)
                
                st.write("**Depression Rates by Division:**")
                for division, rate in division_stats.items():
                    st.write(f"• {division}: {rate}%")
                    
        except Exception as e:
            st.error(f"Error creating division analysis: {e}")
            logger.error(f"Error in division visualization: {e}")
    
    with tab4:
        st.subheader("Depression Analysis by Year of Study")
        try:
            fig = plot_depression_by_year_of_study(df)
            st.pyplot(fig)
            
            # Add summary statistics
            if "depression" in df.columns and "year_of_study" in df.columns:
                year_stats = df.groupby('year_of_study')['depression'].apply(
                    lambda x: (x == 'Yes').sum() / len(x) * 100
                ).round(1).sort_index()
                
                st.write("**Depression Rates by Year of Study:**")
                for year, rate in year_stats.items():
                    st.write(f"• Year {year}: {rate}%")
                    
        except Exception as e:
            st.error(f"Error creating year of study analysis: {e}")
            logger.error(f"Error in year of study visualization: {e}")
    
    with tab5:
        st.subheader("Monthly Depression Trend")
        try:
            fig = plot_monthly_depression_trend(df)
            st.pyplot(fig)
            
            # Add trend insights
            if "depression" in df.columns and "timestamp" in df.columns:
                try:
                    df_copy = df.copy()
                    df_copy['timestamp'] = pd.to_datetime(df_copy['timestamp'])
                    df_copy['month'] = df_copy['timestamp'].dt.strftime('%Y-%m')  # type: ignore
                    
                    monthly_rates = df_copy.groupby('month')['depression'].apply(
                        lambda x: (x == 'Yes').sum() / len(x) * 100
                    ).round(1)
                    
                    if len(monthly_rates) > 0:
                        highest_month = monthly_rates.idxmax()
                        lowest_month = monthly_rates.idxmin()
                        
                        st.write("**Monthly Trend Insights:**")
                        st.write(f"• Highest depression rate: {monthly_rates[highest_month]}% in {highest_month}")
                        st.write(f"• Lowest depression rate: {monthly_rates[lowest_month]}% in {lowest_month}")
                        st.write(f"• Average monthly rate: {monthly_rates.mean():.1f}%")
                        
                except Exception as e:
                    st.warning(f"Could not compute trend insights: {e}")
                    
        except Exception as e:
            st.error(f"Error creating monthly trend: {e}")
            logger.error(f"Error in monthly trend visualization: {e}")
    
    # ---- Data Export Section ----
    st.markdown("---")
    st.subheader("📋 Data Export & Details")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Filtered Data")
        st.dataframe(df, use_container_width=True)
    
    with col2:
        st.subheader("Export Options")
        
        # CSV download
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"mental_health_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        # Data summary
        st.write("**Data Summary:**")
        st.write(f"• Total Records: {len(df)}")
        if "depression" in df.columns:
            depression_yes = (df['depression'] == 'Yes').sum()
            st.write(f"• With Depression: {depression_yes}")
            st.write(f"• Depression Rate: {(depression_yes/len(df)*100):.1f}%")
        
        # Applied filters summary
        active_filters = []
        if gender_param: active_filters.append(f"Gender: {gender_param}")
        if division_param: active_filters.append(f"Division: {division_param}")
        if year_param: active_filters.append(f"Year of Study: {year_param}")
        if depression_param: active_filters.append(f"Depression: {depression_param}")
        
        if active_filters:
            st.write("**Active Filters:**")
            for filter_info in active_filters:
                st.write(f"• {filter_info}")
        else:
            st.write("**No filters applied** - showing all data")


if __name__ == "__main__":
    main()
