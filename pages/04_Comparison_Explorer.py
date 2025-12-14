"""
Comparison Explorer Page

This page provides a flexible playground for researchers to explore 
relationships between different variables and mental health metrics.
"""

import streamlit as st
import pandas as pd
import logging
import sys
import os

# Add the parent directory to the path so we can import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.comparison_analysis import ComparisonAnalysisService, InsightGenerator
from db.repository import StudentMentalHealthRepository

# Configure logging
logger = logging.getLogger(__name__)

# Configure page
st.set_page_config(page_title="Comparison Explorer", page_icon="🔄", layout="wide")

# Initialize services
@st.cache_resource
def init_services():
    """Initialize services with caching."""
    try:
        repository = StudentMentalHealthRepository('data/student_mental_health.db')
        comparison_service = ComparisonAnalysisService(repository)
        logger.info("Comparison Explorer services initialized successfully")
        return comparison_service
    except Exception as e:
        logger.error(f"Error initializing services: {e}")
        st.error(f"Error initializing services: {e}")
        return None

def main():
    """Main Comparison Explorer page function."""
    st.title("🔄 Comparison Explorer")
    st.write("""
    **Interactive Playground** - Pick any variable to compare against mental health metrics.
    Explore relationships and discover insights in the data.
    """)
    
    # Initialize services
    comparison_service = init_services()
    if not comparison_service:
        return
    
    # Create two columns for controls
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Comparison Settings")
        
        # X-axis selector
        x_options = comparison_service.get_available_x_axis_options()
        x_display_names = {
            'gender': 'Gender',
            'division': 'Geographical Division (Bangladesh)',
            'university': 'University',
            'course': 'Academic Course/Field',
            'year_of_study': 'Year of Study',
            'financial_stress_level': 'Financial Stress Level',
            'family_history_mental_illness': 'Family History of Mental Illness'
        }
        
        selected_x = st.selectbox(
            "**X-axis Variable**",
            options=x_options,
            format_func=lambda x: x_display_names.get(x, x.replace('_', ' ').title()) or x.replace('_', ' ').title(),
            help="Choose the variable to group and compare by"
        )
        
        # Y-metric selector
        y_metrics = comparison_service.get_available_y_metrics()
        selected_y = st.selectbox(
            "**Y-axis Metric**",
            options=list(y_metrics.keys()),
            format_func=lambda x: y_metrics[x],
            help="Choose the mental health metric to analyze"
        )
        
        # Chart type selection (automatic recommendation with manual override)
        recommended_chart_type = comparison_service.get_chart_type_recommendation(selected_x)
        chart_type = st.selectbox(
            "**Chart Type**",
            options=['bar', 'line'],
            index=0 if recommended_chart_type == 'bar' else 1,
            format_func=lambda x: f"{x.title()} Chart{'  (Recommended)' if x == recommended_chart_type else ''}",
            help="Bar charts work best for categorical data, line charts for temporal/ordered data"
        )
    
    with col2:
        st.subheader("🔍 Additional Filters")
        st.write("Apply optional filters to focus your analysis:")
        
        # Get available filter options (we'll keep this simple for now)
        filter_options = {
            'gender': ['Male', 'Female'],
            'depression': ['Yes', 'No'],
            'anxiety': ['Yes', 'No'],
            'financial_stress_level': ['Low', 'Medium', 'High']
        }
        
        filters = {}
        
        # Only show filter options that are different from selected X-axis
        available_filters = {k: v for k, v in filter_options.items() if k != selected_x}
        
        if available_filters:
            selected_filter_type = st.selectbox(
                "**Filter by**",
                options=['None'] + list(available_filters.keys()),
                format_func=lambda x: x.replace('_', ' ').title() if x != 'None' else 'No additional filter',
                help="Optionally filter the data by another variable"
            )
            
            if selected_filter_type != 'None':
                filter_value = st.selectbox(
                    f"**{selected_filter_type.replace('_', ' ').title()} Value**",
                    options=available_filters[selected_filter_type],
                    help=f"Only include records where {selected_filter_type} equals this value"
                )
                filters[selected_filter_type] = filter_value
        
        # Show current filter summary
        if filters:
            st.info(f"**Active Filter:** {list(filters.keys())[0].replace('_', ' ').title()} = {list(filters.values())[0]}")
        else:
            st.info("**No additional filters applied** - showing all data")
    
    # Generate comparison data and visualization
    try:
        # Compute comparison data
        with st.spinner("Computing comparison data..."):
            comparison_data = comparison_service.compute_comparison_data(
                x_axis=selected_x,
                y_metric=selected_y,
                filters=filters if filters else None
            )
        
        if comparison_data.empty:
            st.warning("⚠️ No data available for the selected combination of filters.")
            st.info("Try removing some filters or selecting different options.")
            return
        
        # Create visualization section
        st.subheader("📈 Interactive Comparison Visualization")
        
        # Add visualization options
        viz_type = st.radio(
            "**Visualization Type:**",
            options=['Standard Chart', 'Comprehensive Dashboard', 'Multi-Metric Analysis'],
            horizontal=True,
            help="Choose between a simple chart, comprehensive dashboard, or multi-metric comparison"
        )
        
        if viz_type == 'Standard Chart':
            # Create interactive chart
            with st.spinner("Creating interactive chart..."):
                interactive_chart = comparison_service.create_interactive_comparison_chart(
                    data=comparison_data,
                    x_axis=selected_x,
                    y_metric=selected_y,
                    chart_type=chart_type
                )
            
            # Display interactive chart
            st.plotly_chart(interactive_chart, use_container_width=True)
            
        elif viz_type == 'Comprehensive Dashboard':
            # Create comprehensive dashboard
            with st.spinner("Creating comprehensive dashboard..."):
                dashboard = comparison_service.create_comparison_dashboard(
                    data=comparison_data,
                    x_axis=selected_x,
                    y_metric=selected_y
                )
            
            # Display dashboard
            st.plotly_chart(dashboard, use_container_width=True)
            
        else:  # Multi-Metric Analysis
            # Create multi-metric comparison
            with st.spinner("Creating multi-metric analysis..."):
                multi_metric_chart = comparison_service.create_multi_metric_comparison(
                    x_axis=selected_x,
                    filters=filters if filters else None
                )
            
            # Display multi-metric chart
            st.plotly_chart(multi_metric_chart, use_container_width=True)
            
            # Add explanation for multi-metric view
            st.info("📊 **Multi-Metric Analysis** shows all mental health metrics (Depression, Anxiety, Panic Attacks, Help-Seeking) simultaneously for the selected variable, making it easy to compare patterns across different conditions.")
        
        # Display data summary
        with st.expander("📊 Data Summary", expanded=False):
            st.write("**Comparison Data:**")
            
            # Format the display data
            display_data = comparison_data.copy()
            display_data.columns = [
                x_display_names.get(col, col.replace('_', ' ').title()) 
                if col == selected_x else y_metrics.get(col, col)
                for col in display_data.columns
            ]
            
            st.dataframe(display_data, width='stretch')
            
            # Summary statistics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Highest Value",
                    f"{comparison_data[selected_y].max():.1f}%",
                    help="Maximum percentage across all categories"
                )
            
            with col2:
                st.metric(
                    "Average Value", 
                    f"{comparison_data[selected_y].mean():.1f}%",
                    help="Mean percentage across all categories"
                )
            
            with col3:
                st.metric(
                    "Range",
                    f"{comparison_data[selected_y].max() - comparison_data[selected_y].min():.1f}pp",
                    help="Difference between highest and lowest percentage"
                )
        
        # Advanced features section
        with st.expander("🔬 Advanced Analysis", expanded=False):
            st.write("**Additional Analysis Options:**")
            
            # Statistical summary
            summary = InsightGenerator.get_comparison_summary(
                data=comparison_data,
                x_axis=selected_x,
                y_metric=selected_y
            )
            
            if summary:
                st.json({
                    "Highest Category": {
                        "Name": summary['highest']['category'],
                        "Value": f"{summary['highest']['value']:.1f}%"
                    },
                    "Lowest Category": {
                        "Name": summary['lowest']['category'], 
                        "Value": f"{summary['lowest']['value']:.1f}%"
                    },
                    "Statistics": {
                        "Average": f"{summary['average']:.1f}%",
                        "Range": f"{summary['range']:.1f} percentage points"
                    }
                })
        
        logger.info(f"Comparison Explorer: {selected_x} vs {selected_y} - {len(comparison_data)} categories")
        
    except Exception as e:
        logger.error(f"Error in comparison analysis: {e}")
        st.error(f"An error occurred while generating the comparison: {e}")
        st.info("Please try different settings or check the data source.")

if __name__ == "__main__":
    main()