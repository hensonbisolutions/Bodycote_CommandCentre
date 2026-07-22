"""
Bodycote Command Centre - Demo Data Generator
Generate realistic manufacturing data for executive dashboard
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# Realistic company name generation
FIRST_NAMES = ["Precision", "Advanced", "Global", "Integrated", "Dynamic", "Tech", "Quantum", "Elite", 
               "Strategic", "Nova", "Summit", "Apex", "Prime", "Nexus"]
SECOND_NAMES = ["Systems", "Solutions", "Industries", "Manufacturing", "Engineering", "Technologies", 
                "Operations", "Group", "Corporation", "Ventures", "Services", "Analytics"]

def generate_company_name():
    """Generate realistic company name"""
    return f"{random.choice(FIRST_NAMES)} {random.choice(SECOND_NAMES)}"


def generate_sites():
    """Generate 12 manufacturing sites across UK"""
    regions = ["North", "Midlands", "South", "Wales", "Scotland"]
    
    sites_data = {
        "site_id": [f"SITE_{i+1:03d}" for i in range(12)],
        "site_name": [
            "Leeds", "Manchester", "Birmingham", "Coventry",
            "Sheffield", "Nottingham", "Bristol", "Southampton",
            "Cardiff", "Glasgow", "Liverpool", "Stoke-on-Trent"
        ],
        "region": [regions[i % 5] for i in range(12)],
        "furnaces": [4, 5, 3, 6, 4, 4, 5, 3, 4, 5, 3, 4],
        "employees": [45, 58, 32, 72, 48, 42, 56, 38, 44, 62, 35, 50],
        "latitude": [53.8, 53.5, 52.5, 52.4, 53.4, 52.9, 51.5, 50.9, 51.5, 55.9, 53.4, 53.1],
        "longitude": [-1.5, -2.2, -1.9, -1.5, -1.4, -1.1, -2.6, -1.4, -3.2, -4.3, -2.9, -2.2],
    }
    
    return pd.DataFrame(sites_data)


def generate_customers(n=400):
    """Generate realistic manufacturing customers"""
    customer_types = ["Aerospace", "Automotive", "Energy", "Medical", "Industrial", "Defence"]
    
    # Real companies to sprinkle in
    real_companies = [
        "Airbus", "Rolls-Royce", "JLR", "BAE Systems", "Siemens", "GE",
        "Bosch", "Schaeffler", "Thales", "Leonardo", "Bombardier", "Safran",
        "Collins Aerospace", "Goodrich", "Lockheed Martin", "Raytheon", "Airbus Helicopters"
    ]
    
    customers = []
    
    # Add real companies
    for company in real_companies:
        customers.append({
            "customer_id": f"CUST_{len(customers)+1:04d}",
            "customer_name": company,
            "customer_type": random.choice(customer_types),
            "country": "UK" if random.random() > 0.3 else random.choice(["Germany", "France", "Italy", "US"]),
            "annual_spend": random.uniform(100000, 5000000)
        })
    
    # Add generated companies
    for i in range(len(customers), n):
        customers.append({
            "customer_id": f"CUST_{i+1:04d}",
            "customer_name": generate_company_name(),
            "customer_type": random.choice(customer_types),
            "country": "UK" if random.random() > 0.4 else random.choice(["Germany", "France", "Italy", "US", "Canada", "Japan"]),
            "annual_spend": random.uniform(50000, 3000000)
        })
    
    return pd.DataFrame(customers)


def generate_furnaces(sites):
    """Generate furnace data"""
    processes = [
        "Vacuum Heat Treatment",
        "HIP (Hot Isostatic Pressing)",
        "Carburising",
        "Nitriding",
        "Induction Hardening",
        "Stress Relieving",
        "Tempering",
        "Brazing"
    ]
    
    furnaces = []
    furnace_id = 1
    
    for _, site in sites.iterrows():
        for f in range(site["furnaces"]):
            # Random date between 10 years ago and now
            days_ago = random.randint(365 * 3, 365 * 10)
            installed_date = (datetime.now() - timedelta(days=days_ago)).date()
            
            furnaces.append({
                "furnace_id": f"FURN_{furnace_id:03d}",
                "site_id": site["site_id"],
                "furnace_name": f"{site['site_name']} Furnace {f+1}",
                "process": random.choice(processes),
                "installed_date": installed_date,
                "max_capacity": random.uniform(500, 2000),  # kg
                "operating_status": random.choice(["Online", "Maintenance", "Idle"]),
            })
            furnace_id += 1
    
    return pd.DataFrame(furnaces)


def generate_orders(sites, customers, furnaces, days_back=180, n_orders=3000):
    """Generate production orders"""
    materials = ["Steel", "Aluminium", "Titanium", "Nickel Alloy", "Stainless Steel", "Superalloy"]
    statuses = ["Completed", "In Progress", "Scheduled", "On Hold", "Delayed"]
    priorities = ["Normal", "High", "Critical"]
    processes = [
        "Vacuum Heat Treatment",
        "HIP (Hot Isostatic Pressing)",
        "Carburising",
        "Nitriding",
        "Induction Hardening",
        "Stress Relieving",
        "Tempering",
        "Brazing"
    ]
    
    orders = []
    start_date = datetime.now() - timedelta(days=days_back)
    
    for i in range(n_orders):
        received_date = start_date + timedelta(days=random.randint(0, days_back))
        due_date = received_date + timedelta(days=random.randint(5, 30))
        completion_date = due_date + timedelta(days=random.randint(-5, 10)) if random.random() > 0.2 else None
        
        revenue = random.uniform(5000, 150000)
        cost = revenue * random.uniform(0.4, 0.7)
        margin = revenue - cost
        
        status = "Completed" if completion_date else random.choice(["In Progress", "Scheduled", "On Hold", "Delayed"])
        
        orders.append({
            "order_id": f"ORD_{i+1:06d}",
            "customer_id": random.choice(customers["customer_id"].values),
            "site_id": random.choice(sites["site_id"].values),
            "furnace_id": random.choice(furnaces["furnace_id"].values),
            "process": random.choice(processes),
            "material": random.choice(materials),
            "weight_kg": random.uniform(10, 1000),
            "received_date": received_date.date(),
            "due_date": due_date.date(),
            "completion_date": completion_date.date() if completion_date else None,
            "status": status,
            "priority": random.choice(priorities),
            "revenue": revenue,
            "cost": cost,
            "margin": margin,
            "quality_result": random.choice(["Pass", "Pass", "Pass", "Pass", "Rework", "Reject"]),
            "operator_id": f"OP_{random.randint(1, 200):03d}",
        })
    
    return pd.DataFrame(orders)


def generate_daily_metrics(sites, days_back=180):
    """Generate daily KPI metrics"""
    metrics = []
    start_date = datetime.now() - timedelta(days=days_back)
    
    for site_id in sites["site_id"].values:
        for day in range(days_back):
            current_date = start_date + timedelta(days=day)
            
            metrics.append({
                "date": current_date.date(),
                "site_id": site_id,
                "revenue": random.uniform(8000, 35000),
                "utilisation": random.uniform(45, 95),
                "orders_completed": random.randint(5, 25),
                "quality_first_pass": random.uniform(85, 99),
                "safety_incidents": random.choice([0, 0, 0, 1]),
                "maintenance_hours": random.uniform(0, 20),
                "on_time_delivery_pct": random.uniform(80, 99),
            })
    
    return pd.DataFrame(metrics)


def generate_complaints(customers, n_complaints=150):
    """Generate customer complaints"""
    complaint_types = ["Quality", "Delivery", "Service", "Documentation", "Pricing"]
    severities = ["Low", "Medium", "High", "Critical"]
    statuses = ["Open", "In Review", "Resolved", "Closed"]
    
    complaint_descriptions = [
        "Product quality below specification",
        "Late delivery affected production schedule",
        "Packaging damaged during transport",
        "Documentation errors on invoice",
        "Pricing discrepancy with quote",
        "Furnace temperature inconsistency",
        "Surface finish not to standard",
        "Missing certifications with order",
        "Communication delay from account manager",
        "Non-conformance to drawing specification"
    ]
    
    complaints = []
    start_date = datetime.now() - timedelta(days=90)
    
    for i in range(n_complaints):
        complaints.append({
            "complaint_id": f"COMP_{i+1:04d}",
            "customer_id": random.choice(customers["customer_id"].values),
            "complaint_type": random.choice(complaint_types),
            "severity": random.choice(severities),
            "status": random.choice(statuses),
            "date_raised": (start_date + timedelta(days=random.randint(0, 90))).date(),
            "description": random.choice(complaint_descriptions),
        })
    
    return pd.DataFrame(complaints)


def generate_maintenance(furnaces, days_back=730):
    """Generate maintenance records"""
    maintenance_types = ["Preventive", "Corrective", "Emergency", "Inspection"]
    
    maintenance_notes = [
        "Thermal element replacement",
        "Bearing lubrication and inspection",
        "Safety valve testing and calibration",
        "Insulation integrity check",
        "Control system diagnostics",
        "Electrical connections inspection",
        "Furnace chamber cleaning",
        "Temperature sensor calibration",
        "Pressure relief valve service",
        "Annual compliance certification"
    ]
    
    maintenance = []
    start_date = datetime.now() - timedelta(days=days_back)
    
    for furnace_id in furnaces["furnace_id"].values:
        n_records = random.randint(3, 15)
        
        for _ in range(n_records):
            maintenance.append({
                "maintenance_id": f"MAINT_{random.randint(10000, 99999)}",
                "furnace_id": furnace_id,
                "maintenance_type": random.choice(maintenance_types),
                "date_scheduled": (start_date + timedelta(days=random.randint(0, days_back))).date(),
                "duration_hours": random.uniform(2, 48),
                "cost": random.uniform(500, 8000),
                "notes": random.choice(maintenance_notes),
            })
    
    return pd.DataFrame(maintenance)


def generate_all_data():
    """Generate all demo data"""
    print("Generating demo data...")
    
    sites = generate_sites()
    customers = generate_customers(400)
    furnaces = generate_furnaces(sites)
    orders = generate_orders(sites, customers, furnaces, days_back=180, n_orders=3000)
    daily_metrics = generate_daily_metrics(sites, days_back=180)
    complaints = generate_complaints(customers, n_complaints=150)
    maintenance = generate_maintenance(furnaces, days_back=180)
    
    print(f"✓ Generated {len(sites)} sites")
    print(f"✓ Generated {len(customers)} customers")
    print(f"✓ Generated {len(furnaces)} furnaces")
    print(f"✓ Generated {len(orders)} orders")
    print(f"✓ Generated {len(daily_metrics)} daily metrics")
    print(f"✓ Generated {len(complaints)} complaints")
    print(f"✓ Generated {len(maintenance)} maintenance records")
    
    return {
        "sites": sites,
        "customers": customers,
        "furnaces": furnaces,
        "orders": orders,
        "daily_metrics": daily_metrics,
        "complaints": complaints,
        "maintenance": maintenance,
    }


if __name__ == "__main__":
    data = generate_all_data()
