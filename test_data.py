#!/usr/bin/env python
"""Quick test of demo data generation"""

from data.generate_demo_data import generate_all_data

print("🏭 Bodycote Command Centre - Data Generation Test\n")

try:
    data = generate_all_data()
    
    print("\n✅ Success! All data generated correctly")
    print(f"\nData Summary:")
    print(f"  📍 Sites: {len(data['sites'])}")
    print(f"  🏢 Customers: {len(data['customers'])}")
    print(f"  📦 Orders: {len(data['orders'])}")
    print(f"  🔧 Furnaces: {len(data['furnaces'])}")
    print(f"  📊 Daily Metrics: {len(data['daily_metrics'])}")
    print(f"  ⚠️  Complaints: {len(data['complaints'])}")
    print(f"  🛠️  Maintenance: {len(data['maintenance'])}")
    
    print("\n✅ Application is ready to run!")
    print("   Run: streamlit run app.py")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
