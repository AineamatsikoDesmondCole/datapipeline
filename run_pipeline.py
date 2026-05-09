#!/usr/bin/env python3


import sys
import os
from pathlib import Path
import logging

# Add the code_files directory to the Python path
sys.path.append(str(Path(__file__).parent))

from extract_data import PatentDataExtractor
from clean_data import PatentDataCleaner
from analyze_data import PatentDataAnalyzer
from generate_reports import PatentReportGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PatentPipeline:
    """Main pipeline orchestrator for patent data processing."""
    
    def __init__(self):
        """Initialize the pipeline."""
        self.extractor = PatentDataExtractor()
        self.cleaner = PatentDataCleaner()
        self.analyzer = PatentDataAnalyzer()
        self.report_generator = PatentReportGenerator()
    
    def run_extraction(self) -> bool:
        """Run data extraction step."""
        logger.info("🔄 Step 1: Data Extraction")
        try:
            result = self.extractor.extract_patent_data()
            if result['status'] == 'success':
                logger.info("✅ Data extraction completed successfully")
                return True
            else:
                logger.error(f"❌ Data extraction failed: {result['message']}")
                return False
        except Exception as e:
            logger.error(f"❌ Data extraction error: {e}")
            return False
    
    def run_cleaning(self) -> bool:
        """Run data cleaning step."""
        logger.info("🔄 Step 2: Data Cleaning")
        try:
            result = self.cleaner.clean_all_data()
            if result['status'] == 'success':
                logger.info("✅ Data cleaning completed successfully")
                for table, count in result['record_counts'].items():
                    logger.info(f"   {table.capitalize()}: {count} records")
                return True
            else:
                logger.error(f"❌ Data cleaning failed: {result['message']}")
                return False
        except Exception as e:
            logger.error(f"❌ Data cleaning error: {e}")
            return False
    
    def run_analysis(self) -> bool:
        """Run data analysis step."""
        logger.info("🔄 Step 3: Data Analysis")
        try:
            results = self.analyzer.run_all_queries()
            if results:
                logger.info("✅ Data analysis completed successfully")
                for query_name, df in results.items():
                    logger.info(f"   {query_name}: {len(df)} records")
                self.analyzer.close_connection()
                return True
            else:
                logger.error("❌ Data analysis failed: No results returned")
                return False
        except Exception as e:
            logger.error(f"❌ Data analysis error: {e}")
            return False
    
    def run_reporting(self) -> bool:
        """Run report generation step."""
        logger.info("🔄 Step 4: Report Generation")
        try:
            result = self.report_generator.generate_all_reports()
            if result['status'] == 'success':
                logger.info("✅ Report generation completed successfully")
                logger.info(f"📁 Reports saved to: {Path(result['files']['console_report']).parent}")
                return True
            else:
                logger.error(f"❌ Report generation failed: {result['message']}")
                return False
        except Exception as e:
            logger.error(f"❌ Report generation error: {e}")
            return False
    
    def run_full_pipeline(self) -> bool:
        """
        Run the complete patent data pipeline.
        
        Returns:
            bool: True if pipeline completed successfully, False otherwise
        """
        logger.info("🚀 Starting Global Patent Intelligence Data Pipeline")
        logger.info("=" * 60)
        
        # Run each step
        steps = [
            ("Data Extraction", self.run_extraction),
            ("Data Cleaning", self.run_cleaning),
            ("Data Analysis", self.run_analysis),
            ("Report Generation", self.run_reporting)
        ]
        
        for step_name, step_func in steps:
            if not step_func():
                logger.error(f"❌ Pipeline failed at {step_name} step")
                return False
        
        logger.info("=" * 60)
        logger.info("🎉 Pipeline completed successfully!")
        logger.info("📊 Check the reports directory for generated reports and visualizations.")
        return True

def main():
    """Main function to run the pipeline."""
    pipeline = PatentPipeline()
    success = pipeline.run_full_pipeline()
    
    if success:
        logger.info("✨ All tasks completed successfully!")
        return 0
    else:
        logger.error("💥 Pipeline failed!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
