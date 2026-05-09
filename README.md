# Patent Intelligence Dashboard


<img width="1366" height="768" alt="Screenshot (211)" src="https://github.com/user-attachments/assets/0ad1f638-6caf-438c-827d-081fa20fcb55" />
<img width="1366" height="768" alt="Screenshot (212)" src="https://github.com/user-attachments/assets/4d7379f2-bafe-46f7-acb3-d950fa3a4975" />
<img width="1366" height="768" alt="Screenshot (213)" src="https://github.com/user-attachments/assets/fbad20e9-bf23-48c0-a2d5-702698a16dad" />
<img width="1366" height="768" alt="Screenshot (222)" src="https://github.com/user-attachments/assets/5779e213-9188-4f31-993b-74e049f805b8" />
<img width="1366" height="768" alt="Screenshot (221)" src="https://github.com/user-attachments/assets/b5634b96-7913-479b-b571-6ef91faf9837" />
<img width="1366" height="768" alt="Screenshot (220)" src="https://github.com/user-attachments/assets/ffa651e8-3df2-4cfc-b109-6dad3961ebe2" />
<img width="1366" height="768" alt="Screenshot (219)" src="https://github.com/user-attachments/assets/0ccb8459-fe9f-4657-b8e3-29ea410b1767" />
<img width="1366" height="768" alt="Screenshot (218)" src="https://github.com/user-attachments/assets/410b5b75-6da4-42ef-bd78-f090d1814b20" />
<img width="1366" height="768" alt="Screenshot (217)" src="https://github.com/user-attachments/assets/9334596f-ed58-479e-b466-49ebbfc289d2" />
<img width="1366" height="768" alt="Screenshot (216)" src="https://github.com/user-attachments/assets/1386b083-fd0a-4dfb-a298-5e78c7302a8e" />
<img width="1366" height="768" alt="Screenshot (215)" src="https://github.com/user-attachments/assets/17f6c525-10bd-40da-8a02-d63b5c00009f" />
<img width="1366" height="768" alt="Screenshot (214)" src="https://github.com/user-attachments/assets/02897cbc-aca4-4051-9d24-21a54d7313e3" />
<img width="1366" height="768" alt="Screenshot (225)" src="https://github.com/user-attachments/assets/5e9ad0c5-dcc5-4f24-aea9-7726856523d8" />
<img width="1366" height="768" alt="Screenshot (224)" src="https://github.com/user-attachments/assets/47c6f2ad-5add-4e31-a45e-41ac3a8dddf0" />



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


