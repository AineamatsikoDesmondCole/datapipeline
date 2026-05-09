#!/usr/bin/env python3
"""
Data Cleaning Script for Global Patent Intelligence Pipeline

This script cleans and processes raw patent data from USPTO TSV files.
It handles large datasets efficiently with chunked processing.

Author: Patent Intelligence Team
Date: 2026
"""

import pandas as pd
import numpy as np
import re
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import gc

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PatentDataCleaner:
    """Clean and process patent data using pandas with memory-efficient operations."""
    
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
        # Remove non-printable characters but keep basic punctuation
        text = re.sub(r'[^\w\s\-\.\,\:\;\(\)\[\]\/\&\@\#]', '', text)
        
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
            'U.S.A.': 'USA',
            'AMERICA': 'USA',
            'CN': 'China',
            'CHINA': 'China',
            'PEOPLES REPUBLIC OF CHINA': 'China',
            'PRC': 'China',
            'JP': 'Japan',
            'JAPAN': 'Japan',
            'DE': 'Germany',
            'GERMANY': 'Germany',
            'GB': 'UK',
            'UK': 'UK',
            'UNITED KINGDOM': 'UK',
            'GREAT BRITAIN': 'UK',
            'FR': 'France',
            'FRANCE': 'France',
            'KR': 'South Korea',
            'SOUTH KOREA': 'South Korea',
            'KOREA': 'South Korea',
            'CA': 'Canada',
            'CANADA': 'Canada',
            'IN': 'India',
            'INDIA': 'India',
            'TW': 'Taiwan',
            'TAIWAN': 'Taiwan',
            'SG': 'Singapore',
            'SINGAPORE': 'Singapore',
            'AU': 'Australia',
            'AUSTRALIA': 'Australia',
            'IT': 'Italy',
            'ITALY': 'Italy',
            'NL': 'Netherlands',
            'NETHERLANDS': 'Netherlands',
            'SE': 'Sweden',
            'SWEDEN': 'Sweden',
            'CH': 'Switzerland',
            'SWITZERLAND': 'Switzerland',
            'BE': 'Belgium',
            'BELGIUM': 'Belgium',
            'AT': 'Austria',
            'AUSTRIA': 'Austria',
            'NO': 'Norway',
            'NORWAY': 'Norway',
            'DK': 'Denmark',
            'DENMARK': 'Denmark',
            'FI': 'Finland',
            'FINLAND': 'Finland',
            'ES': 'Spain',
            'SPAIN': 'Spain',
            'PT': 'Portugal',
            'PORTUGAL': 'Portugal',
            'IE': 'Ireland',
            'IRELAND': 'Ireland',
            'IL': 'Israel',
            'ISRAEL': 'Israel',
            'RU': 'Russia',
            'RUSSIA': 'Russia',
            'BR': 'Brazil',
            'BRAZIL': 'Brazil',
            'MX': 'Mexico',
            'MEXICO': 'Mexico',
            'AR': 'Argentina',
            'ARGENTINA': 'Argentina'
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
        elif re.match(r'^\d+', patent_id):
            return f'US{patent_id}'
        else:
            return patent_id
    
    def clean_patents_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean patents dataframe with memory-efficient operations.
        
        Args:
            df: Raw patents dataframe
            
        Returns:
            Cleaned patents dataframe
        """
        logger.info("Cleaning patents data")
        
        # Make a copy to avoid SettingWithCopyWarning
        df_clean = df.copy()
        
        # Clean patent_id
        logger.info("Validating patent IDs")
        df_clean['patent_id'] = df_clean['patent_id'].apply(self.validate_patent_id)
        
        # Remove rows with invalid patent_id
        initial_count = len(df_clean)
        df_clean = df_clean[df_clean['patent_id'] != ""]
        logger.info(f"Removed {initial_count - len(df_clean)} rows with invalid patent IDs")
        
        # Clean title and abstract
        logger.info("Cleaning text fields")
        if 'title' in df_clean.columns:
            df_clean['title'] = df_clean['title'].apply(self.clean_text)
        if 'abstract' in df_clean.columns:
            df_clean['abstract'] = df_clean['abstract'].apply(self.clean_text)
        
        # Convert and validate dates
        logger.info("Processing dates")
        if 'filing_date' in df_clean.columns:
            df_clean['filing_date'] = pd.to_datetime(df_clean['filing_date'], errors='coerce')
            
            # Remove rows with invalid dates
            invalid_dates = df_clean['filing_date'].isna().sum()
            if invalid_dates > 0:
                logger.warning(f"Found {invalid_dates} rows with invalid filing dates")
                df_clean = df_clean.dropna(subset=['filing_date'])
            
            # Extract year from filing_date
            df_clean['year'] = df_clean['filing_date'].dt.year
        else:
            df_clean['year'] = 2023  # Default year
        
        # Filter reasonable date ranges
        if 'year' in df_clean.columns:
            current_year = datetime.now().year
            df_clean = df_clean[(df_clean['year'] >= 1976) & (df_clean['year'] <= current_year)]
        
        # Remove duplicates based on patent_id
        initial_count = len(df_clean)
        df_clean = df_clean.drop_duplicates(subset=['patent_id'], keep='first')
        logger.info(f"Removed {initial_count - len(df_clean)} duplicate patents")
        
        # Reset index
        df_clean = df_clean.reset_index(drop=True)
        
        # Memory cleanup
        gc.collect()
        
        logger.info(f"Cleaned patents data: {len(df_clean)} records")
        return df_clean
    
    def clean_inventors_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean inventors dataframe with memory-efficient operations.
        
        Args:
            df: Raw inventors dataframe
            
        Returns:
            Cleaned inventors dataframe
        """
        logger.info("Cleaning inventors data")
        
        df_clean = df.copy()
        
        # Clean inventor_id
        df_clean['inventor_id'] = df_clean['inventor_id'].astype(str).str.strip()
        
        # Remove rows with missing inventor_id
        initial_count = len(df_clean)
        df_clean = df_clean[df_clean['inventor_id'] != ""]
        logger.info(f"Removed {initial_count - len(df_clean)} rows with missing inventor IDs")
        
        # Clean name
        if 'name' in df_clean.columns:
            df_clean['name'] = df_clean['name'].apply(self.clean_text)
            # Remove rows with empty names
            df_clean = df_clean[df_clean['name'] != ""]
        
        # Standardize country
        if 'country' in df_clean.columns:
            df_clean['country'] = df_clean['country'].apply(self.standardize_country)
        
        # Remove duplicates based on inventor_id
        initial_count = len(df_clean)
        df_clean = df_clean.drop_duplicates(subset=['inventor_id'], keep='first')
        logger.info(f"Removed {initial_count - len(df_clean)} duplicate inventors")
        
        # Reset index
        df_clean = df_clean.reset_index(drop=True)
        
        # Memory cleanup
        gc.collect()
        
        logger.info(f"Cleaned inventors data: {len(df_clean)} records")
        return df_clean
    
    def clean_companies_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean companies dataframe with memory-efficient operations.
        
        Args:
            df: Raw companies dataframe
            
        Returns:
            Cleaned companies dataframe
        """
        logger.info("Cleaning companies data")
        
        df_clean = df.copy()
        
        # Clean company_id
        df_clean['company_id'] = df_clean['company_id'].astype(str).str.strip()
        
        # Remove rows with missing company_id
        initial_count = len(df_clean)
        df_clean = df_clean[df_clean['company_id'] != ""]
        logger.info(f"Removed {initial_count - len(df_clean)} rows with missing company IDs")
        
        # Clean company name
        if 'name' in df_clean.columns:
            df_clean['name'] = df_clean['name'].apply(self.clean_text)
            # Standardize company names (remove common suffixes)
            df_clean['name'] = df_clean['name'].str.replace(r'\s+(INC|CORP|LLC|LTD|CO|COMPANY)\.?$', '', case=False, regex=True)
            # Remove rows with empty names
            df_clean = df_clean[df_clean['name'] != ""]
        
        # Remove duplicates based on company_id
        initial_count = len(df_clean)
        df_clean = df_clean.drop_duplicates(subset=['company_id'], keep='first')
        logger.info(f"Removed {initial_count - len(df_clean)} duplicate companies")
        
        # Reset index
        df_clean = df_clean.reset_index(drop=True)
        
        # Memory cleanup
        gc.collect()
        
        logger.info(f"Cleaned companies data: {len(df_clean)} records")
        return df_clean
    
    def generate_data_quality_report(self, data_dict: Dict[str, pd.DataFrame]) -> Dict:
        """
        Generate a comprehensive data quality report.
        
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
                'data_types': df.dtypes.to_dict(),
                'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024*1024)
            }
            
            # Add column-specific stats
            if table_name == 'patents':
                if 'year' in df.columns:
                    report[table_name]['year_range'] = {
                        'min': int(df['year'].min()),
                        'max': int(df['year'].max()),
                        'unique_years': df['year'].nunique()
                    }
                if 'title' in df.columns:
                    report[table_name]['title_stats'] = {
                        'avg_length': df['title'].str.len().mean(),
                        'max_length': df['title'].str.len().max(),
                        'empty_titles': (df['title'] == '').sum()
                    }
            
            elif table_name == 'inventors':
                if 'country' in df.columns:
                    report[table_name]['country_stats'] = {
                        'unique_countries': df['country'].nunique(),
                        'top_countries': df['country'].value_counts().head(5).to_dict()
                    }
            
            elif table_name == 'companies':
                if 'name' in df.columns:
                    report[table_name]['name_stats'] = {
                        'unique_names': df['name'].nunique(),
                        'avg_name_length': df['name'].str.len().mean()
                    }
        
        return report
    
    def clean_all_data(self) -> Dict[str, any]:
        """
        Main method to clean all data files with memory-efficient processing.
        
        Returns:
            Dictionary containing cleaning results and file paths
        """
        logger.info("Starting data cleaning process")
        
        try:
            # Check if raw data files exist
            if not self.raw_patents_file.exists():
                logger.error(f"Raw patents file not found: {self.raw_patents_file}")
                return {'status': 'error', 'message': 'Raw patents file not found'}
            
            if not self.raw_inventors_file.exists():
                logger.error(f"Raw inventors file not found: {self.raw_inventors_file}")
                return {'status': 'error', 'message': 'Raw inventors file not found'}
            
            if not self.raw_companies_file.exists():
                logger.error(f"Raw companies file not found: {self.raw_companies_file}")
                return {'status': 'error', 'message': 'Raw companies file not found'}
            
            # Load raw data with memory-efficient reading
            logger.info("Loading raw data files")
            patents_df = pd.read_csv(self.raw_patents_file, low_memory=False)
            inventors_df = pd.read_csv(self.raw_inventors_file, low_memory=False)
            companies_df = pd.read_csv(self.raw_companies_file, low_memory=False)
            
            logger.info(f"Loaded raw data: Patents: {len(patents_df):,}, Inventors: {len(inventors_df):,}, Companies: {len(companies_df):,}")
            
            # Clean each dataset
            clean_patents = self.clean_patents_data(patents_df)
            del patents_df  # Free memory
            gc.collect()
            
            clean_inventors = self.clean_inventors_data(inventors_df)
            del inventors_df  # Free memory
            gc.collect()
            
            clean_companies = self.clean_companies_data(companies_df)
            del companies_df  # Free memory
            gc.collect()
            
            # Save cleaned data
            logger.info("Saving cleaned data files")
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
            logger.info(f"{table.capitalize()}: {count:,} records")
        
        # Log quality summary
        if 'quality_report' in result:
            logger.info("Data Quality Summary:")
            for table, stats in result['quality_report'].items():
                logger.info(f"  {table}: {stats['total_records']:,} records, {stats['memory_usage_mb']:.1f} MB")
    else:
        logger.error(f"Data cleaning failed: {result['message']}")
    
    return result

if __name__ == "__main__":
    main()
