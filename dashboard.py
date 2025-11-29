import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans, DBSCAN
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, silhouette_score
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
import xgboost as xgb
from datetime import datetime, timedelta
import warnings
from scipy import stats
from collections import Counter
import json
warnings.filterwarnings('ignore')

# Column name constants
YEARS = ['2020-21', '2021-22', '2022-23', '2023-24', '2024-25']
VALUE_COLS = [f'Value\n{year}' for year in YEARS]
QTY_COLS = [f'Qty\n{year}' for year in YEARS]
CURRENT_VALUE_COL = VALUE_COLS[-1]  # 'Value\n2024-25'
CURRENT_QTY_COL = QTY_COLS[-1]      # 'Qty\n2024-25'

# Function to get available years from data
def get_available_years(df, prefix):
    available_cols = [col for col in df.columns if col.startswith(prefix)]
    available_years = [col.split('\n')[-1] for col in available_cols]
    return sorted(available_years)

# Page Configuration
st.set_page_config(
    layout="wide", 
    page_title="Orthopedic Implant Analytics Dashboard", 
    page_icon="🏥",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        font-size: 42px;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 10px;
    }
    .sub-header {
        font-size: 18px;
        color: #666;
        text-align: center;
        margin-bottom: 30px;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .insight-box {
        background-color: #f0f8ff;
        padding: 15px;
        border-left: 5px solid #1f77b4;
        border-radius: 5px;
        margin: 10px 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 15px;
        border-left: 5px solid #ffc107;
        border-radius: 5px;
        margin: 10px 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 15px;
        border-left: 5px solid #28a745;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🏥 Orthopedic Implant Analytics Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI-Powered Sales Intelligence & Demand Forecasting Platform</p>', unsafe_allow_html=True)

# Download sample data button
try:
    with open("combined_dummy.xlsx", "rb") as file:
        st.download_button(
            label="📥 Download Sample Data",
            data=file,
            file_name="sample_dashboard_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Download a sample Excel file to see the expected data format"
        )
except FileNotFoundError:
    pass  # Sample file not available

# File upload
combined_file = st.file_uploader("Upload Combined Data (Excel)", type=["xlsx", "xls"])

if combined_file:
    df = pd.read_excel(combined_file, engine='openpyxl')
    st.success(f"Data loaded: {len(df)} rows")
    
    # Preview of uploaded data
    with st.expander("📊 Preview Uploaded Data", expanded=False):
        st.dataframe(df.head(20), use_container_width=True)
    
    # Split data based on 'Type' column or key columns
    if 'Type' in df.columns:
        df_sales = df[df['Type'] == 'Sales']
        df_purchase = df[df['Type'] == 'Purchase']
        df_payment = df[df['Type'] == 'Payment']
    else:
        df_sales = df
        df_purchase = df
        df_payment = df
    
    tabs = st.tabs(["Sales Analytics", "Purchase Analytics", "Customer Insights", "Payment Analysis"])
    
    with tabs[0]:
        if not df_sales.empty:
            st.success(f"Sales data: {len(df_sales)} rows")
            
            # Get available years
            available_value_years = get_available_years(df_sales, 'Value\n')
            available_qty_years = get_available_years(df_sales, 'Qty\n')
            
            # 1. Revenue & Quantity Insights
            st.header("💰 Revenue & Quantity Insights")
            if CURRENT_VALUE_COL in df_sales.columns and 'Company' in df_sales.columns:
                col1, col2, col3 = st.columns(3)
                with col1:
                    rev_pie = px.pie(df_sales, values=CURRENT_VALUE_COL, names='Company', title="Revenue by Company")
                    st.plotly_chart(rev_pie, use_container_width=True, key="sales_rev_pie")
                with col2:
                    if CURRENT_QTY_COL in df_sales.columns:
                        qty_pie = px.pie(df_sales, values=CURRENT_QTY_COL, names='Company', title="Quantity by Company")
                        st.plotly_chart(qty_pie, use_container_width=True, key="sales_qty_pie")
                with col3:
                    # Year-wise trend
                    if available_value_years:
                        yearly_revenue = [df_sales[f'Value\n{year}'].sum() for year in available_value_years]
                        trend_df = pd.DataFrame({'Year': available_value_years, 'Revenue': yearly_revenue})
                        trend_chart = px.line(trend_df, x='Year', y='Revenue', title="Yearly Revenue Trend")
                        st.plotly_chart(trend_chart, use_container_width=True, key="sales_yearly_trend")
            
            # Additional: By State and Category
            if CURRENT_VALUE_COL in df_sales.columns:
                if 'State' in df_sales.columns:
                    state_pie = px.pie(df_sales, values=CURRENT_VALUE_COL, names='State', title="Revenue by State")
                    st.plotly_chart(state_pie, use_container_width=True, key="sales_state_pie")
                if 'Category' in df_sales.columns:
                    cat_pie = px.pie(df_sales, values=CURRENT_VALUE_COL, names='Category', title="Revenue by Category")
                    st.plotly_chart(cat_pie, use_container_width=True, key="sales_cat_pie")
            
            # Comparison by Sub Category
            if 'Sub Category' in df_sales.columns and CURRENT_VALUE_COL in df_sales.columns:
                sub_cat_bar = px.bar(df_sales.groupby('Sub Category')[CURRENT_VALUE_COL].sum().reset_index(), 
                                   x='Sub Category', y=CURRENT_VALUE_COL, title="Revenue by Sub Category")
                st.plotly_chart(sub_cat_bar, use_container_width=True, key="sales_sub_cat_bar")
            
            # Year-wise Quantity Trend
            if available_qty_years:
                yearly_qty = [df_sales[f'Qty\n{year}'].sum() for year in available_qty_years]
                qty_trend_df = pd.DataFrame({'Year': available_qty_years, 'Quantity': yearly_qty})
                qty_trend_chart = px.line(qty_trend_df, x='Year', y='Quantity', title="Yearly Quantity Trend")
                st.plotly_chart(qty_trend_chart, use_container_width=True, key="sales_qty_trend")

            # 1. Sales Forecasting
            st.header("🔮 Sales Forecasting")
            if available_value_years and len(available_value_years) > 1:
                yearly_sales = [df_sales[f'Value\n{year}'].sum() for year in available_value_years]
                
                # Simple linear regression for forecasting
                X = np.array(range(len(available_value_years))).reshape(-1, 1)
                y = yearly_sales
                model = LinearRegression()
                model.fit(X, y)
                
                # Predict for all years including next
                X_all = np.array(range(len(available_value_years) + 1)).reshape(-1, 1)
                predicted_all = model.predict(X_all)
                
                forecast_df = pd.DataFrame({
                    'Year': list(range(len(available_value_years))) + [len(available_value_years)],
                    'Sales': yearly_sales + [np.nan],
                    'Predicted': predicted_all
                })
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Predicted Sales for Next Year", f"₹{predicted_all[-1]:,.0f}")
                with col2:
                    forecast_chart = px.line(forecast_df, x='Year', y=['Sales', 'Predicted'], title="Sales Forecast")
                    st.plotly_chart(forecast_chart, use_container_width=True, key="sales_forecast")
            
            # 2. Customer Segmentation
            st.header("👥 Customer Segmentation")
            if CURRENT_VALUE_COL in df_sales.columns and 'Company' in df_sales.columns:
                customer_sales = df_sales.groupby('Company')[CURRENT_VALUE_COL].sum().reset_index()
                customer_sales['Segment'] = pd.cut(customer_sales[CURRENT_VALUE_COL], bins=3, labels=['Low', 'Medium', 'High'])
                seg_pie = px.pie(customer_sales, values=CURRENT_VALUE_COL, names='Segment', title="Customer Segmentation by Revenue")
                st.plotly_chart(seg_pie, use_container_width=True, key="sales_seg_pie")
            
            # 3. Trend Analysis
            st.header("📈 Trend Analysis")
            if available_value_years and 'Category' in df_sales.columns:
                trend_data = {'Year': available_value_years}
                for cat in df_sales['Category'].unique():
                    trend_data[cat] = [df_sales[df_sales['Category'] == cat][f'Value\n{year}'].sum() for year in available_value_years]
                trend_df = pd.DataFrame(trend_data)
                trend_chart = px.line(trend_df, x='Year', y=trend_df.columns[1:], title="Category-wise Sales Trend")
                st.plotly_chart(trend_chart, use_container_width=True, key="sales_cat_trend")

            # 2. Customer Segmentation (Onion method)
            with st.expander("👥 Customer Segmentation - Click to Drill Down"):
                if 'State' in df_sales.columns and CURRENT_VALUE_COL in df_sales.columns:
                    state_rev = px.bar(df_sales.groupby('State')[CURRENT_VALUE_COL].sum().reset_index(), 
                                     x='State', y=CURRENT_VALUE_COL, title="State-wise Revenue")
                    st.plotly_chart(state_rev, key="sales_state_rev")
                    
                    # City drill-down
                    if 'City' in df_sales.columns:
                        city_rev = px.bar(df_sales.groupby(['State','City'])[CURRENT_VALUE_COL].sum().reset_index(), 
                                        x='City', y=CURRENT_VALUE_COL, color='State', title="City-wise Revenue")
                        st.plotly_chart(city_rev, key="sales_city_rev")

            # 3. Non-Moving Items
            with st.expander("📦 Non-Moving & Slow-Moving Items"):
                product_col = 'Product' if 'Product' in df_sales.columns else ('Product Code' if 'Product Code' in df_sales.columns else None)
                if CURRENT_QTY_COL in df_sales.columns and product_col and CURRENT_VALUE_COL in df_sales.columns:
                    months_back = st.slider("Last X months", 1, 12, 3, key="sales_slow_slider")
                    slow_items = df_sales[df_sales[CURRENT_QTY_COL] < df_sales[CURRENT_QTY_COL].mean() * 0.2]
                    st.dataframe(slow_items[[product_col, CURRENT_QTY_COL, CURRENT_VALUE_COL]].rename(columns={CURRENT_QTY_COL: 'Quantity', CURRENT_VALUE_COL: 'Revenue'}))
                else:
                    st.write("Required columns not found in the data.")

            # 4. Cross-Selling Opportunities
            with st.expander("🔗 Cross-Selling Analysis"):
                if 'Product' in df_sales.columns or 'Product Code' in df_sales.columns:
                    prod_col = 'Product' if 'Product' in df_sales.columns else 'Product Code'
                    top_products = df_sales[prod_col].value_counts().head(5).index.tolist()
                    st.write(f"Top products: {', '.join(top_products)}")
                    # Add product mix table here
                else:
                    st.write("Required column ('Product' or 'Product Code') not found in the data.")

            # Customer Hierarchy: CustID linked to Company
            with st.expander("🔗 Customer Hierarchy (CustID to Company)"):
                if 'CustID' in df_sales.columns and 'Company' in df_sales.columns and 'Value\n2024-25' in df_sales.columns:
                    cust_hierarchy = df_sales.groupby(['CustID', 'Company'])['Value\n2024-25'].sum().reset_index().sort_values('Value\n2024-25', ascending=False)
                    st.dataframe(cust_hierarchy.head(20), use_container_width=True)
                    st.write("This shows each CustID linked to its Company with total revenue.")
            
            # Product Hierarchy: CID linked to Sub Category and Product Code
            with st.expander("🔗 Product Hierarchy (CID to Sub Category to Product Code)"):
                if 'CID' in df_sales.columns and 'Sub Category' in df_sales.columns and 'Product Code' in df_sales.columns:
                    prod_hierarchy = df_sales.groupby(['CID', 'Sub Category', 'Product Code']).size().reset_index(name='Count').sort_values('Count', ascending=False)
                    st.dataframe(prod_hierarchy.head(20), use_container_width=True)
                    st.write("This shows CID linked to Sub Category and associated Product Codes with transaction counts.")
            
            # Sidebar filters
            st.sidebar.header("Filters")
            date_range = st.sidebar.date_input("Date Range", [])
            
            # Dealer Ranking
            if 'Dealer' in df_sales.columns and CURRENT_VALUE_COL in df_sales.columns:
                dealer_rank = df_sales.groupby('Dealer')[CURRENT_VALUE_COL].sum().sort_values(ascending=False).reset_index()
                st.subheader("Dealer Ranking")
                st.dataframe(dealer_rank)
            
            # Predictive Alerts
            st.header("🚨 Predictive & Automated Alerts")
            if CURRENT_QTY_COL in df_sales.columns and 'Month' in df_sales.columns:
                # Simple forecasting: linear trend
                monthly_qty = df_sales.groupby('Month')[CURRENT_QTY_COL].sum().reset_index()
                if len(monthly_qty) > 1:
                    from sklearn.linear_model import LinearRegression
                    X = np.array(range(len(monthly_qty))).reshape(-1, 1)
                    y = monthly_qty[CURRENT_QTY_COL].values
                    model = LinearRegression().fit(X, y)
                    next_month = model.predict([[len(monthly_qty)]])[0]
                    st.write(f"Predicted quantity for next month: {next_month:.2f}")
                    
                    # Alert for low inventory (assuming stock column)
                    if 'Stock' in df_sales.columns:
                        low_stock = df_sales[df_sales['Stock'] < df_sales['Stock'].mean() * 0.5]
                        if not low_stock.empty:
                            st.warning("Low stock items:")
                            st.dataframe(low_stock[['Product', 'Stock']])
            else:
                st.write("Required columns for predictive alerts not found.")
        else:
            st.write("No sales data found.")
    
    with tabs[1]:
        if not df_purchase.empty:
            st.success(f"Purchase data: {len(df_purchase)} rows")
            
            # Get available years
            available_value_years = get_available_years(df_purchase, 'Value\n')
            available_qty_years = get_available_years(df_purchase, 'Qty\n')
            
            # 1. Purchase Insights
            st.header("🛒 Purchase Insights")
            if CURRENT_VALUE_COL in df_purchase.columns and 'Company' in df_purchase.columns:
                col1, col2, col3 = st.columns(3)
                with col1:
                    pur_pie = px.pie(df_purchase, values=CURRENT_VALUE_COL, names='Company', title="Purchase Value by Company")
                    st.plotly_chart(pur_pie, use_container_width=True, key="pur_rev_pie")
                with col2:
                    if CURRENT_QTY_COL in df_purchase.columns:
                        pur_qty_pie = px.pie(df_purchase, values=CURRENT_QTY_COL, names='Company', title="Purchase Quantity by Company")
                        st.plotly_chart(pur_qty_pie, use_container_width=True, key="pur_qty_pie")
                with col3:
                    # Year-wise trend
                    if available_value_years:
                        yearly_purchase = [df_purchase[f'Value\n{year}'].sum() for year in available_value_years]
                        pur_trend_df = pd.DataFrame({'Year': available_value_years, 'Purchase Value': yearly_purchase})
                        pur_trend_chart = px.line(pur_trend_df, x='Year', y='Purchase Value', title="Yearly Purchase Trend")
                        st.plotly_chart(pur_trend_chart, use_container_width=True, key="pur_yearly_trend")
            
            # Additional: By State and Category
            if CURRENT_VALUE_COL in df_purchase.columns:
                if 'State' in df_purchase.columns:
                    pur_state_pie = px.pie(df_purchase, values=CURRENT_VALUE_COL, names='State', title="Purchase by State")
                    st.plotly_chart(pur_state_pie, use_container_width=True, key="pur_state_pie")
                if 'Category' in df_purchase.columns:
                    pur_cat_pie = px.pie(df_purchase, values=CURRENT_VALUE_COL, names='Category', title="Purchase by Category")
                    st.plotly_chart(pur_cat_pie, use_container_width=True, key="pur_cat_pie")
            
            # Comparison by Sub Category
            if 'Sub Category' in df_purchase.columns and CURRENT_VALUE_COL in df_purchase.columns:
                pur_sub_cat_bar = px.bar(df_purchase.groupby('Sub Category')[CURRENT_VALUE_COL].sum().reset_index(), 
                                       x='Sub Category', y=CURRENT_VALUE_COL, title="Purchase by Sub Category")
                st.plotly_chart(pur_sub_cat_bar, use_container_width=True, key="pur_sub_cat_bar")
            
            # Year-wise Quantity Trend
            if available_qty_years:
                yearly_pur_qty = [df_purchase[f'Qty\n{year}'].sum() for year in available_qty_years]
                pur_qty_trend_df = pd.DataFrame({'Year': available_qty_years, 'Purchase Quantity': yearly_pur_qty})
                pur_qty_trend_chart = px.line(pur_qty_trend_df, x='Year', y='Purchase Quantity', title="Yearly Purchase Quantity Trend")
                st.plotly_chart(pur_qty_trend_chart, use_container_width=True, key="pur_qty_trend")

            # 2. Customer Segmentation (Onion method)
            with st.expander("👥 Customer Segmentation - Click to Drill Down"):
                if 'State' in df_purchase.columns and CURRENT_VALUE_COL in df_purchase.columns:
                    state_rev = px.bar(df_purchase.groupby('State')[CURRENT_VALUE_COL].sum().reset_index(), 
                                     x='State', y=CURRENT_VALUE_COL, title="State-wise Revenue")
                    st.plotly_chart(state_rev, key="pur_state_rev")
                    
                    # City drill-down
                    if 'City' in df_purchase.columns:
                        city_rev = px.bar(df_purchase.groupby(['State','City'])[CURRENT_VALUE_COL].sum().reset_index(), 
                                        x='City', y=CURRENT_VALUE_COL, color='State', title="City-wise Revenue")
                        st.plotly_chart(city_rev, key="pur_city_rev")

            # 3. Non-Moving Items
            with st.expander("📦 Non-Moving & Slow-Moving Items"):
                product_col = 'Product' if 'Product' in df_purchase.columns else ('Product Code' if 'Product Code' in df_purchase.columns else None)
                if CURRENT_QTY_COL in df_purchase.columns and product_col and CURRENT_VALUE_COL in df_purchase.columns:
                    months_back = st.slider("Last X months", 1, 12, 3, key="pur_slow_slider")
                    slow_items = df_purchase[df_purchase[CURRENT_QTY_COL] < df_purchase[CURRENT_QTY_COL].mean() * 0.2]
                    st.dataframe(slow_items[[product_col, CURRENT_QTY_COL, CURRENT_VALUE_COL]].rename(columns={CURRENT_QTY_COL: 'Quantity', CURRENT_VALUE_COL: 'Revenue'}))
                else:
                    st.write("Required columns not found in the data.")

            # 4. Cross-Selling Opportunities
            with st.expander("🔗 Cross-Selling Analysis"):
                if 'Product' in df_purchase.columns or 'Product Code' in df_purchase.columns:
                    prod_col = 'Product' if 'Product' in df_purchase.columns else 'Product Code'
                    top_products = df_purchase[prod_col].value_counts().head(5).index.tolist()
                    st.write(f"Top products: {', '.join(top_products)}")
                    # Add product mix table here
                else:
                    st.write("Required column ('Product' or 'Product Code') not found in the data.")

            # Sidebar filters
            st.sidebar.header("Filters")
            date_range = st.sidebar.date_input("Date Range", [])
            
            # Dealer Ranking
            if 'Dealer' in df_purchase.columns and CURRENT_VALUE_COL in df_purchase.columns:
                dealer_rank = df_purchase.groupby('Dealer')[CURRENT_VALUE_COL].sum().sort_values(ascending=False).reset_index()
                st.subheader("Dealer Ranking")
                st.dataframe(dealer_rank)
            
            # Predictive Alerts
            st.header("🚨 Predictive & Automated Alerts")
            if CURRENT_QTY_COL in df_purchase.columns and 'Month' in df_purchase.columns:
                # Simple forecasting: linear trend
                monthly_qty = df_purchase.groupby('Month')[CURRENT_QTY_COL].sum().reset_index()
                if len(monthly_qty) > 1:
                    from sklearn.linear_model import LinearRegression
                    X = np.array(range(len(monthly_qty))).reshape(-1, 1)
                    y = monthly_qty[CURRENT_QTY_COL].values
                    model = LinearRegression().fit(X, y)
                    next_month = model.predict([[len(monthly_qty)]])[0]
                    st.write(f"Predicted quantity for next month: {next_month:.2f}")
                    
                    # Alert for low inventory (assuming stock column)
                    if 'Stock' in df_purchase.columns:
                        low_stock = df_purchase[df_purchase['Stock'] < df_purchase['Stock'].mean() * 0.5]
                        if not low_stock.empty:
                            st.warning("Low stock items:")
                            st.dataframe(low_stock[['Product', 'Stock']])
            else:
                st.write("Required columns for predictive alerts not found.")
    
    with tabs[2]:
        if not df_sales.empty:
            
            # Customer Segmentation
            st.header("👥 Customer Segmentation")
            with st.expander("Drill-Down Analysis"):
                if 'state' in df_sales.columns and CURRENT_VALUE_COL in df_sales.columns:
                    state_rev = px.bar(df_sales.groupby('state')[CURRENT_VALUE_COL].sum().reset_index(), 
                                     x='state', y=CURRENT_VALUE_COL, title="State-wise Revenue")
                    st.plotly_chart(state_rev, key="ci_state_rev")
                    
                    # City drill-down
                    if 'city' in df_sales.columns:
                        city_rev = px.bar(df_sales.groupby(['state','city'])[CURRENT_VALUE_COL].sum().reset_index(), 
                                        x='city', y=CURRENT_VALUE_COL, color='state', title="City-wise Revenue")
                        st.plotly_chart(city_rev, key="ci_city_rev")
                    
                    # Executive drill-down
                    if 'executive' in df_sales.columns:
                        exec_rev = px.bar(df_sales.groupby('executive')[CURRENT_VALUE_COL].sum().reset_index(), 
                                        x='executive', y=CURRENT_VALUE_COL, title="Executive-wise Revenue")
                        st.plotly_chart(exec_rev, key="ci_exec_rev")
            
            # Non-Moving/Slow-Moving Items
            st.header("📦 Non-Moving & Slow-Moving Items")
            if 'Qty\n2024-25' in df_sales.columns and 'Product Code' in df_sales.columns and 'Value\n2024-25' in df_sales.columns:
                months_back = st.slider("Filter by last X months", 1, 12, 3, key="slow_slider")
                # Assuming 'date' column for filtering
                if 'date' in df_sales.columns:
                    df_sales['date'] = pd.to_datetime(df_sales['date'])
                    recent = df_sales[df_sales['date'] > pd.Timestamp.now() - pd.DateOffset(months=months_back)]
                    slow_items = recent[recent[CURRENT_QTY_COL] < recent[CURRENT_QTY_COL].mean() * 0.2]
                else:
                    slow_items = df_sales[df_sales[CURRENT_QTY_COL] < df_sales[CURRENT_QTY_COL].mean() * 0.2]
                st.dataframe(slow_items[['Product Code', CURRENT_QTY_COL, CURRENT_VALUE_COL]].rename(columns={CURRENT_QTY_COL: 'Quantity', CURRENT_VALUE_COL: 'Revenue'}))
            else:
                st.write("Required columns not found.")
            
            # Cross-Selling Opportunities
            st.header("🔗 Cross-Selling Analysis")
            if 'Product Code' in df_sales.columns:
                customer_products = df_sales.groupby('CustID')['Product Code'].apply(list).reset_index()
                # Simple logic: find customers who bought A but not B, etc.
                st.write("Top product combinations:")
                # Placeholder for more advanced analysis
                top_prods = df_sales['Product Code'].value_counts().head(5)
                st.bar_chart(top_prods)
            else:
                st.write("Product data needed.")
            
            # Product Drop-Off Tracker
            st.header("📉 Product Drop-Off Tracker")
            if 'month' in df_sales.columns and 'Product Code' in df_sales.columns and 'Qty\n2024-25' in df_sales.columns:
                monthly_sales = df_sales.groupby(['month', 'Product Code'])['Qty\n2024-25'].sum().unstack().fillna(0)
                drop_off = monthly_sales.pct_change().iloc[-1].sort_values()
                st.write("Products with highest drop-off:")
                st.dataframe(drop_off.head(10).reset_index())
            else:
                st.write("Month, product, quantity columns needed.")
        else:
            st.write("No sales data for customer insights.")
    
    with tabs[3]:
        if not df_payment.empty:
            
            # Get available years
            available_value_years = get_available_years(df_payment, 'Value\n')
            available_qty_years = get_available_years(df_payment, 'Qty\n')
            
            # 1. Payment Insights
            st.header("💳 Payment Insights")
            if CURRENT_VALUE_COL in df_payment.columns and 'Company' in df_payment.columns:
                col1, col2, col3 = st.columns(3)
                with col1:
                    pay_pie = px.pie(df_payment, values=CURRENT_VALUE_COL, names='Company', title="Payment Value by Company")
                    st.plotly_chart(pay_pie, use_container_width=True, key="pay_rev_pie")
                with col2:
                    if CURRENT_QTY_COL in df_payment.columns:
                        pay_qty_pie = px.pie(df_payment, values=CURRENT_QTY_COL, names='Company', title="Payment Quantity by Company")
                        st.plotly_chart(pay_qty_pie, use_container_width=True, key="pay_qty_pie")
                with col3:
                    # Year-wise trend
                    if available_value_years:
                        yearly_payment = [df_payment[f'Value\n{year}'].sum() for year in available_value_years]
                        pay_trend_df = pd.DataFrame({'Year': available_value_years, 'Payment Value': yearly_payment})
                        pay_trend_chart = px.line(pay_trend_df, x='Year', y='Payment Value', title="Yearly Payment Trend")
                        st.plotly_chart(pay_trend_chart, use_container_width=True, key="pay_yearly_trend")
            
            # Additional: By State and Category
            if CURRENT_VALUE_COL in df_payment.columns:
                if 'State' in df_payment.columns:
                    pay_state_pie = px.pie(df_payment, values=CURRENT_VALUE_COL, names='State', title="Payment by State")
                    st.plotly_chart(pay_state_pie, use_container_width=True, key="pay_state_pie")
                if 'Category' in df_payment.columns:
                    pay_cat_pie = px.pie(df_payment, values=CURRENT_VALUE_COL, names='Category', title="Payment by Category")
                    st.plotly_chart(pay_cat_pie, use_container_width=True, key="pay_cat_pie")
            
            # Comparison by Sub Category
            if 'Sub Category' in df_payment.columns and CURRENT_VALUE_COL in df_payment.columns:
                pay_sub_cat_bar = px.bar(df_payment.groupby('Sub Category')[CURRENT_VALUE_COL].sum().reset_index(), 
                                       x='Sub Category', y=CURRENT_VALUE_COL, title="Payment by Sub Category")
                st.plotly_chart(pay_sub_cat_bar, use_container_width=True, key="pay_sub_cat_bar")
            
            # Year-wise Quantity Trend
            if available_qty_years:
                yearly_pay_qty = [df_payment[f'Qty\n{year}'].sum() for year in available_qty_years]
                pay_qty_trend_df = pd.DataFrame({'Year': available_qty_years, 'Payment Quantity': yearly_pay_qty})
                pay_qty_trend_chart = px.line(pay_qty_trend_df, x='Year', y='Payment Quantity', title="Yearly Payment Quantity Trend")
                st.plotly_chart(pay_qty_trend_chart, use_container_width=True, key="pay_qty_trend")

            # 2. Customer Segmentation (Onion method)
            with st.expander("👥 Customer Segmentation - Click to Drill Down"):
                if 'State' in df_payment.columns and CURRENT_VALUE_COL in df_payment.columns:
                    state_rev = px.bar(df_payment.groupby('State')[CURRENT_VALUE_COL].sum().reset_index(), 
                                     x='State', y=CURRENT_VALUE_COL, title="State-wise Revenue")
                    st.plotly_chart(state_rev, key="pay_state_rev")
                    
                    # City drill-down
                    if 'City' in df_payment.columns:
                        city_rev = px.bar(df_payment.groupby(['State','City'])[CURRENT_VALUE_COL].sum().reset_index(), 
                                        x='City', y=CURRENT_VALUE_COL, color='State', title="City-wise Revenue")
                        st.plotly_chart(city_rev, key="pay_city_rev")

            # 3. Non-Moving Items
            with st.expander("📦 Non-Moving & Slow-Moving Items"):
                product_col = 'Product' if 'Product' in df_payment.columns else ('Product Code' if 'Product Code' in df_payment.columns else None)
                if CURRENT_QTY_COL in df_payment.columns and product_col and CURRENT_VALUE_COL in df_payment.columns:
                    months_back = st.slider("Last X months", 1, 12, 3, key="pay_slow_slider")
                    slow_items = df_payment[df_payment[CURRENT_QTY_COL] < df_payment[CURRENT_QTY_COL].mean() * 0.2]
                    st.dataframe(slow_items[[product_col, CURRENT_QTY_COL, CURRENT_VALUE_COL]].rename(columns={CURRENT_QTY_COL: 'Quantity', CURRENT_VALUE_COL: 'Revenue'}))
                else:
                    st.write("Required columns not found in the data.")

            # 4. Cross-Selling Opportunities
            with st.expander("🔗 Cross-Selling Analysis"):
                if 'Product' in df_payment.columns or 'Product Code' in df_payment.columns:
                    prod_col = 'Product' if 'Product' in df_payment.columns else 'Product Code'
                    top_products = df_payment[prod_col].value_counts().head(5).index.tolist()
                    st.write(f"Top products: {', '.join(top_products)}")
                    # Add product mix table here
                else:
                    st.write("Required column ('Product' or 'Product Code') not found in the data.")

            # Sidebar filters
            st.sidebar.header("Filters")
            date_range = st.sidebar.date_input("Date Range", [])
            
            # Dealer Ranking
            if 'Dealer' in df_payment.columns and CURRENT_VALUE_COL in df_payment.columns:
                dealer_rank = df_payment.groupby('Dealer')[CURRENT_VALUE_COL].sum().sort_values(ascending=False).reset_index()
                st.subheader("Dealer Ranking")
                st.dataframe(dealer_rank)
            
            # Predictive Alerts
            st.header("🚨 Predictive & Automated Alerts")
            if CURRENT_QTY_COL in df_payment.columns and 'Month' in df_payment.columns:
                # Simple forecasting: linear trend
                monthly_qty = df_payment.groupby('Month')[CURRENT_QTY_COL].sum().reset_index()
                if len(monthly_qty) > 1:
                    from sklearn.linear_model import LinearRegression
                    X = np.array(range(len(monthly_qty))).reshape(-1, 1)
                    y = monthly_qty[CURRENT_QTY_COL].values
                    model = LinearRegression().fit(X, y)
                    next_month = model.predict([[len(monthly_qty)]])[0]
                    st.write(f"Predicted quantity for next month: {next_month:.2f}")
                    
                    # Alert for low inventory (assuming stock column)
                    if 'Stock' in df_payment.columns:
                        low_stock = df_payment[df_payment['Stock'] < df_payment['Stock'].mean() * 0.5]
                        if not low_stock.empty:
                            st.warning("Low stock items:")
                            st.dataframe(low_stock[['Product', 'Stock']])
        else:
            st.write("No payment data found.")
else:
    st.info("Please upload a combined Excel file to get started. Make sure it has a 'Type' column with values: 'Sales', 'Purchase', 'Payment'.")
