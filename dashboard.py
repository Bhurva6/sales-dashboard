import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.linear_model import LinearRegression
from api_client import (
    init_session_state, 
    login_form, 
    logout_button, 
    fetch_dashboard_data,
    clear_cached_data
)

# Page configuration
st.set_page_config(page_title="Orthopedic Implant Analytics Dashboard", layout="wide")

# Initialize API session state
init_session_state()

# Check authentication - show login form if not authenticated
if not st.session_state.authenticated:
    login_form()
    st.stop()

# Load data from API
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data():
    df = fetch_dashboard_data()
    if df is not None:
        df.columns = df.columns.str.strip()
    return df

# Sidebar with logout and refresh options
with st.sidebar:
    st.title("Dashboard Controls")
    logout_button()
    st.markdown("---")
    if st.button(" Refresh Data", use_container_width=True):
        clear_cached_data()
        st.cache_data.clear()
        st.rerun()
    st.markdown("---")
    # Filter to hide "Innovative" dealers
    hide_innovative = st.checkbox("Hide 'Innovative Ortho Surgicals' Dealer", value=False, key="hide_innovative")
    st.markdown("---")
    st.caption("Data loaded from API")

df = load_data()

# Handle case when data couldn't be loaded
if df is None:
    st.error("Failed to load data from API. Please try again or contact support.")
    st.stop()

# Apply filter to hide "Innovative" dealers if checkbox is checked
if 'hide_innovative' in st.session_state and st.session_state.hide_innovative:
    if 'Dealer Name' in df.columns:
        df = df[~df['Dealer Name'].str.contains('Innovative', case=False, na=False)]

# Helper function to format currency in Indian format (Lakhs/Crores)
def format_inr(value):
    if pd.isna(value):
        return "Rs. 0"
    if value >= 1e7:
        return f"Rs. {value/1e7:.2f} Cr"
    elif value >= 1e5:
        return f"Rs. {value/1e5:.2f} Lakh"
    else:
        return f"Rs. {value:,.0f}"

# Helper function to format quantity in Indian format (Thousands/Lakhs/Crores)
def format_qty(value):
    if pd.isna(value):
        return "0"
    if value >= 1e7:
        return f"{value/1e7:.2f} Cr"
    elif value >= 1e5:
        return f"{value/1e5:.2f} Lakh"
    elif value >= 1e3:
        return f"{value/1e3:.2f} K"
    else:
        return f"{value:,.0f}"

# Helper function to format chart Y-axis in Lakhs/Crores
def format_yaxis_inr(fig, yaxis_col=None):
    """Update chart to show Y-axis values in Lakhs/Crores format"""
    fig.update_layout(
        yaxis=dict(
            tickformat='.2s',
            tickprefix='Rs. ',
        )
    )
    # Custom tick formatting for Indian numbering
    fig.update_yaxes(
        tickvals=None,
        ticktext=None,
    )
    return fig

# Helper function to update hover template for INR values
def add_inr_hover(fig, value_col):
    """Add custom hover template showing values in Lakhs/Crores"""
    fig.update_traces(
        hovertemplate='%{x}<br>%{customdata}<extra></extra>'
    )
    return fig

# Dynamic year detection - for backward compatibility with Excel data
def get_available_years(dataframe, prefix='Value'):
    cols = [c for c in dataframe.columns if c.startswith(prefix) and c != prefix]
    return cols

# Column detection - check for both API format (single Value/Qty) and Excel format (Value 2024-25)
VALUE_COLS = get_available_years(df, 'Value')
QTY_COLS = get_available_years(df, 'Qty')

# If no year-based columns found, use single Value/Qty columns from API
if not VALUE_COLS and 'Value' in df.columns:
    VALUE_COLS = ['Value']
if not QTY_COLS and 'Qty' in df.columns:
    QTY_COLS = ['Qty']

# Define the primary value and quantity columns to use
VALUE_COL = VALUE_COLS[0] if VALUE_COLS else None
QTY_COL = QTY_COLS[0] if QTY_COLS else None

# Title
st.title("Orthopedic Implant Analytics Dashboard - Stage 1")
st.markdown("---")

# Check if data is loaded properly
if df.empty:
    st.error("No data available. Please check your data file.")
    st.stop()

# Main Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Sales Analytics", "Purchase Analytics", "Customer Insights", "Payment Analysis"])

