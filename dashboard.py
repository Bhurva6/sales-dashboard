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

# Sidebar with logout and refresh options
with st.sidebar:
    st.title("Dashboard Controls")
    logout_button()
    st.markdown("---")
    if st.button(" Refresh Data", use_container_width=True):
        # Clear all cached API data for date ranges
        for key in list(st.session_state.keys()):
            if key.startswith("api_data_"):
                del st.session_state[key]
        st.cache_data.clear()
        st.rerun()
    st.markdown("---")
    # Filter to hide "Innovative" dealers
    hide_innovative = st.checkbox("Hide 'Innovative Ortho Surgicals' Dealer", value=False, key="hide_innovative")
    st.markdown("---")
    st.caption("Data loaded from API")

# Date range selector with calendar picker
st.sidebar.markdown("### 📅 Select Date Range")

from datetime import datetime, timedelta

# Get current month start and today
today = datetime.now()
month_start = today.replace(day=1)

# Create columns for date inputs
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input(
        "Start Date",
        value=month_start,
        key="start_date_picker"
    )

with col2:
    end_date = st.date_input(
        "End Date",
        value=today,
        key="end_date_picker"
    )

# Convert dates to DD-MM-YYYY format for API
start_date_str = start_date.strftime("%d-%m-%Y")
end_date_str = end_date.strftime("%d-%m-%Y")

# Force date change detection and cache invalidation
force_refresh = False

# Check if dates have changed, and if so, clear the cache
if 'last_start_date' not in st.session_state:
    st.session_state.last_start_date = start_date_str
if 'last_end_date' not in st.session_state:
    st.session_state.last_end_date = end_date_str

current_date_key = f"{start_date_str}_{end_date_str}"
last_date_key = f"{st.session_state.last_start_date}_{st.session_state.last_end_date}"

if current_date_key != last_date_key:
    # Date changed, clear ALL cache IMMEDIATELY before updating session state
    print(f"📅 DATE CHANGE DETECTED: {last_date_key} → {current_date_key}")
    force_refresh = True
    
    # Clear all cached data - including Streamlit's internal cache
    for key in list(st.session_state.keys()):
        if key.startswith("api_data_"):
            del st.session_state[key]
            print(f"   Cleared cache: {key}")
    
    # Also delete the specific cache key for the new date range (in case it exists)
    new_cache_key = f"api_data_{start_date_str}_{end_date_str}"
    if new_cache_key in st.session_state:
        del st.session_state[new_cache_key]
        print(f"   Cleared new cache key: {new_cache_key}")
    
    # Update session state BEFORE rerun
    st.session_state.last_start_date = start_date_str
    st.session_state.last_end_date = end_date_str
    st.session_state.force_data_refresh = True
    st.session_state.skip_all_caches = True  # NEW: Additional flag
    
    # Force Streamlit to re-run the entire script
    st.rerun()

# Check if we need to force refresh (set during date change above)
force_refresh = st.session_state.get('force_data_refresh', False)
skip_all_caches = st.session_state.get('skip_all_caches', False)

if force_refresh or skip_all_caches:
    # Create cache key and delete it to force fresh fetch
    cache_key = f"api_data_{start_date_str}_{end_date_str}"
    if cache_key in st.session_state:
        del st.session_state[cache_key]
        print(f"   Tier 2 cleanup: Deleted cache key {cache_key}")
    
    # Also clear any metrics cache if it exists
    metrics_cache_key = f"metrics_{start_date_str}_{end_date_str}"
    if metrics_cache_key in st.session_state:
        del st.session_state[metrics_cache_key]
        print(f"   Tier 2 cleanup: Deleted metrics cache key {metrics_cache_key}")
    
    # Reset the flags
    st.session_state.force_data_refresh = False
    st.session_state.skip_all_caches = False
    print(f"✅ Force refresh enabled - will fetch fresh data from API")

print(f"📊 Fetching data for date range: {start_date_str} to {end_date_str}")
df = fetch_dashboard_data(start_date=start_date_str, end_date=end_date_str, force_refresh=force_refresh)

# Debug: Print info about fetched data
if df is not None:
    print(f"✅ Data fetched successfully")
    print(f"   - Rows: {len(df)}")
    print(f"   - Columns: {len(df.columns)}")
    print(f"   - Object ID: {id(df)}")
    if 'Value' in df.columns:
        print(f"   - Total Revenue: Rs. {df['Value'].sum():,.2f}")
    if 'Qty' in df.columns:
        print(f"   - Total Qty: {df['Qty'].sum():,.0f}")
    if 'Dealer Name' in df.columns:
        print(f"   - Unique Dealers: {df['Dealer Name'].nunique()}")
else:
    print(f"❌ Failed to fetch data")

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
def format_yaxis_inr(fig):
    """Update chart to show Y-axis values in Indian format (Lakhs/Crores)"""
    fig.update_layout(
        yaxis=dict(
            tickprefix='Rs. ',
        )
    )
    return fig

# Helper function to format Y-axis for quantity charts
def format_yaxis_qty(fig):
    """Update chart to show Y-axis values in Indian format for quantities"""
    return fig

# Helper function to format axis ticks in Indian number format
def format_indian_ticks(value):
    """Format a single value for axis tick in Indian format"""
    if value >= 1e7:
        return f"{value/1e7:.1f} Cr"
    elif value >= 1e5:
        return f"{value/1e5:.1f} L"
    elif value >= 1e3:
        return f"{value/1e3:.1f} K"
    else:
        return f"{value:.0f}"

# Helper function to update chart axes with Indian formatting
def apply_indian_format_to_chart(fig, axis='y', prefix=''):
    """Apply Indian number formatting to chart axis ticks"""
    import plotly.graph_objects as go
    
    # Update tick format to avoid M/B suffixes
    if axis == 'y':
        fig.update_yaxes(
            tickformat=',.0f',
            separatethousands=True
        )
    elif axis == 'x':
        fig.update_xaxes(
            tickformat=',.0f',
            separatethousands=True
        )
    return fig

# Helper function to update hover template for INR values
def add_inr_hover(fig, value_col):
    """Add custom hover template showing values in Lakhs/Crores"""
    fig.update_traces(
        hovertemplate='%{x}<br>%{customdata}<extra></extra>'
    )
    return fig

# Helper function to get display limit from dropdown
def get_display_limit(key, default=10, options=None):
    """Return the number of items to display based on user selection"""
    if options is None:
        options = {"Top 10": 10, "Top 20": 20, "Top 50": 50, "All": None}
    selected = st.selectbox("Show", list(options.keys()), index=0, key=key)
    return options[selected]

# Helper function to apply display limit to dataframe
def apply_limit(df, limit):
    """Apply row limit to dataframe, return all if limit is None"""
    if limit is None:
        return df
    return df.head(limit)

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

# ================================
# KEY STATISTICS SECTION
# ================================

# Create a unique render key based on dates to force Streamlit to re-render metrics
metrics_render_key = f"{start_date_str}_{end_date_str}"
print(f"📊 METRICS RENDER KEY: {metrics_render_key}")

st.subheader("📊 Key Metrics - Selected Date Range")

# CRITICAL: Force Streamlit to clear any cached metrics
# This ensures metrics recalculate with fresh data
if force_refresh or skip_all_caches:
    st.cache_data.clear()
    print(f"🧹 Streamlit cache cleared due to date change")

# Use the selected date range for metrics (same as main dashboard)
current_period_label = f"Selected Range ({start_date_str} to {end_date_str})"

# IMPORTANT: Use a fresh reference to the dataframe to avoid any caching issues
# Create a copy to ensure we're working with fresh data
current_period_data = df.copy()

print(f"📈 KEY METRICS CALCULATION")
print(f"   Data shape: {current_period_data.shape}")
print(f"   Object ID (current_period_data): {id(current_period_data)}")
print(f"   Render Key: {metrics_render_key}")

# Calculate key statistics
if not current_period_data.empty:
    # 1. Revenue this period
    revenue_this_period = current_period_data[VALUE_COL].sum() if VALUE_COL else 0
    print(f"   - Revenue calculated: Rs. {revenue_this_period:,.2f}")
    
    # 2. Quantity this period
    quantity_this_period = current_period_data[QTY_COL].sum() if QTY_COL else 0
    print(f"   - Quantity calculated: {quantity_this_period:,.0f}")
    
    # 3. Most sold item (by quantity)
    if QTY_COL and QTY_COL in current_period_data.columns:
        prod_col = 'Product Name' if 'Product Name' in current_period_data.columns else 'Item Name' if 'Item Name' in current_period_data.columns else 'Sub Category' if 'Sub Category' in current_period_data.columns else None
        if prod_col:
            most_sold = current_period_data.groupby(prod_col)[QTY_COL].sum().idxmax() if not current_period_data.empty else "N/A"
        else:
            most_sold = "N/A"
    else:
        most_sold = "N/A"
    
    # 4. Most orders from state
    if 'State' in current_period_data.columns:
        most_orders_state = current_period_data['State'].value_counts().idxmax() if len(current_period_data) > 0 else "N/A"
        state_orders_count = current_period_data['State'].value_counts().max() if len(current_period_data) > 0 else 0
    else:
        most_orders_state = "N/A"
        state_orders_count = 0
    
    # 5. Most orders from area/city
    if 'City' in current_period_data.columns:
        most_orders_area = current_period_data['City'].value_counts().idxmax() if len(current_period_data) > 0 else "N/A"
        area_orders_count = current_period_data['City'].value_counts().max() if len(current_period_data) > 0 else 0
    else:
        most_orders_area = "N/A"
        area_orders_count = 0
    
    # 6. Most orders from dealer
    if 'Dealer Name' in current_period_data.columns:
        most_orders_dealer = current_period_data['Dealer Name'].value_counts().idxmax() if len(current_period_data) > 0 else "N/A"
        dealer_orders_count = current_period_data['Dealer Name'].value_counts().max() if len(current_period_data) > 0 else 0
    else:
        most_orders_dealer = "N/A"
        dealer_orders_count = 0
    
    # Store metrics in session state with date-based keys to force updates on date change
    # This ensures metrics refresh when dates change
    metrics_state_key = f"metrics_data_{metrics_render_key}"
    if metrics_state_key not in st.session_state:
        st.session_state[metrics_state_key] = {
            'revenue': revenue_this_period,
            'quantity': quantity_this_period,
            'most_sold': most_sold,
            'total_orders': len(current_period_data),
            'top_state': most_orders_state,
            'state_count': state_orders_count,
            'top_area': most_orders_area,
            'area_count': area_orders_count,
            'top_dealer': most_orders_dealer,
            'dealer_count': dealer_orders_count
        }
    
    # Create metric boxes in a grid layout
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💰 Revenue", 
            format_inr(st.session_state[metrics_state_key]['revenue'])
        )
        st.caption(current_period_label)
    
    with col2:
        st.metric(
            "📦 Total Quantity", 
            format_qty(st.session_state[metrics_state_key]['quantity'])
        )
        st.caption(current_period_label)
    
    with col3:
        st.metric(
            "🏆 Most Sold Item", 
            st.session_state[metrics_state_key]['most_sold']
        )
        st.caption("By Quantity")
    
    with col4:
        st.metric(
            "📊 Total Orders", 
            st.session_state[metrics_state_key]['total_orders']
        )
        st.caption(current_period_label)
    
    # Second row of statistics
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.metric(
            "🗺️ Top State", 
            st.session_state[metrics_state_key]['top_state']
        )
        st.caption(f"{st.session_state[metrics_state_key]['state_count']} orders")
    
    with col6:
        st.metric(
            "🏙️ Top Area", 
            st.session_state[metrics_state_key]['top_area']
        )
        st.caption(f"{st.session_state[metrics_state_key]['area_count']} orders")
    
    with col7:
        st.metric(
            "🤝 Top Dealer", 
            st.session_state[metrics_state_key]['top_dealer']
        )
        st.caption(f"{st.session_state[metrics_state_key]['dealer_count']} orders")
    
    with col8:
        # Category count
        if 'Category' in current_period_data.columns:
            category_count = current_period_data['Category'].nunique()
            st.metric(
                "📂 Categories", 
                category_count
            )
        else:
            st.metric(
                "📂 Categories", 
                "N/A"
            )
        st.caption("Unique")
    
    st.markdown("---")
