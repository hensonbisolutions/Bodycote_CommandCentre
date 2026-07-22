#!/usr/bin/env python
"""
Bodycote Command Centre - Comprehensive Verification Script
Validates all components are working correctly
"""

import sys
import os

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_success(text):
    """Print success message"""
    print(f"  ✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"  ❌ {text}")

def check_files():
    """Check all required files exist"""
    print_header("FILE STRUCTURE VERIFICATION")
    
    files = [
        "app.py",
        "requirements.txt",
        "README.md",
        "QUICKSTART.md",
        "BUILD_SUMMARY.md",
        "pages/__init__.py",
        "pages/Executive.py",
        "pages/Site.py",
        "pages/Orders.py",
        "pages/Customers.py",
        "utils/__init__.py",
        "utils/data.py",
        "utils/charts.py",
        "utils/helpers.py",
        "data/generate_demo_data.py",
        "assets/style.css",
    ]
    
    all_exist = True
    for file in files:
        if os.path.exists(file):
            print_success(file)
        else:
            print_error(f"{file} - MISSING!")
            all_exist = False
    
    return all_exist

def check_imports():
    """Check all imports work"""
    print_header("IMPORT VERIFICATION")
    
    try:
        import pandas as pd
        print_success("Pandas imported successfully")
    except ImportError as e:
        print_error(f"Pandas import failed: {e}")
        return False
    
    try:
        import numpy as np
        print_success("NumPy imported successfully")
    except ImportError as e:
        print_error(f"NumPy import failed: {e}")
        return False
    
    try:
        import plotly.graph_objects as go
        print_success("Plotly imported successfully")
    except ImportError as e:
        print_error(f"Plotly import failed: {e}")
        return False
    
    try:
        import streamlit as st
        print_success("Streamlit imported successfully")
    except ImportError as e:
        print_error(f"Streamlit import failed: {e}")
        return False
    
    try:
        import altair as alt
        print_success("Altair imported successfully")
    except ImportError as e:
        print_error(f"Altair import failed: {e}")
        return False
    
    return True

def check_modules():
    """Check all modules import correctly"""
    print_header("MODULE VERIFICATION")
    
    try:
        from data.generate_demo_data import generate_all_data
        print_success("Data generation module loads")
    except Exception as e:
        print_error(f"Data generation module failed: {e}")
        return False
    
    try:
        from utils.data import get_data, get_sites, get_orders
        print_success("Data utilities module loads")
    except Exception as e:
        print_error(f"Data utilities module failed: {e}")
        return False
    
    try:
        from utils.charts import revenue_trend_chart, apply_template
        print_success("Charts module loads")
    except Exception as e:
        print_error(f"Charts module failed: {e}")
        return False
    
    try:
        from utils.helpers import format_currency, create_metric_card
        print_success("Helpers module loads")
    except Exception as e:
        print_error(f"Helpers module failed: {e}")
        return False
    
    return True

def check_data_generation():
    """Check data generation works"""
    print_header("DATA GENERATION VERIFICATION")
    
    try:
        from data.generate_demo_data import generate_all_data
        
        print("  Generating demo data...")
        data = generate_all_data()
        
        # Verify data structure
        required_keys = ["sites", "customers", "furnaces", "orders", "daily_metrics", "complaints", "maintenance"]
        
        for key in required_keys:
            if key in data:
                print_success(f"{key}: {len(data[key])} records")
            else:
                print_error(f"{key} - MISSING from data!")
                return False
        
        # Verify data content
        if len(data["sites"]) != 12:
            print_error(f"Expected 12 sites, got {len(data['sites'])}")
            return False
        
        if len(data["customers"]) != 400:
            print_error(f"Expected 400 customers, got {len(data['customers'])}")
            return False
        
        if len(data["furnaces"]) != 50:
            print_error(f"Expected 50 furnaces, got {len(data['furnaces'])}")
            return False
        
        if len(data["orders"]) < 2500:
            print_error(f"Expected ~3000 orders, got {len(data['orders'])}")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Data generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_calculations():
    """Check data calculation functions"""
    print_header("CALCULATION VERIFICATION")
    
    try:
        from utils.data import (
            get_mtd_revenue, get_ytd_revenue, get_orders_running,
            get_on_time_delivery_pct, get_first_pass_yield,
            get_furnace_utilisation, get_gross_margin
        )
        
        # Run calculations
        mtd = get_mtd_revenue()
        print_success(f"MTD Revenue: £{mtd:,.0f}")
        
        ytd = get_ytd_revenue()
        print_success(f"YTD Revenue: £{ytd:,.0f}")
        
        orders_running = get_orders_running()
        print_success(f"Orders Running: {orders_running}")
        
        on_time = get_on_time_delivery_pct()
        print_success(f"On-Time Delivery: {on_time:.1f}%")
        
        fpy = get_first_pass_yield()
        print_success(f"First Pass Yield: {fpy:.1f}%")
        
        util = get_furnace_utilisation()
        print_success(f"Furnace Utilisation: {util:.1f}%")
        
        margin = get_gross_margin()
        print_success(f"Gross Margin: {margin:.1f}%")
        
        return True
        
    except Exception as e:
        print_error(f"Calculations failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_requirements():
    """Check requirements.txt"""
    print_header("REQUIREMENTS VERIFICATION")
    
    try:
        with open("requirements.txt", "r") as f:
            requirements = f.read().strip().split("\n")
        
        print_success(f"Found {len(requirements)} requirements:")
        for req in requirements:
            print(f"    • {req}")
        
        return True
    except Exception as e:
        print_error(f"Failed to read requirements: {e}")
        return False

def main():
    """Run all verification checks"""
    print("\n" + "🏭" * 35)
    print("\nBODYCOTE EXECUTIVE COMMAND CENTRE")
    print("COMPREHENSIVE VERIFICATION SCRIPT")
    print("\n" + "🏭" * 35)
    
    results = []
    
    # Run checks
    results.append(("File Structure", check_files()))
    results.append(("Requirements", check_requirements()))
    results.append(("Imports", check_imports()))
    results.append(("Modules", check_modules()))
    results.append(("Data Generation", check_data_generation()))
    results.append(("Calculations", check_calculations()))
    
    # Print summary
    print_header("VERIFICATION SUMMARY")
    
    for check_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {check_name:<30} {status}")
    
    # Overall result
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 70)
    if all_passed:
        print("\n  🎉 ALL VERIFICATION CHECKS PASSED!")
        print("\n  ✅ Application is ready to run:")
        print("     streamlit run app.py")
        print("\n" + "=" * 70)
        return 0
    else:
        print("\n  ❌ SOME VERIFICATION CHECKS FAILED!")
        print("\n  Please fix the errors above before running the application.")
        print("\n" + "=" * 70)
        return 1

if __name__ == "__main__":
    sys.exit(main())
