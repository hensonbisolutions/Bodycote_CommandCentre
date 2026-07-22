# Bodycote Executive Operations Command Centre

A premium, production-quality executive dashboard built with Python and Streamlit for manufacturing operations intelligence and real-time decision making.

## 🏭 Overview

This is a comprehensive Executive Operations Command Centre designed specifically for Bodycote manufacturing operations. It provides real-time visibility into:

- **Financial Performance**: Revenue, margins, EBITDA
- **Operational Efficiency**: Furnace utilisation, on-time delivery, first pass yield
- **Quality & Safety**: Quality metrics, safety incidents, compliance
- **Customer Analytics**: Top customers, revenue breakdown, complaint tracking
- **Order Management**: Searchable order database with advanced filtering
- **Site Performance**: Individual site drill-down with detailed analytics

## 🎨 Design Philosophy

- **Premium Enterprise**: Inspired by Microsoft Fabric, Power BI, Palantir Foundry, and Grafana
- **Dark Mode**: Professional dark theme with Bodycote brand colors
- **Executive Focus**: Large, clear KPIs with trend indicators
- **Interactive**: Full cross-filtering and drill-down capabilities
- **Responsive**: Works seamlessly on desktop and tablet displays

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- pip or conda

### Installation

1. Clone or download the project:
```bash
cd bodycote_command_centre
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

4. Open browser to `http://localhost:8501`

## 📊 Pages

### 1. Executive Dashboard
The main command centre with:
- Real-time KPI cards (Revenue MTD/YTD, Orders, Delivery, Utilisation, Quality, Safety)
- Executive alerts and insights
- Revenue trends
- Site performance rankings
- Regional analysis
- Process mix breakdown
- Quality trends
- Maintenance tracking
- Top customers

### 2. Site Analytics
Drill-down view for individual manufacturing sites:
- Site-specific KPIs
- Furnace status and utilisation
- Site orders (searchable and filterable)
- Revenue trends
- Quality performance
- Order distribution
- Data export

### 3. Order Management
Comprehensive order search and filtering:
- Searchable order database (10,000+ orders)
- Advanced multi-filter system:
  - Customer, Site, Region
  - Status, Priority, Process
  - Quality result, Date range
- Detailed order information
- Order status breakdown
- Summary statistics
- CSV export

### 4. Customer Analytics
Customer performance tracking:
- Top 20 customers by revenue
- Customer KPIs (revenue, margin, delivery, quality)
- Order history and status breakdown
- Quality metrics (passed/rework/reject)
- Complaint tracking
- Revenue trends
- Site assignments
- CSV export

## 📁 Project Structure

```
bodycote_command_centre/
├── app.py                    # Main application entry point
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── pages/
│   ├── __init__.py
│   ├── Executive.py          # Main dashboard
│   ├── Site.py               # Site detail page
│   ├── Orders.py             # Order management
│   └── Customers.py          # Customer analytics
├── data/
│   └── generate_demo_data.py # Demo data generation
├── utils/
│   ├── __init__.py
│   ├── data.py               # Data utilities and caching
│   ├── charts.py             # Chart generation (Plotly)
│   └── helpers.py            # UI helpers and styling
└── assets/
    ├── style.css             # Custom CSS
    └── logo.png              # Placeholder logo
```

## 📈 Demo Data

The application generates realistic manufacturing data:

- **12 Manufacturing Sites** across UK regions
- **400 Customers** (mix of real companies like Airbus, Rolls-Royce, JLR and generated)
- **10,000 Production Orders** with detailed tracking
- **50 Furnaces** with capacity and process data
- **5 Business Regions** (North, Midlands, South, Wales, Scotland)
- **730 Days** of production history with:
  - Daily revenue metrics
  - Utilisation tracking
  - Quality data
  - Maintenance records
  - Safety incidents
  - Delivery performance
- **150 Customer Complaints** with severity tracking

Data is cached in Streamlit's session state for performance.

## 🎯 Key Metrics

### Financial KPIs
- **MTD Revenue**: Month-to-date revenue with target comparison
- **YTD Revenue**: Year-to-date cumulative revenue
- **Gross Margin %**: Margin percentage with target
- **EBITDA %**: Estimated operating profit margin

