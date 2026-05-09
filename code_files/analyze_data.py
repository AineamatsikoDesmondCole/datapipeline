#!/usr/bin/env python3
"""
Data Analysis Script for Global Patent Intelligence Pipeline

This script performs SQL analysis queries on the patent database.
It executes the required queries and generates insights.

Author: Patent Intelligence Team
Date: 2026
"""

import sqlite3
import pandas as pd
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Optional
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PatentDataAnalyzer:
    """Analyze patent data using SQL queries."""
    
    def __init__(self, db_path: str = "../Pipeline/patents.db", schema_path: str = "../database_file/schema.sql"):
        """
        Initialize the data analyzer.
        
        Args:
            db_path: Path to the SQLite database
            schema_path: Path to the database schema file
        """
        self.db_path = db_path
        self.schema_path = Path(schema_path)
        self.conn = None
        
    def connect_to_database(self) -> bool:
        """
        Connect to the SQLite database and create schema if needed.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            
            # Create schema if database is new
            if self.schema_path.exists():
                with open(self.schema_path, 'r') as f:
                    schema_sql = f.read()
                self.conn.executescript(schema_sql)
                self.conn.commit()
                logger.info("Database schema created successfully")
            
            logger.info("Connected to database successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            return False
    
    def load_data_to_database(self, clean_data_dir: str = "../Pipeline/clean_data_files") -> bool:
        """
        Load cleaned data into the database.
        
        Args:
            clean_data_dir: Directory containing cleaned CSV files
            
        Returns:
            bool: True if data loaded successfully, False otherwise
        """
        try:
            clean_data_path = Path(clean_data_dir)
            
            # Load cleaned data
            patents_df = pd.read_csv(clean_data_path / 'clean_patents.csv')
            inventors_df = pd.read_csv(clean_data_path / 'clean_inventors.csv')
            companies_df = pd.read_csv(clean_data_path / 'clean_companies.csv')
            
            # Load data into database
            patents_df.to_sql('patents', self.conn, if_exists='replace', index=False)
            inventors_df.to_sql('inventors', self.conn, if_exists='replace', index=False)
            companies_df.to_sql('companies', self.conn, if_exists='replace', index=False)
            
            # Create relationships table (sample data for demonstration)
            # In a real scenario, this would come from the actual patent-inventor relationships
            relationships_data = []
            
            # Create some sample relationships based on the data we have
            for i, patent_id in enumerate(patents_df['patent_id'].head(100)):
                # Assign 1-3 inventors per patent
                num_inventors = min(3, len(inventors_df))
                selected_inventors = inventors_df.sample(n=num_inventors)
                
                for j, (_, inventor) in enumerate(selected_inventors.iterrows()):
                    company_id = (i % len(companies_df)) + 1
                    relationships_data.append([patent_id, inventor['inventor_id'], company_id])
            
            relationships_df = pd.DataFrame(relationships_data, columns=['patent_id', 'inventor_id', 'company_id'])
            relationships_df.to_sql('relationships', self.conn, if_exists='replace', index=False)
            
            self.conn.commit()
            logger.info("Data loaded into database successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading data into database: {e}")
            return False
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """
        Execute a SQL query and return results as DataFrame.
        
        Args:
            query: SQL query string
            
        Returns:
            DataFrame with query results
        """
        try:
            result = pd.read_sql_query(query, self.conn)
            return result
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return pd.DataFrame()
    
    def execute_query_with_params(self, query: str, params: tuple = ()) -> pd.DataFrame:
        """
        Execute a SQL query with parameters and return results as DataFrame.
        
        Args:
            query: SQL query string
            params: Parameters for the query
            
        Returns:
            DataFrame with query results
        """
        try:
            result = pd.read_sql_query(query, self.conn, params=params)
            return result
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return pd.DataFrame()
    
    def query_top_inventors(self, limit: int = 10) -> pd.DataFrame:
        """
        Q1: Top Inventors - Who has the most patents?
        
        Args:
            limit: Number of top inventors to return
            
        Returns:
            DataFrame with top inventors and patent counts
        """
        query = """
        SELECT 
            i.name as inventor_name,
            i.country as inventor_country,
            COUNT(DISTINCT r.patent_id) as patent_count
        FROM inventors i
        JOIN relationships r ON i.inventor_id = r.inventor_id
        GROUP BY i.inventor_id, i.name, i.country
        ORDER BY patent_count DESC
        LIMIT ?
        """
        
        logger.info("Executing Q1: Top Inventors query")
        return self.execute_query_with_params(query, (limit,))
    
    def query_top_companies(self, limit: int = 10) -> pd.DataFrame:
        """
        Q2: Top Companies - Which companies own the most patents?
        
        Args:
            limit: Number of top companies to return
            
        Returns:
            DataFrame with top companies and patent counts
        """
        query = """
        SELECT 
            c.name as company_name,
            COUNT(DISTINCT r.patent_id) as patent_count
        FROM companies c
        JOIN relationships r ON c.company_id = r.company_id
        GROUP BY c.company_id, c.name
        ORDER BY patent_count DESC
        LIMIT ?
        """
        
        logger.info("Executing Q2: Top Companies query")
        return self.execute_query_with_params(query, (limit,))
    
    def query_top_countries(self, limit: int = 10) -> pd.DataFrame:
        """
        Q3: Countries - Which countries produce the most patents?
        
        Args:
            limit: Number of top countries to return
            
        Returns:
            DataFrame with top countries and patent counts
        """
        query = """
        SELECT 
            i.country,
            COUNT(DISTINCT r.patent_id) as patent_count,
            ROUND(COUNT(DISTINCT r.patent_id) * 100.0 / (SELECT COUNT(*) FROM patents), 2) as percentage_share
        FROM inventors i
        JOIN relationships r ON i.inventor_id = r.inventor_id
        GROUP BY i.country
        ORDER BY patent_count DESC
        LIMIT ?
        """
        
        logger.info("Executing Q3: Top Countries query")
        return self.execute_query_with_params(query, (limit,))
    
    def query_trends_over_time(self) -> pd.DataFrame:
        """
        Q4: Trends Over Time - How many patents are created each year?
        
        Returns:
            DataFrame with patent counts by year
        """
        query = """
        SELECT 
            year,
            COUNT(*) as patent_count,
            LAG(COUNT(*)) OVER (ORDER BY year) as previous_year_count,
            ROUND((COUNT(*) - LAG(COUNT(*)) OVER (ORDER BY year)) * 100.0 / LAG(COUNT(*)) OVER (ORDER BY year), 2) as year_over_year_growth
        FROM patents
        WHERE year IS NOT NULL
        GROUP BY year
        ORDER BY year
        """
        
        logger.info("Executing Q4: Trends Over Time query")
        return self.execute_query(query)
    
    def query_join_patents_inventors_companies(self, limit: int = 20) -> pd.DataFrame:
        """
        Q5: JOIN Query - Combine patents with inventors and companies
        
        Args:
            limit: Number of records to return
            
        Returns:
            DataFrame with joined patent information
        """
        query = """
        SELECT 
            p.patent_id,
            p.title,
            p.year,
            i.name as inventor_name,
            i.country as inventor_country,
            c.name as company_name
        FROM patents p
        JOIN relationships r ON p.patent_id = r.patent_id
        JOIN inventors i ON r.inventor_id = i.inventor_id
        LEFT JOIN companies c ON r.company_id = c.company_id
        ORDER BY p.year DESC, p.patent_id
        LIMIT ?
        """
        
        logger.info("Executing Q5: JOIN Query")
        return self.execute_query_with_params(query, (limit,))
    
    def query_cte_analysis(self) -> pd.DataFrame:
        """
        Q6: CTE Query - Break a complex query into steps
        Analyze patent productivity by country and company
        
        Returns:
            DataFrame with CTE analysis results
        """
        query = """
        WITH country_patents AS (
            SELECT 
                i.country,
                COUNT(DISTINCT r.patent_id) as total_patents
            FROM inventors i
            JOIN relationships r ON i.inventor_id = r.inventor_id
            GROUP BY i.country
        ),
        company_patents AS (
            SELECT 
                c.name as company_name,
                i.country as company_country,
                COUNT(DISTINCT r.patent_id) as company_patents
            FROM companies c
            JOIN relationships r ON c.company_id = r.company_id
            JOIN inventors i ON r.inventor_id = r.inventor_id
            GROUP BY c.name, i.country
        )
        SELECT 
            cp.country,
            cp.total_patents,
            comp.company_name,
            comp.company_patents,
            ROUND(comp.company_patents * 100.0 / cp.total_patents, 2) as country_share_percentage
        FROM country_patents cp
        JOIN company_patents comp ON cp.country = comp.company_country
        ORDER BY cp.total_patents DESC, comp.company_patents DESC
        """
        
        logger.info("Executing Q6: CTE Query")
        return self.execute_query(query)
    
    def query_ranking_inventors(self) -> pd.DataFrame:
        """
        Q7: Ranking Query - Rank inventors using window functions
        
        Returns:
            DataFrame with ranked inventors
        """
        query = """
        SELECT 
            i.name as inventor_name,
            i.country as inventor_country,
            COUNT(DISTINCT r.patent_id) as patent_count,
            RANK() OVER (ORDER BY COUNT(DISTINCT r.patent_id) DESC) as overall_rank,
            RANK() OVER (PARTITION BY i.country ORDER BY COUNT(DISTINCT r.patent_id) DESC) as country_rank,
            LAG(COUNT(DISTINCT r.patent_id)) OVER (ORDER BY COUNT(DISTINCT r.patent_id) DESC) as previous_inventor_patents
        FROM inventors i
        JOIN relationships r ON i.inventor_id = r.inventor_id
        GROUP BY i.inventor_id, i.name, i.country
        ORDER BY patent_count DESC
        """
        
        logger.info("Executing Q7: Ranking Query")
        return self.execute_query(query)
    
    def run_all_queries(self) -> Dict[str, pd.DataFrame]:
        """
        Run all required SQL queries.
        
        Returns:
            Dictionary containing all query results
        """
        if not self.connect_to_database():
            return {}
        
        if not self.load_data_to_database():
            return {}
        
        logger.info("Running all SQL analysis queries")
        
        results = {
            'top_inventors': self.query_top_inventors(),
            'top_companies': self.query_top_companies(),
            'top_countries': self.query_top_countries(),
            'trends_over_time': self.query_trends_over_time(),
            'join_query': self.query_join_patents_inventors_companies(),
            'cte_analysis': self.query_cte_analysis(),
            'ranking_inventors': self.query_ranking_inventors()
        }
        
        logger.info("All queries executed successfully")
        return results
    
    def close_connection(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

def main():
    """Main function to run the data analysis."""
    analyzer = PatentDataAnalyzer()
    
    try:
        results = analyzer.run_all_queries()
        
        if results:
            logger.info("Analysis completed successfully!")
            for query_name, df in results.items():
                logger.info(f"{query_name}: {len(df)} records")
                if not df.empty:
                    logger.info(f"Sample data:\n{df.head()}")
        else:
            logger.error("Analysis failed - no results returned")
            
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
    finally:
        analyzer.close_connection()

if __name__ == "__main__":
    main()
