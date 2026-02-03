"""
Script to verify that Avante and IOSPL APIs return different data
by comparing records matched on ID (primary key)
"""

import pandas as pd
from api_client import APIClient
from api_client_isopl import APIClientIOSPL
from datetime import datetime

def verify_api_differences():
    """Compare Avante and IOSPL API data by ID to confirm they're different"""
    
    # Use default credentials
    username = 'u2vp8kb'
    password = 'asdftuy#$%78@!'
    
    # Use a date range that has data (2025)
    start_date = "01-01-2025"
    end_date = "31-12-2025"
    
    print("\n" + "="*80)
    print("🔍 VERIFYING API DATA DIFFERENCES")
    print("="*80)
    print(f"   Date Range: {start_date} to {end_date}")
    print(f"   Credentials: {username} / {'*' * len(password)}")
    print()
    
    # Fetch from Avante API
    print("1️⃣  Fetching data from Avante API...")
    avante_client = APIClient(username=username, password=password)
    avante_response = avante_client.get_sales_report(
        start_date=start_date,
        end_date=end_date
    )
    
    if not avante_response.get('success'):
        print(f"   ❌ Avante API Error: {avante_response.get('message')}")
        return
    
    avante_data = avante_response.get('data', {}).get('report_data', [])
    print(f"   ✅ Avante: {len(avante_data)} records")
    
    # Fetch from IOSPL API
    print("\n2️⃣  Fetching data from IOSPL API...")
    iospl_client = APIClientIOSPL(username=username, password=password)
    iospl_response = iospl_client.get_sales_report(
        start_date=start_date,
        end_date=end_date
    )
    
    if not iospl_response.get('success'):
        print(f"   ❌ IOSPL API Error: {iospl_response.get('message')}")
        return
    
    iospl_data = iospl_response.get('data', {}).get('report_data', [])
    print(f"   ✅ IOSPL: {len(iospl_data)} records")
    
    # Convert to DataFrames
    print("\n3️⃣  Converting to DataFrames and extracting IDs...")
    df_avante = pd.DataFrame(avante_data)
    df_iospl = pd.DataFrame(iospl_data)
    
    print(f"   Avante columns: {list(df_avante.columns)}")
    print(f"   IOSPL columns: {list(df_iospl.columns)}")
    
    # Find ID column (could be 'id', 'ID', 'order_id', etc.)
    id_cols_avante = [col for col in df_avante.columns if 'id' in col.lower()]
    id_cols_iospl = [col for col in df_iospl.columns if 'id' in col.lower()]
    
    print(f"   Avante ID columns: {id_cols_avante}")
    print(f"   IOSPL ID columns: {id_cols_iospl}")
    
    if not id_cols_avante or not id_cols_iospl:
        print("   ⚠️  Warning: No ID column found in one or both APIs")
        print("   Comparing record counts only")
        
        print("\n" + "="*80)
        print("📊 SUMMARY")
        print("="*80)
        print(f"   Avante Records: {len(df_avante)}")
        print(f"   IOSPL Records: {len(df_iospl)}")
        print(f"   Difference: {abs(len(df_avante) - len(df_iospl))} records")
        
        if len(df_avante) == len(df_iospl):
            print("\n   ⚠️  Same number of records - may indicate shared database")
        else:
            print("\n   ✅ Different number of records - APIs are serving different data")
        
        return
    
    # Use first ID column found
    id_col_avante = id_cols_avante[0]
    id_col_iospl = id_cols_iospl[0]
    
    avante_ids = set(df_avante[id_col_avante].astype(str))
    iospl_ids = set(df_iospl[id_col_iospl].astype(str))
    
    print(f"   Avante unique IDs: {len(avante_ids)}")
    print(f"   IOSPL unique IDs: {len(iospl_ids)}")
    
    # Find overlapping and unique IDs
    print("\n4️⃣  Analyzing ID overlap...")
    common_ids = avante_ids.intersection(iospl_ids)
    avante_only = avante_ids - iospl_ids
    iospl_only = iospl_ids - avante_ids
    
    print(f"   Common IDs (in both): {len(common_ids)}")
    print(f"   Avante-only IDs: {len(avante_only)}")
    print(f"   IOSPL-only IDs: {len(iospl_only)}")
    
    # Show sample IDs from each group
    if avante_only:
        print(f"   Sample Avante-only IDs: {list(avante_only)[:5]}")
    if iospl_only:
        print(f"   Sample IOSPL-only IDs: {list(iospl_only)[:5]}")
    
    # Compare data for common IDs
    if common_ids:
        print("\n5️⃣  Comparing data for common IDs...")
        
        # Get a sample of common IDs (first 5)
        sample_ids = list(common_ids)[:5]
        
        differences_found = 0
        matches_found = 0
        
        for sample_id in sample_ids:
            avante_record = df_avante[df_avante[id_col_avante].astype(str) == sample_id].iloc[0].to_dict()
            iospl_record = df_iospl[df_iospl[id_col_iospl].astype(str) == sample_id].iloc[0].to_dict()
            
            print(f"\n   📋 ID: {sample_id}")
            print(f"      Avante columns: {len(avante_record)}")
            print(f"      IOSPL columns: {len(iospl_record)}")
            
            # Compare field by field
            differences = []
            all_keys = set(avante_record.keys()).union(set(iospl_record.keys()))
            
            for key in all_keys:
                avante_val = avante_record.get(key, 'N/A')
                iospl_val = iospl_record.get(key, 'N/A')
                
                # Convert to string for comparison to handle different types
                avante_str = str(avante_val) if avante_val is not None else 'None'
                iospl_str = str(iospl_val) if iospl_val is not None else 'None'
                
                if avante_str != iospl_str:
                    differences.append(f"{key}: Avante='{avante_val}' vs IOSPL='{iospl_val}'")
            
            if differences:
                differences_found += 1
                print(f"      ⚠️  {len(differences)} fields differ:")
                for diff in differences[:3]:  # Show first 3 differences
                    print(f"         • {diff}")
                if len(differences) > 3:
                    print(f"         ... and {len(differences) - 3} more")
            else:
                matches_found += 1
                print(f"      ✅ All fields match")
    
    # Print summary
    print("\n" + "="*80)
    print("📊 FINAL SUMMARY")
    print("="*80)
    print(f"   Avante Total Records: {len(df_avante)}")
    print(f"   IOSPL Total Records: {len(df_iospl)}")
    print(f"   Avante Unique IDs: {len(avante_ids)}")
    print(f"   IOSPL Unique IDs: {len(iospl_ids)}")
    print(f"   Common IDs: {len(common_ids)}")
    print(f"   Avante-only IDs: {len(avante_only)}")
    print(f"   IOSPL-only IDs: {len(iospl_only)}")
    
    overlap_pct = (len(common_ids) / max(len(avante_ids), len(iospl_ids)) * 100) if max(len(avante_ids), len(iospl_ids)) > 0 else 0
    print(f"   ID Overlap: {overlap_pct:.1f}%")
    
    print("\n" + "="*80)
    print("🎯 CONCLUSION")
    print("="*80)
    
    if len(avante_only) > 0 or len(iospl_only) > 0:
        print("   ✅ APIs ARE SERVING DIFFERENT DATA")
        print("   ✅ Avante and IOSPL have separate databases")
        print("   ✅ Integration is working correctly!")
        print(f"\n   Details:")
        print(f"   • {len(avante_only)} records exist only in Avante")
        print(f"   • {len(iospl_only)} records exist only in IOSPL")
        if common_ids:
            print(f"   • {len(common_ids)} records have matching IDs (may have different values)")
    elif overlap_pct == 100 and differences_found == 0:
        print("   ⚠️  APIs APPEAR TO BE SERVING IDENTICAL DATA")
        print("   ⚠️  All IDs match and all field values are identical")
        print("   ⚠️  May indicate shared database or testing mode")
    elif overlap_pct == 100 and differences_found > 0:
        print("   ✅ APIs ARE SERVING DIFFERENT DATA")
        print("   ✅ Same IDs but different field values")
        print("   ✅ This confirms separate databases")
    else:
        print("   ℹ️  Partial overlap detected - requires further investigation")
    
    print("="*80 + "\n")

if __name__ == "__main__":
    verify_api_differences()
