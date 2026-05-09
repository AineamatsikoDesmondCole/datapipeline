#!/usr/bin/env python3


import pandas as pd
import numpy as np
import re
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PatentDataCleaner:
    """Clean and process patent data using pandas."""
    
    def __init__(self, raw_data_dir: str = "../data", clean_data_dir: str = "../clean_data_files"):
        """
        Initialize the data cleaner.
        
        Args:
            raw_data_dir: Directory containing raw data files
            clean_data_dir: Directory to save cleaned data files
        """
        self.raw_data_dir = Path(raw_data_dir)
        self.clean_data_dir = Path(clean_data_dir)
        self.clean_data_dir.mkdir(exist_ok=True)
        
        # File paths
        self.raw_patents_file = self.raw_data_dir / 'raw_patents.csv'
        self.raw_inventors_file = self.raw_data_dir / 'raw_inventors.csv'
        self.raw_companies_file = self.raw_data_dir / 'raw_companies.csv'
        self.raw_relationships_file = self.raw_data_dir / 'raw_relationships.csv'
        
        # Clean file paths
        self.clean_patents_file = self.clean_data_dir / 'clean_patents.csv'
        self.clean_inventors_file = self.clean_data_dir / 'clean_inventors.csv'
        self.clean_companies_file = self.clean_data_dir / 'clean_companies.csv'
    
    def clean_text(self, text: str) -> str:
        """
        Clean text data by removing extra whitespace and special characters.
        
        Args:
            text: Input text string
            
        Returns:
            Cleaned text string
        """
        if pd.isna(text) or text is None:
            return ""
        
        # Convert to string and clean
        text = str(text).strip()
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\-\.\,\:\;]', '', text)
        
        return text.strip()
    
    def standardize_country(self, country: str) -> str:
        """
        Standardize country names.
        
        Args:
            country: Country name string
            
        Returns:
            Standardized country name
        """
        if pd.isna(country) or country is None:
            return "Unknown"
        
        country = str(country).strip().upper()
        
        # Country name mapping
        country_mapping = {
            'US': 'USA',
            'USA': 'USA',
            'UNITED STATES': 'USA',
            'CN': 'China',
            'CHINA': 'China',
            'JP': 'Japan',
            'JAPAN': 'Japan',
            'DE': 'Germany',
            'GERMANY': 'Germany',
            'GB': 'UK',
            'UK': 'UK',
            'UNITED KINGDOM': 'UK',
            'FR': 'France',
            'FRANCE': 'France',
            'KR': 'South Korea',
            'SOUTH KOREA': 'South Korea',
            'CA': 'Canada',
            'CANADA': 'Canada',
            'IN': 'India',
            'INDIA': 'India'
        }
        
        return country_mapping.get(country, country.title())
    
    def validate_patent_id(self, patent_id: str) -> str:
        """
        Validate and standardize patent IDs.
        
        Args:
            patent_id: Patent ID string
            
        Returns:
            Validated patent ID
        """
        if pd.isna(patent_id) or patent_id is None:
            return ""
        
        patent_id = str(patent_id).strip().upper()
        
        # Basic validation for US patent format
        if re.match(r'^US\d+', patent_id):
            return patent_id
        else:
            # Try to add US prefix if missing
            if re.match(r'^\d+', patent_id):
                return f'US{patent_id}'
            else:
                return patent_id
    
    def clean_patents_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean patents dataframe.
        
        Args:
            df: Raw patents dataframe
            
        Returns:
            Cleaned patents dataframe
        """
        logger.info("Cleaning patents data")
        
        # Make a copy to avoid SettingWithCopyWarning
        df_clean = df.copy()
        
        # Clean patent_id
        df_clean['patent_id'] = df_clean['patent_id'].apply(self.validate_patent_id)
        
        # Clean title and abstract
        df_clean['title'] = df_clean['title'].apply(self.clean_text)
        df_clean['abstract'] = df_clean['abstract'].apply(self.clean_text)
        
        # Convert filing_date to datetime
        df_clean['filing_date'] = pd.to_datetime(df_clean['filing_date'], errors='coerce')
        
        # Extract year from filing_date
        df_clean['year'] = df_clean['filing_date'].dt.year
        
        # Fill missing years with reasonable defaults
        current_year = datetime.now().year
        df_clean['year'] = df_clean['year'].fillna(current_year).astype(int)
        
        # Remove rows with missing patent_id
        df_clean = df_clean[df_clean['patent_id'] != ""]
        
        # Remove duplicates based on patent_id
        df_clean = df_clean.drop_duplicates(subset=['patent_id'], keep='first')
        
        # Reset index
        df_clean = df_clean.reset_index(drop=True)
        
        logger.info(f"Cleaned patents data: {len(df_clean)} records")
        return df_clean
    
    def clean_inventors_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean inventors dataframe.
        
        Args:
            df: Raw inventors dataframe
            
        Returns:
            Cleaned inventors dataframe
        """
        logger.info("Cleaning inventors data")
        
        df_clean = df.copy()
        
        # Clean inventor_id
        df_clean['inventor_id'] = df_clean['inventor_id'].astype(str).str.strip()
        
        # Clean name
        df_clean['name'] = df_clean['name'].apply(self.clean_text)
        
        # Standardize country
        df_clean['country'] = df_clean['country'].apply(self.standardize_country)
        
        # Remove rows with missing inventor_id or name
        df_clean = df_clean[(df_clean['inventor_id'] != "") & (df_clean['name'] != "")]
        
        # Remove duplicates
        df_clean = df_clean.drop_duplicates(subset=['inventor_id'], keep='first')
        
        # Reset index
        df_clean = df_clean.reset_index(drop=True)
        
        logger.info(f"Cleaned inventors data: {len(df_clean)} records")
        return df_clean
    
    def clean_companies_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean companies dataframe.
        
        Args:
            df: Raw companies dataframe
            
        Returns:
            Cleaned companies dataframe
        """
        logger.info("Cleaning companies data")
        
        df_clean = df.copy()
        
        # Clean company_id
        df_clean['company_id'] = df_clean['company_id'].astype(str).str.strip()
        
        # Clean company name
        df_clean['name'] = df_clean['name'].apply(self.clean_text)
        
        # Standardize company names (remove common suffixes)
        df_clean['name'] = df_clean['name'].str.replace(r'\s+(INC|CORP|LLC|LTD|CO)\.?$', '', case=False, regex=True)
        
        # Remove rows with missing company_id or name
        df_clean = df_clean[(df_clean['company_id'] != "") & (df_clean['name'] != "")]
        
        # Remove duplicates
        df_clean = df_clean.drop_duplicates(subset=['company_id'], keep='first')
        
        # Reset index
        df_clean = df_clean.reset_index(drop=True)
        
        logger.info(f"Cleaned companies data: {len(df_clean)} records")
        return df_clean
    
    def generate_data_quality_report(self, data_dict: Dict[str, pd.DataFrame]) -> Dict:
        """
        Generate a data quality report.
        
        Args:
            data_dict: Dictionary containing cleaned dataframes
            
        Returns:
            Data quality report dictionary
        """
        report = {}
        
        for table_name, df in data_dict.items():
            report[table_name] = {
                'total_records': len(df),
                'total_columns': len(df.columns),
                'missing_values': df.isnull().sum().to_dict(),
                'duplicate_rows': df.duplicated().sum(),
                'data_types': df.dtypes.to_dict()
            }
        
        return report
    
    def clean_all_data(self) -> Dict[str, any]:
        """
        Main method to clean all data files.
        
        Returns:
            Dictionary containing cleaning results and file paths
        """
        logger.info("Starting data cleaning process")
        
        try:
            # Load raw data
            patents_df = pd.read_csv(self.raw_patents_file)
            inventors_df = pd.read_csv(self.raw_inventors_file)
            companies_df = pd.read_csv(self.raw_companies_file)
            
            logger.info(f"Loaded raw data: Patents: {len(patents_df)}, Inventors: {len(inventors_df)}, Companies: {len(companies_df)}")
            
            # Clean each dataset
            clean_patents = self.clean_patents_data(patents_df)
            clean_inventors = self.clean_inventors_data(inventors_df)
            clean_companies = self.clean_companies_data(companies_df)
            
            # Save cleaned data
            clean_patents.to_csv(self.clean_patents_file, index=False)
            clean_inventors.to_csv(self.clean_inventors_file, index=False)
            clean_companies.to_csv(self.clean_companies_file, index=False)
            
            # Generate data quality report
            data_dict = {
                'patents': clean_patents,
                'inventors': clean_inventors,
                'companies': clean_companies
            }
            quality_report = self.generate_data_quality_report(data_dict)
            
            logger.info("Data cleaning completed successfully!")
            
            result = {
                'status': 'success',
                'message': 'Data cleaning completed successfully',
                'files': {
                    'patents': str(self.clean_patents_file),
                    'inventors': str(self.clean_inventors_file),
                    'companies': str(self.clean_companies_file)
                },
                'record_counts': {
                    'patents': len(clean_patents),
                    'inventors': len(clean_inventors),
                    'companies': len(clean_companies)
                },
                'quality_report': quality_report
            }
            
        except Exception as e:
            logger.error(f"Error during data cleaning: {e}")
            result = {
                'status': 'error',
                'message': f'Data cleaning failed: {str(e)}',
                'files': {},
                'record_counts': {},
                'quality_report': {}
            }
        
        return result

def main():
    """Main function to run the data cleaning."""
    cleaner = PatentDataCleaner()
    result = cleaner.clean_all_data()
    
    if result['status'] == 'success':
        logger.info("Data cleaning completed successfully!")
        for table, count in result['record_counts'].items():
            logger.info(f"{table.capitalize()}: {count} records")
    else:
        logger.error(f"Data cleaning failed: {result['message']}")
    
    return result

if __name__ == "__main__":
    main()
