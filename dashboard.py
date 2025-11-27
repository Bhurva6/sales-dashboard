import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

st.set_page_config(layout="wide", page_title="Business Analytics Dashboard")

st.title("Business Analytics Dashboard")
st.markdown("Upload a combined Excel file with all data (add a 'Type' column: 'Sales', 'Purchase', 'Payment').")

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
        df_purchase = df[df['purchase_amount'].notna()] if 'purchase_amount' in df.columns else pd.DataFrame()
        df_payment = df[df['due_date'].notna()] if 'due_date' in df.columns else pd.DataFrame()
    
    tabs = st.tabs(["Sales Analytics", "Purchase Analytics", "Customer Insights", "Payment Analysis"])
    
    with tabs[0]:
        if not df_sales.empty:
            st.success(f"Sales data: {len(df_sales)} rows")
            
            # 1. Revenue & Quantity Insights
            st.header("💰 Revenue & Quantity Insights")
            if 'Revenue' in df_sales.columns and 'Dealer' in df_sales.columns:
                col1, col2, col3 = st.columns(3)
                with col1:
                    rev_pie = px.pie(df_sales, values='Revenue', names='Dealer', title="Revenue by Dealer")
                    st.plotly_chart(rev_pie, use_container_width=True)
                with col2:
                    if 'Quantity' in df_sales.columns:
                        qty_pie = px.pie(df_sales, values='Quantity', names='Dealer', title="Quantity by Dealer")
                        st.plotly_chart(qty_pie, use_container_width=True)
                with col3:
                    if 'Month' in df_sales.columns:
                        trend = px.line(df_sales.groupby('Month')['Revenue'].sum().reset_index(), 
                                      x='Month', y='Revenue', title="Monthly Revenue Trend")
                        st.plotly_chart(trend, use_container_width=True)
            
            # Additional: By State and Executive
            if 'Revenue' in df_sales.columns:
                if 'State' in df_sales.columns:
                    state_pie = px.pie(df_sales, values='Revenue', names='State', title="Revenue by State")
                    st.plotly_chart(state_pie, use_container_width=True)
                if 'Executive' in df_sales.columns:
                    exec_pie = px.pie(df_sales, values='Revenue', names='Executive', title="Revenue by Executive")
                    st.plotly_chart(exec_pie, use_container_width=True)
            
            # Comparison by Product Categories
            if 'Product Family' in df_sales.columns and 'Revenue' in df_sales.columns:
                cat_bar = px.bar(df_sales.groupby('Product Family')['Revenue'].sum().reset_index(), 
                               x='Product Family', y='Revenue', title="Revenue by Product Family")
                st.plotly_chart(cat_bar, use_container_width=True)
            
            # Month-wise Quantity Trend
            if 'Month' in df_sales.columns and 'Quantity' in df_sales.columns:
                qty_trend = px.line(df_sales.groupby('Month')['Quantity'].sum().reset_index(), 
                                  x='Month', y='Quantity', title="Monthly Quantity Trend")
                st.plotly_chart(qty_trend, use_container_width=True)

            # 2. Customer Segmentation (Onion method)
            with st.expander("👥 Customer Segmentation - Click to Drill Down"):
                if 'State' in df_sales.columns and 'Revenue' in df_sales.columns:
                    state_rev = px.bar(df_sales.groupby('State')['Revenue'].sum().reset_index(), 
                                     x='State', y='Revenue', title="State-wise Revenue")
                    st.plotly_chart(state_rev)
                    
                    # City drill-down
                    if 'City' in df_sales.columns:
                        city_rev = px.bar(df_sales.groupby(['State','City'])['Revenue'].sum().reset_index(), 
                                        x='City', y='Revenue', color='State', title="City-wise Revenue")
                        st.plotly_chart(city_rev)

            # 3. Non-Moving Items
            with st.expander("📦 Non-Moving & Slow-Moving Items"):
                if 'Quantity' in df_sales.columns and 'Product' in df_sales.columns and 'Revenue' in df_sales.columns:
                    months_back = st.slider("Last X months", 1, 12, 3)
                    slow_items = df_sales[df_sales['Quantity'] < df_sales['Quantity'].mean() * 0.2]
                    st.dataframe(slow_items[['Product', 'Quantity', 'Revenue']])
                else:
                    st.write("Required columns ('Quantity', 'Product', 'Revenue') not found in the data.")

            # 4. Cross-Selling Opportunities
            with st.expander("🔗 Cross-Selling Analysis"):
                if 'Product' in df_sales.columns:
                    top_products = df_sales['Product'].value_counts().head(5).index.tolist()
                    st.write(f"Top products: {', '.join(top_products)}")
                    # Add product mix table here
                else:
                    st.write("Required column ('Product') not found in the data.")

            # Sidebar filters
            st.sidebar.header("Filters")
            date_range = st.sidebar.date_input("Date Range", [])
            
            # Dealer Ranking
            if 'Dealer' in df_sales.columns and 'Revenue' in df_sales.columns:
                dealer_rank = df_sales.groupby('Dealer')['Revenue'].sum().sort_values(ascending=False).reset_index()
                st.subheader("Dealer Ranking")
                st.dataframe(dealer_rank)
            
            # Predictive Alerts
            st.header("🚨 Predictive & Automated Alerts")
            if 'Quantity' in df_sales.columns and 'Month' in df_sales.columns:
                # Simple forecasting: linear trend
                monthly_qty = df_sales.groupby('Month')['Quantity'].sum().reset_index()
                if len(monthly_qty) > 1:
                    from sklearn.linear_model import LinearRegression
                    X = np.array(range(len(monthly_qty))).reshape(-1, 1)
                    y = monthly_qty['Quantity'].values
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
            st.write("No sales data found.")
    
    with tabs[1]:
        if not df_purchase.empty:
            # Mirror Sales Analytics for Purchases
            st.header("🛒 Purchase Analytics")
            if 'purchase_amount' in df_purchase.columns and 'vendor' in df_purchase.columns:
                col1, col2, col3 = st.columns(3)
                with col1:
                    pur_pie = px.pie(df_purchase, values='purchase_amount', names='vendor', title="Purchase Amount by Vendor")
                    st.plotly_chart(pur_pie, use_container_width=True)
                with col2:
                    if 'quantity' in df_purchase.columns:
                        qty_pie = px.pie(df_purchase, values='quantity', names='vendor', title="Quantity by Vendor")
                        st.plotly_chart(qty_pie, use_container_width=True)
                with col3:
                    if 'month' in df_purchase.columns:
                        trend = px.line(df_purchase.groupby('month')['purchase_amount'].sum().reset_index(), 
                                      x='month', y='purchase_amount', title="Monthly Purchase Trend")
                        st.plotly_chart(trend, use_container_width=True)
            
            # Additional for Purchases
            if 'material' in df_purchase.columns and 'purchase_amount' in df_purchase.columns:
                mat_bar = px.bar(df_purchase.groupby('material')['purchase_amount'].sum().reset_index(), 
                               x='material', y='purchase_amount', title="Purchase by Material")
                st.plotly_chart(mat_bar, use_container_width=True)
            
            # Non-moving purchases
            if 'quantity' in df_purchase.columns and 'material' in df_purchase.columns:
                slow_purchases = df_purchase[df_purchase['quantity'] < df_purchase['quantity'].mean() * 0.2]
                st.subheader("Slow-Moving Purchases")
                st.dataframe(slow_purchases[['material', 'quantity', 'purchase_amount']])
        else:
            st.write("No purchase data found.")
    
    with tabs[2]:
        if not df_sales.empty:
            
            # Customer Segmentation
            st.header("👥 Customer Segmentation")
            with st.expander("Drill-Down Analysis"):
                if 'state' in df_sales.columns and 'revenue' in df_sales.columns:
                    state_rev = px.bar(df_sales.groupby('state')['revenue'].sum().reset_index(), 
                                     x='state', y='revenue', title="State-wise Revenue")
                    st.plotly_chart(state_rev)
                    
                    # City drill-down
                    if 'city' in df_sales.columns:
                        city_rev = px.bar(df_sales.groupby(['state','city'])['revenue'].sum().reset_index(), 
                                        x='city', y='revenue', color='state', title="City-wise Revenue")
                        st.plotly_chart(city_rev)
                    
                    # Executive drill-down
                    if 'executive' in df_sales.columns:
                        exec_rev = px.bar(df_sales.groupby('executive')['revenue'].sum().reset_index(), 
                                        x='executive', y='revenue', title="Executive-wise Revenue")
                        st.plotly_chart(exec_rev)
            
            # Non-Moving/Slow-Moving Items
            st.header("📦 Non-Moving & Slow-Moving Items")
            if 'quantity' in df_sales.columns and 'product' in df_sales.columns and 'revenue' in df_sales.columns:
                months_back = st.slider("Filter by last X months", 1, 12, 3, key="slow_slider")
                # Assuming 'date' column for filtering
                if 'date' in df_sales.columns:
                    df_sales['date'] = pd.to_datetime(df_sales['date'])
                    recent = df_sales[df_sales['date'] > pd.Timestamp.now() - pd.DateOffset(months=months_back)]
                    slow_items = recent[recent['quantity'] < recent['quantity'].mean() * 0.2]
                else:
                    slow_items = df_sales[df_sales['quantity'] < df_sales['quantity'].mean() * 0.2]
                st.dataframe(slow_items[['product', 'quantity', 'revenue']])
            else:
                st.write("Required columns not found.")
            
            # Cross-Selling Opportunities
            st.header("🔗 Cross-Selling Analysis")
            if 'customer' in df_sales.columns and 'product' in df_sales.columns:
                customer_products = df_sales.groupby('customer')['product'].apply(list).reset_index()
                # Simple logic: find customers who bought A but not B, etc.
                st.write("Top product combinations:")
                # Placeholder for more advanced analysis
                top_prods = df_sales['product'].value_counts().head(5)
                st.bar_chart(top_prods)
            else:
                st.write("Customer and product data needed.")
            
            # Product Drop-Off Tracker
            st.header("📉 Product Drop-Off Tracker")
            if 'month' in df_sales.columns and 'product' in df_sales.columns and 'quantity' in df_sales.columns:
                monthly_sales = df_sales.groupby(['month', 'product'])['quantity'].sum().unstack().fillna(0)
                drop_off = monthly_sales.pct_change().iloc[-1].sort_values()
                st.write("Products with highest drop-off:")
                st.dataframe(drop_off.head(10).reset_index())
            else:
                st.write("Month, product, quantity columns needed.")
        else:
            st.write("No sales data for customer insights.")
    
    with tabs[3]:
        if not df_payment.empty:
            st.header("💳 Payment & Credit Analysis")
            
            # Overdue Analysis
            if 'due_date' in df_payment.columns and 'amount' in df_payment.columns:
                df_payment['due_date'] = pd.to_datetime(df_payment['due_date'])
                overdue = df_payment[df_payment['due_date'] < pd.Timestamp.now()]
                st.subheader("Overdue Payments")
                st.dataframe(overdue[['customer', 'amount', 'due_date']])
                
                # Aging Buckets
                today = pd.Timestamp.now()
                df_payment['days_overdue'] = (today - df_payment['due_date']).dt.days
                bins = [0, 30, 60, 90, 120, np.inf]
                labels = ['0-30 days', '31-60 days', '61-90 days', '91-120 days', '120+ days']
                df_payment['aging_bucket'] = pd.cut(df_payment['days_overdue'], bins=bins, labels=labels)
                aging_summary = df_payment.groupby('aging_bucket')['amount'].sum().reset_index()
                aging_chart = px.bar(aging_summary, x='aging_bucket', y='amount', title="Aging Analysis")
                st.plotly_chart(aging_chart)
            
            # Interest Calculation (simple)
            if 'days_overdue' in df_payment.columns and 'amount' in df_payment.columns:
                interest_rate = st.slider("Interest Rate (%)", 0.0, 10.0, 2.0)
                df_payment['interest'] = df_payment['amount'] * (interest_rate / 100) * (df_payment['days_overdue'] / 365)
                st.subheader("Interest on Overdue")
                st.dataframe(df_payment[['customer', 'amount', 'interest']])
        else:
            st.write("No payment data found.")
else:
    st.info("Please upload a combined Excel file to get started. Make sure it has a 'Type' column with values: 'Sales', 'Purchase', 'Payment'.")
