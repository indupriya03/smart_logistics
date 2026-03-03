# 🚚 Smart Logistics Management

A comprehensive logistics analytics system for analyzing shipments, optimizing routes, and monitoring operational efficiency. Built with Python, MySQL, and Streamlit.

💡 Project Overview

- Smart Logistics Management is a complete end-to-end logistics analytics system that simulates real-world operations, covering:
- Data Engineering: Profiling, cleaning, and preprocessing multiple datasets
- Database Design: MySQL schema creation, table population, and integrity checks
- ETL Pipelines: Automated fixes and transformations for routes and shipments
- Analytics & Queries: SQL queries for cost, courier, route, and warehouse analysis
- Visualization: KPI dashboards and interactive Streamlit pages
  
This project demonstrates a full pipeline from raw data to actionable business insights.

🏗️ Project Structure
```
smart_logistics/
│
├── Logistics.ipynb           # Data profiling, cleaning, DB design, table creation
├── fix_routes.ipynb          # ETL fixes for routes table
├── db.py                     # MySQL database connection
├── queries.py                # SQL queries for analytics
├── components.py             # Reusable Streamlit components (KPI cards)
│
├── data/                     # Source datasets
│   ├── costs.csv
│   ├── courier_staff.csv
│   ├── routes.csv
│   ├── shipment_tracking.csv
│   ├── shipments.json
│   └── warehouses.json
│
├── streamlit_pages/          # Interactive dashboard pages
│   ├── logistics_kpi.py      # Homepage / KPI dashboard
│   ├── cost_analytics.py
│   ├── courier_analytics.py
│   ├── route_analytics.py
│   └── warehouse_analytics.py
│
└── requirements.txt          # Project dependencies
```
pip install -r requirements.txt

🖥️ Features

- End-to-end data pipeline: raw data → database → ETL → dashboards
- Relational database design with integrity checks
- Pre-built SQL queries for analytics
- Interactive dashboards with KPIs
- Modular, scalable project structure

⚙️ Tech Stack

| Layer           | Technologies                   |
| --------------- | ------------------------------ |
| Data Processing | Python, Pandas                 |
| Database        | MySQL, SQLAlchemy              |
| ETL             | Python, Pandas                 |
| Visualization   | Streamlit, Matplotlib, Seaborn |
| Data Formats    | CSV, JSON                      |

   
## 🚀 How to Run

1. Clone the repo  
   ```bash
   git clone https://github.com/yourusername/smart_logistics.git
2. Navigate into the project folder:
   cd smart_logistics
3. Install all required dependencies:
   pip install -r requirements.txt
4. Set up the MySQL database:
  - Run Logistics.ipynb to create tables and insert data
  - Update credentials in db.py

📈 Portfolio Highlights

- End-to-End Pipeline: Raw data → Database → ETL → Dashboards
- Real-World Relevance: Simulates logistics operations (shipments, routes, warehouses, courier staff, costs)
- Modular Architecture: Notebooks, scripts, and dashboards are organized for reusability
- Technical Skills Showcase: Python, SQL, Streamlit, ETL, Database design

👤 Author
## Indupriya Chidambararaj ##


   
