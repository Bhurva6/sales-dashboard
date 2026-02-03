"""
Verify IOSPL API Bearer Token and Compare Data with Avante API
"""

import pandas as pd
from api_client import APIClient
from api_client_isopl import APIClientIOSPL
from datetime import datetime, timedelta
import json

def format_dataframe_info(df, name):
    """Format dataframe information for display"""
    print(f"\n{'='*80}")
    print(f"{name} API DATA")
    print(f"{'='*80}")
    if df is not None and not df.empty:
        print(f"✅ Records: {len(df)}")
        print(f"✅ Columns: {list(df.columns)}")
        
        # Show value and quantity totals
        value_cols = [c for c in df.columns if 'value' in c.lower() or c == 'SV']
        qty_cols = [c for c in df.columns if 'qty' in c.lower() or c == 'SQ']
        
        if value_cols:
            total_value = pd.to_numeric(df[value_cols[0]], errors='coerce').sum()
            print(f"✅ Total Value: ₹{total_value:,.2f}")
        
        if qty_cols:
            total_qty = pd.to_numeric(df[qty_cols[0]], errors='coerce').sum()
            print(f"✅ Total Quantity: {total_qty:,.0f}")
        
        # Show sample records
        print(f"\n📊 Sample Records (First 3):")
        print(df.head(3).to_string())
        
        # Show unique values for key columns
        key_columns = ['comp_nm', 'Dealer Name', 'state', 'State', 'city', 'City', 
                       'category_name', 'Category']
        for col in key_columns:
            if col in df.columns:
                unique_count = df[col].nunique()
                print(f"\n📍 Unique {col}: {unique_count}")
                print(f"   Top 5: {df[col].value_counts().head(5).to_dict()}")
    else:
        print("❌ No data returned")
    print(f"{'='*80}\n")

def compare_apis():
    """Compare data from both APIs"""
    print("\n" + "="*80)
    print("🔍 VERIFYING IOSPL API WITH BEARER TOKEN")
    print("="*80)
    
    # Use last month's data for testing
    today = datetime.now()
    end_date = today
    start_date = today - timedelta(days=30)
    
    start_date_str = start_date.strftime("%d-%m-%Y")
    end_date_str = end_date.strftime("%d-%m-%Y")
    
    print(f"\n📅 Date Range: {start_date_str} to {end_date_str}")
    
    credentials = {
        'username': 'u2vp8kb',
        'password': 'asdftuy#$%78@!'
    }
    
    # Test IOSPL API with bearer token
    print("\n" + "="*80)
    print("🔵 TESTING IOSPL API (with Bearer Token)")
    print("="*80)
    
    try:
        iospl_client = APIClientIOSPL(**credentials)
        print(f"✅ IOSPL Client initialized with bearer token")
        print(f"   Token: {iospl_client.token[:50]}...")
        
        iospl_response = iospl_client.get_sales_report(
            start_date=start_date_str,
            end_date=end_date_str
        )
        
        if iospl_response.get('success'):
            iospl_data = iospl_response.get('data', {})
            iospl_records = iospl_data.get('report_data', [])
            iospl_df = pd.DataFrame(iospl_records) if iospl_records else pd.DataFrame()
            
            format_dataframe_info(iospl_df, "IOSPL")
        else:
            print(f"❌ IOSPL API Error: {iospl_response.get('message')}")
            iospl_df = pd.DataFrame()
    except Exception as e:
        print(f"❌ IOSPL API Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        iospl_df = pd.DataFrame()
    
    # Test Avante API
    print("\n" + "="*80)
    print("🟢 TESTING AVANTE API (Original)")
    print("="*80)
    
    try:
        avante_client = APIClient(**credentials)
        print(f"✅ Avante Client initialized")
        
        avante_response = avante_client.get_sales_report(
            start_date=start_date_str,
            end_date=end_date_str
        )
        
        if avante_response.get('success'):
            avante_data = avante_response.get('data', {})
            avante_records = avante_data.get('report_data', [])
            avante_df = pd.DataFrame(avante_records) if avante_records else pd.DataFrame()
            
            format_dataframe_info(avante_df, "AVANTE")
        else:
            print(f"❌ Avante API Error: {avante_response.get('message')}")
            avante_df = pd.DataFrame()
    except Exception as e:
        print(f"❌ Avante API Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        avante_df = pd.DataFrame()
    
    # Compare the two datasets
    print("\n" + "="*80)
    print("📊 COMPARISON SUMMARY")
    print("="*80)
    
    comparison = {
        'IOSPL Records': len(iospl_df) if not iospl_df.empty else 0,
        'Avante Records': len(avante_df) if not avante_df.empty else 0,
    }
    
    print(f"\n📈 Record Count:")
    for key, value in comparison.items():
        print(f"   {key}: {value:,}")
    
    if not iospl_df.empty and not avante_df.empty:
        # Compare totals
        iospl_value_col = next((c for c in iospl_df.columns if 'value' in c.lower() or c == 'SV'), None)
        avante_value_col = next((c for c in avante_df.columns if 'value' in c.lower() or c == 'SV'), None)
        
        if iospl_value_col and avante_value_col:
            iospl_total = pd.to_numeric(iospl_df[iospl_value_col], errors='coerce').sum()
            avante_total = pd.to_numeric(avante_df[avante_value_col], errors='coerce').sum()
            
            print(f"\n💰 Total Value:")
            print(f"   IOSPL:  ₹{iospl_total:,.2f}")
            print(f"   Avante: ₹{avante_total:,.2f}")
            
            diff = abs(iospl_total - avante_total)
            max_val = max(iospl_total, avante_total)
            if max_val > 0:
                diff_pct = (diff / max_val) * 100
                print(f"   Difference: ₹{diff:,.2f} ({diff_pct:.2f}%)")
            else:
                print(f"   Difference: ₹0.00 (0.00%)")
        
        # Check if data is identical or different
        if len(iospl_df) == len(avante_df):
            print(f"\n✅ Same number of records")
        else:
            print(f"\n⚠️ Different number of records - Data sources may be different!")
    
    print("\n" + "="*80)
    print("🎯 CONCLUSION")
    print("="*80)
    
    if iospl_df.empty and avante_df.empty:
        print("❌ Both APIs returned no data")
    elif iospl_df.empty:
        print("❌ IOSPL API returned no data (check bearer token or API endpoint)")
    elif avante_df.empty:
        print("❌ Avante API returned no data")
    elif len(iospl_df) == len(avante_df):
        print("✅ IOSPL API is working! Data appears to be from the SAME source")
    else:
        print("⚠️ IOSPL API is working! Data appears to be from a DIFFERENT source")
        print("   This could indicate separate databases or different filtering")
    
    print("="*80 + "\n")

if __name__ == "__main__":
    compare_apis()
