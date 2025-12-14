# Download utilities for PDF and image generation
import io
import base64
from datetime import datetime
from typing import List, Tuple
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure


def create_pdf_from_figures(figures: List[Figure], title: str = "Dashboard Export") -> bytes:
    """
    Create a PDF from a list of matplotlib figures.
    
    Args:
        figures: List of matplotlib Figure objects
        title: Title for the PDF document
        
    Returns:
        bytes: PDF content as bytes
    """
    # Create a BytesIO buffer
    pdf_buffer = io.BytesIO()
    
    # Create PDF with multiple pages
    with PdfPages(pdf_buffer) as pdf:
        # Add title page
        title_fig = plt.figure(figsize=(8.5, 11))
        title_fig.suptitle(title, fontsize=20, fontweight='bold', y=0.8)
        
        # Add timestamp and metadata
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        title_fig.text(0.5, 0.6, f"Generated on: {timestamp}", 
                      ha='center', va='center', fontsize=14)
        title_fig.text(0.5, 0.5, "Student Mental Health Dashboard", 
                      ha='center', va='center', fontsize=16, style='italic')
        
        # Remove axes from title page
        title_fig.gca().set_axis_off()
        pdf.savefig(title_fig, bbox_inches='tight')
        plt.close(title_fig)
        
        # Add each figure to the PDF
        for fig in figures:
            if fig is not None:
                pdf.savefig(fig, bbox_inches='tight', dpi=300)
    
    # Get PDF content
    pdf_content = pdf_buffer.getvalue()
    pdf_buffer.close()
    
    return pdf_content


def save_figure_as_image(figure: Figure, format: str = 'png', dpi: int = 300) -> bytes:
    """
    Save a matplotlib figure as an image in memory.
    
    Args:
        figure: Matplotlib Figure object
        format: Image format ('png', 'jpg', 'svg')
        dpi: Resolution for raster formats
        
    Returns:
        bytes: Image content as bytes
    """
    img_buffer = io.BytesIO()
    
    # Save figure to buffer
    figure.savefig(img_buffer, format=format, bbox_inches='tight', dpi=dpi, 
                   facecolor='white', edgecolor='none')
    
    # Get image content
    img_content = img_buffer.getvalue()
    img_buffer.close()
    
    return img_content


def create_download_section(page_name: str, figures: List[Figure] = None):
    """
    Create a download section with PDF export option.
    
    Args:
        page_name: Name of the current page for file naming
        figures: List of matplotlib figures to include in downloads
    """
    st.markdown("### 📥 Download Options")
    
    if figures is None or len(figures) == 0:
        st.info("📊 Download options will appear after visualizations are loaded.")
        return
    
    # Filter out None figures
    valid_figures = [fig for fig in figures if fig is not None]
    
    if len(valid_figures) == 0:
        st.info("📊 Download options will appear after visualizations are loaded.")
        return
    
    # PDF Download
    try:
        pdf_content = create_pdf_from_figures(
            valid_figures, 
            f"{page_name.replace('_', ' ').title()} - Dashboard Export"
        )
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{page_name}_{timestamp}.pdf"
        
        st.download_button(
            label="📄 Download as PDF",
            data=pdf_content,
            file_name=filename,
            mime="application/pdf",
            key=f"pdf_download_{page_name}",
            help=f"Download all {len(valid_figures)} charts as PDF",
            use_container_width=True
        )
        
    except Exception as e:
        st.error(f"PDF generation error: {str(e)}")
    
    st.markdown("---")


def create_combined_figure(figures: List[Figure], title: str) -> Figure:
    """
    Create a combined figure from multiple matplotlib figures.
    Since copying matplotlib figures is complex, we create a simple overview.
    
    Args:
        figures: List of matplotlib Figure objects
        title: Title for the combined figure
        
    Returns:
        Figure: Combined matplotlib figure with summary info
    """
    # Create a summary figure
    combined_fig = plt.figure(figsize=(10, 6))
    combined_fig.suptitle(f"{title.replace('_', ' ').title()} - Dashboard Export Summary", 
                         fontsize=16, fontweight='bold')
    
    # Remove axes and add summary text
    ax = combined_fig.add_subplot(1, 1, 1)
    ax.axis('off')
    
    # Add summary information
    n_figures = len([fig for fig in figures if fig is not None])
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    summary_text = f"""
    📊 Dashboard Export Summary
    
    Generated: {timestamp}
    Total Visualizations: {n_figures}
    
    This export contains all the visualizations from the 
    {title.replace('_', ' ').title()} page of the Student Mental Health Dashboard.
    
    Each chart provides insights into different aspects of student mental health,
    including depression rates, demographic patterns, and risk factors.
    
    For the complete interactive experience, visit the dashboard online.
    """
    
    ax.text(0.5, 0.5, summary_text, ha='center', va='center', 
            transform=ax.transAxes, fontsize=12, 
            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8))
    
    plt.tight_layout()
    return combined_fig