# ================================
# TAB 1: SALES ANALYTICS
# ================================
with tab1:
    st.header("Sales Analytics")
    
    sales_sub1, sales_sub2, sales_sub3, sales_sub4, sales_sub5 = st.tabs([
        "Revenue & Quantity Insights", 
        "Customer Segmentation", 
        "Non-Moving & Slow-Moving Items",
        "Cross-Selling Analytics",
        "Product Drop-Off Tracker"
    ])
    
    # 1.1 Revenue & Quantity Insights
    with sales_sub1:
        st.subheader("Revenue & Quantity Insights")
        
        if not VALUE_COL:
            st.warning("No value columns found in the dataset")
        else:
            # For API data, we have single Value/Qty columns
            # For Excel data, we may have multiple year columns
            if len(VALUE_COLS) > 1:
                selected_value_col = st.selectbox("Select Year", VALUE_COLS, key="sales_year_select")
                selected_qty_col = selected_value_col.replace('Value', 'Qty') if 'Value' in selected_value_col else QTY_COLS[0] if QTY_COLS else None
            else:
                selected_value_col = VALUE_COL
                selected_qty_col = QTY_COL
            
            # PIE CHARTS
            st.markdown("#### Revenue Distribution")
            pie_col1, pie_col2, pie_col3 = st.columns(3)
            
            with pie_col1:
                if 'Dealer Name' in df.columns:
                    dealer_rev = df.groupby('Dealer Name')[selected_value_col].sum().reset_index()
                    dealer_rev = dealer_rev[dealer_rev[selected_value_col] > 0].nlargest(10, selected_value_col)
                    if not dealer_rev.empty:
                        dealer_rev['Formatted'] = dealer_rev[selected_value_col].apply(format_inr)
                        fig_dealer = px.pie(dealer_rev, values=selected_value_col, names='Dealer Name', 
                                           title="Top 10 Dealers by Revenue",
                                           custom_data=['Formatted'])
                        fig_dealer.update_traces(textposition='inside', textinfo='percent+label',
                                                hovertemplate='%{label}<br>%{customdata[0]}<extra></extra>')
                        st.plotly_chart(fig_dealer, use_container_width=True, key="pie_dealer")
                    else:
                        st.info("No dealer revenue data available")
                else:
                    st.info("Dealer Name column not found")
            
            with pie_col2:
                if 'State' in df.columns:
                    state_rev = df.groupby('State')[selected_value_col].sum().reset_index()
                    state_rev = state_rev[state_rev[selected_value_col] > 0]
                    if not state_rev.empty:
                        state_rev['Formatted'] = state_rev[selected_value_col].apply(format_inr)
                        fig_state = px.pie(state_rev, values=selected_value_col, names='State', 
                                          title="Revenue by State",
                                          custom_data=['Formatted'])
                        fig_state.update_traces(textposition='inside', textinfo='percent+label',
                                               hovertemplate='%{label}<br>%{customdata[0]}<extra></extra>')
                        st.plotly_chart(fig_state, use_container_width=True, key="pie_state")
                    else:
                        st.info("No state revenue data available")
                else:
                    st.info("State column not found")
            
            with pie_col3:
                exec_col = 'Sales Executive' if 'Sales Executive' in df.columns else 'Executive' if 'Executive' in df.columns else None
                if exec_col:
                    exec_rev = df.groupby(exec_col)[selected_value_col].sum().reset_index()
                    exec_rev = exec_rev[exec_rev[selected_value_col] > 0]
                    if not exec_rev.empty:
                        exec_rev['Formatted'] = exec_rev[selected_value_col].apply(format_inr)
                        fig_exec = px.pie(exec_rev, values=selected_value_col, names=exec_col, 
                                         title="Revenue by Sales Executive",
                                         custom_data=['Formatted'])
                        fig_exec.update_traces(textposition='inside', textinfo='percent+label',
                                              hovertemplate='%{label}<br>%{customdata[0]}<extra></extra>')
                        st.plotly_chart(fig_exec, use_container_width=True, key="pie_exec")
                    else:
                        st.info("No executive revenue data available")
                else:
                    st.info("Sales Executive column not found")
            
            # TREND GRAPHS
            st.markdown("#### Trend Analysis")
            
            if 'Month' in df.columns:
                monthly_rev = df.groupby('Month')[selected_value_col].sum().reset_index()
                if not monthly_rev.empty and monthly_rev[selected_value_col].sum() > 0:
                    monthly_rev['Formatted'] = monthly_rev[selected_value_col].apply(format_inr)
                    fig_trend = px.line(monthly_rev, x='Month', y=selected_value_col, 
                                       title="Month-wise Revenue Trend", markers=True,
                                       custom_data=['Formatted'])
                    fig_trend.update_layout(yaxis_title="Revenue", xaxis_title="Month")
                    fig_trend.update_traces(hovertemplate='%{x}<br>%{customdata[0]}<extra></extra>')
                    st.plotly_chart(fig_trend, use_container_width=True, key="trend_monthly")
                else:
                    st.info("No monthly trend data available")
            else:
                st.info("Month column not found for trend analysis")
            
            # Category Analysis
            trend_col1, trend_col2 = st.columns(2)
            
            with trend_col1:
                if 'Category' in df.columns:
                    cat_rev = df.groupby('Category')[selected_value_col].sum().reset_index()
                    cat_rev = cat_rev[cat_rev[selected_value_col] > 0].sort_values(selected_value_col, ascending=True)
                    if not cat_rev.empty:
                        cat_rev['Formatted'] = cat_rev[selected_value_col].apply(format_inr)
                        fig_cat = px.bar(cat_rev, x=selected_value_col, y='Category', orientation='h',
                                        title="Revenue by Category", text='Formatted', custom_data=['Formatted'])
                        fig_cat.update_traces(textposition='outside', hovertemplate='%{y}<br>%{customdata[0]}<extra></extra>')
                        st.plotly_chart(fig_cat, use_container_width=True, key="cat_rev_bar")
                    else:
                        st.info("No category revenue data available")
                else:
                    st.info("Category column not found")
            
            with trend_col2:
                if 'Category' in df.columns and selected_qty_col and selected_qty_col in df.columns:
                    cat_qty = df.groupby('Category')[selected_qty_col].sum().reset_index()
                    cat_qty = cat_qty[cat_qty[selected_qty_col] > 0].sort_values(selected_qty_col, ascending=True)
                    if not cat_qty.empty:
                        cat_qty['Formatted'] = cat_qty[selected_qty_col].apply(format_qty)
                        fig_cat_qty = px.bar(cat_qty, x=selected_qty_col, y='Category', orientation='h',
                                            title="Quantity by Category", text='Formatted', custom_data=['Formatted'])
                        fig_cat_qty.update_traces(textposition='outside', hovertemplate='%{y}<br>%{customdata[0]}<extra></extra>')
                        st.plotly_chart(fig_cat_qty, use_container_width=True, key="cat_qty_bar")
                    else:
                        st.info("No category quantity data available")
                else:
                    st.info("Quantity data not available")
            
            # Sub-Category with Filter
            st.markdown("#### Sub-Category Analysis")
            if 'Sub Category' in df.columns:
                all_subcats = df['Sub Category'].dropna().unique().tolist()
                if all_subcats:
                    selected_subcats = st.multiselect("Filter Sub-Categories", all_subcats, default=all_subcats[:10] if len(all_subcats) > 10 else all_subcats, key="sales_subcat_filter")
                    
                    if selected_subcats:
                        subcat_data = df[df['Sub Category'].isin(selected_subcats)]
                        subcat_rev = subcat_data.groupby('Sub Category')[selected_value_col].sum().reset_index()
                        subcat_rev = subcat_rev[subcat_rev[selected_value_col] > 0].sort_values(selected_value_col, ascending=False)
                        
                        if not subcat_rev.empty:
                            subcat_rev['Formatted'] = subcat_rev[selected_value_col].apply(format_inr)
                            fig_subcat = px.bar(subcat_rev, x='Sub Category', y=selected_value_col,
                                               title="Revenue by Sub-Category", text='Formatted', custom_data=['Formatted'])
                            fig_subcat.update_traces(textposition='outside', hovertemplate='%{x}<br>%{customdata[0]}<extra></extra>')
                            fig_subcat.update_layout(xaxis_tickangle=-45)
                            st.plotly_chart(fig_subcat, use_container_width=True, key="subcat_bar")
                        else:
                            st.info("No revenue data for selected sub-categories")
                    else:
                        st.info("Please select at least one sub-category")
                else:
                    st.info("No sub-categories available")
            else:
                st.info("Sub Category column not found")
    
    # 1.2 Customer Segmentation (Onion Method)
    with sales_sub2:
        st.subheader("Customer Segmentation - Drill-Down Analysis")
        st.info("Onion Method: State -> City -> Customer")
        
        if not VALUE_COL:
            st.warning("No value columns found in the dataset")
        elif 'State' not in df.columns:
            st.warning("State column not found for segmentation analysis")
        else:
            # For API data, use single Value column; for Excel, allow year selection
            if len(VALUE_COLS) > 1:
                seg_value_col = st.selectbox("Select Year", VALUE_COLS, key="seg_year")
            else:
                seg_value_col = VALUE_COL
            
            st.markdown("#### Level 1: State Overview")
            state_summary = df.groupby('State')[seg_value_col].sum().reset_index()
            state_summary.columns = ['State', 'Total Revenue']
            state_summary = state_summary[state_summary['Total Revenue'] > 0]
            state_summary['Formatted'] = state_summary['Total Revenue'].apply(format_inr)
            state_summary = state_summary.sort_values('Total Revenue', ascending=False)
            
            if state_summary.empty:
                st.info("No state revenue data available for the selected year")
            else:
                fig_state = px.bar(state_summary, x='State', y='Total Revenue', 
                                  title="Revenue by State", text='Formatted',
                                  color='Total Revenue', color_continuous_scale='Blues',
                                  custom_data=['Formatted'])
                fig_state.update_traces(textposition='outside', hovertemplate='%{x}<br>%{customdata[0]}<extra></extra>')
                fig_state.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_state, use_container_width=True, key="seg_state_bar")
                
                selected_state = st.selectbox("Select State to drill down", state_summary['State'].tolist(), key="drill_state")
                
                if selected_state and 'City' in df.columns:
                    with st.expander(f"Level 2: Cities in {selected_state}", expanded=True):
                        state_df = df[df['State'] == selected_state]
                        city_summary = state_df.groupby('City')[seg_value_col].sum().reset_index()
                        city_summary.columns = ['City', 'Total Revenue']
                        city_summary = city_summary[city_summary['Total Revenue'] > 0]
                        city_summary['Formatted'] = city_summary['Total Revenue'].apply(format_inr)
                        city_summary = city_summary.sort_values('Total Revenue', ascending=False)
                        
                        if city_summary.empty:
                            st.info(f"No city data available for {selected_state}")
                        else:
                            fig_city = px.bar(city_summary, x='City', y='Total Revenue',
                                             title=f"Cities in {selected_state}", text='Formatted',
                                             color='Total Revenue', color_continuous_scale='Greens',
                                             custom_data=['Formatted'])
                            fig_city.update_traces(textposition='outside', hovertemplate='%{x}<br>%{customdata[0]}<extra></extra>')
                            st.plotly_chart(fig_city, use_container_width=True, key="seg_city_bar")
                            
                            selected_city = st.selectbox("Select City", city_summary['City'].tolist(), key="drill_city")
                            
                            if selected_city and 'Dealer Name' in df.columns:
                                with st.expander(f"Level 3: Customers in {selected_city}", expanded=True):
                                    city_df = state_df[state_df['City'] == selected_city]
                                    cust_summary = city_df.groupby('Dealer Name')[seg_value_col].sum().reset_index()
                                    cust_summary.columns = ['Customer', 'Total Revenue']
                                    cust_summary = cust_summary[cust_summary['Total Revenue'] > 0]
                                    cust_summary['Formatted'] = cust_summary['Total Revenue'].apply(format_inr)
                                    cust_summary = cust_summary.sort_values('Total Revenue', ascending=False)
                                    
                                    if cust_summary.empty:
                                        st.info(f"No customer data available for {selected_city}")
                                    else:
                                        fig_cust = px.bar(cust_summary, x='Customer', y='Total Revenue',
                                                         title=f"Customers in {selected_city}", text='Formatted',
                                                         color='Total Revenue', color_continuous_scale='Oranges',
                                                         custom_data=['Formatted'])
                                        fig_cust.update_traces(textposition='outside', hovertemplate='%{x}<br>%{customdata[0]}<extra></extra>')
                                        fig_cust.update_layout(xaxis_tickangle=-45)
                                        st.plotly_chart(fig_cust, use_container_width=True, key="seg_cust_bar")
                                        
                                        st.dataframe(cust_summary[['Customer', 'Formatted']], use_container_width=True)
                            elif 'Dealer Name' not in df.columns:
                                st.info("Dealer Name column not found")
                elif 'City' not in df.columns:
                    st.info("City column not found for drill-down")
            
            st.markdown("---")
            st.markdown("#### Executive Performance")
            exec_col = 'Sales Executive' if 'Sales Executive' in df.columns else 'Executive' if 'Executive' in df.columns else None
            
            if exec_col:
                exec_perf = df.groupby(exec_col)[seg_value_col].sum().reset_index()
                exec_perf.columns = [exec_col, 'Revenue']
                exec_perf = exec_perf[exec_perf['Revenue'] > 0]
                exec_perf['Formatted'] = exec_perf['Revenue'].apply(format_inr)
                exec_perf = exec_perf.sort_values('Revenue', ascending=False)
                
                if exec_perf.empty:
                    st.info("No executive performance data available")
                else:
                    fig_exec = px.bar(exec_perf, x=exec_col, y='Revenue', 
                                     title="Executive Performance", text='Formatted',
                                     color='Revenue', color_continuous_scale='Purples',
                                     custom_data=['Formatted'])
                    fig_exec.update_traces(textposition='outside', hovertemplate='%{x}<br>%{customdata[0]}<extra></extra>')
                    st.plotly_chart(fig_exec, use_container_width=True, key="seg_exec_bar")
            else:
                st.info("Sales Executive column not found")
    
    # 1.3 Non-Moving & Slow-Moving Items
    with sales_sub3:
        st.subheader("Non-Moving & Slow-Moving Items")
        
        if not VALUE_COL:
            st.warning("No value columns found in the dataset")
        else:
            # For API data, use single Value column; for Excel, allow year selection
            if len(VALUE_COLS) > 1:
                analysis_value_col = st.selectbox("Select Year", VALUE_COLS, key="nonmov_year")
            else:
                analysis_value_col = VALUE_COL
            hide_null = st.checkbox("Hide null/zero revenue items", value=True, key="sales_hide_null")
            
            prod_col = 'Product Name' if 'Product Name' in df.columns else 'Item Name' if 'Item Name' in df.columns else 'Sub Category' if 'Sub Category' in df.columns else None
            
            if not prod_col:
                st.warning("No product/item column found for analysis")
            else:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Non-Moving (Zero Sales)")
                    product_sales = df.groupby(prod_col)[analysis_value_col].sum().reset_index()
                    non_moving = product_sales[product_sales[analysis_value_col] == 0]
                    
                    st.metric("Non-Moving Products", len(non_moving))
                    if len(non_moving) > 0:
                        st.dataframe(non_moving.head(20), use_container_width=True)
                    else:
                        st.success("No non-moving items found!")
                
                with col2:
                    st.markdown("#### Slow-Moving (Below Average)")
                    product_sales = df.groupby(prod_col)[analysis_value_col].sum().reset_index()
                    if hide_null:
                        product_sales = product_sales[product_sales[analysis_value_col] > 0]
                    
                    if product_sales.empty:
                        st.info("No product sales data available")
                    else:
                        avg_sales = product_sales[analysis_value_col].mean()
                        slow_moving = product_sales[
                            (product_sales[analysis_value_col] > 0) & 
                            (product_sales[analysis_value_col] < avg_sales * 0.5)
                        ].sort_values(analysis_value_col)
                        
                        slow_moving['Formatted'] = slow_moving[analysis_value_col].apply(format_inr)
                        
                        st.metric("Slow-Moving Products", len(slow_moving))
                        st.caption(f"Average: {format_inr(avg_sales)}")
                        
                        if len(slow_moving) > 0:
                            fig_slow = px.bar(slow_moving.head(15), x=prod_col, y=analysis_value_col,
                                             title="Slow-Moving Items", text='Formatted', custom_data=['Formatted'])
                            fig_slow.update_traces(textposition='outside', hovertemplate='%{x}<br>%{customdata[0]}<extra></extra>')
                            fig_slow.update_layout(xaxis_tickangle=-45)
                            st.plotly_chart(fig_slow, use_container_width=True, key="slow_moving_bar")
                        else:
                            st.success("No slow-moving items found!")
                
                st.markdown("---")
                st.markdown("#### Category-wise Status")
                if 'Category' in df.columns:
                    cat_analysis = df.groupby('Category').agg({
                        analysis_value_col: ['sum', 'count', lambda x: (x == 0).sum()]
                    }).reset_index()
                    cat_analysis.columns = ['Category', 'Total Revenue', 'Total Items', 'Zero Sales']
                    cat_analysis['Non-Moving %'] = (cat_analysis['Zero Sales'] / cat_analysis['Total Items'] * 100).round(1)
                    cat_analysis['Formatted'] = cat_analysis['Total Revenue'].apply(format_inr)
                    
                    if cat_analysis.empty:
                        st.info("No category data available")
                    else:
                        fig_cat = px.bar(cat_analysis, x='Category', y='Non-Moving %',
                                        title="Non-Moving % by Category", color='Non-Moving %',
                                        color_continuous_scale='Reds')
                        st.plotly_chart(fig_cat, use_container_width=True, key="nonmov_cat_bar")
                else:
                    st.info("Category column not found")
    
    # 1.4 Cross-Selling Analytics
    with sales_sub4:
        st.subheader("Cross-Selling Analytics")
        
        if 'Dealer Name' not in df.columns:
            st.warning("Dealer Name column not found for cross-selling analysis")
        elif 'Category' not in df.columns:
            st.warning("Category column not found for cross-selling analysis")
        elif not VALUE_COL:
            st.warning("No value columns found in the dataset")
        else:
            # For API data, use single Value column; for Excel, allow year selection
            if len(VALUE_COLS) > 1:
                cross_value_col = st.selectbox("Select Year", VALUE_COLS, key="cross_year")
            else:
                cross_value_col = VALUE_COL
            
            customer_categories = df.groupby(['Dealer Name', 'Category'])[cross_value_col].sum().unstack(fill_value=0)
            
            if customer_categories.empty:
                st.info("No cross-selling data available")
            else:
                st.markdown("#### Customers Buying X but not Y")
                categories = df['Category'].dropna().unique().tolist()
                
                if len(categories) < 2:
                    st.info("Need at least 2 categories for cross-selling analysis")
                else:
                    col1, col2 = st.columns(2)
                    with col1:
                        cat_x = st.selectbox("Customers who buy", categories, key="cat_x")
                    with col2:
                        cat_y = st.selectbox("But don't buy", categories, key="cat_y")
                    
                    if cat_x == cat_y:
                        st.info("Please select different categories for comparison")
                    elif cat_x not in customer_categories.columns:
                        st.info(f"No data available for category: {cat_x}")
                    elif cat_y not in customer_categories.columns:
                        st.info(f"No data available for category: {cat_y}")
                    else:
                        buying_x = customer_categories[customer_categories[cat_x] > 0]
                        not_buying_y = buying_x[buying_x[cat_y] == 0]
                        
                        st.metric(f"Customers buying {cat_x} but not {cat_y}", len(not_buying_y))
                        
                        if len(not_buying_y) > 0:
                            opportunity = pd.DataFrame({
                                'Customer': not_buying_y.index,
                                f'{cat_x} Revenue': not_buying_y[cat_x].values
                            })
                            opportunity['Formatted'] = opportunity[f'{cat_x} Revenue'].apply(format_inr)
                            opportunity = opportunity.sort_values(f'{cat_x} Revenue', ascending=False)
                            
                            fig_opp = px.bar(opportunity.head(10), x='Customer', y=f'{cat_x} Revenue',
                                            title=f"Top Cross-Sell Opportunities for {cat_y}", text='Formatted',
                                            custom_data=['Formatted'])
                            fig_opp.update_traces(textposition='outside', hovertemplate='%{x}<br>%{customdata[0]}<extra></extra>')
                            fig_opp.update_layout(xaxis_tickangle=-45)
                            st.plotly_chart(fig_opp, use_container_width=True, key="cross_sell_bar")
                        else:
                            st.info(f"All customers buying {cat_x} are also buying {cat_y}")
                
                st.markdown("---")
                st.markdown("#### Product Mix - Top Customers")
                top_custs = df.groupby('Dealer Name')[cross_value_col].sum().nlargest(10).index.tolist()
                mix_data = customer_categories.loc[customer_categories.index.isin(top_custs)]
                
                if mix_data.empty:
                    st.info("No product mix data available for top customers")
                else:
                    mix_pct = mix_data.div(mix_data.sum(axis=1), axis=0) * 100
                    mix_melted = mix_pct.reset_index().melt(id_vars='Dealer Name', var_name='Category', value_name='%')
                    
                    fig_mix = px.bar(mix_melted, x='Dealer Name', y='%', color='Category',
                                    title="Category Mix % by Top Customers", barmode='stack')
                    fig_mix.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig_mix, use_container_width=True, key="product_mix_bar")
    
    # 1.5 Product Drop-Off Tracker
    with sales_sub5:
        st.subheader("Product Drop-Off Tracker")
        
        if len(VALUE_COLS) < 2:
            st.info("Drop-off analysis requires multiple time periods. Current data shows single period aggregated values.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                prev_period = st.selectbox("Previous Period", VALUE_COLS, index=0, key="prev_period")
            with col2:
                curr_period = st.selectbox("Current Period", VALUE_COLS, index=min(1, len(VALUE_COLS)-1), key="curr_period")
            
            decline_threshold = st.slider("Decline Threshold (%)", 10, 90, 30, key="decline_thresh")
            
            prod_col = 'Product Name' if 'Product Name' in df.columns else 'Item Name' if 'Item Name' in df.columns else 'Sub Category' if 'Sub Category' in df.columns else None
            
            if not prod_col:
                st.warning("No product/item column found for drop-off analysis")
            else:
                comparison = df.groupby(prod_col).agg({
                    prev_period: 'sum',
                    curr_period: 'sum'
                }).reset_index()
                
                comparison['Change %'] = ((comparison[curr_period] - comparison[prev_period]) / 
                                          comparison[prev_period].replace(0, np.nan) * 100).round(1)
                
                declined = comparison[
                    (comparison['Change %'] <= -decline_threshold) & 
                    (comparison[prev_period] > 0)
                ].sort_values('Change %')
                
                declined['Previous'] = declined[prev_period].apply(format_inr)
                declined['Current'] = declined[curr_period].apply(format_inr)
                
                st.metric("Products with Decline", len(declined))
                
                if len(declined) > 0:
                    fig_dec = px.bar(declined.head(15), x=prod_col, y='Change %',
                                    title=f"Products with >{decline_threshold}% Decline",
                                    color='Change %', color_continuous_scale='Reds_r')
                    fig_dec.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig_dec, use_container_width=True, key="dropoff_bar")
                    
                    st.dataframe(declined[[prod_col, 'Previous', 'Current', 'Change %']].head(20), use_container_width=True)
                else:
                    st.success("No significant decline found!")
            
            st.markdown("---")
            st.markdown("#### Category Trends")
            if 'Category' in df.columns:
                cat_trend = df.groupby('Category').agg({
                    prev_period: 'sum',
                    curr_period: 'sum'
                }).reset_index()
                
                cat_trend['Change %'] = ((cat_trend[curr_period] - cat_trend[prev_period]) / 
                                          cat_trend[prev_period].replace(0, np.nan) * 100).round(1)
                cat_trend['Previous'] = cat_trend[prev_period].apply(format_inr)
                cat_trend['Current'] = cat_trend[curr_period].apply(format_inr)
                
                if cat_trend.empty:
                    st.info("No category trend data available")
                else:
                    fig_cat_trend = px.bar(cat_trend, x='Category', y='Change %',
                                           title="Category Change", color='Change %',
                                           color_continuous_scale='RdYlGn', text='Change %')
                    fig_cat_trend.update_traces(textposition='outside')
                    st.plotly_chart(fig_cat_trend, use_container_width=True, key="cat_trend_bar")
            else:
                st.info("Category column not found")