else:
    st.warning(f"No data available for {current_period_label}")

# Main Tabs
tab1, tab2, tab3 = st.tabs(["Sales Analytics", "Customer Insights", "Payment Analysis"])

# ================================
# TAB 1: SALES ANALYTICS
# ================================
with tab1:
    st.header("Sales Analytics")
    
    sales_sub1, sales_sub2, sales_sub3, sales_sub4, sales_sub5, sales_sub6, sales_sub7, sales_sub8 = st.tabs([
        "Revenue & Quantity Insights", 
        "Customer Segmentation", 
        "Non-Moving & Slow-Moving Items",
        "Cross-Selling Analytics",
        "Product Drop-Off Tracker",
        "Day & Date-wise Analytics",
        "State-wise Revenue Analysis",
        "Dealer & State Comparative Analysis"
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
            dealer_limit = get_display_limit("dealer_pie_limit", default=10)
            pie_col1, pie_col2, pie_col3 = st.columns(3)
            
            with pie_col1:
                if 'Dealer Name' in df.columns:
                    dealer_rev = df.groupby('Dealer Name')[selected_value_col].sum().reset_index()
                    dealer_rev = dealer_rev[dealer_rev[selected_value_col] > 0].sort_values(selected_value_col, ascending=False)
                    dealer_rev_full = dealer_rev.copy()
                    
                    # Create formatted column first
                    dealer_rev['Formatted'] = dealer_rev[selected_value_col].apply(format_inr)
                    
                    dealer_rev = apply_limit(dealer_rev, dealer_limit)
                    
                    # Show pie chart first
                    title_suffix = f"Top {dealer_limit}" if dealer_limit else "All"
                    fig_dealer = px.pie(dealer_rev, values=selected_value_col, names='Dealer Name', 
                                       title=f"{title_suffix} Dealers by Revenue",
                                       custom_data=['Formatted'])
                    fig_dealer.update_traces(textposition='inside', textinfo='percent+label',
                                            hovertemplate='%{label}<br>%{customdata[0]}<extra></extra>')
                    st.plotly_chart(fig_dealer, use_container_width=True, key="pie_dealer")
                    
                    # Add dropdown selector for dealer BELOW the chart
                    st.markdown("**Select Dealers to View Details**")
                    available_dealers = dealer_rev['Dealer Name'].tolist()
                    selected_dealers = st.multiselect(
                        "Choose dealers",
                        available_dealers,
                        default=[available_dealers[0]] if available_dealers else [],
                        key="dealer_detail_select"
                    )
                    
                    # Get details for selected dealers
                    if selected_dealers:
                        dealer_details_data = []
                        for dealer in selected_dealers:
                            dealer_data = dealer_rev[dealer_rev['Dealer Name'] == dealer]
                            if not dealer_data.empty:
                                dealer_info = dealer_data.iloc[0]
                                dealer_details_data.append({
                                    'Dealer': dealer,
                                    'Revenue': dealer_info['Formatted']
                                })
                        
                        if dealer_details_data:
                            dealer_details_df = pd.DataFrame(dealer_details_data)
                            st.dataframe(dealer_details_df, use_container_width=True, hide_index=True)
                else:
                    st.info("No dealer revenue data available")
            
            with pie_col2:
                if 'State' in df.columns:
                    state_rev = df.groupby('State')[selected_value_col].sum().reset_index()
                    state_rev = state_rev[state_rev[selected_value_col] > 0].sort_values(selected_value_col, ascending=False)
                    state_rev_full = state_rev.copy()
                    
                    # Create formatted column first
                    state_rev['Formatted'] = state_rev[selected_value_col].apply(format_inr)
                    
                    # Show pie chart first
                    fig_state = px.pie(state_rev, values=selected_value_col, names='State', 
                                      title="Revenue by State",
                                      custom_data=['Formatted'])
                    fig_state.update_traces(textposition='inside', textinfo='percent+label',
                                           hovertemplate='%{label}<br>%{customdata[0]}<extra></extra>')
                    st.plotly_chart(fig_state, use_container_width=True, key="pie_state")
                    
                    # Add dropdown selector for state BELOW the chart
                    st.markdown("**Select States to View Details**")
                    available_states = state_rev['State'].tolist()
                    selected_states = st.multiselect(
                        "Choose states",
                        available_states,
                        default=[available_states[0]] if available_states else [],
                        key="state_detail_select"
                    )
                    
                    # Get details for selected states
                    if selected_states:
                        state_details_data = []
                        for state in selected_states:
                            state_data = state_rev[state_rev['State'] == state]
                            if not state_data.empty:
                                state_info = state_data.iloc[0]
                                state_details_data.append({
                                    'State': state,
                                    'Revenue': state_info['Formatted']
                                })
                        
                        if state_details_data:
                            state_details_df = pd.DataFrame(state_details_data)
                            st.dataframe(state_details_df, use_container_width=True, hide_index=True)
                else:
                    st.info("No state revenue data available")
            
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
                    fig_trend.update_yaxes(tickformat=',.0f')
                    fig_trend.update_traces(hovertemplate='%{x}<br>%{customdata[0]}<extra></extra>')
                    st.plotly_chart(fig_trend, use_container_width=True, key="trend_monthly")
                else:
                    st.info("No monthly trend data available")
            
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
                        fig_cat.update_xaxes(tickformat=',.0f')
                        st.plotly_chart(fig_cat, use_container_width=True, key="cat_rev_bar")
                    else:
                        st.info("No category revenue data available")
            
            with trend_col2:
                if 'Category' in df.columns and selected_qty_col and selected_qty_col in df.columns:
                    cat_qty = df.groupby('Category')[selected_qty_col].sum().reset_index()
                    cat_qty = cat_qty[cat_qty[selected_qty_col] > 0].sort_values(selected_qty_col, ascending=True)
                    if not cat_qty.empty:
                        cat_qty['Formatted'] = cat_qty[selected_qty_col].apply(format_qty)
                        fig_cat_qty = px.bar(cat_qty, x=selected_qty_col, y='Category', orientation='h',
                                            title="Quantity by Category", text='Formatted', custom_data=['Formatted'])
                        fig_cat_qty.update_traces(textposition='outside', hovertemplate='%{y}<br>%{customdata[0]}<extra></extra>')
                        fig_cat_qty.update_xaxes(tickformat=',.0f')
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
                            fig_subcat.update_yaxes(tickformat=',.0f')
                            st.plotly_chart(fig_subcat, use_container_width=True, key="subcat_bar")
                        else:
                            st.info("No revenue data for selected sub-categories")
                    else:
                        st.info("Please select at least one sub-category")
                else:
                    st.info("No sub-categories available")
    
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
                fig_state.update_yaxes(tickformat=',.0f')
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
                            fig_city.update_yaxes(tickformat=',.0f')
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
                                        fig_cust.update_yaxes(tickformat=',.0f')
                                        st.plotly_chart(fig_cust, use_container_width=True, key="seg_cust_bar")
                                        
                                        st.dataframe(cust_summary[['Customer', 'Formatted']], use_container_width=True)
            
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
                    fig_exec.update_yaxes(tickformat=',.0f')
                    st.plotly_chart(fig_exec, use_container_width=True, key="seg_exec_bar")
    
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
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                hide_null = st.checkbox("Hide null/zero revenue items", value=True, key="sales_hide_null")
            with col2:
                nonmov_analysis_view = st.selectbox("View by", ["Overall", "Category-wise", "State-wise"], key="nonmov_view_type")
            with col3:
                nonmov_limit = get_display_limit("nonmov_limit", default=20)
            
            prod_col = 'Product Name' if 'Product Name' in df.columns else 'Item Name' if 'Item Name' in df.columns else 'Sub Category' if 'Sub Category' in df.columns else None
            
            if not prod_col:
                st.warning("No product/item column found for analysis")
            else:
                # OVERALL VIEW
                if nonmov_analysis_view == "Overall":
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### Non-Moving (Zero Sales)")
                        product_sales = df.groupby(prod_col)[analysis_value_col].sum().reset_index()
                        non_moving = product_sales[product_sales[analysis_value_col] == 0]
                        
                        st.metric("Non-Moving Products", len(non_moving))
                        if len(non_moving) > 0:
                            display_non_moving = apply_limit(non_moving, nonmov_limit)
                            st.dataframe(display_non_moving, use_container_width=True)
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
                                display_slow = apply_limit(slow_moving, nonmov_limit)
                                fig_slow = px.bar(display_slow, x=prod_col, y=analysis_value_col,
                                                 title="Slow-Moving Items", text='Formatted', custom_data=['Formatted'])
                                fig_slow.update_traces(textposition='outside', hovertemplate='%{x}<br>%{customdata[0]}<extra></extra>')
                                fig_slow.update_layout(xaxis_tickangle=-45)
                                fig_slow.update_yaxes(tickformat=',.0f')
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
                
                # CATEGORY-WISE VIEW
                elif nonmov_analysis_view == "Category-wise":
                    if 'Category' in df.columns:
                        all_categories = df['Category'].dropna().unique().tolist()
                        all_categories = sorted(all_categories)
                        
                        selected_cat_nonmov = st.selectbox("Select Category", all_categories, key="nonmov_cat_select")
                        
                        if selected_cat_nonmov:
                            cat_df = df[df['Category'] == selected_cat_nonmov]
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown(f"#### Non-Moving in {selected_cat_nonmov}")
                                cat_product_sales = cat_df.groupby(prod_col)[analysis_value_col].sum().reset_index()
                                cat_non_moving = cat_product_sales[cat_product_sales[analysis_value_col] == 0]
                                
                                st.metric("Non-Moving Products", len(cat_non_moving))
                                if len(cat_non_moving) > 0:
                                    display_cat_non_moving = apply_limit(cat_non_moving, nonmov_limit)
                                    st.dataframe(display_cat_non_moving, use_container_width=True)
                                else:
                                    st.success("No non-moving items in this category!")
                            
                            with col2:
                                st.markdown(f"#### Slow-Moving in {selected_cat_nonmov}")
                                cat_product_sales = cat_df.groupby(prod_col)[analysis_value_col].sum().reset_index()
                                if hide_null:
                                    cat_product_sales = cat_product_sales[cat_product_sales[analysis_value_col] > 0]
                                
                                if cat_product_sales.empty:
                                    st.info("No product sales data in this category")
                                else:
                                    cat_avg_sales = cat_product_sales[analysis_value_col].mean()
                                    cat_slow_moving = cat_product_sales[
                                        (cat_product_sales[analysis_value_col] > 0) & 
                                        (cat_product_sales[analysis_value_col] < cat_avg_sales * 0.5)
                                    ].sort_values(analysis_value_col)
                                    
                                    cat_slow_moving['Formatted'] = cat_slow_moving[analysis_value_col].apply(format_inr)
                                    
                                    st.metric("Slow-Moving Products", len(cat_slow_moving))
                                    st.caption(f"Average: {format_inr(cat_avg_sales)}")
                                    
                                    if len(cat_slow_moving) > 0:
                                        display_cat_slow = apply_limit(cat_slow_moving, nonmov_limit)
                                        fig_cat_slow = px.bar(display_cat_slow, x=prod_col, y=analysis_value_col,
                                                             title=f"Slow-Moving Items in {selected_cat_nonmov}", text='Formatted', 
                                                             custom_data=['Formatted'])
                                        fig_cat_slow.update_traces(textposition='outside', hovertemplate='%{x}<br>%{customdata[0]}<extra></extra>')
                                        fig_cat_slow.update_layout(xaxis_tickangle=-45)
                                        fig_cat_slow.update_yaxes(tickformat=',.0f')
                                        st.plotly_chart(fig_cat_slow, use_container_width=True, key="slow_moving_cat_bar")
                                    else:
                                        st.success("No slow-moving items in this category!")
                            
                            st.markdown("---")
                            st.markdown(f"#### Sub-Category Status in {selected_cat_nonmov}")
                            if 'Sub Category' in df.columns:
                                subcat_analysis = cat_df.groupby('Sub Category').agg({
                                    analysis_value_col: ['sum', 'count', lambda x: (x == 0).sum()]
                                }).reset_index()
                                subcat_analysis.columns = ['Sub Category', 'Total Revenue', 'Total Items', 'Zero Sales']
                                subcat_analysis['Non-Moving %'] = (subcat_analysis['Zero Sales'] / subcat_analysis['Total Items'] * 100).round(1)
                                subcat_analysis['Formatted'] = subcat_analysis['Total Revenue'].apply(format_inr)
                                
                                if subcat_analysis.empty:
                                    st.info("No sub-category data available")
                                else:
                                    fig_subcat = px.bar(subcat_analysis, x='Sub Category', y='Non-Moving %',
                                                       title=f"Non-Moving % by Sub-Category in {selected_cat_nonmov}", 
                                                       color='Non-Moving %',
                                                       color_continuous_scale='Oranges')
                                    fig_subcat.update_layout(xaxis_tickangle=-45)
                                    st.plotly_chart(fig_subcat, use_container_width=True, key="nonmov_subcat_bar")
                
                # STATE-WISE VIEW
                elif nonmov_analysis_view == "State-wise":
                    if 'State' in df.columns:
                        all_states = df['State'].dropna().unique().tolist()
                        all_states = sorted(all_states)
                        
                        selected_state_nonmov = st.selectbox("Select State", all_states, key="nonmov_state_select")
                        
                        if selected_state_nonmov:
                            state_df = df[df['State'] == selected_state_nonmov]
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown(f"#### Non-Moving in {selected_state_nonmov}")
                                state_product_sales = state_df.groupby(prod_col)[analysis_value_col].sum().reset_index()
                                state_non_moving = state_product_sales[state_product_sales[analysis_value_col] == 0]
                                
                                st.metric("Non-Moving Products", len(state_non_moving))
                                if len(state_non_moving) > 0:
                                    display_state_non_moving = apply_limit(state_non_moving, nonmov_limit)
                                    st.dataframe(display_state_non_moving, use_container_width=True)
                                else:
                                    st.success("No non-moving items in this state!")
                            
                            with col2:
                                st.markdown(f"#### Slow-Moving in {selected_state_nonmov}")
                                state_product_sales = state_df.groupby(prod_col)[analysis_value_col].sum().reset_index()
                                if hide_null:
                                    state_product_sales = state_product_sales[state_product_sales[analysis_value_col] > 0]
                                
                                if state_product_sales.empty:
                                    st.info("No product sales data in this state")
                                else:
                                    state_avg_sales = state_product_sales[analysis_value_col].mean()
                                    state_slow_moving = state_product_sales[
                                        (state_product_sales[analysis_value_col] > 0) & 
                                        (state_product_sales[analysis_value_col] < state_avg_sales * 0.5)
                                    ].sort_values(analysis_value_col)
                                    
                                    state_slow_moving['Formatted'] = state_slow_moving[analysis_value_col].apply(format_inr)
                                    
                                    st.metric("Slow-Moving Products", len(state_slow_moving))
                                    st.caption(f"Average: {format_inr(state_avg_sales)}")
                                    
                                    if len(state_slow_moving) > 0:
                                        display_state_slow = apply_limit(state_slow_moving, nonmov_limit)
                                        fig_state_slow = px.bar(display_state_slow, x=prod_col, y=analysis_value_col,
                                                               title=f"Slow-Moving Items in {selected_state_nonmov}", text='Formatted', 
                                                               custom_data=['Formatted'])
                                        fig_state_slow.update_traces(textposition='outside', hovertemplate='%{x}<br>%{customdata[0]}<extra></extra>')
                                        fig_state_slow.update_layout(xaxis_tickangle=-45)
                                        fig_state_slow.update_yaxes(tickformat=',.0f')
                                        st.plotly_chart(fig_state_slow, use_container_width=True, key="slow_moving_state_bar")
                                    else:
                                        st.success("No slow-moving items in this state!")
                            
                            st.markdown("---")
                            st.markdown(f"#### Category Status in {selected_state_nonmov}")
                            if 'Category' in df.columns:
                                state_cat_analysis = state_df.groupby('Category').agg({
                                    analysis_value_col: ['sum', 'count', lambda x: (x == 0).sum()]
                                }).reset_index()
                                state_cat_analysis.columns = ['Category', 'Total Revenue', 'Total Items', 'Zero Sales']
                                state_cat_analysis['Non-Moving %'] = (state_cat_analysis['Zero Sales'] / state_cat_analysis['Total Items'] * 100).round(1)
                                state_cat_analysis['Formatted'] = state_cat_analysis['Total Revenue'].apply(format_inr)
                                
                                if state_cat_analysis.empty:
                                    st.info("No category data available")
                                else:
                                    fig_state_cat = px.bar(state_cat_analysis, x='Category', y='Non-Moving %',
                                                           title=f"Non-Moving % by Category in {selected_state_nonmov}", 
                                                           color='Non-Moving %',
                                                           color_continuous_scale='Reds')
                                    st.plotly_chart(fig_state_cat, use_container_width=True, key="nonmov_state_cat_bar")
                            else:
                                st.info("Category column not found")
    
    # 1.4 Cross-Selling Analytics
    with sales_sub4:
        st.subheader("Cross-Selling Analytics")
        
        if 'Dealer Name' in df.columns and 'Category' in df.columns and VALUE_COL:
            # For API data, use single Value column; for Excel, allow year selection
            if len(VALUE_COLS) > 1:
                cross_value_col = st.selectbox("Select Year", VALUE_COLS, key="cross_year")
            else:
                cross_value_col = VALUE_COL
            
            # Analysis type selector
            analysis_type = st.radio("Analyze by", ["Category", "Sub Category"], horizontal=True, key="cross_analysis_type")
            
            if analysis_type == "Category":
                group_col = 'Category'
            else:
                group_col = 'Sub Category' if 'Sub Category' in df.columns else 'Category'
                if 'Sub Category' not in df.columns:
                    st.warning("Sub Category column not found, using Category instead")
            
            customer_groups = df.groupby(['Dealer Name', group_col])[cross_value_col].sum().unstack(fill_value=0)
            
            if customer_groups.empty:
                st.info("No cross-selling data available")
            else:
                st.markdown(f"#### Customers Buying X but not Y (by {group_col})")
                group_options = df[group_col].dropna().unique().tolist()
                
                if len(group_options) < 2:
                    st.info(f"Need at least 2 {group_col.lower()}s for cross-selling analysis")
                else:
                    col1, col2, col3 = st.columns([2, 2, 1])
                    with col1:
                        group_x = st.selectbox(f"Customers who buy", group_options, key="group_x")
                    with col2:
                        group_y = st.selectbox(f"But don't buy", group_options, key="group_y")
                    with col3:
                        cross_sell_limit = get_display_limit("cross_sell_limit", default=10)
                    
                    if group_x == group_y:
                        st.info("Please select different options for comparison")
                    elif group_x not in customer_groups.columns:
                        st.info(f"No data available for: {group_x}")
                    elif group_y not in customer_groups.columns:
                        st.info(f"No data available for: {group_y}")
                    else:
                        buying_x = customer_groups[customer_groups[group_x] > 0]
                        not_buying_y = buying_x[buying_x[group_y] == 0]
                        
                        st.metric(f"Customers buying {group_x} but not {group_y}", len(not_buying_y))
                        
                        if len(not_buying_y) > 0:
                            opportunity = pd.DataFrame({
                                'Customer': not_buying_y.index,
                                f'{group_x} Revenue': not_buying_y[group_x].values
                            })
                            opportunity['Formatted'] = opportunity[f'{group_x} Revenue'].apply(format_inr)
                            opportunity = opportunity.sort_values(f'{group_x} Revenue', ascending=False)
                            
                            display_opportunity = apply_limit(opportunity, cross_sell_limit)
                            title_suffix = f"Top {cross_sell_limit}" if cross_sell_limit else "All"
                            fig_opp = px.bar(display_opportunity, x='Customer', y=f'{group_x} Revenue',
                                            title=f"{title_suffix} Cross-Sell Opportunities for {group_y}", text='Formatted',
                                            custom_data=['Formatted'])
                            fig_opp.update_traces(textposition='outside', hovertemplate='%{x}<br>%{customdata[0]}<extra></extra>')
                            fig_opp.update_layout(xaxis_tickangle=-45)
                            fig_opp.update_yaxes(tickformat=',.0f')
                            st.plotly_chart(fig_opp, use_container_width=True, key="cross_sell_bar")
                        else:
                            st.info(f"All customers buying {group_x} are also buying {group_y}")
                
                st.markdown("---")
                st.markdown(f"#### Product Mix - Top Customers (by {group_col})")
                mix_limit = get_display_limit("mix_limit", default=10)
                top_custs_for_mix = df.groupby('Dealer Name')[cross_value_col].sum().sort_values(ascending=False)
                top_custs_for_mix = apply_limit(top_custs_for_mix, mix_limit).index.tolist()
                mix_data = customer_groups.loc[customer_groups.index.isin(top_custs_for_mix)]
                
                if mix_data.empty:
                    st.info("No product mix data available for top customers")
                else:
                    # Create options for category selection
                    all_categories = list(mix_data.columns)
                    default_categories = all_categories[:5] if len(all_categories) > 5 else all_categories
                    
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        selected_mix_categories = st.multiselect(
                            f"Select {group_col}s to display", 
                            all_categories, 
                            default=default_categories,
                            key="mix_category_selector"
                        )
                    with col2:
                        mix_display_type = st.selectbox("Show by", ["Value", "Revenue", "Quantity", "%"], key="mix_display_type")
                    
                    if selected_mix_categories:
                        # Filter mix_data for selected categories
                        mix_data_filtered = mix_data[selected_mix_categories]
                        
                        # Prepare data for visualization based on display type
                        if mix_display_type == "Value":
                            # Display actual values
                            mix_values = mix_data_filtered.reset_index().melt(id_vars='Dealer Name', var_name=group_col, value_name='Value')
                            mix_melted = mix_values.copy()
                            mix_melted['Label'] = mix_melted.apply(
                                lambda row: f"{format_inr(row['Value'])}" if row['Value'] > 0 else "Rs. 0",
                                axis=1
                            )
                            fig_mix = px.bar(mix_melted, x='Dealer Name', y='Value', color=group_col,
                                            title=f"{group_col} Mix (by Value) - Top Customers", barmode='stack')
                            fig_mix.update_layout(xaxis_tickangle=-45, yaxis_title="Value (Rs.)")
                            fig_mix.update_yaxes(tickformat=',.0f')
                            fig_mix.update_traces(
                                text=mix_melted['Label'],
                                textposition='inside',
                                hovertemplate='<b>%{fullData.name}</b><br>Customer: %{x}<br>%{customdata[0]}<extra></extra>',
                                customdata=mix_melted[['Label']].values
                            )
                        elif mix_display_type == "Revenue":
                            # Display revenue (same as Value, but with different label for clarity)
                            mix_revenue = mix_data_filtered.reset_index().melt(id_vars='Dealer Name', var_name=group_col, value_name='Revenue')
                            mix_melted = mix_revenue.copy()
                            mix_melted['Label'] = mix_melted.apply(
                                lambda row: f"{format_inr(row['Revenue'])}" if row['Revenue'] > 0 else "Rs. 0",
                                axis=1
                            )
                            fig_mix = px.bar(mix_melted, x='Dealer Name', y='Revenue', color=group_col,
                                            title=f"{group_col} Mix (by Revenue) - Top Customers", barmode='stack')
                            fig_mix.update_layout(xaxis_tickangle=-45, yaxis_title="Revenue (Rs.)")
                            fig_mix.update_yaxes(tickformat=',.0f')
                            fig_mix.update_traces(
                                text=mix_melted['Label'],
                                textposition='inside',
                                hovertemplate='<b>%{fullData.name}</b><br>Customer: %{x}<br>%{customdata[0]}<extra></extra>',
                                customdata=mix_melted[['Label']].values
                            )
                        elif mix_display_type == "Quantity":
                            # Display quantity data
                            qty_col_check = selected_value_col.replace('Value', 'Qty') if 'Value' in selected_value_col else QTY_COL if QTY_COL else None
                            if qty_col_check and qty_col_check in df.columns:
                                # Build quantity matrix similar to mix_data
                                qty_data = df.groupby(['Dealer Name', group_col])[qty_col_check].sum().unstack(fill_value=0)
                                qty_data_filtered = qty_data.loc[qty_data.index.isin(top_custs_for_mix), selected_mix_categories]
                                mix_qty = qty_data_filtered.reset_index().melt(id_vars='Dealer Name', var_name=group_col, value_name='Quantity')
                                mix_melted = mix_qty.copy()
                                mix_melted['Label'] = mix_melted.apply(
                                    lambda row: f"{format_qty(row['Quantity'])}" if row['Quantity'] > 0 else "0",
                                    axis=1
                                )
                                fig_mix = px.bar(mix_melted, x='Dealer Name', y='Quantity', color=group_col,
                                                title=f"{group_col} Mix (by Quantity) - Top Customers", barmode='stack')
                                fig_mix.update_layout(xaxis_tickangle=-45, yaxis_title="Quantity")
                                fig_mix.update_yaxes(tickformat=',.0f')
                                fig_mix.update_traces(
                                    text=mix_melted['Label'],
                                    textposition='inside',
                                    hovertemplate='<b>%{fullData.name}</b><br>Customer: %{x}<br>%{customdata[0]}<extra></extra>',
                                    customdata=mix_melted[['Label']].values
                                )
                            else:
                                st.warning("Quantity data not available for selected period")
                                fig_mix = None
                        else:
                            # Display percentages
                            mix_pct = mix_data_filtered.div(mix_data_filtered.sum(axis=1), axis=0) * 100
                            mix_melted = mix_pct.reset_index().melt(id_vars='Dealer Name', var_name=group_col, value_name='%')
                            mix_melted['Label'] = mix_melted['%'].apply(lambda x: f"{x:.1f}%")
                            fig_mix = px.bar(mix_melted, x='Dealer Name', y='%', color=group_col,
                                            title=f"{group_col} Mix (%) - Top Customers", barmode='stack')
                            fig_mix.update_layout(xaxis_tickangle=-45)
                            fig_mix.update_traces(
                                hovertemplate='<b>%{fullData.name}</b><br>Customer: %{x}<br>%{y:.1f}%<extra></extra>'
                            )
                        
                        if fig_mix is not None:
                            st.plotly_chart(fig_mix, use_container_width=True, key="product_mix_bar")
                        
                        # Dealer Drill-Down Section
                        st.markdown("---")
                        st.markdown(f"#### Drill-Down by Dealer (by {group_col})")
                        
                        dealer_options = list(top_custs_for_mix)
                        selected_dealer = st.selectbox(
                            "Select a dealer to view detailed breakdown",
                            dealer_options,
                            key="drill_down_dealer"
                        )
                        
                        if selected_dealer:
                            dealer_detail = mix_data_filtered.loc[selected_dealer]
                            
                            # Create two columns for detail view
                            detail_col1, detail_col2 = st.columns(2)
                            
                            with detail_col1:
                                st.subheader(f"📊 Dealer: {selected_dealer}")
                                
                                # Show breakdown by selected metric
                                if mix_display_type == "Value":
                                    dealer_breakdown = pd.DataFrame({
                                        group_col: dealer_detail.index,
                                        'Value': dealer_detail.values
                                    }).sort_values('Value', ascending=False)
                                    dealer_breakdown['Formatted'] = dealer_breakdown['Value'].apply(format_inr)
                                    dealer_breakdown['%'] = (dealer_breakdown['Value'] / dealer_breakdown['Value'].sum() * 100).round(1)
                                    
                                    fig_dealer_pie = px.pie(dealer_breakdown, values='Value', names=group_col,
                                                           title=f"{selected_dealer} - {group_col} Mix (by Value)",
                                                           custom_data=['Formatted', '%'])
                                    fig_dealer_pie.update_traces(
                                        hovertemplate='<b>%{label}</b><br>Value: %{customdata[0]}<br>%{customdata[1]:.1f}%<extra></extra>'
                                    )
                                    st.plotly_chart(fig_dealer_pie, use_container_width=True, key=f"dealer_pie_{selected_dealer}")
                                
                                elif mix_display_type == "Revenue":
                                    dealer_breakdown = pd.DataFrame({
                                        group_col: dealer_detail.index,
                                        'Revenue': dealer_detail.values
                                    }).sort_values('Revenue', ascending=False)
                                    dealer_breakdown['Formatted'] = dealer_breakdown['Revenue'].apply(format_inr)
                                    dealer_breakdown['%'] = (dealer_breakdown['Revenue'] / dealer_breakdown['Revenue'].sum() * 100).round(1)
                                    
                                    fig_dealer_pie = px.pie(dealer_breakdown, values='Revenue', names=group_col,
                                                           title=f"{selected_dealer} - {group_col} Mix (by Revenue)",
                                                           custom_data=['Formatted', '%'])
                                    fig_dealer_pie.update_traces(
                                        hovertemplate='<b>%{label}</b><br>Revenue: %{customdata[0]}<br>%{customdata[1]:.1f}%<extra></extra>'
                                    )
                                    st.plotly_chart(fig_dealer_pie, use_container_width=True, key=f"dealer_pie_{selected_dealer}")
                                
                                elif mix_display_type == "Quantity":
                                    qty_col_check = selected_value_col.replace('Value', 'Qty') if 'Value' in selected_value_col else QTY_COL if QTY_COL else None
                                    if qty_col_check and qty_col_check in df.columns:
                                        qty_detail = df[df['Dealer Name'] == selected_dealer].groupby(group_col)[qty_col_check].sum()
                                        dealer_breakdown = pd.DataFrame({
                                            group_col: qty_detail.index,
                                            'Quantity': qty_detail.values
                                        }).sort_values('Quantity', ascending=False)
                                        dealer_breakdown['Formatted'] = dealer_breakdown['Quantity'].apply(format_qty)
                                        dealer_breakdown['%'] = (dealer_breakdown['Quantity'] / dealer_breakdown['Quantity'].sum() * 100).round(1)
                                        
                                        fig_dealer_pie = px.pie(dealer_breakdown, values='Quantity', names=group_col,
                                                               title=f"{selected_dealer} - {group_col} Mix (by Quantity)",
                                                               custom_data=['Formatted', '%'])
                                        fig_dealer_pie.update_traces(
                                            hovertemplate='<b>%{label}</b><br>Qty: %{customdata[0]}<br>%{customdata[1]:.1f}%<extra></extra>'
                                        )
                                        st.plotly_chart(fig_dealer_pie, use_container_width=True, key=f"dealer_pie_{selected_dealer}")
                                
                                else:  # Percentage
                                    dealer_breakdown = pd.DataFrame({
                                        group_col: dealer_detail.index,
                                        'Value': dealer_detail.values
                                    }).sort_values('Value', ascending=False)
                                    dealer_breakdown['%'] = (dealer_breakdown['Value'] / dealer_breakdown['Value'].sum() * 100).round(1)
                                    dealer_breakdown['Formatted'] = dealer_breakdown['%'].apply(lambda x: f"{x:.1f}%")
                                    
                                    fig_dealer_pie = px.pie(dealer_breakdown, values='Value', names=group_col,
                                                           title=f"{selected_dealer} - {group_col} Mix (%)",
                                                           custom_data=['%'])
                                    fig_dealer_pie.update_traces(
                                        hovertemplate='<b>%{label}</b><br>%{customdata[0]:.1f}%<extra></extra>'
                                    )
                                    st.plotly_chart(fig_dealer_pie, use_container_width=True, key=f"dealer_pie_{selected_dealer}")
                            
                            with detail_col2:
                                st.subheader(f"📋 Detailed Breakdown")
                                st.dataframe(dealer_breakdown[[group_col, 'Formatted', '%']], use_container_width=True)
                                
                                # Show summary metrics
                                st.markdown("**Summary**")
                                total_val = dealer_breakdown['Value'].sum() if 'Value' in dealer_breakdown.columns else dealer_breakdown['Revenue'].sum() if 'Revenue' in dealer_breakdown.columns else dealer_breakdown['Quantity'].sum()
                                st.metric("Total Value", format_inr(total_val) if mix_display_type in ["Value", "Revenue"] else format_qty(total_val))
                                st.metric(f"Number of {group_col}s", len(dealer_breakdown))
                                st.metric("Top Category", dealer_breakdown[group_col].iloc[0] if len(dealer_breakdown) > 0 else "N/A")
                    else:
                        st.info(f"Please select at least one {group_col}")
    
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
            
            col1, col2 = st.columns([3, 1])
            with col1:
                decline_threshold = st.slider("Decline Threshold (%)", 10, 90, 30, key="decline_thresh")
            with col2:
                dropoff_limit = get_display_limit("dropoff_limit", default=20)
            
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
                    display_declined = apply_limit(declined, dropoff_limit)
                    fig_dec = px.bar(display_declined, x=prod_col, y='Change %',
                                    title=f"Products with >{decline_threshold}% Decline",
                                    color='Change %', color_continuous_scale='Reds_r')
                    fig_dec.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig_dec, use_container_width=True, key="dropoff_bar")
                    
                    st.dataframe(display_declined[[prod_col, 'Previous', 'Current', 'Change %']], use_container_width=True)
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
    
    # 1.6 Day & Date-wise Analytics
    with sales_sub6:
        st.subheader("Day & Date-wise Analytics")
        
        if not VALUE_COL:
            st.warning("No value columns found in the dataset")
        else:
            # For API data, use single Value column; for Excel, allow year selection
            if len(VALUE_COLS) > 1:
                date_value_col = st.selectbox("Select Year", VALUE_COLS, key="date_year_select")
            else:
                date_value_col = VALUE_COL
            
            # Check if Date column exists
            has_date = 'Date' in df.columns or 'Transaction Date' in df.columns or 'Order Date' in df.columns
            
            if not has_date:
                st.info("📅 No specific date column found in the dataset.")
                st.info("The current data appears to be aggregated at period level (Year/Month format).")
                
                # Show period-wise analysis instead
                st.markdown("#### Period-wise Analysis")
                if 'Month' in df.columns:
                    period_data = df.groupby('Month')[date_value_col].sum().reset_index()
                    period_data = period_data[period_data[date_value_col] > 0].sort_values(date_value_col, ascending=False)
                    
                    if not period_data.empty:
                        period_data['Formatted'] = period_data[date_value_col].apply(format_inr)
                        
                        fig_period = px.bar(period_data, x='Month', y=date_value_col,
                                          title="Revenue by Month", text='Formatted',
                                          color=date_value_col, color_continuous_scale='Viridis',
                                          custom_data=['Formatted'])
                        fig_period.update_traces(textposition='outside', hovertemplate='%{x}<br>%{customdata[0]}<extra></extra>')
                        fig_period.update_layout(xaxis_tickangle=-45)
                        fig_period.update_yaxes(tickformat=',.0f')
                        st.plotly_chart(fig_period, use_container_width=True, key="period_bar")
                        
                        # Show table view
                        st.markdown("#### Monthly Summary")
                        summary_df = period_data[['Month', 'Formatted']].copy()
                        summary_df.columns = ['Month', 'Revenue']
                        st.dataframe(summary_df, use_container_width=True)
                    else:
                        st.info("No monthly data available")
                else:
                    st.info("No month or date data available in the dataset")
                
                st.markdown("---")
                st.markdown("#### Dealer Activity by Period")
                if 'Dealer Name' in df.columns and 'Month' in df.columns:
                    dealer_period = df.groupby(['Month', 'Dealer Name'])[date_value_col].sum().reset_index()
                    dealer_period = dealer_period[dealer_period[date_value_col] > 0]
                    
                    if not dealer_period.empty:
                        # Get top dealers
                        top_dealers_period = df.groupby('Dealer Name')[date_value_col].sum().nlargest(5).index.tolist()
                        dealer_period_filtered = dealer_period[dealer_period['Dealer Name'].isin(top_dealers_period)]
                        
                        dealer_period_filtered['Formatted'] = dealer_period_filtered[date_value_col].apply(format_inr)
                        
                        fig_dealer_period = px.line(dealer_period_filtered, x='Month', y=date_value_col, 
                                                   color='Dealer Name', markers=True,
                                                   title="Top 5 Dealers - Monthly Trend",
                                                   custom_data=['Formatted'])
                        fig_dealer_period.update_traces(hovertemplate='%{x}<br>%{fullData.name}<br>%{customdata[0]}<extra></extra>')
                        fig_dealer_period.update_yaxes(tickformat=',.0f')
                        st.plotly_chart(fig_dealer_period, use_container_width=True, key="dealer_period_line")
                    else:
                        st.info("No dealer period data available")
                else:
                    st.info("Dealer Name or Month column not found")
            
            else:
                # Process date data
                date_col = None
                if 'Date' in df.columns:
                    date_col = 'Date'
                elif 'Transaction Date' in df.columns:
                    date_col = 'Transaction Date'
                elif 'Order Date' in df.columns:
                    date_col = 'Order Date'
                
                # Convert to datetime
                try:
                    df_date = df.copy()
                    df_date[date_col] = pd.to_datetime(df_date[date_col], errors='coerce')
                    df_date = df_date[df_date[date_col].notna()]
                    
                    if df_date.empty:
                        st.warning("Could not parse dates properly")
                    else:
                        # Add helper columns
                        df_date['Date Only'] = df_date[date_col].dt.date
                        df_date['Day Name'] = df_date[date_col].dt.day_name()
                        df_date['Week Number'] = df_date[date_col].dt.isocalendar().week
                        df_date['Day of Month'] = df_date[date_col].dt.day
                        
                        # Tabs for different views
                        date_view1, date_view2, date_view3, date_view4 = st.tabs(
                            ["Daily Analysis", "Weekday Analysis", "Weekly Analysis", "Calendar Heatmap"]
                        )
                        
                        with date_view1:
                            st.markdown("#### Daily Revenue Trend")
                            daily_data = df_date.groupby('Date Only')[date_value_col].sum().reset_index()
                            daily_data = daily_data[daily_data[date_value_col] > 0].sort_values('Date Only')
                            daily_data['Formatted'] = daily_data[date_value_col].apply(format_inr)
                            
                            if not daily_data.empty:
                                fig_daily = px.line(daily_data, x='Date Only', y=date_value_col,
                                                   title="Daily Revenue Trend", markers=True,
                                                   custom_data=['Formatted'])
                                fig_daily.update_layout(xaxis_title="Date", yaxis_title="Revenue")
                                fig_daily.update_traces(hovertemplate='%{x}<br>%{customdata[0]}<extra></extra>')
                                fig_daily.update_yaxes(tickformat=',.0f')
                                st.plotly_chart(fig_daily, use_container_width=True, key="daily_trend")
                                
                                # Top days
                                st.markdown("#### Top 10 Best Days")
                                top_daily = daily_data.nlargest(10, date_value_col)[['Date Only', 'Formatted']].copy()
                                top_daily.columns = ['Date', 'Revenue']
                                st.dataframe(top_daily, use_container_width=True)
                            else:
                                st.info("No daily data available")
                        
                        with date_view2:
                            st.markdown("#### Weekday Analysis")
                            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                            weekday_data = df_date.groupby('Day Name')[date_value_col].sum().reset_index()
                            weekday_data['Day Name'] = pd.Categorical(weekday_data['Day Name'], categories=day_order, ordered=True)
                            weekday_data = weekday_data.sort_values('Day Name')
                            weekday_data['Formatted'] = weekday_data[date_value_col].apply(format_inr)
                            weekday_data['Count'] = df_date.groupby('Day Name').size().values
                            
                            if not weekday_data.empty:
                                # Revenue by weekday
                                fig_weekday = px.bar(weekday_data, x='Day Name', y=date_value_col,
                                                    title="Revenue by Weekday", text='Formatted',
                                                    color=date_value_col, color_continuous_scale='Blues',
                                                    custom_data=['Formatted', 'Count'])
                                fig_weekday.update_traces(
                                    textposition='outside',
                                    hovertemplate='<b>%{x}</b><br>Revenue: %{customdata[0]}<br>Transactions: %{customdata[1]}<extra></extra>'
                                )
                                fig_weekday.update_layout(xaxis_title="Day of Week")
                                fig_weekday.update_yaxes(tickformat=',.0f')
                                st.plotly_chart(fig_weekday, use_container_width=True, key="weekday_bar")
                                
                                # Summary table
                                summary_weekday = weekday_data[['Day Name', 'Formatted', 'Count']].copy()
                                summary_weekday.columns = ['Day', 'Revenue', 'Transactions']
                                st.dataframe(summary_weekday, use_container_width=True)
                            else:
                                st.info("No weekday data available")
                        
                        with date_view3:
                            st.markdown("#### Weekly Analysis")
                            weekly_data = df_date.groupby('Week Number')[date_value_col].sum().reset_index()
                            weekly_data = weekly_data[weekly_data[date_value_col] > 0].sort_values('Week Number')
                            weekly_data['Formatted'] = weekly_data[date_value_col].apply(format_inr)
                            weekly_data['Week'] = 'Week ' + weekly_data['Week Number'].astype(str)
                            
                            if not weekly_data.empty:
                                fig_weekly = px.bar(weekly_data, x='Week', y=date_value_col,
                                                   title="Revenue by Week", text='Formatted',
                                                   color=date_value_col, color_continuous_scale='Greens',
                                                   custom_data=['Formatted'])
                                fig_weekly.update_traces(textposition='outside', hovertemplate='%{x}<br>%{customdata[0]}<extra></extra>')
                                fig_weekly.update_yaxes(tickformat=',.0f')
                                st.plotly_chart(fig_weekly, use_container_width=True, key="weekly_bar")
                                
                                # Summary
                                summary_weekly = weekly_data[['Week', 'Formatted']].copy()
                                summary_weekly.columns = ['Week', 'Revenue']
                                st.dataframe(summary_weekly, use_container_width=True)
                            else:
                                st.info("No weekly data available")
                        
                        with date_view4:
                            st.markdown("#### Calendar Heatmap (Day of Month)")
                            day_month_data = df_date.groupby('Day of Month')[date_value_col].sum().reset_index()
                            day_month_data = day_month_data[day_month_data[date_value_col] > 0]
                            day_month_data['Formatted'] = day_month_data[date_value_col].apply(format_inr)
                            
                            if not day_month_data.empty:
                                fig_calendar = px.bar(day_month_data, x='Day of Month', y=date_value_col,
                                                     title="Revenue by Day of Month", text='Formatted',
                                                     color=date_value_col, color_continuous_scale='Oranges',
                                                     custom_data=['Formatted'])
                                fig_calendar.update_traces(textposition='outside', hovertemplate='Day %{x}<br>%{customdata[0]}<extra></extra>')
                                fig_calendar.update_layout(xaxis_title="Day of Month (1-31)")
                                fig_calendar.update_yaxes(tickformat=',.0f')
                                st.plotly_chart(fig_calendar, use_container_width=True, key="calendar_bar")
                                
                                # Insights
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    best_day = day_month_data.loc[day_month_data[date_value_col].idxmax()]
                                    st.metric("🏆 Best Day of Month", f"Day {int(best_day['Day of Month'])}", best_day['Formatted'])
                                with col2:
                                    worst_day = day_month_data.loc[day_month_data[date_value_col].idxmin()]
                                    st.metric("📉 Lowest Day", f"Day {int(worst_day['Day of Month'])}", worst_day['Formatted'])
                                with col3:
                                    avg_revenue = day_month_data[date_value_col].mean()
                                    st.metric("📊 Average Daily", format_inr(avg_revenue))
                            else:
                                st.info("No day-of-month data available")
                
                except Exception as e:
                    st.error(f"Error processing date data: {str(e)}")
    
    # 1.7 State-wise Revenue Analysis
    with sales_sub7:
        st.subheader("State-wise Revenue Analysis")
        
        if VALUE_COL and 'State' in df.columns:
            # For API data, use single Value column; for Excel, allow year selection
            if len(VALUE_COLS) > 1:
                state_rev_col = st.selectbox("Select Year", VALUE_COLS, key="state_year_select")
            else:
                state_rev_col = VALUE_COL
            
            # Get all states
            all_states = df['State'].dropna().unique().tolist()
            all_states = sorted(all_states)
            
            st.markdown("#### Overall State-wise Revenue")
            state_revenue = df.groupby('State')[state_rev_col].sum().reset_index()
            state_revenue = state_revenue[state_revenue[state_rev_col] > 0].sort_values(state_rev_col, ascending=False)
            state_revenue['Formatted'] = state_revenue[state_rev_col].apply(format_inr)
            state_revenue['%'] = (state_revenue[state_rev_col] / state_revenue[state_rev_col].sum() * 100).round(1)
            
            # Create visualization
            col1, col2 = st.columns([2, 1])
            with col1:
                fig_state_rev = px.bar(state_revenue, x='State', y=state_rev_col,
                                       title="Revenue by State", text='Formatted',
                                       color=state_rev_col, color_continuous_scale='Viridis',
                                       custom_data=['Formatted', '%'])
                fig_state_rev.update_traces(textposition='outside', 
                                           hovertemplate='<b>%{x}</b><br>Revenue: %{customdata[0]}<br>%{customdata[1]:.1f}%<extra></extra>')
                fig_state_rev.update_layout(xaxis_tickangle=-45)
                fig_state_rev.update_yaxes(tickformat=',.0f')
                st.plotly_chart(fig_state_rev, use_container_width=True, key="state_revenue_bar")
            
            with col2:
                st.markdown("#### State Summary")
                summary_states = state_revenue[['State', 'Formatted', '%']].copy()
                summary_states.columns = ['State', 'Revenue', '%']
                st.dataframe(summary_states, use_container_width=True, height=400)
            
            st.markdown("---")
            st.markdown("#### Drill-Down Analysis by State")
            
            # State selector
            selected_state = st.selectbox("Select State", all_states, key="state_analysis_select")
            
            if selected_state:
                state_data = df[df['State'] == selected_state]
                
                # Create tabs for different views
                view_dealers, view_products = st.tabs(["State Dealers", "State Product-wise"])
                
                with view_dealers:
                    st.markdown(f"#### Dealers in {selected_state}")
                    
                    dealers_in_state = state_data.groupby('Dealer Name')[state_rev_col].sum().reset_index()
                    dealers_in_state = dealers_in_state[dealers_in_state[state_rev_col] > 0].sort_values(state_rev_col, ascending=False)
                    dealers_in_state['Formatted'] = dealers_in_state[state_rev_col].apply(format_inr)
                    dealers_in_state['%'] = (dealers_in_state[state_rev_col] / dealers_in_state[state_rev_col].sum() * 100).round(1)
                    
                    if not dealers_in_state.empty:
                        # Show metrics
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Revenue", format_inr(dealers_in_state[state_rev_col].sum()))
                        with col2:
                            st.metric("Number of Dealers", len(dealers_in_state))
                        with col3:
                            st.metric("Top Dealer", dealers_in_state['Dealer Name'].iloc[0] if len(dealers_in_state) > 0 else "N/A")
                        with col4:
                            avg_per_dealer = dealers_in_state[state_rev_col].mean()
                            st.metric("Avg per Dealer", format_inr(avg_per_dealer))
                        
                        st.markdown("##### Dealer Performance")
                        # Bar chart
                        fig_dealers = px.bar(dealers_in_state, x='Dealer Name', y=state_rev_col,
                                            title=f"Dealers Revenue in {selected_state}", text='Formatted',
                                            color=state_rev_col, color_continuous_scale='Blues',
                                            custom_data=['Formatted', '%'])
                        fig_dealers.update_traces(textposition='outside',
                                                 hovertemplate='<b>%{x}</b><br>Revenue: %{customdata[0]}<br>%{customdata[1]:.1f}%<extra></extra>')
                        fig_dealers.update_layout(xaxis_tickangle=-45)
                        fig_dealers.update_yaxes(tickformat=',.0f')
                        st.plotly_chart(fig_dealers, use_container_width=True, key=f"dealers_{selected_state}")
                        
                        # Data table
                        st.markdown("##### Dealer Details")
                        dealer_details = dealers_in_state[['Dealer Name', 'Formatted', '%']].copy()
                        dealer_details.columns = ['Dealer Name', 'Revenue', '%']
                        st.dataframe(dealer_details, use_container_width=True)
                        
                        # Additional analysis by dealer
                        st.markdown("---")
                        st.markdown("##### Dealer Category Mix")
                        
                        dealer_options = dealers_in_state['Dealer Name'].tolist()
                        selected_dealer_state = st.selectbox("Select Dealer for Category Analysis", dealer_options, 
                                                             key="dealer_category_select")
                        
                        if selected_dealer_state:
                            dealer_cat_data = state_data[state_data['Dealer Name'] == selected_dealer_state]
                            
                            if 'Category' in dealer_cat_data.columns:
                                dealer_categories = dealer_cat_data.groupby('Category')[state_rev_col].sum().reset_index()
                                dealer_categories = dealer_categories[dealer_categories[state_rev_col] > 0].sort_values(state_rev_col, ascending=False)
                                dealer_categories['Formatted'] = dealer_categories[state_rev_col].apply(format_inr)
                                dealer_categories['%'] = (dealer_categories[state_rev_col] / dealer_categories[state_rev_col].sum() * 100).round(1)
                                
                                if not dealer_categories.empty:
                                    # Pie chart
                                    fig_dealer_cat_pie = px.pie(dealer_categories, values=state_rev_col, names='Category',
                                                               title=f"{selected_dealer_state} - Category Mix",
                                                               custom_data=['Formatted', '%'])
                                    fig_dealer_cat_pie.update_traces(
                                        hovertemplate='<b>%{label}</b><br>%{customdata[0]}<br>%{customdata[1]:.1f}%<extra></extra>'
                                    )
                                    st.plotly_chart(fig_dealer_cat_pie, use_container_width=True, key=f"dealer_cat_pie_{selected_dealer_state}")
                                    
                                    # Table
                                    cat_table = dealer_categories[['Category', 'Formatted', '%']].copy()
                                    cat_table.columns = ['Category', 'Revenue', '%']
                                    st.dataframe(cat_table, use_container_width=True)
                            else:
                                st.info("Category data not available")
                    else:
                        st.info(f"No dealer data available for {selected_state}")
                
                with view_products:
                    st.markdown(f"#### Products in {selected_state}")
                    
                    # Determine product column
                    prod_col = 'Product Name' if 'Product Name' in state_data.columns else ('Item Name' if 'Item Name' in state_data.columns else ('Sub Category' if 'Sub Category' in state_data.columns else None))
                    
                    if not prod_col:
                        st.warning("No product/item column found for product analysis")
                    else:
                        # Get categories for filtering
                        if 'Category' in state_data.columns:
                            all_categories = state_data['Category'].dropna().unique().tolist()
                            all_categories = sorted(all_categories)
                            
                            selected_categories_prod = st.multiselect(
                                "Select Categories to display",
                                all_categories,
                                default=all_categories[:5] if len(all_categories) > 5 else all_categories,
                                key="state_prod_category_filter"
                            )
                            
                            if selected_categories_prod:
                                prod_data = state_data[state_data['Category'].isin(selected_categories_prod)]
                            else:
                                prod_data = state_data
                        else:
                            prod_data = state_data
                        
                        products_in_state = prod_data.groupby(prod_col)[state_rev_col].sum().reset_index()
                        products_in_state = products_in_state[products_in_state[state_rev_col] > 0].sort_values(state_rev_col, ascending=False)
                        products_in_state['Formatted'] = products_in_state[state_rev_col].apply(format_inr)
                        products_in_state['%'] = (products_in_state[state_rev_col] / products_in_state[state_rev_col].sum() * 100).round(1)
                        
                        if not products_in_state.empty:
                            # Show metrics
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Total Revenue", format_inr(products_in_state[state_rev_col].sum()))
                            with col2:
                                st.metric(f"Number of {prod_col}s", len(products_in_state))
                            with col3:
                                st.metric("Top Product", products_in_state[prod_col].iloc[0][:30] if len(products_in_state) > 0 else "N/A")
                            with col4:
                                avg_per_prod = products_in_state[state_rev_col].mean()
                                st.metric("Avg per Product", format_inr(avg_per_prod))
                            
                            st.markdown(f"##### Top 20 {prod_col}s by Revenue")
                            
                            # Bar chart (top 20)
                            top_products = products_in_state.head(20)
                            fig_products = px.bar(top_products, x=prod_col, y=state_rev_col,
                                                 title=f"Top {prod_col}s Revenue in {selected_state}", text='Formatted',
                                                 color=state_rev_col, color_continuous_scale='Greens',
                                                 custom_data=['Formatted', '%'])
                            fig_products.update_traces(textposition='outside',
                                                      hovertemplate='<b>%{x}</b><br>Revenue: %{customdata[0]}<br>%{customdata[1]:.1f}%<extra></extra>')
                            fig_products.update_layout(xaxis_tickangle=-45, height=600)
                            fig_products.update_yaxes(tickformat=',.0f')
                            st.plotly_chart(fig_products, use_container_width=True, key=f"products_{selected_state}")
                            
                            # Data table with all products
                            st.markdown(f"##### All {prod_col}s Details")
                            prod_details = products_in_state[[prod_col, 'Formatted', '%']].copy()
                            prod_details.columns = [prod_col, 'Revenue', '%']
                            st.dataframe(prod_details, use_container_width=True)
                            
                            # Category-wise product breakdown
                            if 'Category' in state_data.columns:
                                st.markdown("---")
                                st.markdown("##### Category-wise Product Summary")
                                
                                cat_prod_summary = prod_data.groupby(['Category', prod_col])[state_rev_col].sum().reset_index()
                                cat_prod_summary = cat_prod_summary[cat_prod_summary[state_rev_col] > 0].sort_values(['Category', state_rev_col], ascending=[True, False])
                                cat_prod_summary['Formatted'] = cat_prod_summary[state_rev_col].apply(format_inr)
                                
                                # Show for each category
                                for category in sorted(prod_data['Category'].unique()):
                                    cat_prod = cat_prod_summary[cat_prod_summary['Category'] == category]
                                    if not cat_prod.empty:
                                        with st.expander(f"📦 {category} Products", expanded=False):
                                            cat_prod_display = cat_prod[[prod_col, 'Formatted']].copy()
                                            cat_prod_display.columns = [prod_col, 'Revenue']
                                            st.dataframe(cat_prod_display, use_container_width=True)
                        else:
                            st.info(f"No product data available for {selected_state}")
    
    # 1.8 Dealer & State Comparative Analysis
    with sales_sub8:
        st.subheader("Dealer & State Comparative Analysis")
        
        if VALUE_COL and 'State' in df.columns and 'Dealer Name' in df.columns:
            # For API data, use single Value column; for Excel, allow year selection
            if len(VALUE_COLS) > 1:
                comp_value_col = st.selectbox("Select Year", VALUE_COLS, key="comp_year_select")
            else:
                comp_value_col = VALUE_COL
            
            # Get all states
            all_states = df['State'].dropna().unique().tolist()
            all_states = sorted(all_states)
            
            st.markdown("#### State Revenue Comparison")
            state_comp = df.groupby('State')[comp_value_col].sum().reset_index()
            state_comp = state_comp[state_comp[comp_value_col] > 0].sort_values(comp_value_col, ascending=False)
            state_comp['Formatted'] = state_comp[comp_value_col].apply(format_inr)
            state_comp['%'] = (state_comp[comp_value_col] / state_comp[comp_value_col].sum() * 100).round(1)
            
            # Bar chart
            fig_state_comp = px.bar(state_comp, x='State', y=comp_value_col,
                                   title="Revenue Distribution by State", text='Formatted',
                                   color=comp_value_col, color_continuous_scale='Viridis',
                                   custom_data=['Formatted', '%'])
            fig_state_comp.update_traces(textposition='outside',
                                        hovertemplate='<b>%{x}</b><br>Revenue: %{customdata[0]}<br>%{customdata[1]:.1f}%<extra></extra>')
            fig_state_comp.update_layout(xaxis_tickangle=-45)
            fig_state_comp.update_yaxes(tickformat=',.0f')
            st.plotly_chart(fig_state_comp, use_container_width=True, key="state_comp_bar")
            
            st.markdown("---")
            st.markdown("#### Select State for Detailed Analysis")
            
            selected_comp_state = st.selectbox("Choose State", all_states, key="comp_state_select")
            
            if selected_comp_state:
                state_data_comp = df[df['State'] == selected_comp_state]
                
                # Get dealers in this state
                dealers_in_comp_state = state_data_comp.groupby('Dealer Name')[comp_value_col].sum().reset_index()
                dealers_in_comp_state = dealers_in_comp_state[dealers_in_comp_state[comp_value_col] > 0].sort_values(comp_value_col, ascending=False)
                dealers_in_comp_state['Formatted'] = dealers_in_comp_state[comp_value_col].apply(format_inr)
                dealers_in_comp_state['%'] = (dealers_in_comp_state[comp_value_col] / dealers_in_comp_state[comp_value_col].sum() * 100).round(1)
                
                st.markdown(f"#### 📍 State: {selected_comp_state}")
                
                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Revenue", format_inr(dealers_in_comp_state[comp_value_col].sum()))
                with col2:
                    st.metric("Number of Dealers", len(dealers_in_comp_state))
                with col3:
                    top_dealer = dealers_in_comp_state['Dealer Name'].iloc[0] if len(dealers_in_comp_state) > 0 else "N/A"
                    st.metric("Top Dealer", top_dealer[:25])
                with col4:
                    avg_dealer_rev = dealers_in_comp_state[comp_value_col].mean()
                    st.metric("Avg Dealer Revenue", format_inr(avg_dealer_rev))
                
                st.markdown("---")
                
                # Create tabs for different views
                tab_dealers_comp, tab_cat_comp, tab_subcat_comp = st.tabs([
                    "Dealer Comparison",
                    "Category Mix Analysis",
                    "Sub-Category Mix Analysis"
                ])
                
                with tab_dealers_comp:
                    st.markdown(f"#### Dealers in {selected_comp_state}")
                    
                    # Pie chart for dealer distribution
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        fig_dealers_pie = px.pie(dealers_in_comp_state, values=comp_value_col, names='Dealer Name',
                                                title=f"Dealer Revenue Distribution in {selected_comp_state}",
                                                custom_data=['Formatted', '%'])
                        fig_dealers_pie.update_traces(
                            hovertemplate='<b>%{label}</b><br>Revenue: %{customdata[0]}<br>%{customdata[1]:.1f}%<extra></extra>'
                        )
                        st.plotly_chart(fig_dealers_pie, use_container_width=True, key=f"dealers_pie_{selected_comp_state}")
                    
                    with col2:
                        st.markdown("##### Dealer Ranking")
                        dealer_rank = dealers_in_comp_state[['Dealer Name', 'Formatted', '%']].copy()
                        dealer_rank.columns = ['Dealer', 'Revenue', '%']
                        st.dataframe(dealer_rank, use_container_width=True, height=400)
                    
                    # Dealer comparison bar chart
                    st.markdown("---")
                    st.markdown("##### Dealer Revenue Comparison")
                    fig_dealers_bar = px.bar(dealers_in_comp_state, x='Dealer Name', y=comp_value_col,
                                            title=f"Dealer Revenue in {selected_comp_state}", text='Formatted',
                                            color=comp_value_col, color_continuous_scale='Blues',
                                            custom_data=['Formatted', '%'])
                    fig_dealers_bar.update_traces(textposition='outside',
                                                 hovertemplate='<b>%{x}</b><br>Revenue: %{customdata[0]}<br>%{customdata[1]:.1f}%<extra></extra>')
                    fig_dealers_bar.update_layout(xaxis_tickangle=-45)
                    fig_dealers_bar.update_yaxes(tickformat=',.0f')
                    st.plotly_chart(fig_dealers_bar, use_container_width=True, key=f"dealers_bar_{selected_comp_state}")
                
                with tab_cat_comp:
                    st.markdown(f"#### Category Mix in {selected_comp_state}")
                    
                    if 'Category' not in state_data_comp.columns:
                        st.warning("Category column not found")
                    else:
                        # Overall category distribution
                        cat_comp = state_data_comp.groupby('Category')[comp_value_col].sum().reset_index()
                        cat_comp = cat_comp[cat_comp[comp_value_col] > 0].sort_values(comp_value_col, ascending=False)
                        cat_comp['Formatted'] = cat_comp[comp_value_col].apply(format_inr)
                        cat_comp['%'] = (cat_comp[comp_value_col] / cat_comp[comp_value_col].sum() * 100).round(1)
                        
                        # Metrics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Categories", len(cat_comp))
                        with col2:
                            top_cat = cat_comp['Category'].iloc[0] if len(cat_comp) > 0 else "N/A"
                            st.metric("Top Category", top_cat)
                        with col3:
                            top_cat_rev = cat_comp[comp_value_col].iloc[0] if len(cat_comp) > 0 else 0
                            st.metric("Top Category Revenue", format_inr(top_cat_rev))
                        
                        st.markdown("---")
                        
                        # Pie chart and table
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            fig_cat_pie = px.pie(cat_comp, values=comp_value_col, names='Category',
                                               title=f"Category Revenue Distribution in {selected_comp_state}",
                                               custom_data=['Formatted', '%'])
                            fig_cat_pie.update_traces(
                                hovertemplate='<b>%{label}</b><br>Revenue: %{customdata[0]}<br>%{customdata[1]:.1f}%<extra></extra>'
                            )
                            st.plotly_chart(fig_cat_pie, use_container_width=True, key=f"cat_pie_{selected_comp_state}")
                        
                        with col2:
                            st.markdown("##### Category Ranking")
                            cat_rank = cat_comp[['Category', 'Formatted', '%']].copy()
                            cat_rank.columns = ['Category', 'Revenue', '%']
                            st.dataframe(cat_rank, use_container_width=True, height=400)
                        
                        st.markdown("---")
                        st.markdown("##### Category Revenue Comparison")
                        fig_cat_bar = px.bar(cat_comp, x='Category', y=comp_value_col,
                                            title=f"Category Revenue in {selected_comp_state}", text='Formatted',
                                            color=comp_value_col, color_continuous_scale='Greens',
                                            custom_data=['Formatted', '%'])
                        fig_cat_bar.update_traces(textposition='outside',
                                                 hovertemplate='<b>%{x}</b><br>Revenue: %{customdata[0]}<br>%{customdata[1]:.1f}%<extra></extra>')
                        fig_cat_bar.update_layout(xaxis_tickangle=-45)
                        fig_cat_bar.update_yaxes(tickformat=',.0f')
                        st.plotly_chart(fig_cat_bar, use_container_width=True, key=f"cat_bar_{selected_comp_state}")
                        
                        # Category-wise dealer breakdown
                        st.markdown("---")
                        st.markdown("##### Category-wise Dealer Analysis")
                        
                        selected_cat = st.selectbox("Select Category to see dealer breakdown",
                                                    cat_comp['Category'].tolist(),
                                                    key="comp_cat_select")
                        
                        if selected_cat:
                            cat_dealer_data = state_data_comp[state_data_comp['Category'] == selected_cat]
                            cat_dealer_comp = cat_dealer_data.groupby('Dealer Name')[comp_value_col].sum().reset_index()
                            cat_dealer_comp = cat_dealer_comp[cat_dealer_comp[comp_value_col] > 0].sort_values(comp_value_col, ascending=False)
                            cat_dealer_comp['Formatted'] = cat_dealer_comp[comp_value_col].apply(format_inr)
                            cat_dealer_comp['%'] = (cat_dealer_comp[comp_value_col] / cat_dealer_comp[comp_value_col].sum() * 100).round(1)
                            
                            if not cat_dealer_comp.empty:
                                fig_cat_dealer_pie = px.pie(cat_dealer_comp, values=comp_value_col, names='Dealer Name',
                                                           title=f"{selected_cat} - Dealer Distribution",
                                                           custom_data=['Formatted', '%'])
                                fig_cat_dealer_pie.update_traces(
                                    hovertemplate='<b>%{label}</b><br>Revenue: %{customdata[0]}<br>%{customdata[1]:.1f}%<extra></extra>'
                                )
                                st.plotly_chart(fig_cat_dealer_pie, use_container_width=True, key=f"cat_dealer_pie_{selected_cat}")
                            else:
                                st.info(f"No dealer data for {selected_cat}")
                
                with tab_subcat_comp:
                    st.markdown(f"#### Sub-Category Mix in {selected_comp_state}")
                    
                    if 'Sub Category' in state_data_comp.columns:
                        # Get categories for filtering
                        state_categories = state_data_comp['Category'].dropna().unique().tolist()
                        state_categories = sorted(state_categories)
                        
                        selected_cat_for_subcat = st.selectbox("Select Category to see Sub-Categories",
                                                               state_categories,
                                                               key="comp_cat_for_subcat")
                        
                        if selected_cat_for_subcat:
                            subcat_data = state_data_comp[state_data_comp['Category'] == selected_cat_for_subcat]
                            subcat_comp = subcat_data.groupby('Sub Category')[comp_value_col].sum().reset_index()
                            subcat_comp = subcat_comp[subcat_comp[comp_value_col] > 0].sort_values(comp_value_col, ascending=False)
                            subcat_comp['Formatted'] = subcat_comp[comp_value_col].apply(format_inr)
                            subcat_comp['%'] = (subcat_comp[comp_value_col] / subcat_comp[comp_value_col].sum() * 100).round(1)
                            
                            if not subcat_comp.empty:
                                # Metrics
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Sub-Categories", len(subcat_comp))
                                with col2:
                                    top_subcat = subcat_comp['Sub Category'].iloc[0] if len(subcat_comp) > 0 else "N/A"
                                    st.metric("Top Sub-Category", top_subcat[:25])
                                with col3:
                                    total_subcat_rev = subcat_comp[comp_value_col].sum()
                                    st.metric("Category Total", format_inr(total_subcat_rev))
                                
                                st.markdown("---")
                                
                                # Pie chart and table
                                col1, col2 = st.columns([2, 1])
                                
                                with col1:
                                    fig_subcat_pie = px.pie(subcat_comp, values=comp_value_col, names='Sub Category',
                                                           title=f"{selected_cat_for_subcat} - Sub-Category Distribution",
                                                           custom_data=['Formatted', '%'])
                                    fig_subcat_pie.update_traces(
                                        hovertemplate='<b>%{label}</b><br>Revenue: %{customdata[0]}<br>%{customdata[1]:.1f}%<extra></extra>'
                                    )
                                    st.plotly_chart(fig_subcat_pie, use_container_width=True, key=f"subcat_pie_{selected_cat_for_subcat}")
                                
                                with col2:
                                    st.markdown("##### Sub-Category Ranking")
                                    subcat_rank = subcat_comp[['Sub Category', 'Formatted', '%']].copy()
                                    subcat_rank.columns = ['Sub-Category', 'Revenue', '%']
                                    st.dataframe(subcat_rank, use_container_width=True, height=400)
                                
                                st.markdown("---")
                                st.markdown("##### Sub-Category Revenue Comparison")
                                fig_subcat_bar = px.bar(subcat_comp, x='Sub Category', y=comp_value_col,
                                                       title=f"{selected_cat_for_subcat} - Sub-Categories", text='Formatted',
                                                       color=comp_value_col, color_continuous_scale='Oranges',
                                                       custom_data=['Formatted', '%'])
                                fig_subcat_bar.update_traces(textposition='outside',
                                                            hovertemplate='<b>%{x}</b><br>Revenue: %{customdata[0]}<br>%{customdata[1]:.1f}%<extra></extra>')
                                fig_subcat_bar.update_layout(xaxis_tickangle=-45, height=600)
                                fig_subcat_bar.update_yaxes(tickformat=',.0f')
                                st.plotly_chart(fig_subcat_bar, use_container_width=True, key=f"subcat_bar_{selected_cat_for_subcat}")
                                
                                # Sub-Category dealer breakdown
                                st.markdown("---")
                                st.markdown("##### Sub-Category Dealer Analysis")
                                
                                selected_subcat = st.selectbox("Select Sub-Category to see dealer breakdown",
                                                               subcat_comp['Sub Category'].tolist(),
                                                               key="comp_subcat_select")
                                
                                if selected_subcat:
                                    subcat_dealer_data = subcat_data[subcat_data['Sub Category'] == selected_subcat]
                                    subcat_dealer_comp = subcat_dealer_data.groupby('Dealer Name')[comp_value_col].sum().reset_index()
                                    subcat_dealer_comp = subcat_dealer_comp[subcat_dealer_comp[comp_value_col] > 0].sort_values(comp_value_col, ascending=False)
                                    subcat_dealer_comp['Formatted'] = subcat_dealer_comp[comp_value_col].apply(format_inr)
                                    subcat_dealer_comp['%'] = (subcat_dealer_comp[comp_value_col] / subcat_dealer_comp[comp_value_col].sum() * 100).round(1)
                                    
                                    if not subcat_dealer_comp.empty:
                                        fig_subcat_dealer_pie = px.pie(subcat_dealer_comp, values=comp_value_col, names='Dealer Name',
                                                                      title=f"{selected_subcat} - Dealer Distribution",
                                                                      custom_data=['Formatted', '%'])
                                        fig_subcat_dealer_pie.update_traces(
                                            hovertemplate='<b>%{label}</b><br>Revenue: %{customdata[0]}<br>%{customdata[1]:.1f}%<extra></extra>'
                                        )
                                        st.plotly_chart(fig_subcat_dealer_pie, use_container_width=True, key=f"subcat_dealer_pie_{selected_subcat}")
                                    else:
                                        st.info(f"No dealer data for {selected_subcat}")
                            else:
                                st.info(f"No sub-category data for {selected_cat_for_subcat}")

# ================================
# TAB 2: CUSTOMER INSIGHTS
# ================================
with tab2:
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
            col1, col2 = st.columns([3, 1])
            with col1:
                if len(VALUE_COLS) > 1:
                    cust_value_col = st.selectbox("Select Year", VALUE_COLS, key="cust_year")
                else:
                    cust_value_col = VALUE_COL
            with col2:
                cust_limit = get_display_limit("cust_overview_limit", default=20)
            
            top_custs = df.groupby('Dealer Name')[cust_value_col].sum().reset_index()
            top_custs = top_custs[top_custs[cust_value_col] > 0].sort_values(cust_value_col, ascending=False)
            
            if top_custs.empty:
                st.info("No customer data available for the selected year")
            else:
                top_custs['Formatted'] = top_custs[cust_value_col].apply(format_inr)
                display_custs = apply_limit(top_custs, cust_limit)
                title_suffix = f"Top {cust_limit}" if cust_limit else "All"
                fig = px.bar(display_custs, x='Dealer Name', y=cust_value_col,
                            title=f"{title_suffix} Customers", text='Formatted', color=cust_value_col,
                            color_continuous_scale='Blues', custom_data=['Formatted'])
                fig.update_traces(textposition='outside', hovertemplate='%{x}<br>%{customdata[0]}<extra></extra>')
                fig.update_layout(xaxis_tickangle=-45)
                fig.update_yaxes(tickformat=',.0f')
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
                fig.update_yaxes(tickformat=',.0f')
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
                        fig.update_yaxes(tickformat=',.0f')
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
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                prev_y = st.selectbox("Previous", VALUE_COLS, index=0, key="cust_prev")
            with col2:
                curr_y = st.selectbox("Current", VALUE_COLS, index=min(1, len(VALUE_COLS)-1), key="cust_curr")
            with col3:
                perf_limit = get_display_limit("perf_limit", default=10)
            
            perf = df.groupby('Dealer Name').agg({prev_y: 'sum', curr_y: 'sum'}).reset_index()
            perf['Growth %'] = ((perf[curr_y] - perf[prev_y]) / perf[prev_y].replace(0, np.nan) * 100).round(1)
            
            growers = perf[perf['Growth %'] > 0].sort_values('Growth %', ascending=False)
            decliners = perf[perf['Growth %'] < 0].sort_values('Growth %')
            
            display_growers = apply_limit(growers, perf_limit)
            display_decliners = apply_limit(decliners, perf_limit)
            
            if len(display_growers) > 0:
                st.markdown("#### Top Growers")
                display_growers['Growth Text'] = display_growers['Growth %'].apply(lambda x: f"{x:.1f}%")
                fig = px.bar(display_growers, x='Dealer Name', y='Growth %', title="Growing Customers",
                            text='Growth Text', color='Growth %', color_continuous_scale='Greens')
                fig.update_traces(textposition='outside', hovertemplate='%{x}<br>Growth: %{y:.1f}%<extra></extra>')
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True, key="cust_growers_chart")
            else:
                st.info("No growing customers found for the selected periods")
            
            if len(display_decliners) > 0:
                st.markdown("#### Declining")
                display_decliners['Growth Text'] = display_decliners['Growth %'].apply(lambda x: f"{x:.1f}%")
                fig = px.bar(display_decliners, x='Dealer Name', y='Growth %', title="Declining Customers",
                            text='Growth Text', color='Growth %', color_continuous_scale='Reds_r')
                fig.update_traces(textposition='outside', hovertemplate='%{x}<br>Growth: %{y:.1f}%<extra></extra>')
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True, key="cust_decliners_chart")
            else:
                st.info("No declining customers found for the selected periods")

