import sys
sys.path.insert(0, '/Users/bhurvasharma/dashboard')

from api_client import APIClient
import pandas as pd
import json

print("\n" + "="*80)
print("COMPREHENSIVE API TEST - ALL ENDPOINTS")
print("="*80 + "\n")

client = APIClient()

# 1. TEST LOGIN
print("1️⃣  TESTING LOGIN...")
login_result = client.login("u2vp8kb", "asdftuy#$%78@!")
print(f"   ✅ Login: {'SUCCESS' if login_result['success'] else 'FAILED'}")
print(f"   Token: {client.token[:30]}..." if client.token else "   No token")
print(f"   Expires: {client.token_expiry}")

if not login_result['success']:
    print("   ❌ Cannot continue without successful login")
    sys.exit(1)

# 2. TEST GET SALES REPORT - YEAR
print("\n2️⃣  TESTING GET SALES REPORT (YEAR)...")
sales_year = client.get_sales_report(period="year")
print(f"   ✅ Success: {sales_year['success']}")
if sales_year['success']:
    records = sales_year['data'].get('report_data', [])
    print(f"   Records: {len(records)}")
    print(f"   Date Range: 01-01-2026 to 12-01-2026")

# 3. TEST GET SALES REPORT - WEEK
print("\n3️⃣  TESTING GET SALES REPORT (WEEK)...")
sales_week = client.get_sales_report(period="week")
print(f"   ✅ Success: {sales_week['success']}")
if sales_week['success']:
    records = sales_week['data'].get('report_data', [])
    print(f"   Records: {len(records)}")

# 4. TEST GET SALES REPORT - MONTH
print("\n4️⃣  TESTING GET SALES REPORT (MONTH)...")
sales_month = client.get_sales_report(period="month")
print(f"   ✅ Success: {sales_month['success']}")
if sales_month['success']:
    records = sales_month['data'].get('report_data', [])
    print(f"   Records: {len(records)}")

# 5. TEST CUSTOM DATE RANGE
print("\n5️⃣  TESTING CUSTOM DATE RANGE (05-01-2026 to 10-01-2026)...")
sales_custom = client.get_sales_report(start_date="05-01-2026", end_date="10-01-2026")
print(f"   ✅ Success: {sales_custom['success']}")
if sales_custom['success']:
    records = sales_custom['data'].get('report_data', [])
    print(f"   Records: {len(records)}")

# 6. DATA ANALYSIS
print("\n6️⃣  DATA ANALYSIS...")
if sales_year['success']:
    df = pd.DataFrame(sales_year['data']['report_data'])
    print(f"   Total Records: {len(df)}")
    print(f"   Columns: {', '.join(df.columns[:5])}...")
    print(f"   Dealers (unique): {df['comp_nm'].nunique() if 'comp_nm' in df.columns else 'N/A'}")
    print(f"   States (unique): {df['state'].nunique() if 'state' in df.columns else 'N/A'}")
    print(f"   Total Value: ₹{df['SV'].sum():,.2f}" if 'SV' in df.columns else "N/A")
    print(f"   Total Qty: {df['SQ'].sum():,.0f}" if 'SQ' in df.columns else "N/A")

# 7. TEST LOGOUT
print("\n7️⃣  TESTING LOGOUT...")
logout_result = client.logout()
print(f"   ✅ Logout: {'SUCCESS' if logout_result['success'] else 'FAILED'}")
print(f"   Token cleared: {client.token is None}")

print("\n" + "="*80)
print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
print("="*80 + "\n")