# ================================
# TAB 2: PURCHASE ANALYTICS
# ================================
with tab2:
    st.header("Purchase Analytics")
    
    purch_sub1, purch_sub2, purch_sub3 = st.tabs(["Overview", "Trends", "Supplier Analysis"])
    
    with purch_sub1:
        st.subheader("Purchase Overview")
        if not VALUE_COL:
            st.warning("No value columns found in the dataset")
        else:
            # For API data, use single Value column; for Excel, allow year selection
            if len(VALUE_COLS) > 1:
                purch_value_col = st.selectbox("Select Year", VALUE_COLS, key="purch_year")
            else:
                purch_value_col = VALUE_COL
            total_purch = df[purch_value_col].sum()
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Value", format_inr(total_purch))
            if 'Category' in df.columns:
                m2.metric("Categories", df['Category'].nunique())
            else:
                m2.metric("Categories", "N/A")
            if 'Dealer Name' in df.columns:
                m3.metric("Dealers", df['Dealer Name'].nunique())
            else:
                m3.metric("Dealers", "N/A")
            
            if 'Category' in df.columns:
                cat_purch = df.groupby('Category')[purch_value_col].sum().reset_index()
                cat_purch = cat_purch[cat_purch[purch_value_col] > 0]
                if not cat_purch.empty:
                    cat_purch['Formatted'] = cat_purch[purch_value_col].apply(format_inr)
                    fig = px.pie(cat_purch, values=purch_value_col, names='Category', title="By Category",
                                custom_data=['Formatted'])
                    fig.update_traces(hovertemplate='%{label}<br>%{customdata[0]}<extra></extra>')
                    st.plotly_chart(fig, use_container_width=True, key="purch_cat_pie")
                else:
                    st.info("No category data available for the selected year")
            else:
                st.info("Category column not found")
    
    with purch_sub2:
        st.subheader("Trends")
        if 'Month' not in df.columns:
            st.info("Month column not found for trend analysis. API data shows aggregated values.")
        elif not VALUE_COL:
            st.warning("No value columns found in the dataset")
        else:
            # For API data, use single Value column; for Excel, allow year selection
            if len(VALUE_COLS) > 1:
                trend_value_col = st.selectbox("Select Year", VALUE_COLS, key="purch_trend_year")
            else:
                trend_value_col = VALUE_COL
            monthly = df.groupby('Month')[trend_value_col].sum().reset_index()
            if monthly.empty or monthly[trend_value_col].sum() == 0:
                st.info("No monthly trend data available")
            else:
                monthly['Formatted'] = monthly[trend_value_col].apply(format_inr)
                fig = px.line(monthly, x='Month', y=trend_value_col, title="Monthly Trend", markers=True,
                             custom_data=['Formatted'])
                fig.update_traces(hovertemplate='%{x}<br>%{customdata[0]}<extra></extra>')
                st.plotly_chart(fig, use_container_width=True, key="purch_trend_line")
    
    with purch_sub3:
        st.subheader("Supplier Analysis")
        if 'Dealer Name' not in df.columns:
            st.warning("Dealer Name column not found for supplier analysis")
        elif not VALUE_COL:
            st.warning("No value columns found in the dataset")
        else:
            # For API data, use single Value column; for Excel, allow year selection
            if len(VALUE_COLS) > 1:
                supp_value_col = st.selectbox("Select Year", VALUE_COLS, key="supp_year")
            else:
                supp_value_col = VALUE_COL
            supplier = df.groupby('Dealer Name')[supp_value_col].sum().reset_index()
            supplier = supplier[supplier[supp_value_col] > 0].sort_values(supp_value_col, ascending=False)
            
            if supplier.empty:
                st.info("No supplier data available for the selected year")
            else:
                supplier['Formatted'] = supplier[supp_value_col].apply(format_inr)
                fig = px.bar(supplier.head(15), x='Dealer Name', y=supp_value_col,
                            title="Top 15 Suppliers", text='Formatted', custom_data=['Formatted'])
                fig.update_traces(textposition='outside', hovertemplate='%{x}<br>%{customdata[0]}<extra></extra>')
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True, key="purch_supplier_bar")

