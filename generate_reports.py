#!/usr/bin/env python3


import pandas as pd
import json
from pathlib import Path
import logging
from typing import Dict, List, Any
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from analyze_data import PatentDataAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PatentReportGenerator:
    """Generate various types of reports from patent analysis results."""
    
    def __init__(self, output_dir: str = "../reports"):
        """
        Initialize the report generator.
        
        Args:
            output_dir: Directory to save generated reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.analyzer = PatentDataAnalyzer()
        
    def generate_console_report(self, analysis_results: Dict[str, pd.DataFrame]) -> str:
        """
        Generate a formatted console report.
        
        Args:
            analysis_results: Dictionary containing analysis results
            
        Returns:
            Formatted console report string
        """
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("          PATENT INTELLIGENCE REPORT")
        report_lines.append("=" * 60)
        report_lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Total patents
        if 'trends_over_time' in analysis_results and not analysis_results['trends_over_time'].empty:
            total_patents = analysis_results['trends_over_time']['patent_count'].sum()
            report_lines.append(f"📊 TOTAL PATENTS: {total_patents:,}")
            report_lines.append("")
        
        # Top Inventors
        if 'top_inventors' in analysis_results and not analysis_results['top_inventors'].empty:
            report_lines.append("👥 TOP INVENTORS:")
            top_inventors = analysis_results['top_inventors'].head(5)
            for i, (_, row) in enumerate(top_inventors.iterrows(), 1):
                report_lines.append(f"   {i}. {row['inventor_name']} ({row['inventor_country']}) - {row['patent_count']} patents")
            report_lines.append("")
        
        # Top Companies
        if 'top_companies' in analysis_results and not analysis_results['top_companies'].empty:
            report_lines.append("🏢 TOP COMPANIES:")
            top_companies = analysis_results['top_companies'].head(5)
            for i, (_, row) in enumerate(top_companies.iterrows(), 1):
                report_lines.append(f"   {i}. {row['company_name']} - {row['patent_count']} patents")
            report_lines.append("")
        
        # Top Countries
        if 'top_countries' in analysis_results and not analysis_results['top_countries'].empty:
            report_lines.append("🌍 TOP COUNTRIES:")
            top_countries = analysis_results['top_countries'].head(5)
            for i, (_, row) in enumerate(top_countries.iterrows(), 1):
                report_lines.append(f"   {i}. {row['country']} - {row['patent_count']} patents ({row['percentage_share']}%)")
            report_lines.append("")
        
        # Recent Trends
        if 'trends_over_time' in analysis_results and not analysis_results['trends_over_time'].empty:
            report_lines.append("📈 RECENT TRENDS:")
            recent_years = analysis_results['trends_over_time'].tail(3)
            for _, row in recent_years.iterrows():
                growth = f"+{row['year_over_year_growth']}%" if pd.notna(row['year_over_year_growth']) and row['year_over_year_growth'] > 0 else f"{row['year_over_year_growth']}%"
                report_lines.append(f"   {row['year']}: {row['patent_count']} patents ({growth})")
            report_lines.append("")
        
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)
    
    def generate_csv_reports(self, analysis_results: Dict[str, pd.DataFrame]) -> Dict[str, str]:
        """
        Generate CSV reports.
        
        Args:
            analysis_results: Dictionary containing analysis results
            
        Returns:
            Dictionary with file paths of generated CSV files
        """
        csv_files = {}
        
        try:
            # Top Inventors CSV
            if 'top_inventors' in analysis_results and not analysis_results['top_inventors'].empty:
                inventors_file = self.output_dir / 'top_inventors.csv'
                analysis_results['top_inventors'].to_csv(inventors_file, index=False)
                csv_files['top_inventors'] = str(inventors_file)
                logger.info(f"Generated top_inventors.csv: {len(analysis_results['top_inventors'])} records")
            
            # Top Companies CSV
            if 'top_companies' in analysis_results and not analysis_results['top_companies'].empty:
                companies_file = self.output_dir / 'top_companies.csv'
                analysis_results['top_companies'].to_csv(companies_file, index=False)
                csv_files['top_companies'] = str(companies_file)
                logger.info(f"Generated top_companies.csv: {len(analysis_results['top_companies'])} records")
            
            # Country Trends CSV
            if 'top_countries' in analysis_results and not analysis_results['top_countries'].empty:
                countries_file = self.output_dir / 'country_trends.csv'
                analysis_results['top_countries'].to_csv(countries_file, index=False)
                csv_files['country_trends'] = str(countries_file)
                logger.info(f"Generated country_trends.csv: {len(analysis_results['top_countries'])} records")
            
            # Trends Over Time CSV
            if 'trends_over_time' in analysis_results and not analysis_results['trends_over_time'].empty:
                trends_file = self.output_dir / 'patent_trends.csv'
                analysis_results['trends_over_time'].to_csv(trends_file, index=False)
                csv_files['patent_trends'] = str(trends_file)
                logger.info(f"Generated patent_trends.csv: {len(analysis_results['trends_over_time'])} records")
            
        except Exception as e:
            logger.error(f"Error generating CSV reports: {e}")
        
        return csv_files
    
    def generate_json_report(self, analysis_results: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        Generate JSON report.
        
        Args:
            analysis_results: Dictionary containing analysis results
            
        Returns:
            Dictionary containing JSON report data
        """
        json_report = {
            'generated_at': datetime.now().isoformat(),
            'total_patents': 0,
            'top_inventors': [],
            'top_companies': [],
            'top_countries': [],
            'yearly_trends': [],
            'summary': {}
        }
        
        try:
            # Total patents
            if 'trends_over_time' in analysis_results and not analysis_results['trends_over_time'].empty:
                json_report['total_patents'] = int(analysis_results['trends_over_time']['patent_count'].sum())
            
            # Top Inventors
            if 'top_inventors' in analysis_results and not analysis_results['top_inventors'].empty:
                for _, row in analysis_results['top_inventors'].head(10).iterrows():
                    json_report['top_inventors'].append({
                        'name': row['inventor_name'],
                        'country': row['inventor_country'],
                        'patents': int(row['patent_count'])
                    })
            
            # Top Companies
            if 'top_companies' in analysis_results and not analysis_results['top_companies'].empty:
                for _, row in analysis_results['top_companies'].head(10).iterrows():
                    json_report['top_companies'].append({
                        'name': row['company_name'],
                        'patents': int(row['patent_count'])
                    })
            
            # Top Countries
            if 'top_countries' in analysis_results and not analysis_results['top_countries'].empty:
                for _, row in analysis_results['top_countries'].head(10).iterrows():
                    json_report['top_countries'].append({
                        'country': row['country'],
                        'patents': int(row['patent_count']),
                        'share_percentage': float(row['percentage_share'])
                    })
            
            # Yearly Trends
            if 'trends_over_time' in analysis_results and not analysis_results['trends_over_time'].empty:
                for _, row in analysis_results['trends_over_time'].iterrows():
                    trend_data = {
                        'year': int(row['year']),
                        'patents': int(row['patent_count'])
                    }
                    if pd.notna(row['year_over_year_growth']):
                        trend_data['growth_percentage'] = float(row['year_over_year_growth'])
                    json_report['yearly_trends'].append(trend_data)
            
            # Summary
            json_report['summary'] = {
                'total_inventors': len(json_report['top_inventors']),
                'total_companies': len(json_report['top_companies']),
                'total_countries': len(json_report['top_countries']),
                'years_analyzed': len(json_report['yearly_trends'])
            }
            
            # Save JSON report
            json_file = self.output_dir / 'patent_report.json'
            with open(json_file, 'w') as f:
                json.dump(json_report, f, indent=2)
            logger.info(f"Generated patent_report.json")
            
        except Exception as e:
            logger.error(f"Error generating JSON report: {e}")
        
        return json_report
    
    def create_visualizations(self, analysis_results: Dict[str, pd.DataFrame]) -> Dict[str, str]:
        """
        Create data visualizations.
        
        Args:
            analysis_results: Dictionary containing analysis results
            
        Returns:
            Dictionary with file paths of generated visualization files
        """
        visualization_files = {}
        
        try:
            plt.style.use('seaborn-v0_8')
            
            # 1. Top Inventors Bar Chart
            if 'top_inventors' in analysis_results and not analysis_results['top_inventors'].empty:
                plt.figure(figsize=(12, 6))
                top_inventors = analysis_results['top_inventors'].head(10)
                plt.barh(range(len(top_inventors)), top_inventors['patent_count'])
                plt.yticks(range(len(top_inventors)), top_inventors['inventor_name'])
                plt.xlabel('Number of Patents')
                plt.title('Top 10 Inventors by Patent Count')
                plt.tight_layout()
                
                inventors_chart = self.output_dir / 'top_inventors_chart.png'
                plt.savefig(inventors_chart, dpi=300, bbox_inches='tight')
                plt.close()
                visualization_files['top_inventors_chart'] = str(inventors_chart)
                logger.info("Generated top_inventors_chart.png")
            
            # 2. Top Companies Pie Chart
            if 'top_companies' in analysis_results and not analysis_results['top_companies'].empty:
                plt.figure(figsize=(10, 8))
                top_companies = analysis_results['top_companies'].head(8)
                plt.pie(top_companies['patent_count'], labels=top_companies['company_name'], autopct='%1.1f%%')
                plt.title('Top 8 Companies by Patent Share')
                
                companies_chart = self.output_dir / 'top_companies_chart.png'
                plt.savefig(companies_chart, dpi=300, bbox_inches='tight')
                plt.close()
                visualization_files['top_companies_chart'] = str(companies_chart)
                logger.info("Generated top_companies_chart.png")
            
            # 3. Patent Trends Line Chart
            if 'trends_over_time' in analysis_results and not analysis_results['trends_over_time'].empty:
                plt.figure(figsize=(12, 6))
                trends = analysis_results['trends_over_time']
                plt.plot(trends['year'], trends['patent_count'], marker='o', linewidth=2)
                plt.xlabel('Year')
                plt.ylabel('Number of Patents')
                plt.title('Patent Trends Over Time')
                plt.grid(True, alpha=0.3)
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                trends_chart = self.output_dir / 'patent_trends_chart.png'
                plt.savefig(trends_chart, dpi=300, bbox_inches='tight')
                plt.close()
                visualization_files['patent_trends_chart'] = str(trends_chart)
                logger.info("Generated patent_trends_chart.png")
            
            # 4. Countries Distribution
            if 'top_countries' in analysis_results and not analysis_results['top_countries'].empty:
                plt.figure(figsize=(12, 6))
                top_countries = analysis_results['top_countries'].head(10)
                plt.bar(range(len(top_countries)), top_countries['patent_count'])
                plt.xticks(range(len(top_countries)), top_countries['country'], rotation=45)
                plt.ylabel('Number of Patents')
                plt.title('Top 10 Countries by Patent Count')
                plt.tight_layout()
                
                countries_chart = self.output_dir / 'top_countries_chart.png'
                plt.savefig(countries_chart, dpi=300, bbox_inches='tight')
                plt.close()
                visualization_files['top_countries_chart'] = str(countries_chart)
                logger.info("Generated top_countries_chart.png")
                
        except Exception as e:
            logger.error(f"Error creating visualizations: {e}")
        
        return visualization_files
    
    def generate_all_reports(self) -> Dict[str, Any]:
        """
        Generate all types of reports.
        
        Returns:
            Dictionary containing all generated reports and file paths
        """
        logger.info("Starting report generation")
        
        # Run analysis first
        analysis_results = self.analyzer.run_all_queries()
        
        if not analysis_results:
            logger.error("No analysis results available for report generation")
            return {'status': 'error', 'message': 'No analysis results available'}
        
        # Generate different types of reports
        console_report = self.generate_console_report(analysis_results)
        csv_files = self.generate_csv_reports(analysis_results)
        json_report = self.generate_json_report(analysis_results)
        visualization_files = self.create_visualizations(analysis_results)
        
        # Print console report
        print(console_report)
        
        # Save console report to file
        console_file = self.output_dir / 'console_report.txt'
        with open(console_file, 'w') as f:
            f.write(console_report)
        
        result = {
            'status': 'success',
            'message': 'All reports generated successfully',
            'console_report': console_report,
            'json_report': json_report,
            'files': {
                'console_report': str(console_file),
                'json_report': str(self.output_dir / 'patent_report.json'),
                'csv_files': csv_files,
                'visualizations': visualization_files
            }
        }
        
        logger.info("Report generation completed successfully")
        return result

def main():
    """Main function to generate all reports."""
    generator = PatentReportGenerator()
    result = generator.generate_all_reports()
    
    if result['status'] == 'success':
        logger.info("All reports generated successfully!")
        logger.info(f"Files created in: {generator.output_dir}")
    else:
        logger.error(f"Report generation failed: {result['message']}")
    
    return result

if __name__ == "__main__":
    main()
