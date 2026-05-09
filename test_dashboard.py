#!/usr/bin/env python3

import sys
from pathlib import Path

# Add code_files directory to Python path
sys.path.append(str(Path(__file__).parent))

from analyze_data import PatentDataAnalyzer

def test_data_loading():
    """Test if dashboard can load data correctly."""
    print("Testing dashboard data loading...")
    
    try:
        # Test with same paths as dashboard
        analyzer = PatentDataAnalyzer(db_path="../patents.db", schema_path="../database_file/schema.sql")
        
        # Connect and run queries
        if analyzer.connect_to_database():
            print("✅ Database connection successful")
            
            # Run all queries
            results = analyzer.run_all_queries()
            
            print(f"✅ Queries executed successfully")
            print(f"📊 Total patents found: {len(results.get('trends_over_time', []))}")
            print(f"👥 Total inventors found: {len(results.get('top_inventors', []))}")
            print(f"🏢 Total companies found: {len(results.get('top_companies', []))}")
            print(f"🌍 Total countries found: {len(results.get('top_countries', []))}")
            
            analyzer.close_connection()
            print("✅ Test completed successfully")
            
        else:
            print("❌ Failed to connect to database")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")

if __name__ == "__main__":
    test_data_loading()