# ================================
# TAB 3: PAYMENT ANALYSIS
# ================================
with tab3:
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
            
            col1, col2 = st.columns([3, 1])
            with col1:
                hide_null_pay = st.checkbox("Hide zero values", value=True, key="pay_hide_null")
            with col2:
                pay_dealer_limit = get_display_limit("pay_dealer_limit", default=10)
            
            if 'Dealer Name' in df.columns:
                dealer_pay = df.groupby('Dealer Name')[VALUE_COL].sum().reset_index()
                if hide_null_pay:
                    dealer_pay = dealer_pay[dealer_pay[VALUE_COL] > 0]
                dealer_pay = dealer_pay.sort_values(VALUE_COL, ascending=False)
                
                if dealer_pay.empty:
                    st.info("No dealer payment data available")
                else:
                    dealer_pay['Formatted'] = dealer_pay[VALUE_COL].apply(format_inr)
                    display_dealer_pay = apply_limit(dealer_pay, pay_dealer_limit)
                    title_suffix = f"Top {pay_dealer_limit}" if pay_dealer_limit else "All"
                    fig = px.bar(display_dealer_pay, x='Dealer Name', y=VALUE_COL,
                                title=f"{title_suffix} Dealers", text='Formatted', custom_data=['Formatted'])
                    fig.update_traces(textposition='outside', hovertemplate='%{x}<br>%{customdata[0]}<extra></extra>')
                    fig.update_layout(xaxis_tickangle=-45)
                    fig.update_yaxes(tickformat=',.0f')
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
            outstanding_limit = get_display_limit("outstanding_limit", default=10)
            outstanding = df.groupby('Dealer Name')['Outstanding'].sum().reset_index()
            outstanding = outstanding[outstanding['Outstanding'] > 0].sort_values('Outstanding', ascending=False)
            
            if outstanding.empty:
                st.success("No outstanding amounts found!")
            else:
                outstanding['Formatted'] = outstanding['Outstanding'].apply(format_inr)
                st.metric("Total Outstanding", format_inr(outstanding['Outstanding'].sum()))
                
                display_outstanding = apply_limit(outstanding, outstanding_limit)
                title_suffix = f"Top {outstanding_limit}" if outstanding_limit else "All"
                fig = px.bar(display_outstanding, x='Dealer Name', y='Outstanding',
                            title=f"{title_suffix} Outstanding", text='Formatted', color='Outstanding',
                            color_continuous_scale='Reds', custom_data=['Formatted'])
                fig.update_traces(textposition='outside', hovertemplate='%{x}<br>%{customdata[0]}<extra></extra>')
                fig.update_layout(xaxis_tickangle=-45)
                fig.update_yaxes(tickformat=',.0f')
                st.plotly_chart(fig, use_container_width=True, key="pay_outstanding_bar")

# Footer
st.markdown("---")
st.caption("Orthopedic Implant Analytics Dashboard - Stage 1")
