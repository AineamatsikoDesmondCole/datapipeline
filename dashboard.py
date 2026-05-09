#!/usr/bin/env python3


import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path

# Add the code_files directory to the Python path
sys.path.append(str(Path(__file__).parent))

from analyze_data import PatentDataAnalyzer
from generate_reports import PatentReportGenerator

# Configure page
st.set_page_config(
    page_title="Patent Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_analysis_results():
    """Load and cache analysis results."""
    analyzer = PatentDataAnalyzer(db_path="../patents.db", schema_path="../database_file/schema.sql")
    results = analyzer.run_all_queries()
    analyzer.close_connection()
    return results

def create_overview_metrics(results):
    """Create overview metrics cards."""
    if 'trends_over_time' in results and not results['trends_over_time'].empty:
        total_patents = results['trends_over_time']['patent_count'].sum()
        total_inventors = len(results['top_inventors']) if 'top_inventors' in results else 0
        total_companies = len(results['top_companies']) if 'top_companies' in results else 0
        total_countries = len(results['top_countries']) if 'top_countries' in results else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>📊 Total Patents</h3>
                <h2>{:,}</h2>
            </div>
            """.format(total_patents), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3>👥 Inventors</h3>
                <h2>{:,}</h2>
            </div>
            """.format(total_inventors), unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3>🏢 Companies</h3>
                <h2>{:,}</h2>
            </div>
            """.format(total_companies), unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-card">
                <h3>🌍 Countries</h3>
                <h2>{:,}</h2>
            </div>
            """.format(total_countries), unsafe_allow_html=True)

def create_inventors_section(results):
    """Create inventors analysis section."""
    st.header("👥 Top Inventors Analysis")
    
    if 'top_inventors' in results and not results['top_inventors'].empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Bar chart of top inventors
            fig = px.bar(
                results['top_inventors'].head(10),
                x='patent_count',
                y='inventor_name',
                orientation='h',
                title="Top 10 Inventors by Patent Count",
                color='patent_count',
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Top inventors table
            st.subheader("Top 5 Inventors")
            top_inventors_table = results['top_inventors'].head(5).copy()
            top_inventors_table['Rank'] = range(1, 6)
            st.dataframe(
                top_inventors_table[['Rank', 'inventor_name', 'inventor_country', 'patent_count']],
                hide_index=True,
                use_container_width=True
            )

def create_companies_section(results):
    """Create companies analysis section."""
    st.header("🏢 Top Companies Analysis")
    
    if 'top_companies' in results and not results['top_companies'].empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Pie chart of top companies
            fig = px.pie(
                results['top_companies'].head(8),
                values='patent_count',
                names='company_name',
                title="Top 8 Companies by Patent Share"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Top companies table
            st.subheader("Top 5 Companies")
            top_companies_table = results['top_companies'].head(5).copy()
            top_companies_table['Rank'] = range(1, 6)
            st.dataframe(
                top_companies_table[['Rank', 'company_name', 'patent_count']],
                hide_index=True,
                use_container_width=True
            )

def create_countries_section(results):
    """Create countries analysis section."""
    st.header("🌍 Geographic Analysis")
    
    if 'top_countries' in results and not results['top_countries'].empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Bar chart of top countries
            fig = px.bar(
                results['top_countries'].head(10),
                x='country',
                y='patent_count',
                title="Top 10 Countries by Patent Count",
                color='patent_count',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Countries table with percentages
            st.subheader("Top 5 Countries")
            top_countries_table = results['top_countries'].head(5).copy()
            top_countries_table['Rank'] = range(1, 6)
            top_countries_table['Share'] = top_countries_table['percentage_share'].apply(lambda x: f"{x}%")
            st.dataframe(
                top_countries_table[['Rank', 'country', 'patent_count', 'Share']],
                hide_index=True,
                use_container_width=True
            )

def create_trends_section(results):
    """Create trends analysis section."""
    st.header("📈 Patent Trends Over Time")
    
    if 'trends_over_time' in results and not results['trends_over_time'].empty:
        # Line chart of patent trends
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=results['trends_over_time']['year'],
            y=results['trends_over_time']['patent_count'],
            mode='lines+markers',
            name='Patent Count',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8)
        ))
        
        # Add growth rate if available
        if 'year_over_year_growth' in results['trends_over_time'].columns:
            fig.add_trace(go.Scatter(
                x=results['trends_over_time']['year'],
                y=results['trends_over_time']['year_over_year_growth'],
                mode='lines+markers',
                name='YoY Growth (%)',
                yaxis='y2',
                line=dict(color='#ff7f0e', width=2, dash='dash'),
                marker=dict(size=6)
            ))
        
        # Create subplot with secondary y-axis
        fig = make_subplots(
            specs=[[{"secondary_y": True}]],
            subplot_titles=("Patent Trends Over Time",)
        )
        
        fig.add_trace(
            go.Scatter(
                x=results['trends_over_time']['year'],
                y=results['trends_over_time']['patent_count'],
                mode='lines+markers',
                name='Patent Count',
                line=dict(color='#1f77b4', width=3),
                marker=dict(size=8)
            ),
            secondary_y=False,
        )
        
        if 'year_over_year_growth' in results['trends_over_time'].columns:
            fig.add_trace(
                go.Scatter(
                    x=results['trends_over_time']['year'],
                    y=results['trends_over_time']['year_over_year_growth'],
                    mode='lines+markers',
                    name='YoY Growth (%)',
                    line=dict(color='#ff7f0e', width=2, dash='dash'),
                    marker=dict(size=6)
                ),
                secondary_y=True,
            )
        
        fig.update_xaxes(title_text="Year")
        fig.update_yaxes(title_text="Patent Count", secondary_y=False)
        fig.update_yaxes(title_text="Growth Rate (%)", secondary_y=True)
        
        fig.update_layout(height=400, title_text="Patent Trends Over Time")
        st.plotly_chart(fig, use_container_width=True)
        
        # Trends table
        st.subheader("Yearly Patent Data")
        trends_table = results['trends_over_time'].copy()
        if 'year_over_year_growth' in trends_table.columns:
            trends_table['Growth'] = trends_table['year_over_year_growth'].apply(
                lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A"
            )
        st.dataframe(
            trends_table[['year', 'patent_count', 'Growth']].rename(columns={
                'year': 'Year',
                'patent_count': 'Patents'
            }),
            hide_index=True,
            use_container_width=True
        )