# ================================
# TAB 3: CUSTOMER INSIGHTS
# ================================
with tab3:
    st.header("Customer Insights")
    
    cust_sub1, cust_sub2, cust_sub3 = st.tabs(["Overview", "Geographic", "Performance"])
    
    with cust_sub1:
        st.subheader("Customer Overview")
        if 'Dealer Name' not in df.columns:
            st.warning("Dealer Name column not found for customer analysis")
        elif not VALUE_COL:
            st.warning("No value columns found in the dataset")
        else:
            # For API data, use single Value column; for Excel, allow year selection
            if len(VALUE_COLS) > 1:
                cust_value_col = st.selectbox("Select Year", VALUE_COLS, key="cust_year")
            else:
                cust_value_col = VALUE_COL
            top_custs = df.groupby('Dealer Name')[cust_value_col].sum().reset_index()
            top_custs = top_custs[top_custs[cust_value_col] > 0].sort_values(cust_value_col, ascending=False)
            
            if top_custs.empty:
                st.info("No customer data available for the selected year")
            else:
                top_custs['Formatted'] = top_custs[cust_value_col].apply(format_inr)
                fig = px.bar(top_custs.head(20), x='Dealer Name', y=cust_value_col,
                            title="Top 20 Customers", text='Formatted', color=cust_value_col,
                            color_continuous_scale='Blues', custom_data=['Formatted'])
                fig.update_traces(textposition='outside', hovertemplate='%{x}<br>%{customdata[0]}<extra></extra>')
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True, key="cust_overview_chart")
    
    with cust_sub2:
        st.subheader("Geographic Analysis")
        if 'State' not in df.columns:
            st.warning("State column not found for geographic analysis")
        elif not VALUE_COL:
            st.warning("No value columns found in the dataset")
        else:
            # For API data, use single Value column; for Excel, allow year selection
            if len(VALUE_COLS) > 1:
                geo_value_col = st.selectbox("Select Year", VALUE_COLS, key="geo_year")
            else:
                geo_value_col = VALUE_COL
            state_data = df.groupby('State')[geo_value_col].sum().reset_index()
            state_data = state_data[state_data[geo_value_col] > 0].sort_values(geo_value_col, ascending=False)
            
            if state_data.empty:
                st.info("No state data available for the selected year")
            else:
                state_data['Formatted'] = state_data[geo_value_col].apply(format_inr)
                fig = px.bar(state_data, x='State', y=geo_value_col, title="Revenue by State",
                            text='Formatted', color=geo_value_col, color_continuous_scale='Viridis',
                            custom_data=['Formatted'])
                fig.update_traces(textposition='outside', hovertemplate='%{x}<br>%{customdata[0]}<extra></extra>')
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True, key="geo_state_chart")
                
                if 'City' in df.columns:
                    sel_state = st.selectbox("Select State", state_data['State'].tolist(), key="geo_state")
                    city_data = df[df['State'] == sel_state].groupby('City')[geo_value_col].sum().reset_index()
                    city_data = city_data[city_data[geo_value_col] > 0].sort_values(geo_value_col, ascending=False)
                    
                    if city_data.empty:
                        st.info(f"No city data available for {sel_state}")
                    else:
                        city_data['Formatted'] = city_data[geo_value_col].apply(format_inr)
                        fig = px.bar(city_data, x='City', y=geo_value_col, title=f"Cities in {sel_state}",
                                    text='Formatted', custom_data=['Formatted'])
                        fig.update_traces(textposition='outside', hovertemplate='%{x}<br>%{customdata[0]}<extra></extra>')
                        st.plotly_chart(fig, use_container_width=True, key="geo_city_chart")
                else:
                    st.info("City column not found for detailed breakdown")
    
    with cust_sub3:
        st.subheader("Customer Performance")
        if 'Dealer Name' not in df.columns:
            st.warning("Dealer Name column not found for performance analysis")
        elif len(VALUE_COLS) < 2:
            st.info("Performance comparison requires multiple time periods. Current data shows single period aggregated values.")
        else:
            prev_y = st.selectbox("Previous", VALUE_COLS, index=0, key="cust_prev")
            curr_y = st.selectbox("Current", VALUE_COLS, index=min(1, len(VALUE_COLS)-1), key="cust_curr")
            
            perf = df.groupby('Dealer Name').agg({prev_y: 'sum', curr_y: 'sum'}).reset_index()
            perf['Growth %'] = ((perf[curr_y] - perf[prev_y]) / perf[prev_y].replace(0, np.nan) * 100).round(1)
            
            growers = perf[perf['Growth %'] > 0].sort_values('Growth %', ascending=False).head(10)
            decliners = perf[perf['Growth %'] < 0].sort_values('Growth %').head(10)
            
            if len(growers) > 0:
                st.markdown("#### Top Growers")
                growers['Growth Text'] = growers['Growth %'].apply(lambda x: f"{x:.1f}%")
                fig = px.bar(growers, x='Dealer Name', y='Growth %', title="Growing Customers",
                            text='Growth Text', color='Growth %', color_continuous_scale='Greens')
                fig.update_traces(textposition='outside', hovertemplate='%{x}<br>Growth: %{y:.1f}%<extra></extra>')
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True, key="cust_growers_chart")
            else:
                st.info("No growing customers found for the selected periods")
            
            if len(decliners) > 0:
                st.markdown("#### Declining")
                decliners['Growth Text'] = decliners['Growth %'].apply(lambda x: f"{x:.1f}%")
                fig = px.bar(decliners, x='Dealer Name', y='Growth %', title="Declining Customers",
                            text='Growth Text', color='Growth %', color_continuous_scale='Reds_r')
                fig.update_traces(textposition='outside', hovertemplate='%{x}<br>Growth: %{y:.1f}%<extra></extra>')
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True, key="cust_decliners_chart")
            else:
                st.info("No declining customers found for the selected periods")

