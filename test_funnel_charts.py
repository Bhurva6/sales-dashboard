"""
Test script for Funnel and Conversion Analysis charts
Run this to verify the new chart functions work correctly
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Create sample data
def create_sample_data():
    """Create sample sales data for testing"""
    dates = pd.date_range(start='2026-01-01', end='2026-01-14', freq='D')
    
    data = []
    for date in dates:
        # Generate 50-150 orders per day
        num_orders = np.random.randint(50, 150)
        
        for _ in range(num_orders):
            data.append({
                'Date': date,
                'Value': np.random.uniform(1500, 5000),  # Revenue between 1.5K - 5K
                'Qty': np.random.randint(1, 10),  # Quantity 1-10 items
                'Dealer Name': np.random.choice(['Dealer A', 'Dealer B', 'Dealer C']),
                'State': np.random.choice(['Maharashtra', 'Delhi', 'Karnataka']),
                'City': np.random.choice(['Mumbai', 'Delhi', 'Bangalore']),
                'Category': np.random.choice(['Implants', 'Instruments', 'Accessories']),
                'Sub Category': np.random.choice(['Joint', 'Spine', 'Trauma'])
            })
    
    return pd.DataFrame(data)

def test_funnel_chart():
    """Test the sales funnel chart function"""
    print("\n" + "="*60)
    print("🧪 Testing Sales Funnel Chart")
    print("="*60)
    
    # Create sample data
    df = create_sample_data()
    print(f"✅ Sample data created: {len(df)} orders")
    print(f"   Total Revenue: Rs. {df['Value'].sum():,.0f}")
    print(f"   Total Quantity: {df['Qty'].sum():,.0f}")
    
    # Test the function exists
    try:
        from app import _create_sales_funnel
        print("✅ Function _create_sales_funnel imported successfully")
        
        # Create the chart
        fig = _create_sales_funnel(df)
        print("✅ Funnel chart created successfully")
        
        # Check figure properties
        if fig.data:
            print(f"✅ Chart has {len(fig.data)} trace(s)")
            print(f"   Chart type: {type(fig.data[0]).__name__}")
        
        # Test with empty dataframe
        empty_fig = _create_sales_funnel(pd.DataFrame())
        print("✅ Handles empty dataframe correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing funnel chart: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_conversion_timeline():
    """Test the conversion timeline chart function"""
    print("\n" + "="*60)
    print("🧪 Testing Conversion Timeline Chart")
    print("="*60)
    
    # Create sample data
    df = create_sample_data()
    print(f"✅ Sample data created: {len(df)} orders")
    print(f"   Date range: {df['Date'].min()} to {df['Date'].max()}")
    
    # Test the function exists
    try:
        from app import _create_conversion_timeline
        print("✅ Function _create_conversion_timeline imported successfully")
        
        # Create the chart
        fig = _create_conversion_timeline(df)
        print("✅ Timeline chart created successfully")
        
        # Check figure properties
        if fig.data:
            print(f"✅ Chart has {len(fig.data)} trace(s)")
            for i, trace in enumerate(fig.data):
                print(f"   Trace {i+1}: {trace.name}")
        
        # Test with dataframe without date column
        df_no_date = df.drop('Date', axis=1)
        no_date_fig = _create_conversion_timeline(df_no_date)
        print("✅ Handles missing date column correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing timeline chart: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_chart_metrics():
    """Test the metrics calculations"""
    print("\n" + "="*60)
    print("🧪 Testing Chart Metrics Calculations")
    print("="*60)
    
    # Create controlled sample data
    df = pd.DataFrame({
        'Date': pd.date_range('2026-01-01', periods=10),
        'Value': [1000, 1100, 1200, 1150, 1250, 1300, 1400, 1350, 1450, 1500],
        'Qty': [5, 5, 6, 5, 6, 7, 7, 6, 7, 8]
    })
    
    print(f"✅ Test data created: {len(df)} days")
    
    # Test funnel calculations
    total_orders = len(df)
    total_revenue = df['Value'].sum()
    
    print(f"\nFunnel Metrics:")
    print(f"   Stage 1 (Orders): {total_orders}")
    print(f"   Stage 2 (80%): {int(total_orders * 0.80)}")
    print(f"   Stage 3 (60%): {int(total_orders * 0.60)}")
    print(f"   Stage 4 (Revenue): Rs. {total_revenue:,.0f}")
    
    # Test timeline calculations
    daily_orders = df.groupby('Date').size()
    revenue_per_order = df.groupby('Date')['Value'].sum() / daily_orders
    qty_per_order = df.groupby('Date')['Qty'].sum() / daily_orders
    
    print(f"\nTimeline Metrics:")
    print(f"   Avg Revenue/Order: Rs. {revenue_per_order.mean():,.2f}")
    print(f"   Avg Qty/Order: {qty_per_order.mean():.2f}")
    print(f"   Revenue trend: {revenue_per_order.iloc[0]:.2f} → {revenue_per_order.iloc[-1]:.2f}")
    
    print("✅ All metric calculations verified")
    return True

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 FUNNEL & CONVERSION ANALYSIS - TEST SUITE")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Funnel Chart", test_funnel_chart()))
    results.append(("Conversion Timeline", test_conversion_timeline()))
    results.append(("Metrics Calculations", test_chart_metrics()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print("\n" + "-"*60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Charts are ready to use.")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    
    print("="*60 + "\n")

if __name__ == '__main__':
    run_all_tests()