def create_advanced_analysis_section(results):
    """Create advanced analysis section."""
    st.header("🔍 Advanced Analysis")
    
    tab1, tab2, tab3 = st.tabs(["Ranking Analysis", "CTE Analysis", "Join Query Results"])
    
    with tab1:
        if 'ranking_inventors' in results and not results['ranking_inventors'].empty:
            st.subheader("Inventor Rankings")
            ranking_data = results['ranking_inventors'].head(10).copy()
            st.dataframe(
                ranking_data[['inventor_name', 'inventor_country', 'patent_count', 'overall_rank', 'country_rank']],
                hide_index=True,
                use_container_width=True
            )
    
    with tab2:
        if 'cte_analysis' in results and not results['cte_analysis'].empty:
            st.subheader("Country-Company Analysis")
            st.dataframe(
                results['cte_analysis'],
                hide_index=True,
                use_container_width=True
            )
    
    with tab3:
        if 'join_query' in results and not results['join_query'].empty:
            st.subheader("Patent-Inventor-Company Relationships")
            st.dataframe(
                results['join_query'].head(20),
                hide_index=True,
                use_container_width=True
            )

def main():
    """Main dashboard function."""
    # Header
    st.markdown('<h1 class="main-header">📊 Global Patent Intelligence Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Dashboard Controls")
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    # Data loading status
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Data Status")
    
    # Load data with loading indicator
    with st.spinner("Loading patent data..."):
        try:
            results = load_analysis_results()
            st.sidebar.success("✅ Data loaded successfully")
        except Exception as e:
            st.sidebar.error(f"❌ Error loading data: {e}")
            st.error("Failed to load patent data. Please check the data pipeline.")
            return
    
    # Main content
    st.markdown("---")
    
    # Overview metrics
    create_overview_metrics(results)
    
    st.markdown("---")
    
    # Section tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", 
        "👥 Inventors", 
        "🏢 Companies", 
        "🌍 Countries", 
        "📈 Trends"
    ])
    
    with tab1:
        create_advanced_analysis_section(results)
    
    with tab2:
        create_inventors_section(results)
    
    with tab3:
        create_companies_section(results)
    
    with tab4:
        create_countries_section(results)
    
    with tab5:
        create_trends_section(results)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>Global Patent Intelligence Dashboard | Last updated: {}</p>
        <p>Built with Streamlit, Plotly, and Patent Data</p>
    </div>
    """.format(pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