# ================================
# TAB 4: PAYMENT ANALYSIS
# ================================
with tab4:
    st.header("Payment Analysis")
    
    pay_sub1, pay_sub2 = st.tabs(["Overview", "Outstanding"])
    
    with pay_sub1:
        st.subheader("Payment Overview")
        if VALUE_COL is None:
            st.warning("No value column found in the dataset")
        else:
            st.info(f"Analyzing: {VALUE_COL}")
            
            if 'Category' in df.columns:
                cat_pay = df.groupby('Category')[VALUE_COL].sum().reset_index()
                cat_pay = cat_pay[cat_pay[VALUE_COL] > 0]
                if not cat_pay.empty:
                    cat_pay['Formatted'] = cat_pay[VALUE_COL].apply(format_inr)
                    fig = px.pie(cat_pay, values=VALUE_COL, names='Category', title="By Category",
                                custom_data=['Formatted'])
                    fig.update_traces(hovertemplate='%{label}<br>%{customdata[0]}<extra></extra>')
                    st.plotly_chart(fig, use_container_width=True, key="pay_cat_pie")
                else:
                    st.info("No category payment data available")
            else:
                st.info("Category column not found")
            
            hide_null_pay = st.checkbox("Hide zero values", value=True, key="pay_hide_null")
            
            if 'Dealer Name' in df.columns:
                dealer_pay = df.groupby('Dealer Name')[VALUE_COL].sum().reset_index()
                if hide_null_pay:
                    dealer_pay = dealer_pay[dealer_pay[VALUE_COL] > 0]
                dealer_pay = dealer_pay.sort_values(VALUE_COL, ascending=False)
                
                if dealer_pay.empty:
                    st.info("No dealer payment data available")
                else:
                    dealer_pay['Formatted'] = dealer_pay[VALUE_COL].apply(format_inr)
                    fig = px.bar(dealer_pay.head(15), x='Dealer Name', y=VALUE_COL,
                                title="Top 15 Dealers", text='Formatted', custom_data=['Formatted'])
                    fig.update_traces(textposition='outside', hovertemplate='%{x}<br>%{customdata[0]}<extra></extra>')
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True, key="pay_dealer_bar")
            else:
                st.info("Dealer Name column not found")
    
    with pay_sub2:
        st.subheader("Outstanding Analysis")
        if 'Outstanding' not in df.columns:
            st.info("Outstanding column not found in the dataset")
        elif 'Dealer Name' not in df.columns:
            st.info("Dealer Name column not found for outstanding analysis")
        else:
            outstanding = df.groupby('Dealer Name')['Outstanding'].sum().reset_index()
            outstanding = outstanding[outstanding['Outstanding'] > 0].sort_values('Outstanding', ascending=False)
            
            if outstanding.empty:
                st.success("No outstanding amounts found!")
            else:
                outstanding['Formatted'] = outstanding['Outstanding'].apply(format_inr)
                st.metric("Total Outstanding", format_inr(outstanding['Outstanding'].sum()))
                
                fig = px.bar(outstanding.head(15), x='Dealer Name', y='Outstanding',
                            title="Top 15 Outstanding", text='Formatted', color='Outstanding',
                            color_continuous_scale='Reds', custom_data=['Formatted'])
                fig.update_traces(textposition='outside', hovertemplate='%{x}<br>%{customdata[0]}<extra></extra>')
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True, key="pay_outstanding_bar")

# Footer
st.markdown("---")
st.caption("Orthopedic Implant Analytics Dashboard - Stage 1")
