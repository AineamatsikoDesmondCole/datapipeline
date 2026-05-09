# Patent Intelligence Dashboard

A comprehensive patent analytics dashboard built with Streamlit, featuring real-time visualizations and insights from patent data.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AineamatsikoDesmondCole/datapipeline.git
   cd datapipeline
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download Data Files:**
   
   **⚠️ Important**: This repository contains the dashboard code only. You need to download the data files separately:
   
   - **Cleaned Data Files**: Download from [Google Drive Link](https://drive.google.com/your-data-link)
   - **Extract to**: `clean_data_files/` directory
   - **Files needed**: 
     - `clean_patents.csv` (1M+ patent records)
     - `clean_inventors.csv` (50K+ inventor records)  
     - `clean_companies.csv` (company records)

5. **Run the dashboard:**
   ```bash
   streamlit run dashboard_simple.py
   ```

## 🌐 Deployment

### Streamlit Cloud (Recommended)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Deploy patent dashboard"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Visit [Streamlit Cloud](https://share.streamlit.io/)
   - Connect your GitHub repository
   - Select `dashboard_simple.py` as the main file
   - **Important**: Upload data files to Streamlit Cloud secrets or use cloud storage

### Local Development

```bash
streamlit run dashboard_simple.py --server.port 8501
```

## 📊 Features

- **👥 Inventor Analysis**: Top inventors, patent distribution, country heatmaps
- **🏢 Company Insights**: Patent statistics, growth trends, filing patterns  
- **🌍 Geographic Analysis**: Country-wise patent distribution
- **📈 Trend Analysis**: Year-over-year growth, filing timelines
- **🎯 Advanced Analytics**: Multiple visualization types, interactive charts

## 🎨 Dashboard Sections

### 1. Inventors Tab
- Top 20 inventors by patent count
- Patent count distribution histogram
- Country-wise inventor distribution
- Global inventor heatmap
- Patent count scatter analysis

### 2. Companies Tab  
- Patent filing trends by year
- Year-over-year growth analysis
- Patent distribution pie charts
- Cumulative filing timelines
- Growth rate scatter plots

### 3. Countries Tab
- Country-wise patent statistics
- Geographic distribution analysis
- Regional patent insights

### 4. Trends Tab
- Historical patent trends
- Growth rate analysis
- Timeline visualizations

### 5. Advanced Analytics
- Multi-dimensional analysis
- Interactive visualizations
- Statistical insights

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Visualizations**: Plotly
- **Deployment**: Streamlit Cloud

## 📁 Project Structure

```
Patent-Dashboard-Final/
├── dashboard_simple.py    # Main dashboard application
├── requirements.txt       # Python dependencies
├── .gitignore           # Git ignore rules
├── clean_data_files/     # Data directory (create after download)
│   ├── clean_patents.csv
│   ├── clean_inventors.csv
│   └── clean_companies.csv
└── README.md            # This file
```

## 🎯 Data Handling

This dashboard is designed to work with **real patent data**:

- **1M+ Patent Records**: Complete patent dataset with titles, abstracts, filing dates
- **50K+ Inventor Records**: Inventor information with country data
- **Company Records**: Company/assignee information
- **Real-time Analytics**: All visualizations use actual data

## 📥 Data Download Instructions

### Step 1: Download Data Files
1. Visit the data download link: [Download Patent Data](https://drive.google.com/your-data-link)
2. Download the zip file containing all cleaned data
3. Extract to the repository root directory

### Step 2: Verify Data Structure
Ensure you have:
```
clean_data_files/
├── clean_patents.csv    # ~100MB
├── clean_inventors.csv  # ~50MB
└── clean_companies.csv  # ~1MB
```

### Step 3: Run Dashboard
```bash
streamlit run dashboard_simple.py
```

## 🔧 Customization

### Using Your Own Data
1. Prepare your data in CSV format with the required columns
2. Place files in `clean_data_files/` directory
3. Ensure column names match the expected format:
   - **Patents**: `patent_id`, `title`, `abstract`, `filing_date`, `year`
   - **Inventors**: `inventor_id`, `name`, `country`, `patent_count`
   - **Companies**: `company_id`, `name`, `country`

### Customizing Visualizations
- Modify chart colors and styles in the respective section functions
- Add new visualization types using Plotly
- Customize data processing logic as needed

## 🚀 Performance

- **Optimized for 1M+ records**
- **Cached data loading** for faster performance
- **Responsive design** for all screen sizes
- **Interactive charts** with zoom and filter capabilities

## 📞 Support

For issues and questions:
- Check the [GitHub Issues](https://github.com/AineamatsikoDesmondCole/datapipeline/issues)
- Review the documentation
- Contact the development team

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ for patent intelligence and analytics**

## ⚠️ Important Notes

- **Data Files Not Included**: Large data files are not in this repository due to size constraints
- **Download Required**: You must download data files separately for the dashboard to work
- **Real Data Only**: This dashboard is designed for real patent data, not sample data
- **Deployment**: For cloud deployment, ensure data files are accessible to the deployed application
