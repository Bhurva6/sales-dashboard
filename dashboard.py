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

# Utility function for Indian currency formatting
def format_inr(value):
    if value >= 1e7:
        return f"₹{value/1e7:.2f} Cr"
    elif value >= 1e5:
        return f"₹{value/1e5:.2f} Lakh"
    else:
        return f"₹{value:,.0f}"

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

st.markdown('<p class="main-header">Orthopedic Implant Analytics Dashboard</p>', unsafe_allow_html=True)
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
                    rev_pie = px.pie(df_sales, values=CURRENT_VALUE_COL, names='Company', title="Revenue by Company",
                                    hover_data=[df_sales[CURRENT_VALUE_COL].apply(format_inr)])
                    rev_pie.update_traces(textinfo='label+percent', hovertemplate='%{label}: %{value} (%{percent})<br>Value: %{customdata[0]}')
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
                        trend_df['Revenue (INR)'] = trend_df['Revenue'].apply(format_inr)
                        trend_chart = px.line(trend_df, x='Year', y='Revenue', title="Yearly Revenue Trend",
                                             hover_data=['Revenue (INR)'])
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
                # Get all available subcategories
                all_sub_cats = df_sales['Sub Category'].unique().tolist()
                # Add dropdown for subcategory selection
                selected_sub_cats = st.multiselect(
                    "Select Sub Categories to Display:",
                    options=all_sub_cats,
                    default=all_sub_cats,
                    key="sales_sub_cat_filter"
                )
                
                if selected_sub_cats:
                    # Filter data based on selected subcategories
                    filtered_data = df_sales[df_sales['Sub Category'].isin(selected_sub_cats)]
                    sub_cat_data = filtered_data.groupby('Sub Category')[CURRENT_VALUE_COL].sum().reset_index()
                    
                    sub_cat_bar = px.bar(sub_cat_data, 
                                       x='Sub Category', y=CURRENT_VALUE_COL, title="Revenue by Sub Category",
                                       hover_data=[sub_cat_data[CURRENT_VALUE_COL].apply(format_inr)])
                    sub_cat_bar.update_traces(hovertemplate='%{x}: %{y}<br>Value: %{customdata[0]}')
                    st.plotly_chart(sub_cat_bar, use_container_width=True, key="sales_sub_cat_bar")
                else:
                    st.write("Please select at least one subcategory to display the chart.")
            
            # Year-wise Quantity Trend
            if available_qty_years:
                yearly_qty = [df_sales[f'Qty\n{year}'].sum() for year in available_qty_years]
                qty_trend_df = pd.DataFrame({'Year': available_qty_years, 'Quantity': yearly_qty})
                qty_trend_df['Quantity (INR)'] = qty_trend_df['Quantity'].apply(format_inr)
                qty_trend_chart = px.line(qty_trend_df, x='Year', y='Quantity', title="Yearly Quantity Trend",
                                     hover_data=['Quantity (INR)'])
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
                    st.metric("Predicted Sales for Next Year", format_inr(predicted_all[-1]))
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
            
        else:
            st.write("No sales data found.")
    
    with tabs[1]:
        if not df_purchase.empty:
            st.success(f"Purchase data: {len(df_purchase)} rows")
            
            # Key Metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                total_value = df_purchase[CURRENT_VALUE_COL].sum() if CURRENT_VALUE_COL in df_purchase.columns else 0
                st.metric("Total Purchase Value", format_inr(total_value))
            with col2:
                total_qty = df_purchase[CURRENT_QTY_COL].sum() if CURRENT_QTY_COL in df_purchase.columns else 0
                st.metric("Total Purchase Quantity", f"{total_qty:,.0f}")
            with col3:
                avg_value = df_purchase[CURRENT_VALUE_COL].mean() if CURRENT_VALUE_COL in df_purchase.columns else 0
                st.metric("Avg Purchase Value", format_inr(avg_value))
            with col4:
                num_companies = df_purchase['Company'].nunique() if 'Company' in df_purchase.columns else 0
                st.metric("Number of Companies", num_companies)
            
            # Get available years
            available_value_years = get_available_years(df_purchase, 'Value\n')
            available_qty_years = get_available_years(df_purchase, 'Qty\n')
            
            sub_tabs = st.tabs(["Overview", "Forecasting", "Trends", "Segmentation", "Inventory Management", "Cross-Selling"])
            with sub_tabs[0]:
                st.header("🛒 Purchase Insights")
                if CURRENT_VALUE_COL in df_purchase.columns and 'Company' in df_purchase.columns:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        pur_pie = px.pie(df_purchase, values=CURRENT_VALUE_COL, names='Company', title="Purchase Value by Company",
                                        hover_data=[df_purchase[CURRENT_VALUE_COL].apply(format_inr)])
                        pur_pie.update_traces(textinfo='label+percent', hovertemplate='%{label}: %{value} (%{percent})<br>Value: %{customdata[0]}')
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
                            pur_trend_df['Purchase Value (INR)'] = pur_trend_df['Purchase Value'].apply(format_inr)
                            pur_trend_chart = px.line(pur_trend_df, x='Year', y='Purchase Value', title="Yearly Purchase Trend",
                                                      hover_data=['Purchase Value (INR)'])
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
                    # Get all available subcategories
                    all_sub_cats = df_purchase['Sub Category'].unique().tolist()
                    # Add dropdown for subcategory selection
                    selected_sub_cats = st.multiselect(
                        "Select Sub Categories to Display:",
                        options=all_sub_cats,
                        default=all_sub_cats,
                        key="purchase_sub_cat_filter"
                    )
                    
                    if selected_sub_cats:
                        # Filter data based on selected subcategories
                        filtered_data = df_purchase[df_purchase['Sub Category'].isin(selected_sub_cats)]
                        sub_cat_data = filtered_data.groupby('Sub Category')[CURRENT_VALUE_COL].sum().reset_index()
                        
                        pur_sub_cat_bar = px.bar(sub_cat_data, 
                                               x='Sub Category', y=CURRENT_VALUE_COL, title="Purchase by Sub Category",
                                               hover_data=[sub_cat_data[CURRENT_VALUE_COL].apply(format_inr)])
                        pur_sub_cat_bar.update_traces(hovertemplate='%{x}: %{y}<br>Value: %{customdata[0]}')
                        st.plotly_chart(pur_sub_cat_bar, use_container_width=True, key="pur_sub_cat_bar")
                    else:
                        st.write("Please select at least one subcategory to display the chart.")
                
                # Year-wise Quantity Trend
                if available_qty_years:
                    yearly_pur_qty = [df_purchase[f'Qty\n{year}'].sum() for year in available_qty_years]
                    pur_qty_trend_df = pd.DataFrame({'Year': available_qty_years, 'Purchase Quantity': yearly_pur_qty})
                    pur_qty_trend_chart = px.line(pur_qty_trend_df, x='Year', y='Purchase Quantity', title="Yearly Purchase Quantity Trend")
                    st.plotly_chart(pur_qty_trend_chart, use_container_width=True, key="pur_qty_trend")
            with sub_tabs[1]:
                st.header("🔮 Purchase Forecasting")
                if available_value_years and len(available_value_years) > 1:
                    yearly_purchases = [df_purchase[f'Value\n{year}'].sum() for year in available_value_years]
                    
                    # Simple linear regression for forecasting
                    X = np.array(range(len(available_value_years))).reshape(-1, 1)
                    y = yearly_purchases
                    model = LinearRegression()
                    model.fit(X, y)
                    
                    # Predict for all years including next
                    X_all = np.array(range(len(available_value_years) + 1)).reshape(-1, 1)
                    predicted_all = model.predict(X_all)
                    
                    forecast_df = pd.DataFrame({
                        'Year': list(range(len(available_value_years))) + [len(available_value_years)],
                        'Purchases': yearly_purchases + [np.nan],
                        'Predicted': predicted_all
                    })
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Predicted Purchases for Next Year", format_inr(predicted_all[-1]))
                    with col2:
                        forecast_chart = px.line(forecast_df, x='Year', y=['Purchases', 'Predicted'], title="Purchase Forecast")
                        st.plotly_chart(forecast_chart, use_container_width=True, key="pur_forecast")
            with sub_tabs[2]:
                st.header("📈 Trend Analysis")
                if available_value_years and 'Category' in df_purchase.columns:
                    trend_data = {'Year': available_value_years}
                    for cat in df_purchase['Category'].unique():
                        trend_data[cat] = [df_purchase[df_purchase['Category'] == cat][f'Value\n{year}'].sum() for year in available_value_years]
                    trend_df = pd.DataFrame(trend_data)
                    trend_chart = px.line(trend_df, x='Year', y=trend_df.columns[1:], title="Category-wise Purchase Trend")
                    st.plotly_chart(trend_chart, use_container_width=True, key="pur_cat_trend")
            with sub_tabs[3]:
                st.header("👥 Customer Segmentation")
                with st.expander("Click to Drill Down"):
                    if 'State' in df_purchase.columns and CURRENT_VALUE_COL in df_purchase.columns:
                        state_rev = px.bar(df_purchase.groupby('State')[CURRENT_VALUE_COL].sum().reset_index(), 
                                         x='State', y=CURRENT_VALUE_COL, title="State-wise Purchase Value")
                        st.plotly_chart(state_rev, key="pur_state_rev")
                        
                        # City drill-down
                        if 'City' in df_purchase.columns:
                            city_rev = px.bar(df_purchase.groupby(['State','City'])[CURRENT_VALUE_COL].sum().reset_index(), 
                                            x='City', y=CURRENT_VALUE_COL, color='State', title="City-wise Purchase Value")
                            st.plotly_chart(city_rev, key="pur_city_rev")
            with sub_tabs[4]:
                st.header("📦 Inventory Management")
                product_col = 'Product' if 'Product' in df_purchase.columns else ('Product Code' if 'Product Code' in df_purchase.columns else None)
                if CURRENT_QTY_COL in df_purchase.columns and product_col and CURRENT_VALUE_COL in df_purchase.columns:
                    months_back = st.slider("Last X months", 1, 12, 3, key="pur_slow_slider")
                    slow_items = df_purchase[df_purchase[CURRENT_QTY_COL] < df_purchase[CURRENT_QTY_COL].mean() * 0.2]
                    st.dataframe(slow_items[[product_col, CURRENT_QTY_COL, CURRENT_VALUE_COL]].rename(columns={CURRENT_QTY_COL: 'Quantity', CURRENT_VALUE_COL: 'Value'}))
                else:
                    st.write("Required columns not found in the data.")
            with sub_tabs[5]:
                st.header("🔗 Cross-Selling Opportunities")
                if 'Product' in df_purchase.columns or 'Product Code' in df_purchase.columns:
                    prod_col = 'Product' if 'Product' in df_purchase.columns else 'Product Code'
                    top_products = df_purchase[prod_col].value_counts().head(5).index.tolist()
                    st.write(f"Top products: {', '.join(top_products)}")
                    # Add product mix table here
                else:
                    st.write("Required column ('Product' or 'Product Code') not found in the data.")
    
    with tabs[2]:
        if not df_sales.empty:
            
            # Customer Segmentation
            st.header("👥 Customer Segmentation")
            with st.expander("Drill-Down Analysis"):
                if 'state' in df_sales.columns and CURRENT_VALUE_COL in df_sales.columns:
                    # Create columns for better layout
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # State-wise Revenue
                        state_rev = px.bar(df_sales.groupby('state')[CURRENT_VALUE_COL].sum().reset_index().sort_values(CURRENT_VALUE_COL, ascending=False), 
                                         x='state', y=CURRENT_VALUE_COL, title="State-wise Revenue",
                                         color=CURRENT_VALUE_COL, color_continuous_scale='Blues')
                        st.plotly_chart(state_rev, key="ci_state_rev", use_container_width=True)
                        
                        # Customer Count by State
                        state_count = df_sales.groupby('state').size().reset_index(name='Customer Count').sort_values('Customer Count', ascending=False)
                        state_count_chart = px.bar(state_count, x='state', y='Customer Count', 
                                                 title="Customer Count by State", color='Customer Count', 
                                                 color_continuous_scale='Greens')
                        st.plotly_chart(state_count_chart, key="ci_state_count", use_container_width=True)
                    
                    with col2:
                        # Revenue Distribution Pie Chart
                        state_rev_pie = px.pie(df_sales.groupby('state')[CURRENT_VALUE_COL].sum().reset_index().sort_values(CURRENT_VALUE_COL, ascending=False).head(10),
                                             values=CURRENT_VALUE_COL, names='state', title="Top 10 States by Revenue")
                        st.plotly_chart(state_rev_pie, key="ci_state_pie", use_container_width=True)
                        
                        # Average Revenue per Customer by State
                        state_avg = df_sales.groupby('state')[CURRENT_VALUE_COL].mean().reset_index(name='Avg Revenue per Customer').sort_values('Avg Revenue per Customer', ascending=False)
                        state_avg_chart = px.bar(state_avg, x='state', y='Avg Revenue per Customer',
                                               title="Average Revenue per Customer by State", 
                                               color='Avg Revenue per Customer', color_continuous_scale='Reds')
                        st.plotly_chart(state_avg_chart, key="ci_state_avg", use_container_width=True)
                    
                    # City drill-down (if available)
                    if 'city' in df_sales.columns:
                        st.subheader("📍 City-Level Analysis")
                        col3, col4 = st.columns(2)
                        
                        with col3:
                            # Top 10 Cities by Revenue
                            city_rev = px.bar(df_sales.groupby('city')[CURRENT_VALUE_COL].sum().reset_index().sort_values(CURRENT_VALUE_COL, ascending=False).head(10),
                                            x='city', y=CURRENT_VALUE_COL, title="Top 10 Cities by Revenue",
                                            color=CURRENT_VALUE_COL, color_continuous_scale='Purples')
                            st.plotly_chart(city_rev, key="ci_city_rev", use_container_width=True)
                        
                        with col4:
                            # City Revenue by State
                            city_state = df_sales.groupby(['state','city'])[CURRENT_VALUE_COL].sum().reset_index().sort_values(CURRENT_VALUE_COL, ascending=False).head(15)
                            city_state_chart = px.bar(city_state, x='city', y=CURRENT_VALUE_COL, color='state',
                                                    title="Top Cities Revenue by State", barmode='group')
                            st.plotly_chart(city_state_chart, key="ci_city_state", use_container_width=True)
                    
                    # Executive drill-down (if available)
                    if 'executive' in df_sales.columns:
                        st.subheader("👔 Executive Performance")
                        col5, col6 = st.columns(2)
                        
                        with col5:
                            exec_rev = px.bar(df_sales.groupby('executive')[CURRENT_VALUE_COL].sum().reset_index().sort_values(CURRENT_VALUE_COL, ascending=False),
                                            x='executive', y=CURRENT_VALUE_COL, title="Executive-wise Revenue",
                                            color=CURRENT_VALUE_COL, color_continuous_scale='Oranges')
                            st.plotly_chart(exec_rev, key="ci_exec_rev", use_container_width=True)
                        
                        with col6:
                            # Executive Customer Count
                            exec_count = df_sales.groupby('executive').size().reset_index(name='Customers').sort_values('Customers', ascending=False)
                            exec_count_chart = px.bar(exec_count, x='executive', y='Customers', 
                                                    title="Customers per Executive", color='Customers', 
                                                    color_continuous_scale='Teals')
                            st.plotly_chart(exec_count_chart, key="ci_exec_count", use_container_width=True)
                    
                    # Additional Insights
                    st.subheader("📊 Key Insights")
                    insight_col1, insight_col2, insight_col3 = st.columns(3)
                    
                    with insight_col1:
                        total_states = df_sales['state'].nunique()
                        st.metric("Total States", total_states)
                    
                    with insight_col2:
                        if 'city' in df_sales.columns:
                            total_cities = df_sales['city'].nunique()
                            st.metric("Total Cities", total_cities)
                        else:
                            st.metric("Cities Data", "Not Available")
                    
                    with insight_col3:
                        if 'executive' in df_sales.columns:
                            total_execs = df_sales['executive'].nunique()
                            st.metric("Total Executives", total_execs)
                        else:
                            st.metric("Executives Data", "Not Available")
                    
                    # Top Customers Analysis
                    if 'Company' in df_sales.columns:
                        st.subheader("🏆 Top Customers")
                        top_customers = df_sales.groupby('Company')[CURRENT_VALUE_COL].sum().reset_index().sort_values(CURRENT_VALUE_COL, ascending=False).head(10)
                        top_cust_chart = px.bar(top_customers, x='Company', y=CURRENT_VALUE_COL,
                                              title="Top 10 Customers by Revenue", 
                                              color=CURRENT_VALUE_COL, color_continuous_scale='Viridis')
                        st.plotly_chart(top_cust_chart, key="ci_top_customers", use_container_width=True)
                        
                        # Customer Segmentation by Revenue Tiers
                        customer_segments = df_sales.groupby('Company')[CURRENT_VALUE_COL].sum().reset_index()
                        customer_segments['Segment'] = pd.qcut(customer_segments[CURRENT_VALUE_COL], q=4, labels=['Bronze', 'Silver', 'Gold', 'Platinum'])
                        segment_chart = px.pie(customer_segments, values=CURRENT_VALUE_COL, names='Segment',
                                             title="Customer Segmentation by Revenue Tiers")
                        st.plotly_chart(segment_chart, key="ci_segments", use_container_width=True)
                else:
                    st.warning("Required columns ('state' and revenue column) not found for drill-down analysis.")
    
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
