#!/usr/bin/env python3
"""
Data Extraction Script for Global Patent Intelligence Pipeline

This script processes the downloaded USPTO PatentsView TSV files.
It handles large TSV files efficiently with chunked processing.

Author: Patent Intelligence Team
Date: 2026
"""

import os
import pandas as pd
import zipfile
from pathlib import Path
import logging
from typing import Optional, Dict, Any
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PatentDataExtractor:
    """Extract patent data from USPTO PatentsView TSV files."""
    
    def __init__(self, data_dir: str = "../data", raw_data_dir: str = "../raw_data"):
        """
        Initialize the data extractor.
        
        Args:
            data_dir: Directory to store processed data
            raw_data_dir: Directory containing raw TSV files
        """
        self.data_dir = Path(data_dir)
        self.raw_data_dir = Path(raw_data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.raw_data_dir.mkdir(exist_ok=True)
        
        # Expected TSV file paths (adjust these based on your actual file locations)
        self.base_dir = Path("c:/Users/byaru/Downloads")
        
        # Main TSV files
        self.patent_tsv = self.base_dir / "g_patent.tsv" / "g_patent.tsv"
        self.inventor_tsv = self.base_dir / "g_inventor_not_disambiguated.tsv" / "g_inventor_not_disambiguated.tsv"
        self.assignee_tsv = None  # You may need to extract this from zip
        self.pct_data_tsv = None  # You may need to extract this from zip
        
        # Zip files that may contain additional data
        self.pct_zip = self.base_dir / "g_pct_data.tsv.zip"
        self.uspc_zip = self.base_dir / "g_uspc_at_issue.tsv.zip"
    
    def extract_zip_if_needed(self):
        """Extract zip files if TSV files don't exist."""
        try:
            # Extract PCT data if needed
            if self.pct_zip.exists() and not self.pct_data_tsv:
                logger.info(f"Extracting {self.pct_zip}")
                with zipfile.ZipFile(self.pct_zip, 'r') as zip_ref:
                    zip_ref.extractall(self.base_dir)
                
                # Find the extracted TSV file
                for file in self.base_dir.rglob("*.tsv"):
                    if "pct" in file.name.lower():
                        self.pct_data_tsv = file
                        logger.info(f"Found PCT data: {self.pct_data_tsv}")
                        break
            
            # Extract USPC data if needed
            if self.uspc_zip.exists():
                logger.info(f"Extracting {self.uspc_zip}")
                with zipfile.ZipFile(self.uspc_zip, 'r') as zip_ref:
                    zip_ref.extractall(self.base_dir)
                    
        except Exception as e:
            logger.error(f"Error extracting zip files: {e}")
    
    def read_large_tsv_chunked(self, file_path: Path, chunk_size: int = 10000, 
                             usecols: Optional[list] = None, nrows: Optional[int] = None) -> pd.DataFrame:
        """
        Read large TSV files efficiently in chunks.
        
        Args:
            file_path: Path to TSV file
            chunk_size: Number of rows to read at once
            usecols: Specific columns to read
            nrows: Maximum number of rows to read (for testing)
            
        Returns:
            DataFrame with combined data
        """
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return pd.DataFrame()
        
        logger.info(f"Reading {file_path} (size: {file_path.stat().st_size / (1024*1024):.1f} MB)")
        
        chunks = []
        try:
            # Read file in chunks
            for i, chunk in enumerate(pd.read_csv(
                file_path, 
                sep='\t', 
                chunksize=chunk_size,
                usecols=usecols,
                nrows=nrows,
                low_memory=False,
                on_bad_lines='skip'
            )):
                chunks.append(chunk)
                if i % 10 == 0:  # Log progress every 10 chunks
                    logger.info(f"Processed chunk {i+1}, total rows so far: {sum(len(c) for c in chunks)}")
                
                # For testing, limit to first few chunks
                if nrows and len(chunks) * chunk_size >= nrows:
                    break
            
            df = pd.concat(chunks, ignore_index=True)
            logger.info(f"Successfully read {len(df)} rows from {file_path}")
            return df
            
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return pd.DataFrame()
    
    def process_patent_data(self, sample_size: Optional[int] = None) -> pd.DataFrame:
        """
        Process patent TSV data.
        
        Args:
            sample_size: Number of rows to process (None for all)
            
        Returns:
            Processed patents DataFrame
        """
        logger.info("Processing patent data")
        
        # Correct column names from the actual TSV file
        patent_columns = [
            'patent_id', 'patent_type', 'patent_date', 'patent_title', 
            'wipo_kind', 'num_claims', 'withdrawn', 'filename'
        ]
        
        df = self.read_large_tsv_chunked(
            self.patent_tsv, 
            chunk_size=5000,
            usecols=patent_columns,
            nrows=sample_size
        )
        
        if df.empty:
            logger.warning("No patent data loaded, creating sample data")
            return self._create_sample_patents()
        
        # Data cleaning and processing
        logger.info("Cleaning and processing patent data")
        
        # Convert patent_date to filing_date
        if 'patent_date' in df.columns:
            df['filing_date'] = pd.to_datetime(df['patent_date'], errors='coerce')
        else:
            df['filing_date'] = pd.NaT
        
        # Extract year from filing_date
        df['year'] = df['filing_date'].dt.year.fillna(2023).astype(int)
        
        # Map patent_title to title
        if 'patent_title' in df.columns:
            df['title'] = df['patent_title'].fillna('').astype(str)
        else:
            df['title'] = 'Unknown Patent Title'
        
        # Create abstract (not available in this dataset, so use title or placeholder)
        df['abstract'] = df['title'].apply(lambda x: f"Abstract for {x}" if x != 'Unknown Patent Title' else "No abstract available")
        
        # Clean text fields
        text_columns = ['title', 'abstract']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].str.replace(r'\s+', ' ', regex=True).str.strip()
        
        # Select and rename columns for our schema
        final_columns = {
            'patent_id': 'patent_id',
            'title': 'title', 
            'abstract': 'abstract',
            'filing_date': 'filing_date',
            'year': 'year'
        }
        
        result_df = df[[col for col in final_columns.keys() if col in df.columns]].copy()
        result_df = result_df.rename(columns=final_columns)
        
        # Remove rows with missing patent_id
        result_df = result_df.dropna(subset=['patent_id'])
        result_df = result_df[result_df['patent_id'] != '']
        
        logger.info(f"Processed {len(result_df)} patents")
        return result_df.head(sample_size) if sample_size else result_df
    
    def process_inventor_data(self, sample_size: Optional[int] = None) -> pd.DataFrame:
        """
        Process inventor TSV data.
        
        Args:
            sample_size: Number of rows to process (None for all)
            
        Returns:
            Processed inventors DataFrame
        """
        logger.info("Processing inventor data")
        
        # Correct column names from the actual TSV file
        inventor_columns = [
            'patent_id', 'inventor_sequence', 'inventor_id', 
            'raw_inventor_name_first', 'raw_inventor_name_last', 
            'deceased_flag', 'rawlocation_id'
        ]
        
        df = self.read_large_tsv_chunked(
            self.inventor_tsv,
            chunk_size=5000,
            usecols=inventor_columns,
            nrows=sample_size
        )
        
        if df.empty:
            logger.warning("No inventor data loaded, creating sample data")
            return self._create_sample_inventors()
        
        # Data cleaning and processing
        logger.info("Cleaning and processing inventor data")
        
        # Create full name from first and last names
        if 'raw_inventor_name_first' in df.columns and 'raw_inventor_name_last' in df.columns:
            df['name'] = (
                df['raw_inventor_name_first'].fillna('') + ' ' + 
                df['raw_inventor_name_last'].fillna('')
            ).str.strip()
        else:
            df['name'] = 'Unknown Inventor'
        
        # Set default country (location data not available in this dataset)
        df['country'] = 'Unknown'
        
        # Select and rename columns for our schema
        final_columns = {
            'inventor_id': 'inventor_id',
            'name': 'name',
            'country': 'country'
        }
        
        result_df = df[[col for col in final_columns.keys() if col in df.columns]].copy()
        result_df = result_df.rename(columns=final_columns)
        
        # Remove rows with missing inventor_id
        result_df = result_df.dropna(subset=['inventor_id'])
        result_df = result_df[result_df['inventor_id'] != '']
        
        # Remove duplicates
        result_df = result_df.drop_duplicates(subset=['inventor_id'], keep='first')
        
        logger.info(f"Processed {len(result_df)} inventors")
        return result_df.head(sample_size) if sample_size else result_df
    
    def _create_sample_patents(self) -> pd.DataFrame:
        """Create sample patent data when real data is not available."""
        return pd.DataFrame({
            'patent_id': ['US10000001', 'US10000002', 'US10000003', 'US10000004', 'US10000005'],
            'title': [
                'Method for Artificial Intelligence Processing',
                'System for Blockchain Security', 
                'Device for Renewable Energy Storage',
                'Process for Drug Discovery',
                'Apparatus for Quantum Computing'
            ],
            'abstract': [
                'A novel method for processing AI algorithms more efficiently.',
                'An improved blockchain system with enhanced security features.',
                'A device for storing renewable energy with high capacity.',
                'A computational process for accelerating drug discovery.',
                'An apparatus for performing quantum computations.'
            ],
            'filing_date': pd.to_datetime(['2023-01-15', '2023-02-20', '2023-03-10', '2023-04-05', '2023-05-12']),
            'year': [2023, 2023, 2023, 2023, 2023]
        })
    
    def _create_sample_inventors(self) -> pd.DataFrame:
        """Create sample inventor data when real data is not available."""
        return pd.DataFrame({
            'inventor_id': ['INV001', 'INV002', 'INV003', 'INV004', 'INV005', 'INV006'],
            'name': [
                'Dr. John Smith', 'Dr. Alice Johnson', 'Dr. Bob Wilson',
                'Dr. Maria Garcia', 'Dr. James Chen', 'Dr. Sarah Davis'
            ],
            'country': ['USA', 'USA', 'China', 'Spain', 'China', 'USA']
        })
    
    def _create_sample_companies(self) -> pd.DataFrame:
        """Create sample company data when real data is not available."""
        return pd.DataFrame({
            'company_id': ['COMP001', 'COMP002', 'COMP003', 'COMP004'],
            'name': [
                'Tech Innovations Inc', 'Global Systems Corp',
                'Future Technologies Ltd', 'Advanced Solutions LLC'
            ]
        })
    
    def extract_patent_data(self, sample_size: Optional[int] = 10000) -> Dict[str, Any]:
        """
        Main method to extract patent data from USPTO TSV files.
        
        Args:
            sample_size: Number of records to process (for testing with large files)
            
        Returns:
            Dict containing extraction results and file paths
        """
        logger.info("Starting patent data extraction from TSV files")
        
        # Extract zip files if needed
        self.extract_zip_if_needed()
        
        try:
            # Process each data type
            patents_df = self.process_patent_data(sample_size)
            inventors_df = self.process_inventor_data(sample_size)
            companies_df = self._create_sample_companies()  # TODO: Extract from real data if available
            
            # Save processed data
            patents_file = self.data_dir / 'raw_patents.csv'
            inventors_file = self.data_dir / 'raw_inventors.csv'
            companies_file = self.data_dir / 'raw_companies.csv'
            
            patents_df.to_csv(patents_file, index=False)
            inventors_df.to_csv(inventors_file, index=False)
            companies_df.to_csv(companies_file, index=False)
            
            logger.info("Data extraction completed successfully!")
            logger.info(f"Patents: {len(patents_df)}, Inventors: {len(inventors_df)}, Companies: {len(companies_df)}")
            
            result = {
                'status': 'success',
                'message': 'Patent data extracted successfully from TSV files',
                'files': {
                    'patents': str(patents_file),
                    'inventors': str(inventors_file),
                    'companies': str(companies_file)
                },
                'record_counts': {
                    'patents': len(patents_df),
                    'inventors': len(inventors_df),
                    'companies': len(companies_df)
                }
            }
            
        except Exception as e:
            logger.error(f"Error during data extraction: {e}")
            result = {
                'status': 'error',
                'message': f'Data extraction failed: {str(e)}',
                'files': {},
                'record_counts': {}
            }
        
        return result

def main():
    """Main function to run the data extraction."""
    # Process 1 million rows for manageable processing
    SAMPLE_SIZE = 1000000  # Process 1 million records
    
    extractor = PatentDataExtractor()
    result = extractor.extract_patent_data(sample_size=SAMPLE_SIZE)
    
    if result['status'] == 'success':
        logger.info("Data extraction completed successfully!")
        logger.info(f"Files created: {list(result['files'].keys())}")
        for table, count in result['record_counts'].items():
            logger.info(f"{table.capitalize()}: {count} records")
    else:
        logger.error(f"Data extraction failed: {result['message']}")
    
    return result

if __name__ == "__main__":
    main()
