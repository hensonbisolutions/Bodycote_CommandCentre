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

PERSON_FIRST_NAMES = [
    "Oliver", "Amelia", "George", "Isla", "Harry", "Ava", "Noah", "Sophia", "Jack", "Emily",
    "Charlie", "Grace", "Leo", "Freya", "Arthur", "Lily", "Thomas", "Mia", "Oscar", "Evie",
]
PERSON_LAST_NAMES = [
    "Smith", "Johnson", "Taylor", "Brown", "Davies", "Wilson", "Thomas", "Evans", "Walker", "Roberts",
    "Hall", "Clark", "Lewis", "Young", "King", "Scott", "Green", "Baker", "Adams", "Hill",
]
DEPARTMENTS = ["Operations", "Quality", "Maintenance", "Logistics", "Engineering", "Production Planning"]
ROLES = [
    "Operator", "Senior Operator", "Process Technician", "Quality Inspector", "Maintenance Engineer",
    "Production Planner", "Shift Supervisor", "EHS Specialist", "Metallurgist", "Team Leader",
]
SHIFT_PATTERNS = ["Day", "Night", "Early", "Late", "Rotating 2-2-3"]
ABSENCE_REASONS = [
    "Short-term illness", "Musculoskeletal", "Stress", "Family care", "Medical appointment",
    "Injury", "Flu", "Long-term condition",
]
EMPLOYMENT_TYPES = ["Full-Time", "Part-Time", "Agency"]
CONTRACT_TYPES = ["Permanent", "Fixed-Term", "Agency"]

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


def _random_person_name():
    return f"{random.choice(PERSON_FIRST_NAMES)} {random.choice(PERSON_LAST_NAMES)}"


def generate_workforce_employees(sites):
    """Generate workforce roster including active and terminated workers."""
    employees = []
    emp_id = 1
    today = datetime.now().date()

    for _, site in sites.iterrows():
        baseline = int(site["employees"])
        # Add realistic spread around baseline to include turnover and vacancies.
        total_records = max(20, baseline + random.randint(-4, 8))
        manager_pool = [f"Mgr {site['site_name']} {i}" for i in range(1, 6)]

        for _ in range(total_records):
            role = random.choice(ROLES)
            dept = random.choice(DEPARTMENTS)
            grade = random.choice(["G4", "G5", "G6", "G7", "G8"])
            employment_type = random.choices(EMPLOYMENT_TYPES, weights=[0.74, 0.16, 0.10], k=1)[0]
            contract_type = random.choices(CONTRACT_TYPES, weights=[0.78, 0.12, 0.10], k=1)[0]
            hire_days_ago = random.randint(30, 3650)
            hire_date = today - timedelta(days=hire_days_ago)
            terminated = random.random() < 0.12
            termination_date = None
            if terminated:
                last_day_offset = random.randint(10, min(hire_days_ago - 1, 900)) if hire_days_ago > 15 else 10
                termination_date = today - timedelta(days=last_day_offset)
            base_salary = {
                "Operator": 32500,
                "Senior Operator": 38000,
                "Process Technician": 41000,
                "Quality Inspector": 39000,
                "Maintenance Engineer": 46000,
                "Production Planner": 43000,
                "Shift Supervisor": 49000,
                "EHS Specialist": 47000,
                "Metallurgist": 52000,
                "Team Leader": 50500,
            }.get(role, 40000)
            salary = int(base_salary * random.uniform(0.9, 1.18))

            employees.append(
                {
                    "employee_id": f"EMP_{emp_id:05d}",
                    "name": _random_person_name(),
                    "site_id": site["site_id"],
                    "site": site["site_name"],
                    "region": site["region"],
                    "department": dept,
                    "manager": random.choice(manager_pool),
                    "role": role,
                    "grade": grade,
                    "salary": salary,
                    "shift_pattern": random.choice(SHIFT_PATTERNS),
                    "employment_type": employment_type,
                    "contract_type": contract_type,
                    "hire_date": hire_date,
                    "termination_date": termination_date,
                    "training_status": random.choices(["Compliant", "Due", "Overdue"], weights=[0.76, 0.17, 0.07], k=1)[0],
                    "performance_rating": round(random.uniform(2.6, 4.9), 1),
                    "overtime_hours": round(max(0, random.gauss(12, 5)), 1),
                    "safety_training": random.choices(["Completed", "Pending"], weights=[0.86, 0.14], k=1)[0],
                    "engagement_score": round(random.uniform(62, 91), 1),
                    "cross_skilled": random.random() < 0.43,
                }
            )
            emp_id += 1

    return pd.DataFrame(employees)