### Operational KPIs
- **Orders Running**: Current active orders in production
- **On-Time Delivery %**: Percentage delivered on or before due date
- **Furnace Utilisation %**: Average equipment utilisation rate
- **First Pass Yield %**: Quality-first production percentage

### Quality & Safety KPIs
- **Safety Incidents**: Number of incidents in last 30 days
- **Customer Complaints**: Recent complaints by severity
- **Backlog**: Orders in queue or on hold
- **Delayed Orders**: Orders past due date

## 🎨 Colour Scheme

Bodycote brand colours:
- **Primary**: `#005EB8` - Deep blue
- **Accent**: `#00A3E0` - Cyan blue
- **Success**: `#16A34A` - Green
- **Warning**: `#F59E0B` - Amber
- **Critical**: `#DC2626` - Red

Dark theme with professional typography using Segoe UI.

## 🔧 Technical Features

### Architecture
- **Modular Design**: Separate concerns (data, charts, UI)
- **Clean Code**: Well-commented, reusable functions
- **Session State**: Efficient caching and state management
- **No Database**: All demo data generated locally
- **Production Ready**: Error handling, data validation

### Technologies
- **Streamlit**: Web framework for data apps
- **Plotly**: Interactive visualizations
- **Pandas**: Data manipulation
- **NumPy**: Numerical operations
- **Faker**: Realistic data generation

### Performance
- Data caching with `@st.cache_resource`
- Optimized queries and aggregations
- Lazy loading of visualizations
- Minimal state updates

## 🎯 Filters

### Global Filters (Executive Dashboard)
- Region selection
- Site selection
- Date range

### Page-Specific Filters
- **Orders**: Customer, Site, Region, Status, Priority, Process, Quality, Date
- **Site**: Status, Priority, Quality
- **Customers**: Status, Priority, Quality

All filters update dynamically with real-time data.

## 📊 Visualizations

### Chart Types
- **Revenue Trends**: Area charts showing daily/cumulative revenue
- **Rankings**: Horizontal bar charts for site/customer performance
- **Distribution**: Pie charts for regional/process breakdown
- **Metrics**: Line charts for utilisation and quality trends
- **Status**: Stacked bar charts for order distribution

All charts feature:
- Dark theme
- Interactive hover tooltips
- Responsive sizing
- Professional styling

## 💾 Export Features

- **CSV Export**: Download any filtered dataset
- **Order Export**: Full order data with all fields
- **Site Export**: Site-specific data and performance
- **Customer Export**: Customer orders and analytics
- **Timestamped Files**: Automatic date/time stamping

## 🔒 Session State Management

- Maintains filter selections
- Tracks page navigation
- Manages selected sites and customers
- Handles refresh logic

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py
```

### Production Deployment (Streamlit Cloud)
1. Push code to GitHub
2. Connect to Streamlit Cloud
3. Select repository and main file
4. Deploy automatically

### Docker Deployment
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

## 📝 Configuration

### Streamlit Config
Create `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#005EB8"
backgroundColor = "#1A1A1A"
secondaryBackgroundColor = "#1F2937"
textColor = "#E5E7EB"
font = "sans serif"

[client]
showErrorDetails = false
toolbarMode = "minimal"
```

## 🔄 Refresh Data

Click the **🔄 Refresh** button in the header to regenerate demo data. This provides fresh metrics for testing.

## 📱 Responsive Design

- Desktop: Full feature set with optimal layout
- Tablet: Adapted column layouts
- Mobile: Single column with nested expandables

## ⚙️ Performance Optimization

- Data cached for 24 hours
- Lazy loading of charts
- Optimized SQL-like queries with Pandas
- Minimal state updates
- Only render visible content

## 🐛 Troubleshooting

### Application won't start
```bash
pip install --upgrade streamlit
streamlit run app.py
```

### Import errors
```bash
pip install -r requirements.txt --upgrade
```

### Data not loading
- Check internet connection
- Clear Streamlit cache: `streamlit cache clear`
- Refresh browser

## 📚 Additional Resources

### Streamlit Documentation
- https://docs.streamlit.io/

### Plotly Documentation
- https://plotly.com/python/

### Pandas Documentation
- https://pandas.pydata.org/docs/

## 📄 License

Bodycote Executive Operations Command Centre - Proprietary

## 👥 Support

For issues or feature requests, contact the development team.

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Python**: 3.12+  
**Status**: Production Ready
