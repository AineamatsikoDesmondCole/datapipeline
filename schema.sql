-- Global Patent Intelligence Database Schema
-- This schema defines the structure for storing patent data

-- Drop existing views and tables if they exist (for clean rebuilds)
DROP VIEW IF EXISTS patent_details;
DROP TABLE IF EXISTS relationships;
DROP TABLE IF EXISTS patents;
DROP TABLE IF EXISTS inventors;
DROP TABLE IF EXISTS companies;

-- Create companies table (assignees)
CREATE TABLE companies (
    company_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create inventors table
CREATE TABLE inventors (
    inventor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    country TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create patents table
CREATE TABLE patents (
    patent_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    abstract TEXT,
    filing_date DATE,
    year INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create relationships table (many-to-many relationships)
CREATE TABLE relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patent_id TEXT NOT NULL,
    inventor_id INTEGER NOT NULL,
    company_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patent_id) REFERENCES patents(patent_id),
    FOREIGN KEY (inventor_id) REFERENCES inventors(inventor_id),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

-- Create indexes for better query performance
CREATE INDEX idx_patents_year ON patents(year);
CREATE INDEX idx_patents_filing_date ON patents(filing_date);
CREATE INDEX idx_inventors_country ON inventors(country);
CREATE INDEX idx_companies_name ON companies(name);
CREATE INDEX idx_relationships_patent ON relationships(patent_id);
CREATE INDEX idx_relationships_inventor ON relationships(inventor_id);
CREATE INDEX idx_relationships_company ON relationships(company_id);

-- Create view for comprehensive patent information
CREATE VIEW patent_details AS
SELECT 
    p.patent_id,
    p.title,
    p.abstract,
    p.filing_date,
    p.year,
    i.name AS inventor_name,
    i.country AS inventor_country,
    c.name AS company_name
FROM patents p
LEFT JOIN relationships r ON p.patent_id = r.patent_id
LEFT JOIN inventors i ON r.inventor_id = i.inventor_id
LEFT JOIN companies c ON r.company_id = c.company_id;

-- No sample data - will be populated from real data files