def generate_workforce_absence(employees, days_back=365):
    """Generate absence event records with duration, reason, and estimated costs."""
    records = []
    today = datetime.now().date()
    start_date = today - timedelta(days=days_back)

    for _, emp in employees.iterrows():
        term_date = emp["termination_date"]
        active_end = term_date if pd.notna(term_date) and term_date else today
        if active_end < start_date:
            continue

        emp_days = max(1, (active_end - max(start_date, emp["hire_date"])).days)
        expected_events = max(0, int(np.random.poisson(lam=(emp_days / 365) * 1.6)))

        for _ in range(expected_events):
            reason = random.choices(ABSENCE_REASONS, weights=[34, 14, 11, 8, 10, 8, 9, 6], k=1)[0]
            is_long_term = reason in {"Stress", "Long-term condition", "Injury"} and random.random() < 0.45
            duration = random.randint(1, 5) if not is_long_term else random.randint(8, 40)
            event_date = max(start_date, emp["hire_date"]) + timedelta(days=random.randint(0, emp_days - 1))
            daily_cost = (emp["salary"] / 260) * random.uniform(1.0, 1.4)
            records.append(
                {
                    "absence_id": f"ABS_{random.randint(100000, 999999)}",
                    "employee_id": emp["employee_id"],
                    "site_id": emp["site_id"],
                    "site": emp["site"],
                    "region": emp["region"],
                    "department": emp["department"],
                    "shift_pattern": emp["shift_pattern"],
                    "absence_date": event_date,
                    "absence_reason": reason,
                    "absence_type": "Long-term" if duration >= 8 else "Short-term",
                    "lost_days": duration,
                    "estimated_cost": round(duration * daily_cost, 2),
                    "bradford_factor": int((1 if duration >= 8 else random.randint(1, 3)) ** 2 * duration),
                }
            )

    return pd.DataFrame(records)


def generate_recruitment_data(sites, employees, days_back=240):
    """Generate recruitment funnel and vacancy records by site."""
    today = datetime.now().date()
    start_date = today - timedelta(days=days_back)
    vacancies = []

    leavers = employees[employees["termination_date"].notna()].copy()

    for _, site in sites.iterrows():
        site_leavers = leavers[leavers["site_id"] == site["site_id"]]
        vacancy_count = max(2, int(len(site_leavers) * 0.4) + random.randint(0, 4))
        for _ in range(vacancy_count):
            opened = start_date + timedelta(days=random.randint(0, days_back))
            time_to_hire = random.randint(18, 74)
            fill_delay = random.randint(2, 18)
            filled = random.random() > 0.28
            filled_date = opened + timedelta(days=time_to_hire + fill_delay) if filled else None
            apps = random.randint(8, 75)
            interviews = max(2, int(apps * random.uniform(0.14, 0.34)))
            offers = max(1, int(interviews * random.uniform(0.28, 0.46)))
            accepted = max(0, int(offers * random.uniform(0.62, 0.93)))

            vacancies.append(
                {
                    "vacancy_id": f"VAC_{random.randint(10000, 99999)}",
                    "site_id": site["site_id"],
                    "site": site["site_name"],
                    "region": site["region"],
                    "department": random.choice(DEPARTMENTS),
                    "role": random.choice(ROLES),
                    "critical_skill": random.random() < 0.28,
                    "open_date": opened,
                    "filled_date": filled_date,
                    "status": "Filled" if filled else "Open",
                    "applications": apps,
                    "interviews": interviews,
                    "offers": offers,
                    "accepted_offers": accepted,
                    "time_to_hire_days": time_to_hire,
                    "time_to_fill_days": time_to_hire + fill_delay if filled else None,
                    "replacement_cost": round(random.uniform(3500, 18000), 2),
                    "onboarding_cost": round(random.uniform(1800, 8200), 2),
                }
            )

    return pd.DataFrame(vacancies)


def generate_workforce_safety(sites, days_back=180):
    """Generate safety event records by site."""
    events = []
    today = datetime.now().date()
    start_date = today - timedelta(days=days_back)
    incident_types = ["Recordable", "Near Miss", "Observation", "LTI"]

    for _, site in sites.iterrows():
        n_events = random.randint(10, 45)
        for _ in range(n_events):
            event_date = start_date + timedelta(days=random.randint(0, days_back))
            kind = random.choices(incident_types, weights=[0.25, 0.36, 0.31, 0.08], k=1)[0]
            risk_rating = random.choices(["Low", "Medium", "High"], weights=[0.5, 0.36, 0.14], k=1)[0]
            events.append(
                {
                    "event_id": f"SAFE_{random.randint(100000, 999999)}",
                    "site_id": site["site_id"],
                    "site": site["site_name"],
                    "region": site["region"],
                    "event_date": event_date,
                    "event_type": kind,
                    "risk_rating": risk_rating,
                }
            )

    return pd.DataFrame(events)


