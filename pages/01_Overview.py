# Overview Page - Key Metrics and Summary Statistics
import streamlit as st
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from db.repository import StudentMentalHealthRepository
from services.overview_analysis import (
    compute_kpis,
    plot_overall_depression, 
    plot_depression_by_gender_pie,
    plot_depression_by_division_bar,
    plot_risk_profile_radar
)

# Page configuration
st.title("📊 Overview")

st.write("Key metrics, summary statistics, and high-level insights about student mental health.")

# Initialize data repository and load data
try:
    data_repo = StudentMentalHealthRepository("data/student_mental_health.db")
    df = data_repo.get_all_data()
    
    if df.empty:
        st.warning("No data available. Please ensure the database has been initialized with data.")
        st.stop()
        
    # Compute KPIs
    kpis = compute_kpis(df)
    
    st.markdown("---")
    
    # Key Metrics Section
    st.subheader("🎯 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Students", 
            value=kpis['total_students']
        )
    
    with col2:
        st.metric(
            label="Depression Rate", 
            value=f"{kpis['pct_depressed']:.1f}%"
        )
    
    with col3:
        st.metric(
            label="Anxiety Rate", 
            value=f"{kpis['pct_anxious']:.1f}%" if 'pct_anxious' in kpis else "N/A"
        )
    
    with col4:
        st.metric(
            label="Help-Seeking Rate", 
            value=f"{kpis['pct_sought_help']:.1f}%" if 'pct_sought_help' in kpis else "N/A"
        )

    st.markdown("---")

    # Summary Visualizations Section
    st.subheader("📈 Summary Visualizations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Overall Depression Prevalence**")
        fig1 = plot_overall_depression(df)
        st.pyplot(fig1)
    
    with col2:
        st.write("**Depression by Gender**")
        fig2 = plot_depression_by_gender_pie(df)
        st.pyplot(fig2)
    
    # Full width charts
    st.write("**Depression by Academic Division**")
    fig3 = plot_depression_by_division_bar(df)
    st.pyplot(fig3)
    
    st.write("**Mental Health Risk Profile**")
    fig4 = plot_risk_profile_radar(df)
    st.pyplot(fig4)

    st.markdown("---")

    # Quick Insights Section
    st.subheader("💡 Key Insights")
    
    # Generate insights based on KPIs
    insights = []
    
    if kpis['total_students'] > 0:
        insights.append(f"📊 **{kpis['total_students']} students** participated in this mental health survey")
    
    if kpis['depression_rate'] > 0:
        if kpis['depression_rate'] > 30:
            insights.append(f"🚨 **High depression rate**: {kpis['depression_rate']:.1f}% of students report depression symptoms")
        else:
            insights.append(f"📈 **Depression rate**: {kpis['depression_rate']:.1f}% of students report depression symptoms")
    
    if 'help_seeking_rate' in kpis and kpis['help_seeking_rate'] < 50:
        insights.append(f"⚠️ **Low help-seeking behavior**: Only {kpis['help_seeking_rate']:.1f}% of students have sought mental health treatment")
    elif 'help_seeking_rate' in kpis:
        insights.append(f"✅ **Positive help-seeking**: {kpis['help_seeking_rate']:.1f}% of students have sought mental health treatment")
    
    # Display insights
    for insight in insights:
        st.write(insight)

    st.markdown("---")

    # Data Status Section
    st.subheader("🔄 Data Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write(f"**Records**: {len(df)} students")
    
    with col2:
        # Calculate data completeness
        completeness = (df.notna().sum().sum() / (len(df) * len(df.columns)) * 100)
        st.write(f"**Completeness**: {completeness:.1f}%")
    
    with col3:
        # Show available columns
        st.write(f"**Data Points**: {len(df.columns)} fields")

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.write("Please ensure the database has been initialized with data.")