def build_workforce_daily_snapshot(sites, employees, absences, recruitment, safety, daily_metrics):
    """Create site/day workforce snapshots tied to operational metrics for realistic relationships."""
    base = daily_metrics.copy()
    base["date"] = pd.to_datetime(base["date"]).dt.date

    active_by_site = (
        employees[employees["termination_date"].isna()]
        .groupby("site_id")
        .size()
        .to_dict()
    )

    absences = absences.copy()
    if not absences.empty:
        absences["absence_date"] = pd.to_datetime(absences["absence_date"]).dt.date
        abs_group = absences.groupby(["site_id", "absence_date"]).agg(
            absence_events=("absence_id", "count"),
            lost_days=("lost_days", "sum"),
            absence_cost=("estimated_cost", "sum"),
        )
    else:
        abs_group = pd.DataFrame(columns=["absence_events", "lost_days", "absence_cost"])

    safety = safety.copy()
    if not safety.empty:
        safety["event_date"] = pd.to_datetime(safety["event_date"]).dt.date
        safe_group = safety.groupby(["site_id", "event_date"]).agg(
            recordable_incidents=("event_type", lambda s: int((s == "Recordable").sum())),
            near_misses=("event_type", lambda s: int((s == "Near Miss").sum())),
            lti=("event_type", lambda s: int((s == "LTI").sum())),
            observations=("event_type", lambda s: int((s == "Observation").sum())),
        )
    else:
        safe_group = pd.DataFrame(columns=["recordable_incidents", "near_misses", "lti", "observations"])

    recruit_open = recruitment[recruitment["status"] == "Open"].groupby("site_id").size().to_dict() if not recruitment.empty else {}

    rows = []
    for _, row in base.iterrows():
        site_id = row["site_id"]
        date_val = row["date"]
        headcount = int(active_by_site.get(site_id, 40))
        vacancy_count = int(recruit_open.get(site_id, 3))
        scheduled_days = max(1, headcount)
        abs_info = abs_group.loc[(site_id, date_val)] if (site_id, date_val) in abs_group.index else None
        safe_info = safe_group.loc[(site_id, date_val)] if (site_id, date_val) in safe_group.index else None

        lost_days = float(abs_info["lost_days"]) if abs_info is not None else 0.0
        absence_rate = min(12.0, (lost_days / scheduled_days) * 100)
        overtime_hours = max(0.0, (row["utilisation"] - 62) * 0.42 + random.uniform(0.5, 8.0) + (absence_rate * 0.55))
        labour_cost = (headcount * 210) + (overtime_hours * 36) + (float(abs_info["absence_cost"]) if abs_info is not None else 0)
        agency_cost = max(0.0, vacancy_count * 145 + random.uniform(40, 380))

        rows.append(
            {
                "date": date_val,
                "site_id": site_id,
                "headcount": headcount,
                "vacancies": vacancy_count,
                "absence_rate": round(absence_rate, 2),
                "lost_working_days": round(lost_days, 2),
                "absence_cost": round(float(abs_info["absence_cost"]) if abs_info is not None else 0.0, 2),
                "overtime_hours": round(overtime_hours, 2),
                "labour_cost": round(labour_cost, 2),
                "agency_labour_cost": round(agency_cost, 2),
                "recordable_incidents": int(safe_info["recordable_incidents"]) if safe_info is not None else 0,
                "near_misses": int(safe_info["near_misses"]) if safe_info is not None else 0,
                "lost_time_injuries": int(safe_info["lti"]) if safe_info is not None else 0,
                "safety_observations": int(safe_info["observations"]) if safe_info is not None else 0,
            }
        )

    return pd.DataFrame(rows)


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
    workforce_employees = generate_workforce_employees(sites)
    workforce_absence = generate_workforce_absence(workforce_employees, days_back=365)
    workforce_recruitment = generate_recruitment_data(sites, workforce_employees, days_back=240)
    workforce_safety = generate_workforce_safety(sites, days_back=180)
    workforce_daily = build_workforce_daily_snapshot(
        sites,
        workforce_employees,
        workforce_absence,
        workforce_recruitment,
        workforce_safety,
        daily_metrics,
    )
    
    print(f"✓ Generated {len(sites)} sites")
    print(f"✓ Generated {len(customers)} customers")
    print(f"✓ Generated {len(furnaces)} furnaces")
    print(f"✓ Generated {len(orders)} orders")
    print(f"✓ Generated {len(daily_metrics)} daily metrics")
    print(f"✓ Generated {len(complaints)} complaints")
    print(f"✓ Generated {len(maintenance)} maintenance records")
    print(f"✓ Generated {len(workforce_employees)} employee records")
    print(f"✓ Generated {len(workforce_absence)} absence records")
    print(f"✓ Generated {len(workforce_recruitment)} recruitment records")
    print(f"✓ Generated {len(workforce_safety)} safety events")
    print(f"✓ Generated {len(workforce_daily)} workforce daily snapshots")
    
    return {
        "sites": sites,
        "customers": customers,
        "furnaces": furnaces,
        "orders": orders,
        "daily_metrics": daily_metrics,
        "complaints": complaints,
        "maintenance": maintenance,
        "workforce_employees": workforce_employees,
        "workforce_absence": workforce_absence,
        "workforce_recruitment": workforce_recruitment,
        "workforce_safety": workforce_safety,
        "workforce_daily": workforce_daily,
    }


if __name__ == "__main__":
    data = generate_all_data()
