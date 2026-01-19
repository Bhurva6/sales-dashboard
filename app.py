"""
Dash-based Orthopedic Implant Analytics Dashboard
"""

import dash
from dash import dcc, html, Input, Output, State, callback, ctx, no_update, ALL, callback_context
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from api_client import APIClient
from datetime import datetime, timedelta
import json
import os
import uuid
import traceback
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Dash app with modern theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.LUX],
    assets_folder='assets',
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ]
)

# App title
app.title = "Orthopedic Implant Analytics Dashboard"

# Get current month start and today
today = datetime.now()
month_start = today.replace(day=1)

# Modern Color Palette - Magenta Inspired
COLORS = {
    'primary': '#6366f1',      # Indigo
    'secondary': '#8b5cf6',    # Purple
    'success': '#10b981',      # Green
    'danger': '#ef4444',       # Red
    'warning': '#f59e0b',      # Amber
    'info': '#3b82f6',         # Blue
    'light': '#f9fafb',        # Background
    'dark': '#1f2937',         # Dark text
    'card_bg': '#ffffff',      # Card background
    'sidebar_bg': '#f8fafc'    # Sidebar background
}

# Helper functions for formatting
def format_inr(value):
    """Format value in Indian currency format (Lakhs/Crores)"""
    if pd.isna(value):
        return "Rs. 0"
    if value >= 1e7:
        return f"Rs. {value/1e7:.2f} Cr"
    elif value >= 1e5:
        return f"Rs. {value/1e5:.2f} Lakh"
    else:
        return f"Rs. {value:,.0f}"

def format_qty(value):
    """Format quantity in Indian format (Thousands/Lakhs/Crores)"""
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

def get_week_start():
    today = datetime.now()
    return today - timedelta(days=today.weekday())

# City coordinates for geographic mapping
CITY_COORDS = {
    'Mumbai': (19.0760, 72.8777),
    'Delhi': (28.7041, 77.1025),
    'New Delhi': (28.7041, 77.1025),
    'Bangalore': (12.9716, 77.5946),
    'Bengaluru': (12.9716, 77.5946),
    'Hyderabad': (17.3850, 78.4867),
    'Chennai': (13.0827, 80.2707),
    'Kolkata': (22.5726, 88.3639),
    'Pune': (18.5204, 73.8567),
    'Ahmedabad': (23.0225, 72.5714),
    'Jaipur': (26.9124, 75.7873),
    'Surat': (21.1702, 72.8311),
    'Lucknow': (26.8467, 80.9462),
    'Kanpur': (26.4499, 80.3319),
    'Nagpur': (21.1458, 79.0882),
    'Indore': (22.7196, 75.8577),
    'Thane': (19.2183, 72.9781),
    'Bhopal': (23.2599, 77.4126),
    'Visakhapatnam': (17.6868, 83.2185),
    'Pimpri-Chinchwad': (18.6298, 73.7997),
    'Patna': (25.5941, 85.1376),
    'Vadodara': (22.3072, 73.1812),
    'Ghaziabad': (28.6692, 77.4538),
    'Ludhiana': (30.9010, 75.8573),
    'Agra': (27.1767, 78.0081),
    'Nashik': (19.9975, 73.7898),
    'Faridabad': (28.4089, 77.3178),
    'Meerut': (28.9845, 77.7064),
    'Rajkot': (22.3039, 70.8022),
    'Kalyan-Dombivali': (19.2403, 73.1305),
    'Vasai-Virar': (19.4612, 72.7990),
    'Varanasi': (25.3176, 82.9739),
    'Srinagar': (34.0837, 74.7973),
    'Aurangabad': (19.8762, 75.3433),
    'Dhanbad': (23.7957, 86.4304),
    'Amritsar': (31.6340, 74.8723),
    'Navi Mumbai': (19.0330, 73.0297),
    'Allahabad': (25.4358, 81.8463),
    'Prayagraj': (25.4358, 81.8463),
    'Ranchi': (23.3441, 85.3096),
    'Howrah': (22.5958, 88.2636),
    'Coimbatore': (11.0168, 76.9558),
    'Jabalpur': (23.1815, 79.9864),
    'Gwalior': (26.2183, 78.1828),
    'Vijayawada': (16.5062, 80.6480),
    'Jodhpur': (26.2389, 73.0243),
    'Madurai': (9.9252, 78.1198),
    'Raipur': (21.2514, 81.6296),
    'Kota': (25.2138, 75.8648),
    'Chandigarh': (30.7333, 76.7794),
    'Guwahati': (26.1445, 91.7362),
}

# State capital coordinates (fallback for state-level mapping)
STATE_COORDS = {
    'Maharashtra': (19.7515, 75.7139),
    'Delhi': (28.7041, 77.1025),
    'Karnataka': (12.9716, 77.5946),
    'Telangana': (17.3850, 78.4867),
    'Tamil Nadu': (13.0827, 80.2707),
    'West Bengal': (22.5726, 88.3639),
    'Gujarat': (23.0225, 72.5714),
    'Rajasthan': (26.9124, 75.7873),
    'Uttar Pradesh': (26.8467, 80.9462),
    'Madhya Pradesh': (23.2599, 77.4126),
    'Andhra Pradesh': (17.6868, 83.2185),
    'Bihar': (25.5941, 85.1376),
    'Punjab': (31.1471, 75.3412),
    'Haryana': (29.0588, 76.0856),
    'Kerala': (10.8505, 76.2711),
    'Assam': (26.2006, 92.9376),
    'Odisha': (20.9517, 85.0985),
    'Jharkhand': (23.6102, 85.2799),
    'Chhattisgarh': (21.2787, 81.8661),
    'Uttarakhand': (30.0668, 79.0193),
    'Himachal Pradesh': (31.1048, 77.1734),
    'Jammu and Kashmir': (33.7782, 76.5762),
    'Goa': (15.2993, 74.1240),
}

# App layout
app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='session-store', storage_type='session'),
    dcc.Store(id='selected-location-store', storage_type='session'),  # Store for map selection
    dcc.Store(id='chart-data-store', storage_type='memory'),  # Store for chart data
    html.Div(id='saved-charts-data', style={'display': 'none'}),  # Hidden div for saved charts data
    
    # Modern Header with gradient
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Div([
                    html.Div([
                        html.H1([
                            html.Span("Orthopedic Implant Analytics", className="gradient-text")
                        ], className="mb-0", style={'fontWeight': '700', 'letterSpacing': '-0.02em'}),
                        html.P("Real-time Sales & Analytics Dashboard", 
                               className="mb-0", 
                               style={'fontSize': '14px', 'fontWeight': '400', 'color': '#000000'})
                    ]),
                ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'})
            ], className="dashboard-header", style={'padding': '1.5rem 0'})
        ], width=12)
    ], className="mb-4"),
    
    # Sidebar + Main Content
    dbc.Row([
        # Modern Sidebar
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Authentication", className="mb-3", style={'fontWeight': '600', 'color': COLORS['dark']}),
                    
                    dbc.Input(
                        id='username-input',
                        type='text',
                        placeholder='Username',
                        value='u2vp8kb',
                        className="mb-2"
                    ),
                    
                    dbc.Input(
                        id='password-input',
                        type='password',
                        placeholder='Password',
                        value='asdftuy#$%78@!',
                        className="mb-3"
                    ),
                    
                    html.Hr(style={'borderColor': '#e5e7eb'}),
                    
                    # Quick Date Selection Section
                    html.P("Quick Select:", className='small fw-bold mb-2', style={'color': COLORS['dark']}),
                    dbc.Stack([
                        dbc.ButtonGroup([
                            dbc.Button("Today", id='quick-today', color='primary', outline=True, size='sm', className='w-100 mb-1'),
                            dbc.Button("Yesterday", id='quick-yesterday', color='primary', outline=True, size='sm', className='w-100 mb-1'),
                        ], className='d-grid gap-1 mb-1'),
                        dbc.ButtonGroup([
                            dbc.Button("This Week", id='quick-week', color='primary', outline=True, size='sm', className='w-100 mb-1'),
                            dbc.Button("This Month", id='quick-month', color='primary', outline=True, size='sm', className='w-100 mb-1'),
                            dbc.Button("Last 3 Months", id='quick-3months', color='primary', outline=True, size='sm', className='w-100 mb-1'),
                        ], className='d-grid gap-1 mb-1'),
                    ], gap=1, className='mb-3'),
                    
                    html.H5("Date Range", className="mb-3", style={'fontWeight': '600', 'color': COLORS['dark']}),
                    
                    dcc.DatePickerRange(
                        id='date-range-picker',
                        start_date=month_start,
                        end_date=today,
                        display_format='DD-MM-YYYY',
                        className="mb-3",
                        style={'width': '100%'}
                    ),
                    
                    html.Hr(style={'borderColor': '#e5e7eb'}),
                    
                    html.H5("Controls", className="mb-3", style={'fontWeight': '600', 'color': COLORS['dark']}),
                    
                    dbc.Checkbox(
                        id='hide-innovative-check',
                        label="Hide 'Innovative Ortho Surgicals'",
                        value=False,
                        className="mb-3"
                    ),
                    
                    dbc.Button(
                        "Refresh Data",
                        id='refresh-btn',
                        color="primary",
                        className="w-100 mb-3",
                        n_clicks=0
                    ),
                    
                    html.Hr(style={'borderColor': '#e5e7eb'}),
                    
                    html.Div([
                        html.P("Data Status:", className="small mb-2 fw-bold", style={'color': COLORS['dark']}),
                        html.Div(id='data-status', className="alert alert-info py-2 small")
                    ])
                ])
            ], className="sidebar-card shadow")
        ], width=3, lg=3, md=12, sm=12),
        
        # Main Content with Tabs
        dbc.Col([
            dcc.Tabs([
                dcc.Tab(label='Dashboard', children=[
                    dcc.Loading(
                        id='main-loading', 
                        children=[html.Div(id='main-content')],
                        type='default',
                        fullscreen=False,
                        color=COLORS['primary']
                    )
                ], className='custom-tab'),
                dcc.Tab(label='My Charts', children=[
                    html.Div(id='my-charts-content')
                ], className='custom-tab')
            ], style={'marginBottom': '1rem'})
        ], width=9, lg=9, md=12, sm=12)
    ], className="g-3"),
    
], fluid=True, className="py-4", style={'maxWidth': '1400px', 'margin': '0 auto'})

# Main content callback
@app.callback(
    Output('main-content', 'children'),
    Output('data-status', 'children'),
    Output('chart-data-store', 'data'),
    Input('username-input', 'value'),
    Input('password-input', 'value'),
    Input('date-range-picker', 'start_date'),
    Input('date-range-picker', 'end_date'),
    Input('refresh-btn', 'n_clicks'),
    Input('hide-innovative-check', 'value'),
    prevent_initial_call=False
)
def update_dashboard(username, password, start_date, end_date, refresh_clicks, hide_innovative):
    """Update entire dashboard when dates change or refresh is clicked"""
    
    if not start_date or not end_date:
        return dbc.Alert("Please select date range", color="warning"), "No date range", None
    
    try:
        # Convert dates to DD-MM-YYYY format
        start_date_obj = pd.to_datetime(start_date)
        end_date_obj = pd.to_datetime(end_date)
        start_date_str = start_date_obj.strftime("%d-%m-%Y")
        end_date_str = end_date_obj.strftime("%d-%m-%Y")
        
        print(f"\nDASH UPDATE TRIGGERED")
        print(f"   Range: {start_date_str} to {end_date_str}")
        print(f"   Hide Innovative: {hide_innovative}")
        print(f"   Refresh clicks: {refresh_clicks}")
        
        # Fetch data from API
        print("   Fetching from API...")
        try:
            api_client = APIClient(username=username, password=password)
            response = api_client.get_sales_report(
                start_date=start_date_str,
                end_date=end_date_str
            )
            
            if not response.get('success'):
                status_text = f"API Error: {response.get('message', 'Unknown error')} | {datetime.now().strftime('%H:%M:%S')}"
                return dbc.Alert(f"Failed to fetch data: {response.get('message')}", color="danger"), status_text, None
            
            # Extract data from response
            api_response = response.get('data', {})
            report_data = api_response.get('report_data', [])
            
            if not report_data:
                status_text = f"No data | {datetime.now().strftime('%H:%M:%S')}"
                return dbc.Alert("No data available for this date range", color="warning"), status_text, None
            
            # Convert to DataFrame
            df = pd.DataFrame(report_data)
        except Exception as e:
            print(f"   Error: {str(e)}")
            status_text = f"Error: {str(e)} | {datetime.now().strftime('%H:%M:%S')}"
            return dbc.Alert(f"Error fetching data: {str(e)}", color="danger"), status_text, None
        
        if df is None or df.empty:
            status_text = f"No data | {datetime.now().strftime('%H:%M:%S')}"
            return dbc.Alert("No data available for this date range", color="warning"), status_text, None
        
        print(f"   Data fetched: {len(df)} rows")
        print(f"   Available columns: {list(df.columns)}")
        
        # Map API column names to standard names
        column_mapping = {
            'SV': 'Value',              # Sales Value -> Value
            'SQ': 'Qty',                # Sales Quantity -> Qty
            'comp_nm': 'Dealer Name',   # Company Name -> Dealer Name
            'category_name': 'Category',
            'state': 'State',
            'city': 'City',
            'meta_keyword': 'Product Name',
            'parent_category': 'Sub Category',
            'cust_id': 'Customer ID',
            'id': 'Order ID',
            'date': 'Date',             # Date field
            'order_date': 'Date',       # Alternative date field
            'created_at': 'Date',       # Alternative date field
            'sale_date': 'Date'         # Alternative date field
        }
        
        # Rename columns that exist in the dataframe
        rename_dict = {old: new for old, new in column_mapping.items() if old in df.columns}
        if rename_dict:
            df = df.rename(columns=rename_dict)
            print(f"   Column mapping applied: {rename_dict}")
            # Check if any date field was mapped
            date_fields = ['date', 'order_date', 'created_at', 'sale_date']
            mapped_date_fields = [field for field in date_fields if field in rename_dict.keys()]
            if mapped_date_fields:
                print(f"   Date field(s) found and mapped: {mapped_date_fields}")
            else:
                print(f"   ⚠️  No date field found in API response!")
        else:
            print(f"   ⚠️  No columns matched for mapping!")
        
        # Convert numeric columns to float
        if 'Value' in df.columns:
            df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        if 'Qty' in df.columns:
            df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce')
        
        # Apply filter
        if hide_innovative and 'Dealer Name' in df.columns:
            df = df[~df['Dealer Name'].str.contains('Innovative', case=False, na=False)]
            print(f"   Filtered: {len(df)} rows")
        
        # Detect columns
        VALUE_COLS = [c for c in df.columns if c.startswith('Value') and c != 'Value']
        QTY_COLS = [c for c in df.columns if c.startswith('Qty') and c != 'Qty']
        
        if not VALUE_COLS and 'Value' in df.columns:
            VALUE_COLS = ['Value']
        if not QTY_COLS and 'Qty' in df.columns:
            QTY_COLS = ['Qty']
        
        VALUE_COL = VALUE_COLS[0] if VALUE_COLS else None
        QTY_COL = QTY_COLS[0] if QTY_COLS else None
        
        # Calculate metrics
        revenue = df[VALUE_COL].sum() if VALUE_COL else 0
        quantity = df[QTY_COL].sum() if QTY_COL else 0
        total_orders = len(df)
        
        print(f"   Revenue: {format_inr(revenue)}")
        print(f"   Quantity: {format_qty(quantity)}")
        
        # Calculate previous period for comparison (same duration before current period)
        start_date_obj = pd.to_datetime(start_date)
        end_date_obj = pd.to_datetime(end_date)
        period_duration = (end_date_obj - start_date_obj).days
        
        prev_start_date = start_date_obj - pd.Timedelta(days=period_duration + 1)
        prev_end_date = start_date_obj - pd.Timedelta(days=1)
        
        # Fetch previous period data for comparison
        try:
            prev_start_str = prev_start_date.strftime("%d-%m-%Y")
            prev_end_str = prev_end_date.strftime("%d-%m-%Y")
            
            prev_response = api_client.get_sales_report(
                start_date=prev_start_str,
                end_date=prev_end_str
            )
            
            if prev_response.get('success'):
                prev_report_data = prev_response.get('data', {}).get('report_data', [])
                prev_df = pd.DataFrame(prev_report_data)
                
                if not prev_df.empty:
                    # Rename columns
                    prev_df = prev_df.rename(columns={old: new for old, new in column_mapping.items() if old in prev_df.columns})
                    
                    # Convert numeric columns
                    if 'Value' in prev_df.columns:
                        prev_df['Value'] = pd.to_numeric(prev_df['Value'], errors='coerce')
                    if 'Qty' in prev_df.columns:
                        prev_df['Qty'] = pd.to_numeric(prev_df['Qty'], errors='coerce')
                    
                    # Apply filter
                    if hide_innovative and 'Dealer Name' in prev_df.columns:
                        prev_df = prev_df[~prev_df['Dealer Name'].str.contains('Innovative', case=False, na=False)]
                    
                    prev_revenue = prev_df[VALUE_COL].sum() if VALUE_COL else 0
                    prev_quantity = prev_df[QTY_COL].sum() if QTY_COL else 0
                    prev_orders = len(prev_df)
                else:
                    prev_revenue = 0
                    prev_quantity = 0
                    prev_orders = 0
            else:
                prev_revenue = 0
                prev_quantity = 0
                prev_orders = 0
        except:
            prev_revenue = 0
            prev_quantity = 0
            prev_orders = 0
        
        # Calculate trend data (last 30 days) for sparklines
        revenue_trend = []
        quantity_trend = []
        orders_trend = []
        
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df_with_date = df.dropna(subset=['Date'])
            
            if not df_with_date.empty:
                # Get daily aggregates
                daily_data = df_with_date.groupby(df_with_date['Date'].dt.date).agg({
                    VALUE_COL: 'sum' if VALUE_COL else lambda x: 0,
                    QTY_COL: 'sum' if QTY_COL else lambda x: 0
                }).reset_index()
                daily_data['orders'] = df_with_date.groupby(df_with_date['Date'].dt.date).size().values
                
                # Take last 30 days or available days
                daily_data = daily_data.tail(30)
                
                revenue_trend = daily_data[VALUE_COL].tolist() if VALUE_COL else []
                quantity_trend = daily_data[QTY_COL].tolist() if QTY_COL else []
                orders_trend = daily_data['orders'].tolist()
        
        # Calculate additional metrics

        if QTY_COL and QTY_COL in df.columns:
            prod_cols = ['Product Name', 'Item Name', 'Sub Category']
            prod_col = next((c for c in prod_cols if c in df.columns), None)
            most_sold = df.groupby(prod_col)[QTY_COL].sum().idxmax() if prod_col else "N/A"
        else:
            most_sold = "N/A"
        
        # Top locations with previous period data
        most_state = df['State'].value_counts().idxmax() if 'State' in df.columns else "N/A"
        state_count = df['State'].value_counts().max() if 'State' in df.columns else 0
        prev_state_count = prev_df['State'].value_counts().max() if not prev_df.empty and 'State' in prev_df.columns else 0
        
        most_city = df['City'].value_counts().idxmax() if 'City' in df.columns else "N/A"
        city_count = df['City'].value_counts().max() if 'City' in df.columns else 0
        prev_city_count = prev_df['City'].value_counts().max() if not prev_df.empty and 'City' in prev_df.columns else 0
        
        most_dealer = df['Dealer Name'].value_counts().idxmax() if 'Dealer Name' in df.columns else "N/A"
        dealer_count = df['Dealer Name'].value_counts().max() if 'Dealer Name' in df.columns else 0
        prev_dealer_count = prev_df['Dealer Name'].value_counts().max() if not prev_df.empty and 'Dealer Name' in prev_df.columns else 0
        
        category_count = df['Category'].nunique() if 'Category' in df.columns else 0
        prev_category_count = prev_df['Category'].nunique() if not prev_df.empty and 'Category' in prev_df.columns else 0
        
        # Generate trend data for location-based metrics
        state_trend = []
        city_trend = []
        dealer_trend = []
        category_trend = []
        
        if 'Date' in df.columns and not df_with_date.empty:
            try:
                daily_state = df_with_date.groupby(df_with_date['Date'].dt.date)['State'].apply(lambda x: x.value_counts().max() if len(x) > 0 else 0).tail(30).tolist()
                daily_city = df_with_date.groupby(df_with_date['Date'].dt.date)['City'].apply(lambda x: x.value_counts().max() if len(x) > 0 else 0).tail(30).tolist()
                daily_dealer = df_with_date.groupby(df_with_date['Date'].dt.date)['Dealer Name'].apply(lambda x: x.value_counts().max() if len(x) > 0 else 0).tail(30).tolist()
                daily_category = df_with_date.groupby(df_with_date['Date'].dt.date)['Category'].nunique().tail(30).tolist()
                
                state_trend = daily_state
                city_trend = daily_city
                dealer_trend = daily_dealer
                category_trend = daily_category
            except:
                pass

        
        # Check if date data is available and valid
        has_date_data = False
        if 'Date' in df.columns:
            # Convert Date to datetime if not already done
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            # Check if we have any valid dates
            has_date_data = df['Date'].notna().any()
        
        print(f"   Has date data: {has_date_data}")
        if has_date_data:
            print(f"   Date column sample: {df['Date'].head()}")
            print(f"   Valid dates: {df['Date'].notna().sum()} out of {len(df)}")
        else:
            print(f"   Available columns: {list(df.columns)}")
            if 'Date' in df.columns:
                print(f"   Date column exists but no valid dates found")
        
        # Build dashboard content
        metrics_content = html.Div([
            # First row of metrics - Enhanced with sparklines
            dbc.Row([
                dbc.Col([
                    _create_enhanced_metric_card(
                        icon="Revenue",
                        label="Revenue",
                        current_value=format_inr(revenue),
                        previous_value=prev_revenue,
                        trend_values=revenue_trend,
                        color='#2ECC71',
                        gradient_start='rgba(46, 204, 113, 0.1)',
                        gradient_end='rgba(46, 204, 113, 0.02)',
                        date_range_text=f"{start_date_str} → {end_date_str}"
                    )
                ], width=3, className="d-flex"),
                
                dbc.Col([
                    _create_enhanced_metric_card(
                        icon="Quantity",
                        label="Total Quantity",
                        current_value=format_qty(quantity),
                        previous_value=prev_quantity,
                        trend_values=quantity_trend,
                        color='#3498DB',
                        gradient_start='rgba(52, 152, 219, 0.1)',
                        gradient_end='rgba(52, 152, 219, 0.02)',
                        date_range_text=f"{start_date_str} → {end_date_str}"
                    )
                ], width=3, className="d-flex"),
                
                dbc.Col([
                    _create_enhanced_metric_card(
                        icon="Most Sold",
                        label="Most Sold",
                        current_value=most_sold[:25] if len(most_sold) > 25 else most_sold,
                        previous_value=0,
                        trend_values=[],
                        color='#F1C40F',
                        gradient_start='rgba(241, 196, 15, 0.1)',
                        gradient_end='rgba(241, 196, 15, 0.02)',
                        date_range_text="Top item by quantity"
                    )
                ], width=3, className="d-flex"),
                
                dbc.Col([
                    _create_enhanced_metric_card(
                        icon="Orders",
                        label="Orders",
                        current_value=f"{total_orders:,}",
                        previous_value=prev_orders,
                        trend_values=orders_trend,
                        color='#E74C3C',
                        gradient_start='rgba(231, 76, 60, 0.1)',
                        gradient_end='rgba(231, 76, 60, 0.02)',
                        date_range_text=f"{start_date_str} → {end_date_str}"
                    )
                ], width=3, className="d-flex"),
            ], className="mb-4 g-2"),
            
            # Second row of metrics - Enhanced with sparklines
            dbc.Row([
                dbc.Col([
                    _create_enhanced_metric_card(
                        icon="State",
                        label="Top State",
                        current_value=f"{most_state}\n{state_count} orders",
                        previous_value=prev_state_count,
                        trend_values=state_trend,
                        color='#9B59B6',
                        gradient_start='rgba(155, 89, 182, 0.1)',
                        gradient_end='rgba(155, 89, 182, 0.02)',
                        date_range_text=f"{start_date_str} → {end_date_str}"
                    )
                ], width=3, className="d-flex"),
                
                dbc.Col([
                    _create_enhanced_metric_card(
                        icon="City",
                        label="Top City",
                        current_value=f"{most_city}\n{city_count} orders",
                        previous_value=prev_city_count,
                        trend_values=city_trend,
                        color='#1ABC9C',
                        gradient_start='rgba(26, 188, 156, 0.1)',
                        gradient_end='rgba(26, 188, 156, 0.02)',
                        date_range_text=f"{start_date_str} → {end_date_str}"
                    )
                ], width=3, className="d-flex"),
                
                dbc.Col([
                    _create_enhanced_metric_card(
                        icon="Dealer",
                        label="Top Dealer",
                        current_value=f"{most_dealer[:14]}\n{dealer_count} orders",
                        previous_value=prev_dealer_count,
                        trend_values=dealer_trend,
                        color='#E67E22',
                        gradient_start='rgba(230, 126, 34, 0.1)',
                        gradient_end='rgba(230, 126, 34, 0.02)',
                        date_range_text=f"{start_date_str} → {end_date_str}"
                    )
                ], width=3, className="d-flex"),
                
                dbc.Col([
                    _create_enhanced_metric_card(
                        icon="Categories",
                        label="Categories",
                        current_value=f"{category_count}",
                        previous_value=prev_category_count,
                        trend_values=category_trend,
                        color='#34495E',
                        gradient_start='rgba(52, 73, 94, 0.1)',
                        gradient_end='rgba(52, 73, 94, 0.02)',
                        date_range_text="Unique categories"
                    )
                ], width=3, className="d-flex"),
            ], className="mb-4 g-2"),
            
            html.Hr(className="my-4"),
            
            # Geographic Map Section
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("Geographic Sales Distribution", className="mb-0 fw-bold text-primary"),
                            html.Small("Interactive map showing sales across India", style={'color': '#000000'})
                        ]),
                        dbc.CardBody([
                            # Map Controls
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Metric", className="fw-bold"),
                                    dbc.RadioItems(
                                        id='map-metric-selector',
                                        options=[
                                            {'label': 'Revenue', 'value': 'Revenue'},
                                            {'label': 'Quantity', 'value': 'Quantity'},
                                            {'label': 'Order Count', 'value': 'Orders'}
                                        ],
                                        value='Revenue',
                                        inline=True,
                                        className="mb-2"
                                    )
                                ], width=4),
                                dbc.Col([
                                    dbc.Label("View Level", className="fw-bold"),
                                    dbc.RadioItems(
                                        id='map-level-selector',
                                        options=[
                                            {'label': 'State', 'value': 'State'},
                                            {'label': 'City', 'value': 'City'}
                                        ],
                                        value='State',
                                        inline=True,
                                        className="mb-2"
                                    )
                                ], width=4),
                                dbc.Col([
                                    dbc.Label("Map Style", className="fw-bold"),
                                    dbc.Switch(
                                        id='map-bubble-toggle',
                                        label='Bubble Map',
                                        value=False,
                                        className="mb-2"
                                    ),
                                    dbc.Button(
                                        "Reset View",
                                        id='map-reset-btn',
                                        size='sm',
                                        color='secondary',
                                        outline=True,
                                        className="mt-1"
                                    )
                                ], width=4),
                            ], className="mb-3"),
                            
                            # Selected Location Display
                            html.Div(id='selected-location-display', className="mb-2"),
                            
                            # Map
                            dcc.Loading(
                                dcc.Graph(
                                    id='geographic-map',
                                    config={'displayModeBar': True, 'scrollZoom': True},
                                    style={'height': '600px'}
                                ),
                                type='default'
                            )
                        ])
                    ], className="shadow-sm")
                ], width=12)
            ], className="mb-4"),
            
            html.Hr(className="my-4"),
            
            # Charts
            html.H4("Analytics", className="mb-4 fw-bold"),
            
            # First Row - Dealers and States
            dbc.Row([
                # Dealer Pie Chart with Filter
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.Div([
                                html.H6("Top Dealers by Revenue", className="mb-2"),
                                dcc.Dropdown(
                                    id='dealer-filter',
                                    placeholder='Select dealers...',
                                    multi=True,
                                    className='mb-2'
                                )
                            ])
                        ]),
                        dbc.CardBody([
                            dcc.Graph(id='dealer-pie-chart', config={'displayModeBar': True})
                        ])
                    ])
                ], width=6),
                
                # State Pie Chart with Filter
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.Div([
                                html.H6("Revenue by State", className="mb-2"),
                                dcc.Dropdown(
                                    id='state-filter',
                                    placeholder='Select states...',
                                    multi=True,
                                    className='mb-2'
                                )
                            ])
                        ]),
                        dbc.CardBody([
                            dcc.Graph(id='state-pie-chart', config={'displayModeBar': True})
                        ])
                    ])
                ], width=6),
            ], className="g-2 mb-3"),
            
            # Second Row - Categories and Cities
            dbc.Row([
                # Category Bar Chart with Filter
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.Div([
                                html.H6("Revenue by Category", className="mb-2"),
                                dcc.Dropdown(
                                    id='category-filter',
                                    placeholder='Select categories...',
                                    multi=True,
                                    className='mb-2'
                                )
                            ])
                        ]),
                        dbc.CardBody([
                            dcc.Graph(id='category-bar-chart', config={'displayModeBar': True})
                        ])
                    ])
                ], width=6),
                
                # City Bar Chart with Filter
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.Div([
                                html.H6("Top Cities by Revenue", className="mb-2"),
                                dcc.Dropdown(
                                    id='city-filter',
                                    placeholder='Select cities...',
                                    multi=True,
                                    className='mb-2'
                                )
                            ])
                        ]),
                        dbc.CardBody([
                            dcc.Graph(id='city-bar-chart', config={'displayModeBar': True})
                        ])
                    ])
                ], width=6),
            ], className="g-2 mb-4"),
            
            # New Analytics Section - Only include if date data is available
            *(dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=_create_revenue_trend(df, VALUE_COL), config={'displayModeBar': True})
                        ])
                    ])
                ], width=12),
            ], className="g-2 mb-4") if has_date_data else []),
            
            dbc.Row([
                dbc.Col([
                    _create_top_products_table(df, VALUE_COL, QTY_COL)
                ], width=8 if has_date_data else 12),
                
                # Only include weekday pattern if date data is available
                *(dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=_create_weekday_pattern(df, VALUE_COL), config={'displayModeBar': True})
                        ])
                    ])
                ], width=4) if has_date_data else []),
            ], className="g-2 mb-4"),
            
            dbc.Row([
                # Dealer Comparison Chart with Filter
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.Div([
                                html.H6("Dealer Comparison", className="mb-2"),
                                dcc.Dropdown(
                                    id='dealer-comp-filter',
                                    placeholder='Select dealers...',
                                    multi=True,
                                    className='mb-2'
                                )
                            ])
                        ]),
                        dbc.CardBody([
                            dcc.Graph(id='dealer-comparison-chart', config={'displayModeBar': True})
                        ])
                    ])
                ], width=4),
                
                # City Bar Chart 2 with Filter
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.Div([
                                html.H6("Cities by Revenue", className="mb-2"),
                                dcc.Dropdown(
                                    id='city-filter-2',
                                    placeholder='Select cities...',
                                    multi=True,
                                    className='mb-2'
                                )
                            ])
                        ]),
                        dbc.CardBody([
                            dcc.Graph(id='city-bar-chart-2', config={'displayModeBar': True})
                        ])
                    ])
                ], width=4),
                
                # Category Sunburst with Filter
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.Div([
                                html.H6("Category Hierarchy", className="mb-2"),
                                dcc.Dropdown(
                                    id='category-sunburst-filter',
                                    placeholder='Select categories...',
                                    multi=True,
                                    className='mb-2'
                                )
                            ])
                        ]),
                        dbc.CardBody([
                            dcc.Graph(id='category-sunburst-chart', config={'displayModeBar': True})
                        ])
                    ])
                ], width=4),
            ], className="g-2 mb-4"),
            
            # Advanced Revenue Comparison Section - Only show if date data available
            *([] if not has_date_data else [
                html.Hr(className="my-4"),
                html.H4("Advanced Revenue Analysis", className="mb-4 fw-bold"),
                
                dbc.Row([
                    dbc.Col([
                        html.Div(id='revenue-comparison-container')
                    ], width=12)
                ], className="mb-4")
            ]),
            
            # Activity Patterns Section - Only show if date data available
            *([] if not has_date_data else [
                html.Hr(className="my-4"),
                html.H4("� Activity Patterns", className="mb-4 fw-bold"),
                html.P("Analyze sales patterns across time dimensions to identify peak activity periods", className="text-muted mb-4"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                dcc.Graph(
                                    figure=_create_activity_heatmap(df, VALUE_COL),
                                    config={'displayModeBar': True}
                                )
                            ])
                        ], className="shadow-sm")
                    ], width=4),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                dcc.Graph(figure=_create_hourly_heatmap(df, VALUE_COL), config={'displayModeBar': True})
                            ])
                        ])
                    ], width=4),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                dcc.Graph(figure=_create_day_part_analysis(df, VALUE_COL), config={'displayModeBar': True})
                            ])
                        ])
                    ], width=4),
                ], className="mb-4")
            ]),
            
            # Funnel and Conversion Analysis Section
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=_create_sales_funnel(df), config={'displayModeBar': True})
                        ])
                    ])
                ], width=6),
                
                # Only show conversion timeline if date data is available
                *(dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=_create_conversion_timeline(df), config={'displayModeBar': True})
                        ])
                    ])
                ], width=6) if has_date_data else []),
                
                # If no date data, add an info message
                *(dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.I(className="bi bi-info-circle", style={'fontSize': '48px', 'color': '#6c757d'}),
                                html.H5("Conversion Timeline Unavailable", className="mt-3 text-muted"),
                                html.P("Date information is required to display conversion metrics over time.", className="text-muted")
                            ], className="text-center py-5")
                        ])
                    ])
                ], width=6) if not has_date_data else []),
            ], className="g-2 mb-4"),
            
            # Slow-Moving Items Tracker Section - Always visible
            html.Hr(className="my-4"),
            html.H4("📦 Slow-Moving Items Tracker", className="mb-3 fw-bold"),
            html.P("Identify products with low sales velocity to optimize inventory management", className="text-muted mb-4"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.Div([
                                    html.H6("Slow-Moving Products Analysis", className="mb-2 d-inline-block"),
                                    dbc.Badge(f"{start_date_str} → {end_date_str}", color="info", className="ms-2")
                                ])
                            ]),
                            dbc.CardBody([
                                # Enhanced Filters Row
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Inactivity Period", className="fw-bold small"),
                                        dbc.RadioItems(
                                            id='slow-moving-days-filter',
                                            options=[
                                                {'label': '7 Days', 'value': 7},
                                                {'label': '15 Days', 'value': 15},
                                                {'label': '30 Days', 'value': 30},
                                                {'label': '60 Days', 'value': 60},
                                                {'label': '90 Days', 'value': 90}
                                            ],
                                            value=30,
                                            inline=True,
                                            className="mb-2"
                                        )
                                    ], width=12)
                                ], className="mb-3"),
                                
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Filter by Category", className="fw-bold small"),
                                        dcc.Dropdown(
                                            id='slow-moving-category-filter',
                                            placeholder='All Categories',
                                            multi=True,
                                            className='mb-2'
                                        )
                                    ], width=4),
                                    dbc.Col([
                                        dbc.Label("Filter by Dealer", className="fw-bold small"),
                                        dcc.Dropdown(
                                            id='slow-moving-dealer-filter',
                                            placeholder='All Dealers',
                                            multi=True,
                                            className='mb-2'
                                        )
                                    ], width=4),
                                    dbc.Col([
                                        dbc.Label("Sort By", className="fw-bold small"),
                                        dbc.Select(
                                            id='slow-moving-sort-by',
                                            options=[
                                                {'label': 'Days Since Last Sale', 'value': 'days'},
                                                {'label': 'Total Revenue', 'value': 'revenue'},
                                                {'label': 'Total Quantity', 'value': 'quantity'},
                                                {'label': 'Sales Velocity', 'value': 'velocity'}
                                            ],
                                            value='days',
                                            className='mb-2'
                                        )
                                    ], width=4),
                                ], className="mb-3"),
                                
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Show Top N Items", className="fw-bold small"),
                                        dbc.Input(
                                            id='slow-moving-top-n',
                                            type='number',
                                            min=10,
                                            max=100,
                                            step=10,
                                            value=20,
                                            className='mb-2'
                                        )
                                    ], width=3),
                                    dbc.Col([
                                        dbc.Label("Minimum Revenue", className="fw-bold small"),
                                        dbc.Input(
                                            id='slow-moving-min-revenue',
                                            type='number',
                                            placeholder='Optional',
                                            className='mb-2'
                                        )
                                    ], width=3),
                                    dbc.Col([
                                        dbc.Button(
                                            "Download Report",
                                            id='slow-moving-download-btn',
                                            color='success',
                                            size='sm',
                                            className='mt-4'
                                        ),
                                        dcc.Download(id='slow-moving-download')
                                    ], width=3),
                                    dbc.Col([
                                        dbc.Button(
                                            "Reset Filters",
                                            id='slow-moving-reset-btn',
                                            color='secondary',
                                            outline=True,
                                            size='sm',
                                            className='mt-4'
                                        )
                                    ], width=3),
                                ], className="mb-3"),
                                
                                html.Div(id='slow-moving-items-content')
                            ])
                        ], className="shadow-sm")
                    ], width=12)
                ], className="mb-4"),
            
            # Cross-Selling Analysis Section - Always visible
            html.Hr(className="my-4"),
            html.H4("🔗 Cross-Selling Analysis", className="mb-3 fw-bold"),
            html.P("Discover product relationships and frequently bought together items to boost sales opportunities", className="text-muted mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.Div([
                                html.H6("Product Association Analysis", className="mb-2 d-inline-block"),
                                dbc.Badge(f"{start_date_str} → {end_date_str}", color="info", className="ms-2")
                            ])
                        ]),
                        dbc.CardBody([
                            # Enhanced Filters Row
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Analysis Type", className="fw-bold small"),
                                    dbc.RadioItems(
                                        id='cross-sell-analysis-type',
                                        options=[
                                            {'label': 'By Product', 'value': 'product'},
                                            {'label': 'By Category', 'value': 'category'},
                                            {'label': 'By Dealer', 'value': 'dealer'}
                                        ],
                                        value='product',
                                        inline=True,
                                        className="mb-2"
                                    )
                                ], width=12)
                            ], className="mb-3"),
                            
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Filter by Category", className="fw-bold small"),
                                    dcc.Dropdown(
                                        id='cross-sell-category-filter',
                                        placeholder='All Categories',
                                        multi=True,
                                        className='mb-2'
                                    )
                                ], width=4),
                                dbc.Col([
                                    dbc.Label("Filter by Dealer", className="fw-bold small"),
                                    dcc.Dropdown(
                                        id='cross-sell-dealer-filter',
                                        placeholder='All Dealers',
                                        multi=True,
                                        className='mb-2'
                                    )
                                ], width=4),
                                dbc.Col([
                                    dbc.Label("Minimum Support (%)", className="fw-bold small"),
                                    dbc.Input(
                                        id='cross-sell-min-support',
                                        type='number',
                                        min=1,
                                        max=100,
                                        step=1,
                                        value=5,
                                        className='mb-2'
                                    )
                                ], width=4),
                            ], className="mb-3"),
                            
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Top N Associations", className="fw-bold small"),
                                    dbc.Input(
                                        id='cross-sell-top-n',
                                        type='number',
                                        min=5,
                                        max=50,
                                        step=5,
                                        value=10,
                                        className='mb-2'
                                    )
                                ], width=3),
                                dbc.Col([
                                    dbc.Label("Minimum Confidence (%)", className="fw-bold small"),
                                    dbc.Input(
                                        id='cross-sell-min-confidence',
                                        type='number',
                                        min=1,
                                        max=100,
                                        step=1,
                                        value=10,
                                        className='mb-2'
                                    )
                                ], width=3),
                                dbc.Col([
                                    dbc.Button(
                                        "Download Report",
                                        id='cross-sell-download-btn',
                                        color='success',
                                        size='sm',
                                        className='mt-4'
                                    ),
                                    dcc.Download(id='cross-sell-download')
                                ], width=3),
                                dbc.Col([
                                    dbc.Button(
                                        "Reset Filters",
                                        id='cross-sell-reset-btn',
                                        color='secondary',
                                        outline=True,
                                        size='sm',
                                        className='mt-4'
                                    )
                                ], width=3),
                            ], className="mb-3"),
                            
                            html.Div(id='cross-sell-content')
                        ])
                    ], className="shadow-sm")
                ], width=12)
            ], className="mb-4"),
            
            # Sales CRM Section
            html.Hr(className="my-4"),
            html.H4("💼 Sales CRM", className="mb-3 fw-bold"),
            html.P("Comprehensive sales transaction management with detailed insights", className="text-muted mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.Div([
                                html.H6("Sales Transactions", className="mb-2 d-inline-block"),
                                dbc.Badge(f"{start_date_str} → {end_date_str}", color="info", className="ms-2"),
                                dbc.Badge(f"{len(df):,} Transactions", color="success", className="ms-2")
                            ])
                        ]),
                        dbc.CardBody([
                            # Filter Controls Row
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Filter by Dealer", className="fw-bold small"),
                                    dcc.Dropdown(
                                        id='crm-dealer-filter',
                                        placeholder='All Dealers',
                                        multi=True,
                                        className='mb-2'
                                    )
                                ], width=3),
                                dbc.Col([
                                    dbc.Label("Filter by State", className="fw-bold small"),
                                    dcc.Dropdown(
                                        id='crm-state-filter',
                                        placeholder='All States',
                                        multi=True,
                                        className='mb-2'
                                    )
                                ], width=3),
                                dbc.Col([
                                    dbc.Label("Filter by Product Family", className="fw-bold small"),
                                    dcc.Dropdown(
                                        id='crm-product-family-filter',
                                        placeholder='All Product Families',
                                        multi=True,
                                        className='mb-2'
                                    )
                                ], width=3),
                                dbc.Col([
                                    dbc.Label("Payment Status", className="fw-bold small"),
                                    dcc.Dropdown(
                                        id='crm-payment-status-filter',
                                        options=[
                                            {'label': 'All', 'value': 'all'},
                                            {'label': 'Paid', 'value': 'paid'},
                                            {'label': 'Pending', 'value': 'pending'},
                                            {'label': 'Overdue', 'value': 'overdue'}
                                        ],
                                        value='all',
                                        className='mb-2'
                                    )
                                ], width=3),
                            ], className="mb-3"),
                            
                            # Search and Export Controls
                            dbc.Row([
                                dbc.Col([
                                    dbc.InputGroup([
                                        dbc.InputGroupText("🔍"),
                                        dbc.Input(
                                            id='crm-search-input',
                                            placeholder="Search across all fields...",
                                            type="text",
                                            debounce=True
                                        )
                                    ])
                                ], width=8),
                                dbc.Col([
                                    dbc.ButtonGroup([
                                        dbc.Button("Export CRM Data", id='crm-export-btn', color="success", size="sm"),
                                        dbc.Button("Clear Filters", id='crm-clear-filters-btn', color="secondary", outline=True, size="sm"),
                                    ], className="float-end"),
                                    dcc.Download(id='crm-download')
                                ], width=4),
                            ], className="mb-3"),
                            
                            # CRM Table
                            html.Div(id='crm-table-container')
                        ])
                    ], className="shadow-sm")
                ], width=12)
            ], className="mb-4"),
            
            # Custom Chart Builder Section
            html.Hr(),
            dbc.Button("Create Custom Chart", id="toggle-custom-builder", color="secondary", className="mb-3"),
            dbc.Collapse(
                dbc.Card([
                    dbc.CardHeader("Custom Chart Builder"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("X-axis"),
                                dcc.Dropdown(
                                    id='custom-x-axis',
                                    options=[{'label': col, 'value': col} for col in ['Dealer Name', 'State', 'City', 'Category', 'Sub Category', 'Product Name']],
                                    placeholder="Select X-axis"
                                )
                            ], width=6),
                            dbc.Col([
                                dbc.Label("Y-axis"),
                                dcc.Dropdown(
                                    id='custom-y-axis',
                                    options=[{'label': opt, 'value': opt} for opt in ['Sum of Revenue', 'Sum of Quantity', 'Count of Orders', 'Average Revenue', 'Average Quantity']],
                                    placeholder="Select Y-axis"
                                )
                            ], width=6),
                        ], className="mb-3"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Chart Type"),
                                dcc.Dropdown(
                                    id='custom-chart-type',
                                    options=[{'label': opt, 'value': opt} for opt in ['Bar Chart', 'Horizontal Bar', 'Pie Chart', 'Line Chart', 'Scatter Plot', 'Sunburst']],
                                    placeholder="Select Chart Type"
                                )
                            ], width=6),
                            dbc.Col([
                                dbc.Label("Aggregation"),
                                dcc.Dropdown(
                                    id='custom-agg-type',
                                    options=[{'label': opt, 'value': opt} for opt in ['Sum', 'Average', 'Count', 'Min', 'Max']],
                                    value='Sum',
                                    placeholder="Select Aggregation"
                                )
                            ], width=6),
                        ], className="mb-3"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Top N Items"),
                                dbc.Input(type='number', id='custom-top-n', min=5, max=50, value=10, step=5)
                            ], width=6),
                            dbc.Col([
                                dbc.Checkbox(id='custom-sort-desc', label="Sort Descending", value=True),
                                dbc.Button("Generate Chart", id='generate-custom-chart-btn', color='primary', className="mt-2")
                            ], width=6),
                        ], className="mb-3"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Chart Name"),
                                dbc.Input(id='chart-save-name', type='text', placeholder='Enter chart name to save')
                            ], width=8),
                            dbc.Col([
                                dbc.Button("Save Chart", id='save-chart-btn', color='success', className="mt-2")
                            ], width=4),
                        ], className="mb-3"),
                        html.Div(id='save-chart-status'),
                        html.Div(id='custom-chart-output')
                    ])
                ]),
                id="custom-builder-collapse",
                is_open=False,
            ),
            
            # Advanced Data Table Section
            html.Hr(className="my-4"),
            dbc.Button(
                "View Detailed Data Table", 
                id="toggle-data-table", 
                color="info", 
                className="mb-3",
                size="lg"
            ),
            dbc.Collapse(
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Detailed Sales Data", className="mb-0 d-inline-block"),
                        dbc.Badge(f"{len(df):,} records", color="primary", className="ms-2")
                    ]),
                    dbc.CardBody([
                        # Controls Row
                        dbc.Row([
                            dbc.Col([
                                dbc.InputGroup([
                                    dbc.InputGroupText("Search"),
                                    dbc.Input(
                                        id='table-global-search',
                                        placeholder="Search across all columns...",
                                        type="text",
                                        debounce=True
                                    )
                                ])
                            ], width=6),
                            dbc.Col([
                                dbc.ButtonGroup([
                                    dbc.Button("Export Selected", id='export-selected-btn', color="success", size="sm"),
                                    dbc.Button("Export All", id='export-all-btn', color="primary", size="sm"),
                                    dbc.Button("Clear Filters", id='clear-filters-btn', color="secondary", size="sm"),
                                ], className="float-end")
                            ], width=6),
                        ], className="mb-3"),
                        
                        # Column Visibility Controls
                        dbc.Row([
                            dbc.Col([
                                html.Label("Show/Hide Columns:", className="fw-bold small"),
                                dbc.Checklist(
                                    id='column-visibility-checklist',
                                    options=[
                                        {'label': ' Date', 'value': 'Date'},
                                        {'label': ' Order ID', 'value': 'Order ID'},
                                        {'label': ' Dealer Name', 'value': 'Dealer Name'},
                                        {'label': ' City', 'value': 'City'},
                                        {'label': ' State', 'value': 'State'},
                                        {'label': ' Category', 'value': 'Category'},
                                        {'label': ' Product', 'value': 'Product Name'},
                                        {'label': ' Quantity', 'value': 'Qty'},
                                        {'label': ' Revenue', 'value': VALUE_COL},
                                    ],
                                    value=['Date', 'Order ID', 'Dealer Name', 'City', 'State', 'Category', 'Product Name', 'Qty', VALUE_COL],
                                    inline=True,
                                    className="small"
                                )
                            ])
                        ], className="mb-3"),
                        
                        # AG Grid Table
                        html.Div([
                            dag.AgGrid(
                                id='sales-data-table',
                                rowData=df.to_dict('records'),
                                columnDefs=[
                                    {
                                        'headerName': 'Date',
                                        'field': 'Date',
                                        'filter': 'agDateColumnFilter',
                                        'sortable': True,
                                        'resizable': True,
                                        'width': 110,
                                        'checkboxSelection': True,
                                        'headerCheckboxSelection': True,
                                    },
                                    {
                                        'headerName': 'Order ID',
                                        'field': 'Order ID',
                                        'filter': 'agTextColumnFilter',
                                        'sortable': True,
                                        'resizable': True,
                                        'width': 120,
                                    },
                                    {
                                        'headerName': 'Dealer Name',
                                        'field': 'Dealer Name',
                                        'filter': 'agTextColumnFilter',
                                        'sortable': True,
                                        'resizable': True,
                                        'width': 200,
                                    },
                                    {
                                        'headerName': 'City',
                                        'field': 'City',
                                        'filter': 'agTextColumnFilter',
                                        'sortable': True,
                                        'resizable': True,
                                        'width': 130,
                                    },
                                    {
                                        'headerName': 'State',
                                        'field': 'State',
                                        'filter': 'agTextColumnFilter',
                                        'sortable': True,
                                        'resizable': True,
                                        'width': 130,
                                    },
                                    {
                                        'headerName': 'Category',
                                        'field': 'Category',
                                        'filter': 'agTextColumnFilter',
                                        'sortable': True,
                                        'resizable': True,
                                        'width': 150,
                                    },
                                    {
                                        'headerName': 'Product',
                                        'field': 'Product Name',
                                        'filter': 'agTextColumnFilter',
                                        'sortable': True,
                                        'resizable': True,
                                        'width': 250,
                                    },
                                    {
                                        'headerName': 'Quantity',
                                        'field': 'Qty',
                                        'filter': 'agNumberColumnFilter',
                                        'sortable': True,
                                        'resizable': True,
                                        'width': 100,
                                        'type': 'numericColumn',
                                        'valueFormatter': {'function': 'Number(params.value).toLocaleString()'}
                                    },
                                    {
                                        'headerName': 'Revenue (₹)',
                                        'field': VALUE_COL,
                                        'filter': 'agNumberColumnFilter',
                                        'sortable': True,
                                        'resizable': True,
                                        'width': 130,
                                        'type': 'numericColumn',
                                        'valueFormatter': {'function': 'd3.format(",.2f")(params.value)'}
                                    },
                                ],
                                defaultColDef={
                                    'filter': True,
                                    'sortable': True,
                                    'resizable': True,
                                    'minWidth': 100,
                                },
                                dashGridOptions={
                                    'pagination': True,
                                    'paginationPageSize': 50,
                                    'paginationPageSizeSelector': [25, 50, 100, 200],
                                    'enableRangeSelection': True,
                                    'rowSelection': 'multiple',
                                    'suppressRowClickSelection': True,
                                    'animateRows': True,
                                },
                                className="ag-theme-alpine",
                                style={'height': '600px', 'width': '100%'},
                            )
                        ]),
                        
                        # Download component
                        dcc.Download(id='download-table-data'),
                        
                        # Info footer
                        html.Div([
                            html.Small([
                                "Tips: Click column headers to sort • Use filter icons to search • Select rows with checkboxes • Export selected or all data",
                            ], className="text-muted")
                        ], className="mt-3")
                    ])
                ]),
                id="data-table-collapse",
                is_open=False,
            ),
        ])
        
        # Status text
        status_text = f"{len(df):,} records | Last updated: {datetime.now().strftime('%H:%M:%S')}"
        
        # Prepare chart data for store
        chart_data = {
            'data': df.to_dict('records'),
            'VALUE_COL': VALUE_COL,
            'QTY_COL': QTY_COL,
            'dealers': sorted(df['Dealer Name'].unique().tolist()) if 'Dealer Name' in df.columns else [],
            'states': sorted(df['State'].unique().tolist()) if 'State' in df.columns else [],
            'cities': sorted(df['City'].unique().tolist()) if 'City' in df.columns else [],
            'categories': sorted(df['Category'].unique().tolist()) if 'Category' in df.columns else [],
        }
        
        return metrics_content, status_text, chart_data
    
    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
        status_text = f"Error | {datetime.now().strftime('%H:%M:%S')}"
        return dbc.Alert(f"Error: {str(e)}", color="danger"), status_text, None

# Toggle Custom Chart Builder Callback
@app.callback(
    Output("custom-builder-collapse", "is_open"),
    Input("toggle-custom-builder", "n_clicks"),
    State("custom-builder-collapse", "is_open"),
)
def toggle_custom_builder(n, is_open):
    if n:
        return not is_open
    return is_open

# Populate dropdown options from chart data
@app.callback(
    Output('dealer-filter', 'options'),
    Output('dealer-filter', 'value'),
    Output('state-filter', 'options'),
    Output('state-filter', 'value'),
    Output('category-filter', 'options'),
    Output('category-filter', 'value'),
    Output('city-filter', 'options'),
    Output('city-filter', 'value'),
    Output('dealer-comp-filter', 'options'),
    Output('dealer-comp-filter', 'value'),
    Output('city-filter-2', 'options'),
    Output('city-filter-2', 'value'),
    Output('category-sunburst-filter', 'options'),
    Output('category-sunburst-filter', 'value'),
    Input('chart-data-store', 'data'),
    prevent_initial_call=True
)
def populate_filter_options(chart_data):
    """Populate all dropdown filters with available options"""
    if not chart_data:
        return [], [], [], [], [], [], [], [], [], [], [], [], [], []
    
    dealer_options = [{'label': d, 'value': d} for d in chart_data.get('dealers', [])]
    state_options = [{'label': s, 'value': s} for s in chart_data.get('states', [])]
    city_options = [{'label': c, 'value': c} for c in chart_data.get('cities', [])]
    category_options = [{'label': cat, 'value': cat} for cat in chart_data.get('categories', [])]
    
    # Return options and None for values (all selected by default)
    return (
        dealer_options, None,  # dealer-filter
        state_options, None,   # state-filter
        category_options, None,  # category-filter
        city_options, None,    # city-filter
        dealer_options, None,  # dealer-comp-filter
        city_options, None,    # city-filter-2
        category_options, None  # category-sunburst-filter
    )

# Update charts based on filter selections
@app.callback(
    Output('dealer-pie-chart', 'figure'),
    Output('state-pie-chart', 'figure'),
    Output('category-bar-chart', 'figure'),
    Output('city-bar-chart', 'figure'),
    Output('dealer-comparison-chart', 'figure'),
    Output('city-bar-chart-2', 'figure'),
    Output('category-sunburst-chart', 'figure'),
    Input('dealer-filter', 'value'),
    Input('state-filter', 'value'),
    Input('category-filter', 'value'),
    Input('city-filter', 'value'),
    Input('dealer-comp-filter', 'value'),
    Input('city-filter-2', 'value'),
    Input('category-sunburst-filter', 'value'),
    State('chart-data-store', 'data'),
    prevent_initial_call=True
)
def update_filtered_charts(dealer_filter, state_filter, category_filter, city_filter,
                           dealer_comp_filter, city_filter_2, category_sunburst_filter,
                           chart_data):
    """Update all charts based on filter selections"""
    
    if not chart_data or not chart_data.get('data'):
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font={'size': 16, 'color': 'gray'}
        )
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig
    
    # Convert data back to DataFrame
    df = pd.DataFrame(chart_data['data'])
    VALUE_COL = chart_data.get('VALUE_COL', 'Value')
    QTY_COL = chart_data.get('QTY_COL', 'Qty')
    
    # Apply filters and create charts
    # Dealer Pie Chart
    df_dealer = df.copy()
    if dealer_filter and len(dealer_filter) > 0:
        df_dealer = df_dealer[df_dealer['Dealer Name'].isin(dealer_filter)]
    fig_dealer = _create_dealer_pie(df_dealer, VALUE_COL, limit=10)
    
    # State Pie Chart
    df_state = df.copy()
    if state_filter and len(state_filter) > 0:
        df_state = df_state[df_state['State'].isin(state_filter)]
    fig_state = _create_state_pie(df_state, VALUE_COL)
    
    # Category Bar Chart
    df_category = df.copy()
    if category_filter and len(category_filter) > 0:
        df_category = df_category[df_category['Category'].isin(category_filter)]
    fig_category = _create_category_bar(df_category, VALUE_COL)
    
    # City Bar Chart
    df_city = df.copy()
    if city_filter and len(city_filter) > 0:
        df_city = df_city[df_city['City'].isin(city_filter)]
    fig_city = _create_city_bar(df_city, VALUE_COL)
    
    # Dealer Comparison Chart
    df_dealer_comp = df.copy()
    if dealer_comp_filter and len(dealer_comp_filter) > 0:
        df_dealer_comp = df_dealer_comp[df_dealer_comp['Dealer Name'].isin(dealer_comp_filter)]
    fig_dealer_comp = _create_dealer_comparison(df_dealer_comp, VALUE_COL, QTY_COL)
    
    # City Bar Chart 2
    df_city_2 = df.copy()
    if city_filter_2 and len(city_filter_2) > 0:
        df_city_2 = df_city_2[df_city_2['City'].isin(city_filter_2)]
    fig_city_2 = _create_city_bar(df_city_2, VALUE_COL)
    
    # Category Sunburst
    df_sunburst = df.copy()
    if category_sunburst_filter and len(category_sunburst_filter) > 0:
        df_sunburst = df_sunburst[df_sunburst['Category'].isin(category_sunburst_filter)]
    fig_sunburst = _create_category_sunburst(df_sunburst, VALUE_COL)
    
    return fig_dealer, fig_state, fig_category, fig_city, fig_dealer_comp, fig_city_2, fig_sunburst

# Revenue Comparison Chart Callback
@app.callback(
    Output('revenue-comparison-container', 'children'),
    Input('username-input', 'value'),
    Input('password-input', 'value'),
    Input('date-range-picker', 'start_date'),
    Input('date-range-picker', 'end_date'),
    Input('hide-innovative-check', 'value'),
    prevent_initial_call=False
)
def update_revenue_comparison(username, password, start_date, end_date, hide_innovative):
    """Update revenue comparison chart with controls"""
    
    if not start_date or not end_date:
        return dbc.Alert("Please select date range", color="warning")
    
    try:
        # Convert dates
        start_date_obj = pd.to_datetime(start_date)
        end_date_obj = pd.to_datetime(end_date)
        start_date_str = start_date_obj.strftime("%d-%m-%Y")
        end_date_str = end_date_obj.strftime("%d-%m-%Y")
        
        # Fetch data
        api_client = APIClient(username=username, password=password)
        response = api_client.get_sales_report(start_date=start_date_str, end_date=end_date_str)
        
        if not response.get('success'):
            return dbc.Alert(f"API Error: {response.get('message')}", color="danger")
        
        api_response = response.get('data', {})
        report_data = api_response.get('report_data', [])
        
        if not report_data:
            return dbc.Alert("No data available for this date range", color="warning")
        
        df = pd.DataFrame(report_data)
        
        # Map columns
        column_mapping = {
            'SV': 'Value',
            'SQ': 'Qty',
            'comp_nm': 'Dealer Name',
            'category_name': 'Category',
            'state': 'State',
            'city': 'City',
            'meta_keyword': 'Product Name',
            'parent_category': 'Sub Category'
        }
        df = df.rename(columns={old: new for old, new in column_mapping.items() if old in df.columns})
        
        # Convert numeric
        if 'Value' in df.columns:
            df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        if 'Qty' in df.columns:
            df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce')
        
        # Apply filter
        if hide_innovative and 'Dealer Name' in df.columns:
            df = df[~df['Dealer Name'].str.contains('Innovative', case=False, na=False)]
        
        # Get value column
        VALUE_COLS = [c for c in df.columns if c.startswith('Value') and c != 'Value']
        VALUE_COL = VALUE_COLS[0] if VALUE_COLS else ('Value' if 'Value' in df.columns else None)
        
        if not VALUE_COL:
            return dbc.Alert("Revenue data not available", color="warning")
        
        # Create chart with default settings (daily, previous period)
        fig, stats = _create_revenue_comparison_chart(df, VALUE_COL, 'daily', 'previous_period')
        
        # Create the card with controls
        card_content = dbc.Card([
            dbc.CardHeader([
                dbc.Row([
                    dbc.Col([
                        html.H5("Revenue Trend Analysis", className="mb-0 fw-bold text-primary")
                    ], width=4),
                    dbc.Col([
                        dbc.ButtonGroup([
                            dbc.Button("Daily", id='period-daily-btn', color='primary', size='sm', outline=False),
                            dbc.Button("Weekly", id='period-weekly-btn', color='primary', size='sm', outline=True),
                            dbc.Button("Monthly", id='period-monthly-btn', color='primary', size='sm', outline=True),
                        ], size='sm')
                    ], width=4, className="text-center"),
                    dbc.Col([
                        dcc.Dropdown(
                            id='comparison-type-selector',
                            options=[
                                {'label': 'vs Previous Period', 'value': 'previous_period'},
                                {'label': 'vs Last Year', 'value': 'last_year'},
                            ],
                            value='previous_period',
                            clearable=False,
                            style={'fontSize': '12px'}
                        )
                    ], width=4),
                ], align='center')
            ], className="py-2"),
            dbc.CardBody([
                dcc.Graph(
                    id='revenue-comparison-graph',
                    figure=fig,
                    config={'displayModeBar': True, 'displaylogo': False}
                )
            ]),
            dbc.CardFooter([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.Small("Total Change", className="text-muted d-block"),
                            html.H6(
                                f"{stats['change_pct']:+.1f}%",
                                className="mb-0 fw-bold",
                                style={'color': '#2ECC71' if stats['change_pct'] >= 0 else '#E74C3C'}
                            )
                        ], className="text-center")
                    ], width=3),
                    dbc.Col([
                        html.Div([
                            html.Small("Average Daily", className="text-muted d-block"),
                            html.H6(f"Rs. {stats['current_avg']/1e3:.1f}K", className="mb-0 fw-bold text-primary")
                        ], className="text-center")
                    ], width=3),
                    dbc.Col([
                        html.Div([
                            html.Small("Peak Day", className="text-muted d-block"),
                            html.H6(f"{stats['peak_date'].strftime('%d-%b')}", className="mb-0 fw-bold text-warning")
                        ], className="text-center")
                    ], width=3),
                    dbc.Col([
                        html.Div([
                            html.Small("Peak Revenue", className="text-muted d-block"),
                            html.H6(f"Rs. {stats['current_peak']/1e3:.1f}K", className="mb-0 fw-bold text-success")
                        ], className="text-center")
                    ], width=3),
                ])
            ], className="bg-light")
        ], className="shadow-sm")
        
        return card_content
        
    except Exception as e:
        print(f"Error in revenue comparison: {str(e)}")
        traceback.print_exc()
        return dbc.Alert(f"Error loading revenue comparison: {str(e)}", color="danger")

# Revenue Comparison Chart Update Callback (for interactive controls)
@app.callback(
    Output('revenue-comparison-graph', 'figure'),
    Input('period-daily-btn', 'n_clicks'),
    Input('period-weekly-btn', 'n_clicks'),
    Input('period-monthly-btn', 'n_clicks'),
    Input('comparison-type-selector', 'value'),
    State('username-input', 'value'),
    State('password-input', 'value'),
    State('date-range-picker', 'start_date'),
    State('date-range-picker', 'end_date'),
    State('hide-innovative-check', 'value'),
    prevent_initial_call=True
)
def update_comparison_chart(daily_clicks, weekly_clicks, monthly_clicks, comparison_type,
                            username, password, start_date, end_date, hide_innovative):
    """Update chart based on period and comparison selection"""
    
    # Determine which period was selected
    triggered = ctx.triggered_id
    if triggered == 'period-daily-btn':
        period_view = 'daily'
    elif triggered == 'period-weekly-btn':
        period_view = 'weekly'
    elif triggered == 'period-monthly-btn':
        period_view = 'monthly'
    else:
        period_view = 'daily'  # Default
    
    try:
        # Fetch data (same as above)
        start_date_obj = pd.to_datetime(start_date)
        end_date_obj = pd.to_datetime(end_date)
        start_date_str = start_date_obj.strftime("%d-%m-%Y")
        end_date_str = end_date_obj.strftime("%d-%m-%Y")
        
        api_client = APIClient(username=username, password=password)
        response = api_client.get_sales_report(start_date=start_date_str, end_date=end_date_str)
        
        if not response.get('success'):
            return go.Figure()
        
        api_response = response.get('data', {})
        report_data = api_response.get('report_data', [])
        
        if not report_data:
            return go.Figure()
        
        df = pd.DataFrame(report_data)
        
        # Map and clean data
        column_mapping = {
            'SV': 'Value', 'SQ': 'Qty', 'comp_nm': 'Dealer Name',
            'category_name': 'Category', 'state': 'State', 'city': 'City',
            'meta_keyword': 'Product Name', 'parent_category': 'Sub Category'
        }
        df = df.rename(columns={old: new for old, new in column_mapping.items() if old in df.columns})
        
        if 'Value' in df.columns:
            df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        
        if hide_innovative and 'Dealer Name' in df.columns:
            df = df[~df['Dealer Name'].str.contains('Innovative', case=False, na=False)]
        
        VALUE_COLS = [c for c in df.columns if c.startswith('Value') and c != 'Value']
        VALUE_COL = VALUE_COLS[0] if VALUE_COLS else ('Value' if 'Value' in df.columns else None)
        
        if not VALUE_COL:
            return go.Figure()
        
        # Create updated chart
        fig, _ = _create_revenue_comparison_chart(df, VALUE_COL, period_view, comparison_type)
        return fig
        
    except Exception as e:
        print(f"Error updating comparison chart: {str(e)}")
        return go.Figure()

# Custom Chart Builder Callback
@app.callback(
    Output('custom-chart-output', 'children'),
    Input('generate-custom-chart-btn', 'n_clicks'),
    State('custom-x-axis', 'value'),
    State('custom-y-axis', 'value'),
    State('custom-chart-type', 'value'),
    State('custom-agg-type', 'value'),
    State('custom-top-n', 'value'),
    State('custom-sort-desc', 'value'),
    State('date-range-picker', 'start_date'),
    State('date-range-picker', 'end_date'),
    State('hide-innovative-check', 'value'),
    State('username-input', 'value'),
    State('password-input', 'value'),
    prevent_initial_call=True
)
def generate_custom_chart(n_clicks, x_axis, y_axis, chart_type, agg_type, top_n, sort_desc, start_date, end_date, hide_innovative, username, password):
    if not n_clicks or not x_axis or not y_axis or not chart_type:
        return dbc.Alert("Please select X-axis, Y-axis, and Chart Type", color="warning")
    
    try:
        # Convert dates
        start_date_obj = pd.to_datetime(start_date)
        end_date_obj = pd.to_datetime(end_date)
        start_date_str = start_date_obj.strftime("%d-%m-%Y")
        end_date_str = end_date_obj.strftime("%d-%m-%Y")
        
        # Fetch data
        api_client = APIClient(username=username, password=password)
        response = api_client.get_sales_report(start_date=start_date_str, end_date=end_date_str)
        if not response.get('success'):
            return dbc.Alert(f"API Error: {response.get('message')}", color="danger")
        
        api_response = response.get('data', {})
        report_data = api_response.get('report_data', [])
        if not report_data:
            return dbc.Alert("No data available for this date range", color="warning")
        
        df = pd.DataFrame(report_data)
        
        # Map columns
        column_mapping = {
            'SV': 'Value', 'SQ': 'Qty', 'comp_nm': 'Dealer Name', 'category_name': 'Category',
            'state': 'State', 'city': 'City', 'meta_keyword': 'Product Name', 'parent_category': 'Sub Category'
        }
        df = df.rename(columns={old: new for old, new in column_mapping.items() if old in df.columns})
        
        # Convert numeric
        if 'Value' in df.columns:
            df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        if 'Qty' in df.columns:
            df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce')
        
        # Apply filter
        if hide_innovative and 'Dealer Name' in df.columns:
            df = df[~df['Dealer Name'].str.contains('Innovative', case=False, na=False)]
        
        # Detect columns
        VALUE_COLS = [c for c in df.columns if c.startswith('Value') and c != 'Value']
        QTY_COLS = [c for c in df.columns if c.startswith('Qty') and c != 'Qty']
        VALUE_COL = VALUE_COLS[0] if VALUE_COLS else ('Value' if 'Value' in df.columns else None)
        QTY_COL = QTY_COLS[0] if QTY_COLS else ('Qty' if 'Qty' in df.columns else None)
        
        # Determine aggregation column and function
        if y_axis == 'Sum of Revenue':
            agg_col = VALUE_COL
            agg_func = 'sum'
        elif y_axis == 'Sum of Quantity':
            agg_col = QTY_COL
            agg_func = 'sum'
        elif y_axis == 'Count of Orders':
            agg_col = None
            agg_func = 'count'
        elif y_axis == 'Average Revenue':
            agg_col = VALUE_COL
            agg_func = 'mean'
        elif y_axis == 'Average Quantity':
            agg_col = QTY_COL
            agg_func = 'mean'
        else:
            return dbc.Alert("Invalid Y-axis selection", color="danger")
        
        if agg_func == 'count':
            grouped = df.groupby(x_axis).size().reset_index(name='Count')
            sort_col = 'Count'
        else:
            grouped = df.groupby(x_axis)[agg_col].agg(agg_func).reset_index(name='Value')
            sort_col = 'Value'
        
        # Sort
        grouped = grouped.sort_values(sort_col, ascending=not sort_desc).head(top_n)
        
        # Generate chart
        title = f"{y_axis} by {x_axis} - Top {top_n} ({chart_type})"
        
        if chart_type == 'Bar Chart':
            fig = px.bar(grouped, x=x_axis, y=sort_col, title=title, color=sort_col, color_continuous_scale='Blues')
        elif chart_type == 'Horizontal Bar':
            fig = px.bar(grouped, x=sort_col, y=x_axis, orientation='h', title=title, color=sort_col, color_continuous_scale='Blues')
        elif chart_type == 'Pie Chart':
            fig = px.pie(grouped, values=sort_col, names=x_axis, title=title)
        elif chart_type == 'Line Chart':
            fig = px.line(grouped, x=x_axis, y=sort_col, title=title, markers=True)
        elif chart_type == 'Scatter Plot':
            fig = px.scatter(grouped, x=x_axis, y=sort_col, title=title, size=sort_col)
        elif chart_type == 'Sunburst':
            # For sunburst, if x_axis has hierarchy, but since single column, use simple
            fig = px.sunburst(grouped, path=[x_axis], values=sort_col, title=title)
        else:
            return dbc.Alert("Invalid chart type", color="danger")
        
        # Format axes
        if 'Value' in sort_col.lower() or 'revenue' in y_axis.lower():
            fig.update_yaxes(tickformat=".2f", tickprefix="Rs. ", ticksuffix="", 
                           tickvals=[1e5, 1e6, 1e7, 1e8, 1e9], ticktext=["0.1L", "1L", "10L", "1Cr", "10Cr"])
        
        fig.update_layout(height=500, font=dict(size=12, family="Arial, sans-serif"),
                         paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        
        return dbc.Card([
            dbc.CardHeader(title),
            dbc.CardBody([dcc.Graph(figure=fig, config={'displayModeBar': True})])
        ])
    
    except Exception as e:
        return dbc.Alert(f"Error generating chart: {str(e)}", color="danger")

# Clientside callback for deleting charts
app.clientside_callback(
    """
    function(deleteClicks, chartsData) {
        if (!deleteClicks || !deleteClicks.some(click => click)) return window.dash_clientside.no_update;
        
        try {
            // Find which button was clicked
            const ctx = window.dash_clientside.callback_context;
            if (!ctx || !ctx.triggered || ctx.triggered.length === 0) return window.dash_clientside.no_update;
            
            const triggered = ctx.triggered[0];
            const propId = triggered.prop_id;
            
            // Parse the chart ID from the prop_id
            const match = propId.match(/{"index":"([^"]+)","type":"delete-chart-btn"}/);
            if (!match) return window.dash_clientside.no_update;
            
            const chartId = match[1];
            
            // Load current charts
            let savedCharts = [];
            try {
                if (chartsData) {
                    savedCharts = JSON.parse(chartsData);
                }
            } catch (e) {
                console.error('Error parsing charts data:', e);
                savedCharts = [];
            }
            
            if (!Array.isArray(savedCharts)) {
                savedCharts = [];
            }
            
            // Remove the chart
            savedCharts = savedCharts.filter(chart => chart.unique_id !== chartId);
            
            // Save back to storage
            window.storage.set('my-saved-charts', JSON.stringify(savedCharts), false);
            
            // Return updated data
            return JSON.stringify(savedCharts);
            
        } catch (e) {
            console.error('Error deleting chart:', e);
            return window.dash_clientside.no_update;
        }
    }
    """,
    Output('saved-charts-data', 'children', allow_duplicate=True),
    Input({'type': 'delete-chart-btn', 'index': ALL}, 'n_clicks'),
    State('saved-charts-data', 'children'),
    prevent_initial_call=True
)

# Clientside callback for loading saved charts
app.clientside_callback(
    """
    function(trigger) {
        try {
            const chartsStr = window.storage.get('my-saved-charts', false);
            if (chartsStr) {
                const charts = JSON.parse(chartsStr);
                if (Array.isArray(charts)) {
                    return JSON.stringify(charts);
                }
            }
            return JSON.stringify([]);
        } catch (e) {
            console.error('Error loading saved charts:', e);
            return JSON.stringify([]);
        }
    }
    """,
    Output('saved-charts-data', 'children'),
    Input('username-input', 'value'),  # Trigger on any change
)

# Clientside callback for saving charts
app.clientside_callback(
    """
    function(n_clicks, chartName, xAxis, yAxis, chartType, aggType, topN, sortDesc) {
        if (!n_clicks || !chartName || !xAxis || !yAxis || !chartType) {
            return 'Please fill in chart name and all required fields';
        }
        
        try {
            // Create chart configuration object
            const chartConfig = {
                name: chartName,
                x_axis: xAxis,
                y_axis: yAxis,
                chart_type: chartType,
                agg_type: aggType || 'Sum',
                top_n: topN || 10,
                sort_desc: sortDesc !== false,
                timestamp: new Date().toISOString(),
                unique_id: 'chart_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
            };
            
            // Load existing charts from storage
            let savedCharts = [];
            try {
                const chartsStr = window.storage.get('my-saved-charts', false);
                if (chartsStr) {
                    savedCharts = JSON.parse(chartsStr);
                }
            } catch (parseError) {
                console.warn('Error parsing existing charts, starting fresh:', parseError);
                savedCharts = [];
            }
            
            if (!Array.isArray(savedCharts)) {
                savedCharts = [];
            }
            
            // Add new chart
            savedCharts.push(chartConfig);
            
            // Save back to storage
            window.storage.set('my-saved-charts', JSON.stringify(savedCharts), false);
            
            return 'Chart "' + chartName + '" saved successfully! Switch to "My Charts" tab to view it.';
            
        } catch (e) {
            console.error('Error saving chart:', e);
            return 'Error saving chart: ' + e.message;
        }
    }
    """,
    Output('save-chart-status', 'children'),
    Input('save-chart-btn', 'n_clicks'),
    State('chart-save-name', 'value'),
    State('custom-x-axis', 'value'),
    State('custom-y-axis', 'value'),
    State('custom-chart-type', 'value'),
    State('custom-agg-type', 'value'),
    State('custom-top-n', 'value'),
    State('custom-sort-desc', 'value'),
    prevent_initial_call=True
)

# My Charts Content Callback
@app.callback(
    Output('my-charts-content', 'children'),
    Input('username-input', 'value'),
    Input('password-input', 'value'),
    Input('date-range-picker', 'start_date'),
    Input('date-range-picker', 'end_date'),
    Input('hide-innovative-check', 'value'),
    Input('saved-charts-data', 'children'),  # Trigger when saved charts data changes
    prevent_initial_call=False
)
def update_my_charts(username, password, start_date, end_date, hide_innovative, charts_data):
    if not start_date or not end_date:
        return dbc.Alert("Please select date range", color="warning")
    
    try:
        # Check if we have saved charts
        if not charts_data:
            return html.Div([
                html.Div(className="text-center py-5", children=[
                    html.I(className="bi bi-graph-up", style={'fontSize': '64px', 'color': '#6c757d'}),
                    html.H4("No Saved Charts Yet", className="mt-3 text-muted"),
                    html.P("Create and save custom charts from the Dashboard tab to see them here!", className="text-muted"),
                    html.P("Saved charts will automatically update with the current date range.", className="text-muted small")
                ])
            ])
        
        saved_charts = json.loads(charts_data) if isinstance(charts_data, str) else charts_data
        
        if not saved_charts or len(saved_charts) == 0:
            return html.Div([
                html.Div(className="text-center py-5", children=[
                    html.I(className="bi bi-graph-up", style={'fontSize': '64px', 'color': '#6c757d'}),
                    html.H4("No Saved Charts Yet", className="mt-3 text-muted"),
                    html.P("Create and save custom charts from the Dashboard tab to see them here!", className="text-muted"),
                    html.P("Saved charts will automatically update with the current date range.", className="text-muted small")
                ])
            ])
        
        # Fetch current data
        start_date_obj = pd.to_datetime(start_date)
        end_date_obj = pd.to_datetime(end_date)
        start_date_str = start_date_obj.strftime("%d-%m-%Y")
        end_date_str = end_date_obj.strftime("%d-%m-%Y")
        
        api_client = APIClient(username=username, password=password)
        response = api_client.get_sales_report(start_date=start_date_str, end_date=end_date_str)
        
        if not response.get('success'):
            return dbc.Alert(f"API Error: {response.get('message')}", color="danger")
        
        api_response = response.get('data', {})
        report_data = api_response.get('report_data', [])
        
        if not report_data:
            return dbc.Alert("No data available for this date range", color="warning")
        
        df = pd.DataFrame(report_data)
        
        # Map columns
        column_mapping = {
            'SV': 'Value', 'SQ': 'Qty', 'comp_nm': 'Dealer Name', 'category_name': 'Category',
            'state': 'State', 'city': 'City', 'meta_keyword': 'Product Name', 'parent_category': 'Sub Category'
        }
        df = df.rename(columns={old: new for old, new in column_mapping.items() if old in df.columns})
        
        # Convert numeric
        if 'Value' in df.columns:
            df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        if 'Qty' in df.columns:
            df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce')
        
        # Apply filter
        if hide_innovative and 'Dealer Name' in df.columns:
            df = df[~df['Dealer Name'].str.contains('Innovative', case=False, na=False)]
        
        # Detect columns
        VALUE_COLS = [c for c in df.columns if c.startswith('Value') and c != 'Value']
        QTY_COLS = [c for c in df.columns if c.startswith('Qty') and c != 'Qty']
        VALUE_COL = VALUE_COLS[0] if VALUE_COLS else ('Value' if 'Value' in df.columns else None)
        QTY_COL = QTY_COLS[0] if QTY_COLS else ('Qty' if 'Qty' in df.columns else None)
        
        # Generate charts
        chart_cards = []
        
        for chart_config in saved_charts:
            try:
                # Extract config
                x_axis = chart_config.get('x_axis')
                y_axis = chart_config.get('y_axis')
                chart_type = chart_config.get('chart_type')
                agg_type = chart_config.get('agg_type', 'Sum')
                top_n = chart_config.get('top_n', 10)
                sort_desc = chart_config.get('sort_desc', True)
                chart_name = chart_config.get('name', 'Untitled Chart')
                timestamp = chart_config.get('timestamp')
                unique_id = chart_config.get('unique_id')
                
                if not x_axis or not y_axis or not chart_type:
                    continue
                
                # Check if required column exists
                if x_axis not in df.columns:
                    continue
                
                # Determine aggregation column and function
                if y_axis == 'Sum of Revenue':
                    agg_col = VALUE_COL
                    agg_func = 'sum'
                elif y_axis == 'Sum of Quantity':
                    agg_col = QTY_COL
                    agg_func = 'sum'
                elif y_axis == 'Count of Orders':
                    agg_col = None
                    agg_func = 'count'
                elif y_axis == 'Average Revenue':
                    agg_col = VALUE_COL
                    agg_func = 'mean'
                elif y_axis == 'Average Quantity':
                    agg_col = QTY_COL
                    agg_func = 'mean'
                else:
                    continue
                
                if agg_func == 'count':
                    grouped = df.groupby(x_axis).size().reset_index(name='Count')
                    sort_col = 'Count'
                else:
                    if not agg_col or agg_col not in df.columns:
                        continue
                    grouped = df.groupby(x_axis)[agg_col].agg(agg_func).reset_index(name='Value')
                    sort_col = 'Value'
                
                # Sort
                grouped = grouped.sort_values(sort_col, ascending=not sort_desc).head(top_n)
                
                # Generate chart
                title = f"{chart_name}"
                
                if chart_type == 'Bar Chart':
                    fig = px.bar(grouped, x=x_axis, y=sort_col, title=title, color=sort_col, color_continuous_scale='Blues')
                elif chart_type == 'Horizontal Bar':
                    fig = px.bar(grouped, x=sort_col, y=x_axis, orientation='h', title=title, color=sort_col, color_continuous_scale='Blues')
                elif chart_type == 'Pie Chart':
                    fig = px.pie(grouped, values=sort_col, names=x_axis, title=title)
                elif chart_type == 'Line Chart':
                    fig = px.line(grouped, x=x_axis, y=sort_col, title=title, markers=True)
                elif chart_type == 'Scatter Plot':
                    fig = px.scatter(grouped, x=x_axis, y=sort_col, title=title, size=sort_col)
                elif chart_type == 'Sunburst':
                    fig = px.sunburst(grouped, path=[x_axis], values=sort_col, title=title)
                else:
                    continue
                
                # Format axes
                if 'Value' in sort_col or 'revenue' in y_axis.lower():
                    fig.update_yaxes(tickformat=".2f", tickprefix="Rs. ", ticksuffix="", 
                                   tickvals=[1e5, 1e6, 1e7, 1e8, 1e9], ticktext=["0.1L", "1L", "10L", "1Cr", "10Cr"])
                
                fig.update_layout(height=400, font=dict(size=12, family="Arial, sans-serif"),
                                 paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                 margin=dict(t=40, b=10, l=10, r=10))
                
                # Format timestamp
                try:
                    timestamp_obj = datetime.fromisoformat(timestamp)
                    formatted_timestamp = timestamp_obj.strftime("%d-%m-%Y %H:%M")
                except (ValueError, TypeError, AttributeError):
                    formatted_timestamp = "Unknown date"
                
                # Create card
                card = dbc.Card([
                    dbc.CardHeader([
                        html.Div([
                            html.H6(chart_name, className="mb-0 fw-bold"),
                            html.Small(f"Saved on {formatted_timestamp}", className="text-muted")
                        ], style={'flex': '1'}),
                    ], className="d-flex justify-content-between align-items-center"),
                    dbc.CardBody([
                        dcc.Graph(figure=fig, config={'displayModeBar': True}),
                        dbc.Button(
                            "Delete",
                            id={'type': 'delete-chart-btn', 'index': unique_id},
                            color='danger',
                            size='sm',
                            className="mt-2"
                        )
                    ])
                ], className="mb-3")
                
                chart_cards.append(card)
                
            except Exception as e:
                print(f"Error generating saved chart {chart_config.get('name', 'Unknown')}: {str(e)}")
                traceback.print_exc()
                continue
        
        if not chart_cards:
            return dbc.Alert("No charts could be generated with current data", color="warning")
        
        # Return header and grid of cards
        return html.Div([
            html.Div([
                html.H4(f"My Saved Charts ({len(chart_cards)})", className="mb-3"),
                html.P(f"Showing data from {start_date_str} to {end_date_str}", className="text-muted small mb-4")
            ]),
            dbc.Row([
                dbc.Col(card, width=6) for card in chart_cards
            ], className="g-3")
        ])
        
    except Exception as e:
        print(f"Error in update_my_charts: {str(e)}")
        traceback.print_exc()
        return dbc.Alert(f"Error loading My Charts: {str(e)}", color="danger")

# Slow-Moving Items Tracker Callback
@app.callback(
    Output('slow-moving-items-content', 'children'),
    Output('slow-moving-category-filter', 'options'),
    Output('slow-moving-dealer-filter', 'options'),
    Input('slow-moving-days-filter', 'value'),
    Input('slow-moving-category-filter', 'value'),
    Input('slow-moving-dealer-filter', 'value'),
    Input('slow-moving-sort-by', 'value'),
    Input('slow-moving-top-n', 'value'),
    Input('slow-moving-min-revenue', 'value'),
    Input('username-input', 'value'),
    Input('password-input', 'value'),
    Input('date-range-picker', 'start_date'),
    Input('date-range-picker', 'end_date'),
    Input('hide-innovative-check', 'value'),
    prevent_initial_call=False
)
def update_slow_moving_items(days_filter, category_filter, dealer_filter, sort_by, top_n, 
                            min_revenue, username, password, start_date, end_date, hide_innovative):
    """Analyze slow-moving items based on sales velocity with enhanced filters"""
    
    if not start_date or not end_date:
        return dbc.Alert("Please select date range", color="warning"), [], []
    
    try:
        # Convert dates
        start_date_obj = pd.to_datetime(start_date)
        end_date_obj = pd.to_datetime(end_date)
        start_date_str = start_date_obj.strftime("%d-%m-%Y")
        end_date_str = end_date_obj.strftime("%d-%m-%Y")
        
        # Fetch data from API
        api_client = APIClient(username=username, password=password)
        response = api_client.get_sales_report(
            start_date=start_date_str,
            end_date=end_date_str
        )
        
        if not response.get('success'):
            return dbc.Alert(f"API Error: {response.get('message')}", color="danger"), [], []
        
        api_response = response.get('data', {})
        report_data = api_response.get('report_data', [])
        
        if not report_data:
            return dbc.Alert("No data available for this date range", color="warning"), [], []
        
        df = pd.DataFrame(report_data)
        
        # Map columns
        column_mapping = {
            'SV': 'Value', 'SQ': 'Qty', 'comp_nm': 'Dealer Name',
            'category_name': 'Category', 'state': 'State', 'city': 'City',
            'meta_keyword': 'Product Name', 'parent_category': 'Sub Category',
            'date': 'Date', 'order_date': 'Date', 'created_at': 'Date', 'sale_date': 'Date'
        }
        df = df.rename(columns={old: new for old, new in column_mapping.items() if old in df.columns})
        
        # Convert numeric columns
        if 'Value' in df.columns:
            df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        if 'Qty' in df.columns:
            df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce')
        
        # Apply filter
        if hide_innovative and 'Dealer Name' in df.columns:
            df = df[~df['Dealer Name'].str.contains('Innovative', case=False, na=False)]
        
        # Get filter options
        category_options = []
        dealer_options = []
        if 'Category' in df.columns:
            category_options = [{'label': cat, 'value': cat} for cat in sorted(df['Category'].dropna().unique())]
        if 'Dealer Name' in df.columns:
            dealer_options = [{'label': dealer, 'value': dealer} for dealer in sorted(df['Dealer Name'].dropna().unique())]
        
        # Check for required columns
        if 'Date' not in df.columns or 'Product Name' not in df.columns:
            return dbc.Alert("Date or Product Name data not available", color="warning"), category_options, dealer_options
        
        # Convert Date column
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])
        
        if df.empty:
            return dbc.Alert("No valid date data available", color="warning"), category_options, dealer_options
        
        VALUE_COL = 'Value' if 'Value' in df.columns else None
        QTY_COL = 'Qty' if 'Qty' in df.columns else None
        
        if not VALUE_COL or not QTY_COL:
            return dbc.Alert("Revenue or Quantity data not available", color="warning"), category_options, dealer_options
        
        # Apply category filter
        if category_filter and 'Category' in df.columns:
            df = df[df['Category'].isin(category_filter)]
        
        # Apply dealer filter
        if dealer_filter and 'Dealer Name' in df.columns:
            df = df[df['Dealer Name'].isin(dealer_filter)]
        
        # Calculate date range
        date_range_days = (end_date_obj - start_date_obj).days + 1
        
        # Group by product with additional fields
        agg_dict = {
            VALUE_COL: 'sum',
            QTY_COL: 'sum',
            'Date': ['min', 'max', 'count']
        }
        
        # Add category and dealer if available
        if 'Category' in df.columns:
            agg_dict['Category'] = 'first'
        if 'Dealer Name' in df.columns:
            agg_dict['Dealer Name'] = lambda x: ', '.join(x.unique()[:3])  # Top 3 dealers
        
        product_analysis = df.groupby('Product Name').agg(agg_dict).reset_index()
        
        # Flatten column names
        product_analysis.columns = ['Product Name', 'Total Revenue', 'Total Quantity', 'First Sale', 'Last Sale', 'Order Count'] + \
                                   (['Category'] if 'Category' in df.columns else []) + \
                                   (['Dealers'] if 'Dealer Name' in df.columns else [])
        
        # Calculate days since last sale
        product_analysis['Days Since Last Sale'] = (end_date_obj - product_analysis['Last Sale']).dt.days
        
        # Calculate sales velocity (quantity per day)
        product_analysis['Sales Velocity'] = product_analysis['Total Quantity'] / date_range_days
        
        # Calculate average order value
        product_analysis['Avg Order Value'] = product_analysis['Total Revenue'] / product_analysis['Order Count']
        
        # Filter slow-moving items (based on days filter)
        slow_moving = product_analysis[product_analysis['Days Since Last Sale'] >= days_filter].copy()
        
        # Apply minimum revenue filter
        if min_revenue:
            try:
                slow_moving = slow_moving[slow_moving['Total Revenue'] >= float(min_revenue)]
            except:
                pass
        
        # Sort based on selected criteria
        sort_column_map = {
            'days': 'Days Since Last Sale',
            'revenue': 'Total Revenue',
            'quantity': 'Total Quantity',
            'velocity': 'Sales Velocity'
        }
        sort_column = sort_column_map.get(sort_by, 'Days Since Last Sale')
        ascending = False if sort_by in ['revenue', 'quantity', 'velocity'] else False
        slow_moving = slow_moving.sort_values(sort_column, ascending=ascending)
        
        # Limit to top N
        top_n = top_n or 20
        slow_moving_display = slow_moving.head(top_n)
        
        if slow_moving.empty:
            return dbc.Alert(
                f"✅ Great! No products found with no sales in the last {days_filter} days",
                color="success"
            ), category_options, dealer_options
        
        # Create visualizations
        # 1. Summary cards
        summary_cards = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.I(className="bi bi-box-seam", style={'fontSize': '24px', 'color': '#ef4444'}),
                        html.H3(f"{len(slow_moving)}", className="text-danger mb-0 mt-2"),
                        html.P("Slow-Moving Products", className="text-muted small mb-0")
                    ])
                ], className="text-center shadow-sm")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.I(className="bi bi-calendar-x", style={'fontSize': '24px', 'color': '#f59e0b'}),
                        html.H3(f"{slow_moving['Days Since Last Sale'].mean():.0f}", className="text-warning mb-0 mt-2"),
                        html.P("Avg Days Since Sale", className="text-muted small mb-0")
                    ])
                ], className="text-center shadow-sm")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.I(className="bi bi-currency-rupee", style={'fontSize': '24px', 'color': '#3b82f6'}),
                        html.H3(format_inr(slow_moving['Total Revenue'].sum()), className="text-info mb-0 mt-2"),
                        html.P("Total Revenue Impact", className="text-muted small mb-0")
                    ])
                ], className="text-center shadow-sm")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.I(className="bi bi-graph-down", style={'fontSize': '24px', 'color': '#6366f1'}),
                        html.H3(f"{slow_moving['Total Quantity'].sum():,.0f}", className="text-secondary mb-0 mt-2"),
                        html.P("Total Units", className="text-muted small mb-0")
                    ])
                ], className="text-center shadow-sm")
            ], width=3),
        ], className="mb-4 g-2")
        
        # 2. Chart showing days since last sale (or other metric based on sort)
        fig_bar = go.Figure()
        
        # Determine what to display based on sort_by
        if sort_by == 'revenue':
            y_values = slow_moving_display['Total Revenue']
            y_label = "Revenue (₹)"
            color_values = slow_moving_display['Total Revenue']
            text_format = lambda x: format_inr(x)
        elif sort_by == 'quantity':
            y_values = slow_moving_display['Total Quantity']
            y_label = "Quantity"
            color_values = slow_moving_display['Total Quantity']
            text_format = lambda x: f"{x:,.0f}"
        elif sort_by == 'velocity':
            y_values = slow_moving_display['Sales Velocity']
            y_label = "Sales Velocity (units/day)"
            color_values = slow_moving_display['Sales Velocity']
            text_format = lambda x: f"{x:.2f}/day"
        else:
            y_values = slow_moving_display['Days Since Last Sale']
            y_label = "Days Since Last Sale"
            color_values = slow_moving_display['Days Since Last Sale']
            text_format = lambda x: f"{x:.0f} days"
        
        fig_bar.add_trace(go.Bar(
            x=y_values,
            y=slow_moving_display['Product Name'],
            orientation='h',
            marker=dict(
                color=color_values,
                colorscale=[[0, '#10b981'], [0.5, '#f59e0b'], [1, '#ef4444']],
                showscale=True,
                colorbar=dict(title=y_label, thickness=15)
            ),
            text=[text_format(v) for v in y_values],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>' + y_label + ': %{x}<br><extra></extra>'
        ))
        
        chart_title = f"Top {top_n} Slow-Moving Products (No Sales in Last {days_filter}+ Days)"
        if sort_by != 'days':
            chart_title = f"Top {top_n} Slow-Moving Products by {y_label}"
        
        apply_modern_chart_style(fig_bar, chart_title, height=max(400, top_n * 20))
        fig_bar.update_xaxes(title=y_label)
        fig_bar.update_yaxes(title="", tickfont=dict(size=9))
        fig_bar.update_layout(margin=dict(l=250, r=40, t=60, b=40))
        
        # 3. Additional pie chart - Category distribution of slow-moving items
        fig_pie = None
        if 'Category' in slow_moving.columns:
            category_dist = slow_moving.groupby('Category')['Total Revenue'].sum().reset_index()
            category_dist = category_dist.sort_values('Total Revenue', ascending=False)
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=category_dist['Category'],
                values=category_dist['Total Revenue'],
                hole=0.4,
                marker=dict(colors=px.colors.qualitative.Set3),
                textinfo='label+percent',
                hovertemplate='<b>%{label}</b><br>Revenue: ₹%{value:,.0f}<br>%{percent}<extra></extra>'
            )])
            
            apply_modern_chart_style(fig_pie, "Slow-Moving Items by Category", height=400)
        
        # 4. Data table
        table_data = slow_moving_display.copy()
        table_data['Total Revenue'] = table_data['Total Revenue'].apply(lambda x: f"₹ {x:,.0f}")
        table_data['Total Quantity'] = table_data['Total Quantity'].apply(lambda x: f"{x:,.0f}")
        table_data['Sales Velocity'] = table_data['Sales Velocity'].apply(lambda x: f"{x:.2f}/day")
        table_data['Avg Order Value'] = table_data['Avg Order Value'].apply(lambda x: f"₹ {x:,.0f}")
        table_data['First Sale'] = table_data['First Sale'].dt.strftime('%d-%b-%Y')
        table_data['Last Sale'] = table_data['Last Sale'].dt.strftime('%d-%b-%Y')
        
        # Select columns for display
        display_columns = ['Product Name', 'Days Since Last Sale', 'Last Sale', 'Total Revenue', 
                         'Total Quantity', 'Order Count', 'Sales Velocity']
        if 'Category' in table_data.columns:
            display_columns.insert(1, 'Category')
        
        table = dbc.Table.from_dataframe(
            table_data[display_columns],
            striped=True,
            bordered=True,
            hover=True,
            size='sm',
            style={'fontSize': '11px'}
        )
        
        # Return layout
        content = html.Div([
            summary_cards,
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=fig_bar, config={'displayModeBar': True})
                        ])
                    ], className="shadow-sm")
                ], width=8 if fig_pie else 12),
                
                # Category pie chart
                *([] if not fig_pie else [dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=fig_pie, config={'displayModeBar': True})
                        ])
                    ], className="shadow-sm")
                ], width=4)])
            ], className="mb-3 g-2"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H6(f"Detailed Slow-Moving Items Report (Showing {len(slow_moving_display)} of {len(slow_moving)})", className="mb-0")
                        ]),
                        dbc.CardBody([
                            html.Div(table, style={'maxHeight': '500px', 'overflowY': 'auto'})
                        ])
                    ], className="shadow-sm")
                ], width=12)
            ])
        ])
        
        return content, category_options, dealer_options
        
    except Exception as e:
        print(f"Error in slow-moving items: {str(e)}")
        import traceback
        traceback.print_exc()
        return dbc.Alert(f"Error analyzing slow-moving items: {str(e)}", color="danger"), [], []

# Reset Slow-Moving Items Filters Callback
@app.callback(
    Output('slow-moving-category-filter', 'value'),
    Output('slow-moving-dealer-filter', 'value'),
    Output('slow-moving-sort-by', 'value'),
    Output('slow-moving-top-n', 'value'),
    Output('slow-moving-min-revenue', 'value'),
    Output('slow-moving-days-filter', 'value'),
    Input('slow-moving-reset-btn', 'n_clicks'),
    prevent_initial_call=True
)
def reset_slow_moving_filters(n_clicks):
    """Reset all slow-moving items filters to default values"""
    if n_clicks:
        return None, None, 'days', 20, None, 30
    return no_update, no_update, no_update, no_update, no_update, no_update

# Download Slow-Moving Items Report Callback
@app.callback(
    Output('slow-moving-download', 'data'),
    Input('slow-moving-download-btn', 'n_clicks'),
    State('chart-data-store', 'data'),
    State('slow-moving-days-filter', 'value'),
    State('date-range-picker', 'start_date'),
    State('date-range-picker', 'end_date'),
    prevent_initial_call=True
)
def download_slow_moving_report(n_clicks, chart_data, days_filter, start_date, end_date):
    """Download slow-moving items report as CSV"""
    if not n_clicks or not chart_data:
        return no_update
    
    try:
        df = pd.DataFrame(chart_data['data'])
        VALUE_COL = chart_data.get('VALUE_COL')
        QTY_COL = chart_data.get('QTY_COL')
        
        if df.empty or not VALUE_COL or not QTY_COL:
            return no_update
        
        # Convert Date column
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df = df.dropna(subset=['Date'])
        
        if df.empty:
            return no_update
        
        start_date_obj = pd.to_datetime(start_date)
        end_date_obj = pd.to_datetime(end_date)
        date_range_days = (end_date_obj - start_date_obj).days + 1
        
        # Group by product
        product_analysis = df.groupby('Product Name').agg({
            VALUE_COL: 'sum',
            QTY_COL: 'sum',
            'Date': ['min', 'max', 'count']
        }).reset_index()
        
        product_analysis.columns = ['Product Name', 'Total Revenue', 'Total Quantity', 'First Sale', 'Last Sale', 'Order Count']
        product_analysis['Days Since Last Sale'] = (end_date_obj - product_analysis['Last Sale']).dt.days
        product_analysis['Sales Velocity'] = product_analysis['Total Quantity'] / date_range_days
        product_analysis['Avg Order Value'] = product_analysis['Total Revenue'] / product_analysis['Order Count']
        
        # Filter slow-moving items
        slow_moving = product_analysis[product_analysis['Days Since Last Sale'] >= days_filter].copy()
        slow_moving = slow_moving.sort_values('Days Since Last Sale', ascending=False)
        
        # Format dates
        slow_moving['First Sale'] = slow_moving['First Sale'].dt.strftime('%d-%b-%Y')
        slow_moving['Last Sale'] = slow_moving['Last Sale'].dt.strftime('%d-%b-%Y')
        
        # Generate filename
        filename = f"slow_moving_items_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return dcc.send_data_frame(slow_moving.to_csv, filename, index=False)
        
    except Exception as e:
        print(f"Error downloading report: {str(e)}")
        return no_update

# Cross-Selling Analysis Callback
@app.callback(
    Output('cross-sell-content', 'children'),
    Output('cross-sell-category-filter', 'options'),
    Output('cross-sell-dealer-filter', 'options'),
    Input('cross-sell-analysis-type', 'value'),
    Input('cross-sell-category-filter', 'value'),
    Input('cross-sell-dealer-filter', 'value'),
    Input('cross-sell-min-support', 'value'),
    Input('cross-sell-min-confidence', 'value'),
    Input('cross-sell-top-n', 'value'),
    Input('username-input', 'value'),
    Input('password-input', 'value'),
    Input('date-range-picker', 'start_date'),
    Input('date-range-picker', 'end_date'),
    Input('hide-innovative-check', 'value'),
    prevent_initial_call=False
)
def update_cross_selling_analysis(analysis_type, category_filter, dealer_filter, min_support, 
                                  min_confidence, top_n, username, password, start_date, end_date, hide_innovative):
    """Analyze cross-selling patterns and product associations"""
    
    if not start_date or not end_date:
        return dbc.Alert("Please select date range", color="warning"), [], []
    
    try:
        # Convert dates
        start_date_obj = pd.to_datetime(start_date)
        end_date_obj = pd.to_datetime(end_date)
        start_date_str = start_date_obj.strftime("%d-%m-%Y")
        end_date_str = end_date_obj.strftime("%d-%m-%Y")
        
        # Fetch data from API
        api_client = APIClient(username=username, password=password)
        response = api_client.get_sales_report(
            start_date=start_date_str,
            end_date=end_date_str
        )
        
        if not response.get('success'):
            return dbc.Alert(f"API Error: {response.get('message')}", color="danger"), [], []
        
        api_response = response.get('data', {})
        report_data = api_response.get('report_data', [])
        
        if not report_data:
            return dbc.Alert("No data available for this date range", color="warning"), [], []
        
        df = pd.DataFrame(report_data)
        
        # Map columns
        column_mapping = {
            'SV': 'Value', 'SQ': 'Qty', 'comp_nm': 'Dealer Name',
            'category_name': 'Category', 'state': 'State', 'city': 'City',
            'meta_keyword': 'Product Name', 'parent_category': 'Sub Category',
            'cust_id': 'Customer ID', 'id': 'Order ID',
            'date': 'Date', 'order_date': 'Date', 'created_at': 'Date', 'sale_date': 'Date'
        }
        df = df.rename(columns={old: new for old, new in column_mapping.items() if old in df.columns})
        
        # Convert numeric columns
        if 'Value' in df.columns:
            df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        if 'Qty' in df.columns:
            df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce')
        
        # Apply filter
        if hide_innovative and 'Dealer Name' in df.columns:
            df = df[~df['Dealer Name'].str.contains('Innovative', case=False, na=False)]
        
        # Prepare filter options
        category_options = []
        dealer_options = []
        
        if 'Category' in df.columns:
            categories = sorted(df['Category'].dropna().unique().tolist())
            category_options = [{'label': cat, 'value': cat} for cat in categories]
        
        if 'Dealer Name' in df.columns:
            dealers = sorted(df['Dealer Name'].dropna().unique().tolist())
            dealer_options = [{'label': dealer, 'value': dealer} for dealer in dealers]
        
        # Apply filters
        filtered_df = df.copy()
        if category_filter and len(category_filter) > 0 and 'Category' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Category'].isin(category_filter)]
        
        if dealer_filter and len(dealer_filter) > 0 and 'Dealer Name' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Dealer Name'].isin(dealer_filter)]
        
        # Check required columns
        if 'Product Name' not in filtered_df.columns or 'Order ID' not in filtered_df.columns:
            return dbc.Alert("Required columns (Product Name, Order ID) not found in data", color="warning"), category_options, dealer_options
        
        if len(filtered_df) == 0:
            return dbc.Alert("No data available with current filters", color="warning"), category_options, dealer_options
        
        # Group by order/customer to find associations
        if analysis_type == 'product':
            group_col = 'Product Name'
            entity_col = 'Order ID'
        elif analysis_type == 'category':
            group_col = 'Category'
            entity_col = 'Order ID'
        else:  # dealer
            group_col = 'Product Name'
            entity_col = 'Dealer Name'
        
        # Create transaction lists (items bought together)
        transactions = filtered_df.groupby(entity_col)[group_col].apply(list).tolist()
        
        # Calculate item frequencies
        from collections import Counter
        item_counts = Counter()
        for transaction in transactions:
            for item in set(transaction):  # Use set to count each item once per transaction
                item_counts[item] += 1
        
        total_transactions = len(transactions)
        
        # Find associations (items that appear together)
        associations = []
        
        for transaction in transactions:
            unique_items = list(set(transaction))
            # Generate pairs
            for i in range(len(unique_items)):
                for j in range(i + 1, len(unique_items)):
                    item1, item2 = unique_items[i], unique_items[j]
                    associations.append((item1, item2))
        
        # Count pair frequencies
        pair_counts = Counter(associations)
        
        # Calculate support and confidence
        association_rules = []
        
        min_support_count = (min_support / 100) * total_transactions
        
        for (item1, item2), count in pair_counts.items():
            support = (count / total_transactions) * 100
            
            if support >= min_support:
                # Confidence: P(item2 | item1)
                confidence1 = (count / item_counts[item1]) * 100
                # Confidence: P(item1 | item2)
                confidence2 = (count / item_counts[item2]) * 100
                
                # Get revenue data for these items
                item1_revenue = filtered_df[filtered_df[group_col] == item1]['Value'].sum()
                item2_revenue = filtered_df[filtered_df[group_col] == item2]['Value'].sum()
                
                if confidence1 >= min_confidence:
                    association_rules.append({
                        'Item A': item1,
                        'Item B': item2,
                        'Support (%)': round(support, 2),
                        'Confidence (%)': round(confidence1, 2),
                        'Frequency': count,
                        'Item A Revenue': item1_revenue,
                        'Item B Revenue': item2_revenue,
                        'Direction': 'A→B'
                    })
                
                if confidence2 >= min_confidence:
                    association_rules.append({
                        'Item A': item2,
                        'Item B': item1,
                        'Support (%)': round(support, 2),
                        'Confidence (%)': round(confidence2, 2),
                        'Frequency': count,
                        'Item A Revenue': item2_revenue,
                        'Item B Revenue': item1_revenue,
                        'Direction': 'B→A'
                    })
        
        if len(association_rules) == 0:
            return html.Div([
                dbc.Alert([
                    html.H5("No Associations Found", className="mb-2"),
                    html.P("Try adjusting the minimum support or confidence thresholds to discover more patterns.")
                ], color="info")
            ]), category_options, dealer_options
        
        # Convert to DataFrame and sort
        assoc_df = pd.DataFrame(association_rules)
        assoc_df = assoc_df.sort_values('Confidence (%)', ascending=False).head(top_n)
        
        # Create visualizations
        # 1. Summary Cards
        total_associations = len(assoc_df)
        avg_confidence = assoc_df['Confidence (%)'].mean()
        avg_support = assoc_df['Support (%)'].mean()
        most_common_item = assoc_df['Item A'].mode()[0] if len(assoc_df) > 0 else "N/A"
        
        summary_cards = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="bi bi-diagram-3", style={'fontSize': '32px', 'color': COLORS['primary']}),
                            html.H3(f"{total_associations}", className="mt-2 mb-0"),
                            html.P("Associations Found", className="text-muted mb-0 small")
                        ], className="text-center")
                    ])
                ], className="shadow-sm h-100")
            ], width=3),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="bi bi-graph-up-arrow", style={'fontSize': '32px', 'color': COLORS['success']}),
                            html.H3(f"{avg_confidence:.1f}%", className="mt-2 mb-0"),
                            html.P("Avg Confidence", className="text-muted mb-0 small")
                        ], className="text-center")
                    ])
                ], className="shadow-sm h-100")
            ], width=3),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="bi bi-bar-chart", style={'fontSize': '32px', 'color': COLORS['info']}),
                            html.H3(f"{avg_support:.1f}%", className="mt-2 mb-0"),
                            html.P("Avg Support", className="text-muted mb-0 small")
                        ], className="text-center")
                    ])
                ], className="shadow-sm h-100")
            ], width=3),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="bi bi-star-fill", style={'fontSize': '32px', 'color': COLORS['warning']}),
                            html.H6(most_common_item[:20], className="mt-2 mb-0", style={'fontSize': '16px'}),
                            html.P("Top Item", className="text-muted mb-0 small")
                        ], className="text-center")
                    ])
                ], className="shadow-sm h-100")
            ], width=3),
        ], className="g-2 mb-4")
        
        # 2. Network/Chord Diagram - Using Sankey as relation chart
        import plotly.graph_objects as go
        
        # Prepare data for Sankey diagram
        unique_items = list(set(assoc_df['Item A'].tolist() + assoc_df['Item B'].tolist()))
        item_to_idx = {item: idx for idx, item in enumerate(unique_items)}
        
        source_indices = [item_to_idx[item] for item in assoc_df['Item A'].tolist()]
        target_indices = [item_to_idx[item] for item in assoc_df['Item B'].tolist()]
        values = assoc_df['Confidence (%)'].tolist()
        
        # Create color scheme for links based on confidence
        link_colors = []
        for conf in assoc_df['Confidence (%)']:
            if conf >= 50:
                link_colors.append('rgba(46, 204, 113, 0.4)')  # Green for high confidence
            elif conf >= 30:
                link_colors.append('rgba(52, 152, 219, 0.4)')  # Blue for medium
            else:
                link_colors.append('rgba(241, 196, 15, 0.4)')  # Yellow for low
        
        sankey_fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="white", width=0.5),
                label=[item[:30] + "..." if len(item) > 30 else item for item in unique_items],
                color=COLORS['primary']
            ),
            link=dict(
                source=source_indices,
                target=target_indices,
                value=values,
                color=link_colors,
                customdata=assoc_df[['Item A', 'Item B', 'Confidence (%)', 'Support (%)']].values,
                hovertemplate='%{customdata[0]} → %{customdata[1]}<br>Confidence: %{customdata[2]:.1f}%<br>Support: %{customdata[3]:.1f}%<extra></extra>'
            )
        )])
        
        sankey_fig.update_layout(
            title=f"Product Association Network ({analysis_type.title()} Level)",
            font=dict(size=12),
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        # 3. Bar chart - Top associations by confidence
        bar_fig = px.bar(
            assoc_df.head(15),
            x='Confidence (%)',
            y=assoc_df.head(15).apply(lambda row: f"{row['Item A'][:20]} → {row['Item B'][:20]}", axis=1),
            color='Support (%)',
            color_continuous_scale='Viridis',
            orientation='h',
            title=f"Top {min(15, len(assoc_df))} Product Associations by Confidence",
            labels={'y': 'Association', 'Confidence (%)': 'Confidence'},
            height=400
        )
        bar_fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        # 4. Scatter plot - Support vs Confidence
        scatter_fig = px.scatter(
            assoc_df,
            x='Support (%)',
            y='Confidence (%)',
            size='Frequency',
            color='Frequency',
            hover_data=['Item A', 'Item B'],
            title="Association Rules: Support vs Confidence",
            color_continuous_scale='Sunset',
            height=400
        )
        scatter_fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        # 5. Data Table
        table_data = assoc_df.to_dict('records')
        
        table = html.Div([
            dag.AgGrid(
                rowData=table_data,
                columnDefs=[
                    {'headerName': 'Item A', 'field': 'Item A', 'filter': True, 'sortable': True, 'width': 200},
                    {'headerName': 'Item B', 'field': 'Item B', 'filter': True, 'sortable': True, 'width': 200},
                    {'headerName': 'Confidence (%)', 'field': 'Confidence (%)', 'filter': True, 'sortable': True, 'width': 130},
                    {'headerName': 'Support (%)', 'field': 'Support (%)', 'filter': True, 'sortable': True, 'width': 120},
                    {'headerName': 'Frequency', 'field': 'Frequency', 'filter': True, 'sortable': True, 'width': 110},
                    {'headerName': 'Item A Revenue', 'field': 'Item A Revenue', 'filter': True, 'sortable': True, 'width': 150,
                     'valueFormatter': {'function': "d3.format('₹,.0f')(params.value)"}},
                    {'headerName': 'Item B Revenue', 'field': 'Item B Revenue', 'filter': True, 'sortable': True, 'width': 150,
                     'valueFormatter': {'function': "d3.format('₹,.0f')(params.value)"}},
                ],
                defaultColDef={'resizable': True, 'sortable': True, 'filter': True},
                dashGridOptions={'pagination': True, 'paginationPageSize': 10},
                className="ag-theme-alpine",
                style={'height': '400px'}
            )
        ])
        
        # Build content
        content = html.Div([
            summary_cards,
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=sankey_fig, config={'displayModeBar': True})
                        ])
                    ], className="shadow-sm")
                ], width=12)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=bar_fig, config={'displayModeBar': True})
                        ])
                    ], className="shadow-sm")
                ], width=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=scatter_fig, config={'displayModeBar': True})
                        ])
                    ], className="shadow-sm")
                ], width=6),
            ], className="g-2 mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H6(f"Detailed Association Rules (Showing {len(assoc_df)} rules)", className="mb-0")
                        ]),
                        dbc.CardBody([
                            table
                        ])
                    ], className="shadow-sm")
                ], width=12)
            ])
        ])
        
        return content, category_options, dealer_options
        
    except Exception as e:
        print(f"Error in cross-selling analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return dbc.Alert(f"Error analyzing cross-selling patterns: {str(e)}", color="danger"), [], []

# Reset Cross-Selling Filters Callback
@app.callback(
    Output('cross-sell-category-filter', 'value'),
    Output('cross-sell-dealer-filter', 'value'),
    Output('cross-sell-analysis-type', 'value'),
    Output('cross-sell-min-support', 'value'),
    Output('cross-sell-min-confidence', 'value'),
    Output('cross-sell-top-n', 'value'),
    Input('cross-sell-reset-btn', 'n_clicks'),
    prevent_initial_call=True
)
def reset_cross_sell_filters(n_clicks):
    """Reset all cross-selling filters to default values"""
    if n_clicks:
        return None, None, 'product', 5, 10, 10
    return no_update, no_update, no_update, no_update, no_update, no_update

# Download Cross-Selling Report Callback
@app.callback(
    Output('cross-sell-download', 'data'),
    Input('cross-sell-download-btn', 'n_clicks'),
    State('chart-data-store', 'data'),
    State('cross-sell-analysis-type', 'value'),
    State('date-range-picker', 'start_date'),
    State('date-range-picker', 'end_date'),
    prevent_initial_call=True
)
def download_cross_sell_report(n_clicks, chart_data, analysis_type, start_date, end_date):
    """Download cross-selling analysis report as CSV"""
    
    if not n_clicks or not chart_data:
        return no_update
    
    try:
        # This would contain the actual association rules data
        # For now, return a simple message
        import io
        
        output = io.StringIO()
        output.write(f"Cross-Selling Analysis Report\n")
        output.write(f"Date Range: {start_date} to {end_date}\n")
        output.write(f"Analysis Type: {analysis_type}\n")
        output.write(f"\nNote: Detailed association rules will be included in future versions.\n")
        
        return dict(content=output.getvalue(), filename=f"cross_sell_analysis_{start_date}_{end_date}.csv")
    
    except Exception as e:
        print(f"Error downloading cross-sell report: {str(e)}")
        return no_update

# Sales CRM Callback
@app.callback(
    Output('crm-table-container', 'children'),
    Output('crm-dealer-filter', 'options'),
    Output('crm-state-filter', 'options'),
    Output('crm-product-family-filter', 'options'),
    Input('crm-dealer-filter', 'value'),
    Input('crm-state-filter', 'value'),
    Input('crm-product-family-filter', 'value'),
    Input('crm-payment-status-filter', 'value'),
    Input('crm-search-input', 'value'),
    Input('username-input', 'value'),
    Input('password-input', 'value'),
    Input('date-range-picker', 'start_date'),
    Input('date-range-picker', 'end_date'),
    Input('hide-innovative-check', 'value'),
    prevent_initial_call=False
)
def update_crm_table(dealer_filter, state_filter, product_family_filter, payment_status_filter, 
                     search_input, username, password, start_date, end_date, hide_innovative):
    """Update the Sales CRM table with filtered data"""
    
    if not start_date or not end_date:
        return dbc.Alert("Please select date range", color="warning"), [], [], []
    
    try:
        # Convert dates
        start_date_obj = pd.to_datetime(start_date)
        end_date_obj = pd.to_datetime(end_date)
        start_date_str = start_date_obj.strftime("%d-%m-%Y")
        end_date_str = end_date_obj.strftime("%d-%m-%Y")
        
        # Fetch data from API
        api_client = APIClient(username=username, password=password)
        response = api_client.get_sales_report(
            start_date=start_date_str,
            end_date=end_date_str
        )
        
        if not response.get('success'):
            return dbc.Alert(f"API Error: {response.get('message')}", color="danger"), [], [], []
        
        api_response = response.get('data', {})
        report_data = api_response.get('report_data', [])
        
        if not report_data:
            return dbc.Alert("No data available for this date range", color="warning"), [], [], []
        
        df = pd.DataFrame(report_data)
        
        # Map columns
        column_mapping = {
            'SV': 'Value', 'SQ': 'Qty', 'comp_nm': 'Dealer Name',
            'category_name': 'Category', 'state': 'State', 'city': 'City',
            'meta_keyword': 'Product Name', 'parent_category': 'Sub Category',
            'cust_id': 'Customer ID', 'id': 'Order ID',
            'date': 'Date', 'order_date': 'Date', 'created_at': 'Date', 'sale_date': 'Date'
        }
        df = df.rename(columns={old: new for old, new in column_mapping.items() if old in df.columns})
        
        # Convert numeric columns
        if 'Value' in df.columns:
            df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        if 'Qty' in df.columns:
            df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce')
        
        # Apply filter for Innovative
        if hide_innovative and 'Dealer Name' in df.columns:
            df = df[~df['Dealer Name'].str.contains('Innovative', case=False, na=False)]
        
        # Create CRM DataFrame with all required columns
        crm_df = pd.DataFrame()
        
        # Transaction ID - from Order ID or generate
        crm_df['Transaction ID'] = df['Order ID'] if 'Order ID' in df.columns else [f"TXN-{i+1:06d}" for i in range(len(df))]
        
        # Date - from available date field
        if 'Date' in df.columns:
            crm_df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
            crm_df['Month'] = pd.to_datetime(df['Date'], errors='coerce').dt.strftime('%B')
            crm_df['Year'] = pd.to_datetime(df['Date'], errors='coerce').dt.year
            crm_df['Quarter'] = pd.to_datetime(df['Date'], errors='coerce').dt.quarter.apply(lambda x: f"Q{x}" if pd.notna(x) else "Awaiting API updation for data")
        else:
            crm_df['Date'] = "Awaiting API updation for data"
            crm_df['Month'] = "Awaiting API updation for data"
            crm_df['Year'] = "Awaiting API updation for data"
            crm_df['Quarter'] = "Awaiting API updation for data"
        
        # Dealer - from Dealer Name
        crm_df['Dealer'] = df['Dealer Name'] if 'Dealer Name' in df.columns else "Awaiting API updation for data"
        
        # State - from State
        crm_df['State'] = df['State'] if 'State' in df.columns else "Awaiting API updation for data"
        
        # City - from City
        crm_df['City'] = df['City'] if 'City' in df.columns else "Awaiting API updation for data"
        
        # Executive - not available in API
        crm_df['Executive'] = "Awaiting API updation for data"
        
        # Product - from Product Name
        crm_df['Product'] = df['Product Name'] if 'Product Name' in df.columns else "Awaiting API updation for data"
        
        # Product Family - from Category or Sub Category
        crm_df['Product Family'] = df['Category'] if 'Category' in df.columns else "Awaiting API updation for data"
        
        # Quantity - from Qty
        crm_df['Quantity'] = df['Qty'] if 'Qty' in df.columns else 0
        
        # Revenue - from Value
        crm_df['Revenue'] = df['Value'] if 'Value' in df.columns else 0
        
        # Calculate Unit Price (Revenue / Quantity)
        if 'Value' in df.columns and 'Qty' in df.columns:
            crm_df['Unit Price'] = (df['Value'] / df['Qty']).fillna(0).round(2)
        else:
            crm_df['Unit Price'] = "Awaiting API updation for data"
        
        # Payment Status - not available in API
        crm_df['Payment Status'] = "Awaiting API updation for data"
        
        # Days Overdue - not available in API
        crm_df['Days Overdue'] = "Awaiting API updation for data"
        
        # Interest Amount - not available in API
        crm_df['Interest Amount'] = "Awaiting API updation for data"
        
        # Prepare filter options
        dealer_options = [{'label': dealer, 'value': dealer} for dealer in sorted(crm_df['Dealer'].unique()) if dealer != "Awaiting API updation for data"]
        state_options = [{'label': state, 'value': state} for state in sorted(crm_df['State'].unique()) if state != "Awaiting API updation for data"]
        product_family_options = [{'label': pf, 'value': pf} for pf in sorted(crm_df['Product Family'].unique()) if pf != "Awaiting API updation for data"]
        
        # Apply filters
        filtered_df = crm_df.copy()
        
        if dealer_filter:
            filtered_df = filtered_df[filtered_df['Dealer'].isin(dealer_filter)]
        
        if state_filter:
            filtered_df = filtered_df[filtered_df['State'].isin(state_filter)]
        
        if product_family_filter:
            filtered_df = filtered_df[filtered_df['Product Family'].isin(product_family_filter)]
        
        # Apply search filter
        if search_input:
            mask = filtered_df.astype(str).apply(lambda row: row.str.contains(search_input, case=False, na=False).any(), axis=1)
            filtered_df = filtered_df[mask]
        
        # Create AG Grid table
        column_defs = [
            {'headerName': 'Transaction ID', 'field': 'Transaction ID', 'filter': 'agTextColumnFilter', 'sortable': True, 'resizable': True, 'width': 150, 'pinned': 'left', 'checkboxSelection': True, 'headerCheckboxSelection': True},
            {'headerName': 'Date', 'field': 'Date', 'filter': 'agDateColumnFilter', 'sortable': True, 'resizable': True, 'width': 120},
            {'headerName': 'Month', 'field': 'Month', 'filter': 'agTextColumnFilter', 'sortable': True, 'resizable': True, 'width': 110},
            {'headerName': 'Year', 'field': 'Year', 'filter': 'agNumberColumnFilter', 'sortable': True, 'resizable': True, 'width': 90},
            {'headerName': 'Quarter', 'field': 'Quarter', 'filter': 'agTextColumnFilter', 'sortable': True, 'resizable': True, 'width': 90},
            {'headerName': 'Dealer', 'field': 'Dealer', 'filter': 'agTextColumnFilter', 'sortable': True, 'resizable': True, 'width': 200},
            {'headerName': 'State', 'field': 'State', 'filter': 'agTextColumnFilter', 'sortable': True, 'resizable': True, 'width': 130},
            {'headerName': 'City', 'field': 'City', 'filter': 'agTextColumnFilter', 'sortable': True, 'resizable': True, 'width': 130},
            {'headerName': 'Executive', 'field': 'Executive', 'filter': 'agTextColumnFilter', 'sortable': True, 'resizable': True, 'width': 150},
            {'headerName': 'Product', 'field': 'Product', 'filter': 'agTextColumnFilter', 'sortable': True, 'resizable': True, 'width': 250},
            {'headerName': 'Product Family', 'field': 'Product Family', 'filter': 'agTextColumnFilter', 'sortable': True, 'resizable': True, 'width': 180},
            {'headerName': 'Quantity', 'field': 'Quantity', 'filter': 'agNumberColumnFilter', 'sortable': True, 'resizable': True, 'width': 110, 'type': 'numericColumn', 'valueFormatter': {'function': 'Number(params.value).toLocaleString()'}},
            {'headerName': 'Revenue (₹)', 'field': 'Revenue', 'filter': 'agNumberColumnFilter', 'sortable': True, 'resizable': True, 'width': 140, 'type': 'numericColumn', 'valueFormatter': {'function': 'd3.format(",.2f")(params.value)'}},
            {'headerName': 'Unit Price (₹)', 'field': 'Unit Price', 'filter': 'agNumberColumnFilter', 'sortable': True, 'resizable': True, 'width': 130, 'type': 'numericColumn', 'valueFormatter': {'function': 'typeof params.value === "number" ? d3.format(",.2f")(params.value) : params.value'}},
            {'headerName': 'Payment Status', 'field': 'Payment Status', 'filter': 'agTextColumnFilter', 'sortable': True, 'resizable': True, 'width': 150},
            {'headerName': 'Days Overdue', 'field': 'Days Overdue', 'filter': 'agNumberColumnFilter', 'sortable': True, 'resizable': True, 'width': 130},
            {'headerName': 'Interest Amount (₹)', 'field': 'Interest Amount', 'filter': 'agNumberColumnFilter', 'sortable': True, 'resizable': True, 'width': 160},
        ]
        
        crm_table = html.Div([
            # Summary Stats Row
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H3(f"{len(filtered_df):,}", className="mb-0 text-primary"),
                            html.P("Total Transactions", className="text-muted mb-0 small")
                        ])
                    ], className="shadow-sm")
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H3(format_inr(filtered_df['Revenue'].sum() if pd.api.types.is_numeric_dtype(filtered_df['Revenue']) else 0), className="mb-0 text-success"),
                            html.P("Total Revenue", className="text-muted mb-0 small")
                        ])
                    ], className="shadow-sm")
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H3(format_qty(filtered_df['Quantity'].sum() if pd.api.types.is_numeric_dtype(filtered_df['Quantity']) else 0), className="mb-0 text-info"),
                            html.P("Total Quantity", className="text-muted mb-0 small")
                        ])
                    ], className="shadow-sm")
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H3(f"{filtered_df['Dealer'].nunique() if filtered_df['Dealer'].dtype == 'object' else 0}", className="mb-0 text-warning"),
                            html.P("Unique Dealers", className="text-muted mb-0 small")
                        ])
                    ], className="shadow-sm")
                ], width=3),
            ], className="g-2 mb-4"),
            
            # AG Grid Table
            dag.AgGrid(
                id='crm-data-table',
                rowData=filtered_df.to_dict('records'),
                columnDefs=column_defs,
                defaultColDef={
                    'filter': True,
                    'sortable': True,
                    'resizable': True,
                    'minWidth': 100,
                },
                dashGridOptions={
                    'pagination': True,
                    'paginationPageSize': 50,
                    'paginationPageSizeSelector': [25, 50, 100, 200, 500],
                    'enableRangeSelection': True,
                    'rowSelection': 'multiple',
                    'suppressRowClickSelection': True,
                    'animateRows': True,
                    'enableCellTextSelection': True,
                },
                className="ag-theme-alpine",
                style={'height': '600px', 'width': '100%'},
            ),
            
            # Info footer
            html.Div([
                html.Small([
                    html.I(className="bi bi-info-circle me-2"),
                    "Click column headers to sort • Use filter icons to search specific columns • Select rows with checkboxes for bulk export • Scroll horizontally for all columns"
                ], className="text-muted")
            ], className="mt-3")
        ])
        
        return crm_table, dealer_options, state_options, product_family_options
        
    except Exception as e:
        print(f"Error in CRM table: {str(e)}")
        import traceback
        traceback.print_exc()
        return dbc.Alert(f"Error loading CRM data: {str(e)}", color="danger"), [], [], []

# Clear CRM Filters Callback
@app.callback(
    Output('crm-dealer-filter', 'value'),
    Output('crm-state-filter', 'value'),
    Output('crm-product-family-filter', 'value'),
    Output('crm-payment-status-filter', 'value'),
    Output('crm-search-input', 'value'),
    Input('crm-clear-filters-btn', 'n_clicks'),
    prevent_initial_call=True
)
def clear_crm_filters(n_clicks):
    """Clear all CRM filters"""
    if n_clicks:
        return None, None, None, 'all', ""
    return no_update, no_update, no_update, no_update, no_update

# Export CRM Data Callback
@app.callback(
    Output('crm-download', 'data'),
    Input('crm-export-btn', 'n_clicks'),
    State('crm-data-table', 'rowData'),
    State('date-range-picker', 'start_date'),
    State('date-range-picker', 'end_date'),
    prevent_initial_call=True
)
def export_crm_data(n_clicks, row_data, start_date, end_date):
    """Export CRM data to CSV"""
    
    if not n_clicks or not row_data:
        return no_update
    
    try:
        df = pd.DataFrame(row_data)
        
        # Convert to CSV
        csv_string = df.to_csv(index=False, encoding='utf-8')
        
        return dict(content=csv_string, filename=f"sales_crm_{start_date}_{end_date}.csv")
    
    except Exception as e:
        print(f"Error exporting CRM data: {str(e)}")
        return no_update

# Quick Date Selection Callback
@app.callback(
    Output('date-range-picker', 'start_date'),
    Output('date-range-picker', 'end_date'),
    Input('quick-today', 'n_clicks'),
    Input('quick-yesterday', 'n_clicks'),
    Input('quick-week', 'n_clicks'),
    Input('quick-month', 'n_clicks'),
    Input('quick-3months', 'n_clicks'),
    prevent_initial_call=True
)
def quick_date_select(today_click, yest_click, week_click, month_click, three_month_click):
    triggered = ctx.triggered_id
    now = datetime.now()
    if triggered == 'quick-today':
        start = end = now
    elif triggered == 'quick-yesterday':
        start = end = now - timedelta(days=1)
    elif triggered == 'quick-week':
        start = get_week_start()
        end = now
    elif triggered == 'quick-month':
        start = now.replace(day=1)
        end = now
    elif triggered == 'quick-3months':
        start = now - timedelta(days=90)
        end = now
    else:
        return no_update, no_update
    # Format as yyyy-mm-dd for DatePickerRange
    return start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')

# Clientside callback for button feedback
app.clientside_callback(
    """
    function(t, y, w, m, threem) {
        const ids = ['quick-today', 'quick-yesterday', 'quick-week', 'quick-month', 'quick-3months'];
        const btns = ids.map(id => document.getElementById(id));
        let idx = -1;
        if (t) idx = 0;
        else if (y) idx = 1;
        else if (w) idx = 2;
        else if (m) idx = 3;
        else if (threem) idx = 4;
        if (idx >= 0 && btns[idx]) {
            btns[idx].classList.remove('btn-outline-primary');
            btns[idx].classList.add('btn-primary');
            setTimeout(() => {
                btns[idx].classList.add('btn-outline-primary');
                btns[idx].classList.remove('btn-primary');
            }, 500);
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('quick-today', 'n_clicks'),
    Input('quick-today', 'n_clicks'),
    Input('quick-yesterday', 'n_clicks'),
    Input('quick-week', 'n_clicks'),
    Input('quick-month', 'n_clicks'),
    Input('quick-3months', 'n_clicks'),
    prevent_initial_call=True
)

# Clientside callback for period button styling
app.clientside_callback(
    """
    function(daily, weekly, monthly) {
        const ids = ['period-daily-btn', 'period-weekly-btn', 'period-monthly-btn'];
        const btns = ids.map(id => document.getElementById(id));
        
        if (!btns[0]) return window.dash_clientside.no_update;
        
        let selectedIdx = 0;
        if (daily) selectedIdx = 0;
        else if (weekly) selectedIdx = 1;
        else if (monthly) selectedIdx = 2;
        
        // Update button styles
        btns.forEach((btn, idx) => {
            if (btn) {
                if (idx === selectedIdx) {
                    btn.classList.remove('btn-outline-primary');
                    btn.classList.add('btn-primary');
                    btn.style.outline = 'false';
                } else {
                    btn.classList.remove('btn-primary');
                    btn.classList.add('btn-outline-primary');
                    btn.style.outline = 'true';
                }
            }
        });
        
        return window.dash_clientside.no_update;
    }
    """,
    Output('period-daily-btn', 'outline', allow_duplicate=True),
    Input('period-daily-btn', 'n_clicks'),
    Input('period-weekly-btn', 'n_clicks'),
    Input('period-monthly-btn', 'n_clicks'),
    prevent_initial_call=True
)

# Geographic Map Functions
def _create_india_map(df, metric, level='State', is_bubble=False):
    """
    Create interactive India map showing sales distribution
    
    Args:
        df: DataFrame with sales data
        metric: 'Revenue', 'Quantity', or 'Orders'
        level: 'State' or 'City'
        is_bubble: If True, create bubble/scatter map; if False, create choropleth
    """
    if df is None or df.empty:
        return go.Figure().add_annotation(
            text="No geographic data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color='gray')
        )
    
    # Check if required columns exist
    if level not in df.columns:
        return go.Figure().add_annotation(
            text=f"{level} data not available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color='gray')
        )
    
    # Determine metric column and aggregation
    if metric == 'Revenue':
        metric_col = 'Value' if 'Value' in df.columns else None
        agg_func = 'sum'
        title_suffix = "Revenue"
        color_scale = [[0, '#E3F2FD'], [0.5, '#42A5F5'], [1, '#0D47A1']]  # Blue gradient
        hover_format = "Rs. %{customdata[1]:,.0f}"
    elif metric == 'Quantity':
        metric_col = 'Qty' if 'Qty' in df.columns else None
        agg_func = 'sum'
        title_suffix = "Quantity Sold"
        color_scale = [[0, '#E8F5E9'], [0.5, '#66BB6A'], [1, '#1B5E20']]  # Green gradient
        hover_format = "%{customdata[1]:,.0f} units"
    else:  # Orders
        metric_col = None
        agg_func = 'count'
        title_suffix = "Order Count"
        color_scale = [[0, '#FFF3E0'], [0.5, '#FF9800'], [1, '#E65100']]  # Orange gradient
        hover_format = "%{customdata[1]:,.0f} orders"
    
    if not metric_col and agg_func != 'count':
        return go.Figure().add_annotation(
            text=f"{metric} data not available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color='gray')
        )
    
    # Aggregate data by location
    if agg_func == 'count':
        location_data = df.groupby(level).size().reset_index(name='metric_value')
    else:
        location_data = df.groupby(level)[metric_col].sum().reset_index(name='metric_value')
    
    # Calculate percentage of total
    total_value = location_data['metric_value'].sum()
    location_data['percentage'] = (location_data['metric_value'] / total_value * 100).round(2)
    
    # Sort and limit to top locations for better performance
    location_data = location_data.sort_values('metric_value', ascending=False)
    if level == 'City':
        location_data = location_data.head(50)  # Limit to top 50 cities
    
    # Get coordinates dictionary
    coords_dict = CITY_COORDS if level == 'City' else STATE_COORDS
    
    # For State level, ensure ALL states are shown (even with zero data)
    if level == 'State':
        # Create a complete list of all states
        all_states = list(STATE_COORDS.keys())
        existing_states = set(location_data['State'].tolist())
        missing_states = [s for s in all_states if s not in existing_states]
        
        # Add missing states with zero values
        if missing_states:
            zero_data = pd.DataFrame({
                'State': missing_states,
                'metric_value': [0] * len(missing_states),
                'percentage': [0.0] * len(missing_states)
            })
            location_data = pd.concat([location_data, zero_data], ignore_index=True)
    
    if is_bubble:
        # Create bubble/scatter map
        # Get coordinates for locations
        coords_dict = CITY_COORDS if level == 'City' else STATE_COORDS
        
        locations = []
        lats = []
        lons = []
        values = []
        names = []
        percentages = []
        
        for _, row in location_data.iterrows():
            location_name = row[level]
            if location_name in coords_dict:
                lat, lon = coords_dict[location_name]
                locations.append(location_name)
                lats.append(lat)
                lons.append(lon)
                values.append(row['metric_value'])
                names.append(location_name)
                percentages.append(row['percentage'])
        
        if not locations:
            return go.Figure().add_annotation(
                text="No coordinate data available for selected locations",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color='gray')
            )
        
        # Create scatter geo map
        fig = go.Figure(data=go.Scattergeo(
            lon=lons,
            lat=lats,
            text=names,
            mode='markers',
            marker=dict(
                size=[v/max(values)*50 + 10 for v in values],  # Scale bubble size
                color=values,
                colorscale=color_scale,
                showscale=True,
                colorbar=dict(
                    title=title_suffix,
                    thickness=15,
                    len=0.7,
                    x=1.02
                ),
                line=dict(width=1, color='white'),
                sizemode='diameter'
            ),
            customdata=[[name, val, pct] for name, val, pct in zip(names, values, percentages)],
            hovertemplate=(
                '<b>%{customdata[0]}</b><br>' +
                f'{title_suffix}: {hover_format}<br>' +
                'Share: %{customdata[2]:.2f}%<br>' +
                '<extra></extra>'
            ),
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Inter, sans-serif",
                font_color="black"
            )
        ))
        
        # Update geo layout for India - Use scope='asia' for proper geographic rendering
        fig.update_geos(
            scope='asia',
            projection_type='mercator',
            center=dict(lat=23.5, lon=78.5),
            lataxis_range=[6, 37],
            lonaxis_range=[68, 98],
            bgcolor='rgba(0,0,0,0)',
            showland=True,
            landcolor='#f0f0f0',
            showocean=True,
            oceancolor='#e6f2ff',
            showcountries=True,
            countrycolor='white',
            countrywidth=2
        )
        
    else:
        # Create choropleth-style visualization using scatter geo with filled markers
        # Get coordinates for locations
        coords_dict = CITY_COORDS if level == 'City' else STATE_COORDS
        
        locations = []
        lats = []
        lons = []
        values = []
        names = []
        percentages = []
        
        for _, row in location_data.iterrows():
            location_name = row[level]
            if location_name in coords_dict:
                lat, lon = coords_dict[location_name]
                locations.append(location_name)
                lats.append(lat)
                lons.append(lon)
                values.append(row['metric_value'])
                names.append(location_name)
                percentages.append(row['percentage'])
        
        if not locations:
            return go.Figure().add_annotation(
                text="No coordinate data available for selected locations",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color='gray')
            )
        
        # Create scatter geo map with larger markers for choropleth effect
        fig = go.Figure(data=go.Scattergeo(
            lon=lons,
            lat=lats,
            text=names,
            mode='markers',
            marker=dict(
                size=40,  # Fixed larger size for choropleth effect
                color=values,
                colorscale=color_scale,
                showscale=True,
                colorbar=dict(
                    title=title_suffix,
                    thickness=15,
                    len=0.7,
                    x=1.02
                ),
                line=dict(width=2, color='white'),
                sizemode='diameter',
                opacity=0.8
            ),
            customdata=[[name, val, pct] for name, val, pct in zip(names, values, percentages)],
            hovertemplate=(
                '<b>%{customdata[0]}</b><br>' +
                f'{title_suffix}: {hover_format}<br>' +
                'Share: %{customdata[2]:.2f}%<br>' +
                '<extra></extra>'
            ),
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Inter, sans-serif",
                font_color="black"
            )
        ))
        
        # Update geo layout for India - Use scope='asia' for proper geographic rendering
        fig.update_geos(
            scope='asia',
            projection_type='mercator',
            center=dict(lat=23.5, lon=78.5),
            lataxis_range=[6, 37],
            lonaxis_range=[68, 98],
            bgcolor='rgba(0,0,0,0)',
            showland=True,
            landcolor='#f0f0f0',
            showocean=True,
            oceancolor='#e6f2ff',
            showcountries=True,
            countrycolor='white',
            countrywidth=2
        )
    
    # Update layout
    apply_modern_chart_style(fig, f"{title_suffix} Distribution by {level}", height=600)
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=50, b=0),
        geo=dict(bgcolor='rgba(0,0,0,0)')
    )
    
    return fig

# Geographic Map Callback
@app.callback(
    [Output('geographic-map', 'figure'),
     Output('selected-location-display', 'children')],
    [Input('map-metric-selector', 'value'),
     Input('map-level-selector', 'value'),
     Input('map-bubble-toggle', 'on'),
     Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date'),
     Input('hide-innovative-check', 'value'),
     Input('map-reset-btn', 'n_clicks'),
     Input('username-input', 'value'),
     Input('password-input', 'value')],
    prevent_initial_call=False
)
def update_map(metric, level, is_bubble, start_date, end_date, 
               hide_innovative, reset_clicks, username, password):
    """Update geographic map based on user selections"""
    try:
        # Debug logging
        print(f"\nMAP CALLBACK TRIGGERED")
        print(f"   Metric: {metric}, Level: {level}, Bubble: {is_bubble}")
        print(f"   Dates: {start_date} to {end_date}")
        print(f"   Username: {username}, Hide Innovative: {hide_innovative}")
        
        # Convert dates to DD-MM-YYYY format for API
        if start_date and end_date:
            start_date_obj = pd.to_datetime(start_date)
            end_date_obj = pd.to_datetime(end_date)
            start_date_str = start_date_obj.strftime("%d-%m-%Y")
            end_date_str = end_date_obj.strftime("%d-%m-%Y")
        else:
            # Use default dates if not provided
            today = datetime.now()
            month_start = today.replace(day=1)
            start_date_str = month_start.strftime("%d-%m-%Y")
            end_date_str = today.strftime("%d-%m-%Y")
        
        # Initialize API client with provided credentials
        # Use default credentials if not provided
        if not username or not password:
            username = 'u2vp8kb'
            password = 'asdftuy#$%78@!'
            print(f"   Using default credentials")
        
        api_client = APIClient(username=username, password=password)
        
        # Fetch data from API
        print(f"   Fetching data from {start_date_str} to {end_date_str}...")
        response = api_client.get_sales_report(
            start_date=start_date_str,
            end_date=end_date_str
        )
        
        print(f"   API Response success: {response.get('success')}")
        
        if not response.get('success'):
            print(f"   API Error: {response.get('message')}")
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text="Failed to fetch data from API",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            empty_fig.update_layout(
                height=600,
                paper_bgcolor='white'
            )
            return empty_fig, ""
        
        # Extract data from response
        api_response = response.get('data', {})
        report_data = api_response.get('report_data', [])
        
        print(f"   Data rows received: {len(report_data)}")
        
        if not report_data:
            print(f"   No data available")
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text="No data available for selected filters",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            empty_fig.update_layout(
                height=600,
                paper_bgcolor='white',
                geo=dict(
                    scope='asia',
                    projection_type='mercator',
                    center=dict(lat=23.5, lon=78.5),
                    visible=False
                )
            )
            return empty_fig, ""
        
        # Convert to DataFrame
        df = pd.DataFrame(report_data)
        
        # Map columns
        column_mapping = {
            'SV': 'Value',
            'SQ': 'Qty',
            'comp_nm': 'Dealer Name',
            'state': 'State',
            'city': 'City'
        }
        df = df.rename(columns={old: new for old, new in column_mapping.items() if old in df.columns})
        
        print(f"   DataFrame columns after mapping: {list(df.columns)}")
        print(f"   Unique States: {df['State'].nunique() if 'State' in df.columns else 0}")
        print(f"   Unique Cities: {df['City'].nunique() if 'City' in df.columns else 0}")
        
        # Convert numeric columns
        if 'Value' in df.columns:
            df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        if 'Qty' in df.columns:
            df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce')
        
        # Apply innovative filter
        if hide_innovative and 'Dealer Name' in df.columns:
            df = df[~df['Dealer Name'].str.contains('Innovative', case=False, na=False)]
            print(f"   After filter: {len(df)} rows")
        
        # Create the map
        print(f"   Creating map: metric={metric}, level={level}, is_bubble={is_bubble}")
        fig = _create_india_map(df, metric, level, is_bubble)
        
        print(f"   ✅ Map created successfully")
        
        # Location display is not needed without filters
        location_text = ""
        
        return fig, location_text
        
    except Exception as e:
        logger.error(f"Error updating geographic map: {e}")
        error_fig = go.Figure()
        error_fig.add_annotation(
            text=f"Error loading map: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color='red')
        )
        error_fig.update_layout(
            height=600,
            paper_bgcolor='white'
        )
        return error_fig, ""

# Map Click Handler and Filter Sync callbacks are disabled 
# because state-filter and city-filter components are not in the layout
# Uncomment these when filter components are added to the dashboard

# # Map Click Handler - Store selected location
@app.callback(
    Output('selected-location-store', 'data'),
    [Input('geographic-map', 'clickData'),
     Input('map-reset-btn', 'n_clicks')],
    [State('map-level-selector', 'value')],
    prevent_initial_call=True
)
def handle_map_click(click_data, reset_clicks, level):
    """Handle map clicks to filter by location"""
    ctx = callback_context
    
    if not ctx.triggered:
        return None
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Reset button clicked
    if trigger_id == 'map-reset-btn':
        return None
    
    # Map clicked
    if trigger_id == 'geographic-map' and click_data:
        try:
            location = click_data['points'][0]['location']
            return {'location': location, 'level': level}
        except (KeyError, IndexError):
            return None
    
    return None

# Sync map selection to filters
@app.callback(
    [Output('state-filter', 'value', allow_duplicate=True),
     Output('city-filter', 'value', allow_duplicate=True)],
    [Input('selected-location-store', 'data')],
    prevent_initial_call=True
)
def sync_map_to_filters(location_data):
    """Sync map selection to state/city filters"""
    if not location_data:
        return None, None
    
    location = location_data.get('location')
    level = location_data.get('level')
    
    if level == 'State':
        return [location], None
    elif level == 'City':
        return None, [location]
    
    return None, None

# Modern Chart Styling Helper
def apply_modern_chart_style(fig, title="", height=400):
    """Apply modern Magenta-inspired styling to Plotly charts"""
    fig.update_layout(
        template='plotly_white',
        font=dict(
            family='Inter, -apple-system, BlinkMacSystemFont, sans-serif',
            size=12,
            color='#1f2937'
        ),
        title=dict(
            text=title,
            font=dict(size=16, weight=600, color='#1f2937'),
            x=0.5,
            xanchor='center'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=60, b=40),
        height=height,
        hoverlabel=dict(
            bgcolor='white',
            font_size=12,
            font_family='Inter, sans-serif',
            font_color='black',
            bordercolor='#e5e7eb'
        ),
        xaxis=dict(
            gridcolor='#f3f4f6',
            showgrid=False,
            zeroline=False,
            linecolor='#e5e7eb'
        ),
        yaxis=dict(
            gridcolor='#f3f4f6',
            showgrid=True,
            zeroline=False,
            linecolor='#e5e7eb'
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.2,
            xanchor='center',
            x=0.5,
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#e5e7eb',
            borderwidth=1
        )
    )
    return fig

# Chart creation functions
def _create_dealer_pie(df, value_col, limit=10):
    """Create dealer revenue pie chart with modern styling""" 
    if not value_col or 'Dealer Name' not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="No data available", font=dict(size=14, color='#9ca3af'))
        return apply_modern_chart_style(fig, "🏆 Top Dealers by Revenue")
    
    dealer_data = df.groupby('Dealer Name')[value_col].sum().reset_index()
    dealer_data = dealer_data.sort_values(value_col, ascending=False).head(limit)
    
    # Modern color palette - Magenta inspired
    colors = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', 
              '#3b82f6', '#ef4444', '#14b8a6', '#f97316', '#a855f7']
    
    fig = px.pie(
        dealer_data,
        values=value_col,
        names='Dealer Name',
        color_discrete_sequence=colors[:len(dealer_data)]
    )
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Revenue: ₹%{value:,.0f}<br>Share: %{percent}<extra></extra>',
        marker=dict(line=dict(color='white', width=3)),
        pull=[0.05 if i == 0 else 0 for i in range(len(dealer_data))]
    )
    
    return apply_modern_chart_style(fig, f"🏆 Top {limit} Dealers by Revenue", height=450)

def _create_state_pie(df, value_col):
    """Create state revenue pie chart"""
    if not value_col or 'State' not in df.columns:
        return go.Figure().add_annotation(text="No data")
    
    state_data = df.groupby('State')[value_col].sum().reset_index()
    state_data = state_data.sort_values(value_col, ascending=False).head(10)
    
    # Modern color palette
    colors = [COLORS['primary'], COLORS['secondary'], COLORS['success'], COLORS['warning'], 
              COLORS['info'], '#ec4899', '#f97316', '#06b6d4', '#8b5cf6', '#10b981']
    
    fig = px.pie(
        state_data,
        values=value_col,
        names='State',
        title="🗺️ Top 10 States by Revenue",
        color_discrete_sequence=colors[:len(state_data)]
    )
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Revenue: Rs. %{value:,.0f}<br>Share: %{percent}<extra></extra>',
        marker=dict(line=dict(color='white', width=2)),
        pull=[0.03 if i < 3 else 0 for i in range(len(state_data))]
    )
    
    # Apply modern styling
    apply_modern_chart_style(fig, "🗺️ Top 10 States by Revenue", height=450)
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        ),
        margin=dict(t=50, b=100, l=20, r=20)
    )
    return fig

def _create_category_bar(df, value_col):
    """Create category revenue bar chart"""
    if not value_col or 'Category' not in df.columns:
        return go.Figure().add_annotation(text="No data")
    
    cat_data = df.groupby('Category')[value_col].sum().reset_index()
    cat_data = cat_data.sort_values(value_col, ascending=True)
    
    fig = px.bar(
        cat_data,
        x=value_col,
        y='Category',
        orientation='h',
        title="📂 Revenue by Category",
        color=value_col,
        color_continuous_scale=[[0, COLORS['primary']], [1, COLORS['secondary']]]
    )
    fig.update_traces(
        text=[f"Rs. {x/1e5:.1f}L" for x in cat_data[value_col]],
        textposition='outside',
        textfont=dict(size=10),
        hovertemplate='<b>%{y}</b><br>Revenue: Rs. %{x:,.0f}<extra></extra>',
        marker=dict(
            line=dict(color='white', width=1),
            opacity=0.9
        )
    )
    
    # Apply modern styling
    apply_modern_chart_style(fig, "📂 Revenue by Category", height=450)
    fig.update_xaxes(tickformat=',.0f')
    fig.update_yaxes(tickfont=dict(size=11))
    fig.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(t=50, b=20, l=150, r=50)
    )
    return fig

def _create_revenue_trend(df, value_col):
    """Create revenue trend line chart with moving average"""
    if not value_col or 'Date' not in df.columns:
        return go.Figure().add_annotation(text="No date data available")
    
    # Ensure Date column is datetime
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    
    # Group by date and sum revenue
    daily_revenue = df.groupby(df['Date'].dt.date)[value_col].sum().reset_index()
    daily_revenue['Date'] = pd.to_datetime(daily_revenue['Date'])
    daily_revenue = daily_revenue.sort_values('Date')
    
    # Calculate 7-day moving average
    daily_revenue['Moving_Avg'] = daily_revenue[value_col].rolling(window=7, min_periods=1).mean()
    
    # Create figure
    fig = go.Figure()
    
    # Add moving average line first (so it appears behind)
    fig.add_trace(go.Scatter(
        x=daily_revenue['Date'],
        y=daily_revenue['Moving_Avg'],
        mode='lines',
        name='7-Day Moving Average',
        line=dict(color=COLORS['danger'], width=3, dash='dash'),
        fill='tozeroy',
        fillcolor=f"rgba({int(COLORS['danger'][1:3], 16)}, {int(COLORS['danger'][3:5], 16)}, {int(COLORS['danger'][5:7], 16)}, 0.1)"
    ))
    
    # Add actual revenue line with markers
    fig.add_trace(go.Scatter(
        x=daily_revenue['Date'],
        y=daily_revenue[value_col],
        mode='lines+markers',
        name='Daily Revenue',
        line=dict(color=COLORS['success'], width=2),
        marker=dict(size=6, color=COLORS['success'], line=dict(width=1, color='white'))
    ))
    
    # Apply modern styling
    apply_modern_chart_style(fig, "📈 Revenue Trend Over Time", height=400)
    
    # Update layout
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Revenue (Rs.)",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='lightgray',
            borderwidth=1
        ),
        margin=dict(t=60, b=40, l=60, r=40)
    )
    
    # Format y-axis as Indian currency
    fig.update_yaxes(
        tickformat=".2f",
        tickprefix="Rs. ",
        tickvals=[1e5, 1e6, 1e7, 1e8, 1e9],
        ticktext=["0.1L", "1L", "10L", "1Cr", "10Cr"]
    )
    
    # Format x-axis
    fig.update_xaxes(tickformat='%d-%b')
    
    return fig

def _create_top_products_table(df, value_col, qty_col):
    """Create top products table component"""
    if not value_col or not qty_col or 'Product Name' not in df.columns:
        return dbc.Card([
            dbc.CardHeader("🏆 Top 15 Products"),
            dbc.CardBody("No product data available")
        ])
    
    # Group by Product Name and aggregate
    product_data = df.groupby('Product Name').agg({
        value_col: 'sum',
        qty_col: 'sum'
    }).reset_index()
    
    # Sort by value descending and take top 15
    product_data = product_data.sort_values(value_col, ascending=False).head(15)
    
    # Create table rows
    table_rows = []
    for idx, row in product_data.iterrows():
        rank = idx + 1
        product_name = row['Product Name']
        revenue = row[value_col]
        quantity = row[qty_col]
        
        # Format revenue as Rs. X.XX Lakh
        if revenue >= 1e5:
            formatted_revenue = f"Rs. {revenue/1e5:.2f} Lakh"
        else:
            formatted_revenue = f"Rs. {revenue:.0f}"
        
        # Format quantity
        formatted_quantity = format_qty(quantity)
        
        table_rows.append(html.Tr([
            html.Td(rank),
            html.Td(product_name),
            html.Td(formatted_revenue),
            html.Td(formatted_quantity)
        ]))
    
    # Create table
    table = dbc.Table([
        html.Thead(html.Tr([
            html.Th("Rank"),
            html.Th("Product Name"),
            html.Th("Revenue"),
            html.Th("Quantity")
        ])),
        html.Tbody(table_rows)
    ], striped=True, hover=True)
    
    # Wrap in card
    card = dbc.Card([
        dbc.CardHeader([
            html.H6("🏆 Top 15 Products", className="mb-0 fw-bold text-primary"),
            html.Small("Ranked by total revenue", className="text-muted")
        ]),
        dbc.CardBody([
            table
        ], style={'padding': '0.5rem'})
    ])
    
    return card

def _create_dealer_comparison(df, value_col, qty_col):
    """Create dealer comparison bar chart"""
    if not value_col or not qty_col or 'Dealer Name' not in df.columns:
        return go.Figure().add_annotation(text="No dealer data available")
    
    # Group by Dealer Name and aggregate
    dealer_data = df.groupby('Dealer Name').agg({
        value_col: 'sum',
        qty_col: 'sum'
    }).reset_index()
    
    # Sort by value descending and take top 10
    dealer_data = dealer_data.sort_values(value_col, ascending=False).head(10)
    
    # Create figure
    fig = go.Figure()
    
    # Add revenue bars
    fig.add_trace(go.Bar(
        x=dealer_data[value_col],
        y=dealer_data['Dealer Name'],
        name='Revenue',
        orientation='h',
        marker_color=COLORS['info'],
        opacity=0.9,
        hovertemplate='<b>%{y}</b><br>Revenue: Rs. %{x:,.0f}<extra></extra>'
    ))
    
    # Add quantity bars on secondary y-axis
    fig.add_trace(go.Bar(
        x=dealer_data[qty_col],
        y=dealer_data['Dealer Name'],
        name='Quantity',
        orientation='h',
        marker_color=COLORS['danger'],
        opacity=0.9,
        xaxis='x2',
        hovertemplate='<b>%{y}</b><br>Quantity: %{x:,.0f}<extra></extra>'
    ))
    
    # Apply modern styling
    apply_modern_chart_style(fig, "🏪 Top 10 Dealers - Revenue vs Quantity", height=500)
    
    # Update layout
    fig.update_layout(
        xaxis=dict(
            title="Revenue (Rs.)",
            tickformat=".2f",
            tickprefix="Rs. ",
            tickvals=[1e5, 1e6, 1e7, 1e8, 1e9],
            ticktext=["0.1L", "1L", "10L", "1Cr", "10Cr"]
        ),
        xaxis2=dict(
            title="Quantity",
            overlaying='x',
            side='top',
            showgrid=False
        ),
        yaxis=dict(
            title="Dealer Name",
            tickfont=dict(size=10)
        ),
        barmode='group',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='lightgray',
            borderwidth=1
        ),
        margin=dict(t=60, b=80, l=150, r=80)
    )
    
    return fig

def _create_city_bar(df, value_col):
    """Create city revenue bar chart"""
    if not value_col or 'City' not in df.columns:
        return go.Figure().add_annotation(text="No city data available")
    
    # Group by City and sum revenue
    city_data = df.groupby('City')[value_col].sum().reset_index()
    
    # Sort descending and take top 12
    city_data = city_data.sort_values(value_col, ascending=False).head(12)
    
    # Format text for bars
    text_values = [f"Rs. {x/1e5:.1f}L" for x in city_data[value_col]]
    
    # Create bar chart with gradient colors
    fig = px.bar(
        city_data,
        x='City',
        y=value_col,
        title="🏙️ Top 12 Cities by Revenue",
        color=value_col,
        color_continuous_scale=[[0, COLORS['light']], [1, COLORS['info']]]
    )
    
    # Update traces
    fig.update_traces(
        text=text_values,
        textposition='outside',
        textfont=dict(size=9),
        hovertemplate='<b>%{x}</b><br>Revenue: Rs. %{y:,.0f}<extra></extra>',
        marker=dict(
            line=dict(color='white', width=1),
            opacity=0.9
        )
    )
    
    # Apply modern styling
    apply_modern_chart_style(fig, "🏙️ Top 12 Cities by Revenue", height=450)
    
    fig.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(t=50, b=60, l=40, r=40)
    )
    
    # Format y-axis
    fig.update_yaxes(
        tickformat=".2f",
        tickprefix="Rs. ",
        tickvals=[1e5, 1e6, 1e7, 1e8, 1e9],
        ticktext=["0.1L", "1L", "10L", "1Cr", "10Cr"]
    )
    
    # Format x-axis
    fig.update_xaxes(
        tickangle=45,
        tickfont=dict(size=10)
    )
    
    return fig

def _create_category_sunburst(df, value_col):
    """Create category sunburst chart"""
    if not value_col or 'Category' not in df.columns or 'Sub Category' not in df.columns:
        return go.Figure().add_annotation(text="No category data available")
    
    # Group by Category and Sub Category
    sunburst_data = df.groupby(['Category', 'Sub Category'])[value_col].sum().reset_index()
    
    # Create sunburst chart
    fig = px.sunburst(
        sunburst_data,
        path=['Category', 'Sub Category'],
        values=value_col,
        color=value_col,
        color_continuous_scale=[[0, '#FFF5E1'], [0.5, COLORS['warning']], [1, COLORS['danger']]],
        title="📊 Category & Sub-Category Breakdown"
    )
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>Revenue: Rs. %{value:,.0f}<br>Parent: %{parent}<extra></extra>',
        textinfo='label+percent entry',
        textfont=dict(size=11)
    )
    
    # Apply modern styling
    apply_modern_chart_style(fig, "📊 Category & Sub-Category Breakdown", height=550)
    fig.update_layout(margin=dict(t=60, b=20, l=20, r=20))
    
    return fig

def _create_weekday_pattern(df, value_col):
    """Create weekday revenue pattern bar chart"""
    if not value_col or 'Date' not in df.columns:
        return go.Figure().add_annotation(text="No date data available")
    
    # Ensure Date column is datetime
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    
    # Extract weekday name
    df['Weekday'] = df['Date'].dt.day_name()
    
    # Group by weekday and sum revenue
    weekday_data = df.groupby('Weekday')[value_col].sum().reset_index()
    
    # Order weekdays
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_data['Weekday'] = pd.Categorical(weekday_data['Weekday'], categories=weekday_order, ordered=True)
    weekday_data = weekday_data.sort_values('Weekday')
    
    # Create bar chart with gradient colors
    fig = px.bar(
        weekday_data,
        x='Weekday',
        y=value_col,
        title="📅 Revenue by Day of Week",
        color=value_col,
        color_continuous_scale=[[0, '#FFF9C4'], [0.5, COLORS['warning']], [1, '#FF9800']]
    )
    
    # Update traces
    fig.update_traces(
        text=[f"Rs. {x/1e5:.1f}L" for x in weekday_data[value_col]],
        textposition='outside',
        textfont=dict(size=9),
        hovertemplate='<b>%{x}</b><br>Revenue: Rs. %{y:,.0f}<extra></extra>',
        marker=dict(
            line=dict(color='white', width=1),
            opacity=0.9
        )
    )
    
    # Apply modern styling
    apply_modern_chart_style(fig, "📅 Revenue by Day of Week", height=400)
    
    # Update layout
    fig.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(t=50, b=40, l=40, r=40)
    )
    
    # Format y-axis as Lakhs
    fig.update_yaxes(
        tickformat=".2f",
        tickprefix="Rs. ",
        tickvals=[1e5, 1e6, 1e7, 1e8, 1e9],
        ticktext=["0.1L", "1L", "10L", "1Cr", "10Cr"]
    )
    
    # Format x-axis
    fig.update_xaxes(tickfont=dict(size=11))
    
    return fig

def _create_sparkline(values, color='#2ECC71'):
    """
    Create a mini sparkline chart for metric cards
    
    Args:
        values: Array of values (e.g., last 30 days)
        color: Line color for the sparkline
    
    Returns:
        Plotly figure object (60px height, transparent, no axes)
    """
    if not values or len(values) == 0:
        # Return empty figure if no data
        fig = go.Figure()
        fig.update_layout(
            height=60,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig
    
    # Create simple line chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        y=values,
        mode='lines',
        line=dict(color=color, width=2),
        fill='tozeroy',
        fillcolor=f'rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.1)',
        hoverinfo='skip'
    ))
    
    # Update layout for sparkline style
    fig.update_layout(
        height=60,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            visible=False,
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            visible=False,
            showgrid=False,
            zeroline=False
        ),
        showlegend=False,
        hovermode=False
    )
    
    return fig

def _create_enhanced_metric_card(
    icon, 
    label, 
    current_value, 
    previous_value, 
    trend_values, 
    color='#2ECC71',
    gradient_start='rgba(46, 204, 113, 0.1)',
    gradient_end='rgba(46, 204, 113, 0.02)',
    date_range_text=""
):
    """
    Create enhanced metric card with sparkline and period-over-period comparison
    
    Args:
        icon: Emoji or icon for the metric
        label: Metric label (e.g., "Revenue")
        current_value: Current period value (formatted string or numeric)
        previous_value: Previous period value (numeric)
        trend_values: Array of daily values for sparkline
        color: Theme color for the metric
        gradient_start: Starting color for card gradient
        gradient_end: Ending color for card gradient
        date_range_text: Date range description
    
    Returns:
        dbc.Card component with enhanced styling
    """
    # Calculate percentage change
    # Extract numeric value from formatted string for comparison
    if previous_value and previous_value > 0:
        try:
            # Try to extract numeric value from current_value string
            current_numeric = float(str(current_value).replace('Rs. ', '').replace('L', '').replace('K', '').replace(',', '').replace('\n', ' ').split()[0])
            
            # Adjust for K/L suffixes
            if 'L' in str(current_value):
                current_numeric *= 100000
            elif 'K' in str(current_value):
                current_numeric *= 1000
            
            pct_change = ((current_numeric - previous_value) / previous_value) * 100
        except:
            pct_change = 0
    else:
        pct_change = 0
    
    # Determine change color and arrow
    if pct_change > 0:
        change_color = '#28a745'  # Green
        arrow = '↑'
    elif pct_change < 0:
        change_color = '#dc3545'  # Red
        arrow = '↓'
    else:
        change_color = '#6c757d'  # Gray
        arrow = '→'
    
    # Create sparkline
    sparkline_fig = _create_sparkline(trend_values, color)
    
    # Build card with gradient background
    card = dbc.Card([
        dbc.CardBody([
            # Top row: Icon and label
            html.Div([
                html.Span(icon, style={'fontSize': '24px', 'marginRight': '8px'}),
                html.Span(label, className="text-muted", style={'fontSize': '14px', 'fontWeight': '500'})
            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '8px'}),
            
            # Middle row: Main value and change badge
            html.Div([
                html.Div([
                    html.H2(current_value, className="fw-bold mb-0", style={
                        'fontSize': '24px', 
                        'color': '#2c3e50',
                        'lineHeight': '1.2',
                        'minHeight': '58px',
                        'display': 'flex',
                        'alignItems': 'center',
                        'whiteSpace': 'pre-wrap',
                        'wordBreak': 'break-word'
                    }),
                ], style={'flex': '1'}),
                html.Div([
                    html.Span(
                        f"{arrow} {abs(pct_change):.1f}%" if pct_change != 0 else "",
                        style={
                            'fontSize': '14px',
                            'fontWeight': 'bold',
                            'color': change_color,
                            'backgroundColor': f'{change_color}15' if pct_change != 0 else 'transparent',
                            'padding': '4px 8px' if pct_change != 0 else '0',
                            'borderRadius': '4px',
                            'border': f'1px solid {change_color}40' if pct_change != 0 else 'none',
                            'minHeight': '28px'
                        }
                    )
                ], style={'display': 'flex', 'alignItems': 'flex-start'})
            ], style={'display': 'flex', 'alignItems': 'flex-start', 'justifyContent': 'space-between', 'marginBottom': '12px'}),
            
            # Bottom row: Sparkline (fixed height container)
            html.Div([
                dcc.Graph(
                    figure=sparkline_fig,
                    config={'displayModeBar': False, 'staticPlot': True},
                    style={'height': '60px', 'marginBottom': '8px'}
                ) if trend_values and len(trend_values) > 0 else html.Div(style={'height': '60px', 'marginBottom': '8px'})
            ]),
            
            # Date range text
            html.Small(date_range_text, className="text-muted", style={'fontSize': '11px', 'display': 'block', 'minHeight': '16px'})
        ], style={
            'background': f'linear-gradient(135deg, {gradient_start} 0%, {gradient_end} 100%)',
            'borderRadius': '8px',
            'minHeight': '200px',
            'display': 'flex',
            'flexDirection': 'column'
        })
    ], style={
        'border': 'none',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.05)',
        'transition': 'transform 0.2s, box-shadow 0.2s',
        'height': '100%'
    })
    
    return card

def _create_sales_funnel(df):
    """
    Create sales funnel showing conversion through different stages
    
    Stages: Leads/Orders Placed → In Progress → Delivered → Revenue Generated
    """
    if df is None or df.empty:
        return go.Figure().add_annotation(
            text="No data available for funnel analysis",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color='gray')
        )
    
    # Calculate metrics for each funnel stage
    total_orders = len(df)
    
    # Assuming we have status or delivery information
    # If not available, we'll create estimated stages based on data patterns
    
    # Stage 1: Total Orders Placed (Leads)
    stage1_count = total_orders
    stage1_value = df['Value'].sum() if 'Value' in df.columns else 0
    
    # Stage 2: In Progress (80% of orders typically in progress/processing)
    # This is an estimation - adjust based on actual status field if available
    stage2_count = int(total_orders * 0.80)
    stage2_value = stage1_value * 0.80
    
    # Stage 3: Delivered (60% of orders typically delivered)
    stage3_count = int(total_orders * 0.60)
    stage3_value = stage1_value * 0.60
    
    # Stage 4: Revenue Generated (actual revenue from delivered orders)
    # Using actual Value column for final stage
    stage4_count = stage3_count
    stage4_value = stage1_value  # Full revenue
    
    # Calculate conversion rates
    conv_rate_1_2 = (stage2_count / stage1_count * 100) if stage1_count > 0 else 0
    conv_rate_2_3 = (stage3_count / stage2_count * 100) if stage2_count > 0 else 0
    conv_rate_3_4 = (stage4_count / stage3_count * 100) if stage3_count > 0 else 0
    
    # Create funnel data
    stages = ['📝 Orders Placed', '⏳ In Progress', '✅ Delivered', '💰 Revenue Generated']
    values = [stage1_count, stage2_count, stage3_count, stage4_count]
    
    # Create text with both count and percentage
    total = values[0]
    text_values = [
        f"{values[0]:,} orders (100%)",
        f"{values[1]:,} orders ({values[1]/total*100:.1f}%)",
        f"{values[2]:,} orders ({values[2]/total*100:.1f}%)",
        f"{format_inr(stage4_value)}<br>({values[3]/total*100:.1f}%)"
    ]
    
    # Create funnel chart
    fig = go.Figure(go.Funnel(
        y=stages,
        x=values,
        textposition="inside",
        textinfo="text",
        text=text_values,
        marker=dict(
            color=[COLORS['info'], '#5DADE2', '#85C1E9', COLORS['success']],
            line=dict(width=2, color='white')
        ),
        connector=dict(
            line=dict(color='gray', width=2, dash='dot')
        ),
        opacity=0.9
    ))
    
    # Add conversion rate annotations
    annotations = [
        dict(
            x=0.5, y=0.75,
            text=f"↓ {conv_rate_1_2:.1f}% conversion",
            showarrow=False,
            font=dict(size=10, color=COLORS['dark']),
            xref='paper', yref='paper'
        ),
        dict(
            x=0.5, y=0.5,
            text=f"↓ {conv_rate_2_3:.1f}% conversion",
            showarrow=False,
            font=dict(size=10, color=COLORS['dark']),
            xref='paper', yref='paper'
        ),
        dict(
            x=0.5, y=0.25,
            text=f"↓ {conv_rate_3_4:.1f}% conversion",
            showarrow=False,
            font=dict(size=10, color=COLORS['dark']),
            xref='paper', yref='paper'
        )
    ]
    
    # Apply modern styling
    apply_modern_chart_style(fig, "🎯 Sales Funnel Analysis", height=500)
    fig.update_layout(
        margin=dict(t=60, b=40, l=20, r=20),
        annotations=annotations
    )
    
    return fig

def _create_conversion_timeline(df):
    """
    Create conversion timeline showing rates over time
    
    Tracks: Order-to-Delivery rate, Revenue per Order, Quantity per Order
    """
    if df is None or df.empty:
        return go.Figure().add_annotation(
            text="No data available for conversion timeline",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color='gray')
        )
    
    # Check if date column exists
    if 'Date' not in df.columns:
        return go.Figure().add_annotation(
            text="Date information not available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color='gray')
        )
    
    # Ensure Date column is datetime
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    
    if df.empty:
        return go.Figure().add_annotation(
            text="No valid date data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color='gray')
        )
    
    # Group by date
    daily_data = df.groupby(df['Date'].dt.date).agg({
        'Value': 'sum' if 'Value' in df.columns else 'count',
        'Qty': 'sum' if 'Qty' in df.columns else 'count'
    }).reset_index()
    
    daily_data['Date'] = pd.to_datetime(daily_data['Date'])
    daily_data = daily_data.sort_values('Date')
    
    # Calculate metrics
    daily_data['Order_Count'] = df.groupby(df['Date'].dt.date).size().values
    daily_data['Revenue_per_Order'] = daily_data['Value'] / daily_data['Order_Count']
    daily_data['Qty_per_Order'] = daily_data['Qty'] / daily_data['Order_Count']
    
    # Calculate rolling conversion rate (order fulfillment estimation)
    # Using a 7-day rolling window
    daily_data['Conversion_Rate'] = (
        daily_data['Order_Count'].rolling(window=7, min_periods=1).mean() / 
        daily_data['Order_Count'].rolling(window=7, min_periods=1).max() * 100
    )
    
    # Create figure with secondary y-axis
    fig = go.Figure()
    
    # Add Revenue per Order (primary y-axis)
    fig.add_trace(go.Scatter(
        x=daily_data['Date'],
        y=daily_data['Revenue_per_Order'],
        name='Revenue per Order',
        mode='lines',
        line=dict(color='#2ECC71', width=2),
        fill='tozeroy',
        fillcolor='rgba(46, 204, 113, 0.1)',
        yaxis='y',
        hovertemplate='<b>Revenue per Order</b><br>%{y:,.0f} Rs.<br>%{x|%d-%b-%Y}<extra></extra>'
    ))
    
    # Add Quantity per Order (primary y-axis)
    fig.add_trace(go.Scatter(
        x=daily_data['Date'],
        y=daily_data['Qty_per_Order'],
        name='Quantity per Order',
        mode='lines',
        line=dict(color='#3498DB', width=2),
        yaxis='y',
        hovertemplate='<b>Qty per Order</b><br>%{y:.2f} units<br>%{x|%d-%b-%Y}<extra></extra>'
    ))
    
    # Add Conversion Rate (secondary y-axis)
    fig.add_trace(go.Scatter(
        x=daily_data['Date'],
        y=daily_data['Conversion_Rate'],
        name='Conversion Rate (7-day avg)',
        mode='lines',
        line=dict(color='#E74C3C', width=2, dash='dash'),
        yaxis='y2',
        hovertemplate='<b>Conversion Rate</b><br>%{y:.1f}%<br>%{x|%d-%b-%Y}<extra></extra>'
    ))
    
    # Update layout with dual y-axis
    # Apply modern styling
    apply_modern_chart_style(fig, "📊 Conversion Metrics Timeline", height=500)
    
    fig.update_layout(
        xaxis=dict(
            title="Date",
            rangeslider=dict(visible=True, thickness=0.05),
            type='date'
        ),
        yaxis=dict(
            title="Revenue / Quantity",
            titlefont=dict(color=COLORS['success']),
            tickfont=dict(color=COLORS['success'])
        ),
        yaxis2=dict(
            title="Conversion Rate (%)",
            titlefont=dict(color=COLORS['danger']),
            tickfont=dict(color=COLORS['danger']),
            overlaying='y',
            side='right',
            showgrid=False,
            range=[0, 100]
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='lightgray',
            borderwidth=1
        ),
        margin=dict(t=80, b=100, l=60, r=60),
        hovermode='x unified'
    )
    
    return fig

def _create_activity_heatmap(df, value_col='Value'):
    """
    Create calendar-style heatmap showing revenue/orders by day
    
    Args:
        df: DataFrame with Date column
        value_col: Column name for revenue values
    
    Returns:
        Plotly heatmap figure
    """
    if df is None or df.empty or 'Date' not in df.columns:
        return go.Figure().add_annotation(
            text="No date data available for activity heatmap",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color='gray')
        )
    
    # Ensure Date column is datetime
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    
    if df.empty:
        return go.Figure().add_annotation(
            text="No valid date data",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color='gray')
        )
    
    # Extract date components
    df['DayOfWeek'] = df['Date'].dt.day_name()
    df['WeekOfYear'] = df['Date'].dt.isocalendar().week
    df['DateStr'] = df['Date'].dt.strftime('%Y-%m-%d')
    
    # Aggregate by date
    if value_col and value_col in df.columns:
        daily_agg = df.groupby(['DateStr', 'DayOfWeek', 'WeekOfYear']).agg({
            value_col: 'sum'
        }).reset_index()
        daily_agg['OrderCount'] = df.groupby('DateStr').size().values
        metric_col = value_col
    else:
        daily_agg = df.groupby(['DateStr', 'DayOfWeek', 'WeekOfYear']).size().reset_index(name='OrderCount')
        metric_col = 'OrderCount'
    
    # Create pivot table for heatmap
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Prepare data for heatmap
    weeks = sorted(daily_agg['WeekOfYear'].unique())
    heatmap_data = []
    hover_text = []
    
    for day in day_order:
        day_data = []
        day_hover = []
        for week in weeks:
            week_day_data = daily_agg[(daily_agg['DayOfWeek'] == day) & (daily_agg['WeekOfYear'] == week)]
            if not week_day_data.empty:
                value = week_day_data[metric_col].values[0]
                date_str = week_day_data['DateStr'].values[0]
                order_count = week_day_data['OrderCount'].values[0] if 'OrderCount' in week_day_data.columns else 0
                day_data.append(value)
                day_hover.append(f"Date: {date_str}<br>Revenue: Rs. {value:,.0f}<br>Orders: {order_count}")
            else:
                day_data.append(0)
                day_hover.append(f"Week {week}<br>No data")
        heatmap_data.append(day_data)
        hover_text.append(day_hover)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data,
        x=[f"Week {w}" for w in weeks],
        y=day_order,
        colorscale='Greens',
        text=hover_text,
        hovertemplate='%{text}<extra></extra>',
        colorbar=dict(
            title="Revenue",
            thickness=15,
            len=0.7
        )
    ))
    
    # Apply modern styling
    apply_modern_chart_style(fig, "📅 Activity Heatmap - Day x Week", height=400)
    
    fig.update_layout(
        xaxis=dict(
            title="Week of Year",
            side='bottom',
            tickangle=0
        ),
        yaxis=dict(
            title="Day of Week",
            autorange='reversed'
        ),
        margin=dict(t=60, b=60, l=100, r=60)
    )
    
    return fig

def _create_hourly_heatmap(df, value_col='Value'):
    """
    Create heatmap showing sales by hour of day vs day of week
    
    Args:
        df: DataFrame with Date/Timestamp column
        value_col: Column name for revenue values
    
    Returns:
        Plotly heatmap figure
    """
    if df is None or df.empty:
        return go.Figure().add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color='gray')
        )
    
    # Check for timestamp columns
    timestamp_cols = [col for col in df.columns if 'time' in col.lower() or 'date' in col.lower()]
    
    if not timestamp_cols:
        return go.Figure().add_annotation(
            text="⏰ No timestamp data available<br>Hourly analysis requires time information",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color='gray')
        )
    
    # Use the first timestamp column
    time_col = timestamp_cols[0]
    df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
    df = df.dropna(subset=[time_col])
    
    if df.empty:
        return go.Figure().add_annotation(
            text="No valid timestamp data",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color='gray')
        )
    
    # Extract hour and day of week
    df['Hour'] = df[time_col].dt.hour
    df['DayOfWeek'] = df[time_col].dt.day_name()
    
    # Aggregate by hour and day
    if value_col and value_col in df.columns:
        hourly_agg = df.groupby(['DayOfWeek', 'Hour'])[value_col].sum().reset_index()
        metric_col = value_col
        color_label = "Revenue"
    else:
        hourly_agg = df.groupby(['DayOfWeek', 'Hour']).size().reset_index(name='Count')
        metric_col = 'Count'
        color_label = "Orders"
    
    # Create pivot table
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    hours = list(range(24))
    
    heatmap_data = []
    hover_text = []
    
    for day in day_order:
        day_data = []
        day_hover = []
        for hour in hours:
            hour_data = hourly_agg[(hourly_agg['DayOfWeek'] == day) & (hourly_agg['Hour'] == hour)]
            if not hour_data.empty:
                value = hour_data[metric_col].values[0]
                day_data.append(value)
                if metric_col == value_col:
                    day_hover.append(f"{day}<br>Hour: {hour:02d}:00<br>Revenue: Rs. {value:,.0f}")
                else:
                    day_hover.append(f"{day}<br>Hour: {hour:02d}:00<br>Orders: {int(value)}")
            else:
                day_data.append(0)
                day_hover.append(f"{day}<br>Hour: {hour:02d}:00<br>No activity")
        heatmap_data.append(day_data)
        hover_text.append(day_hover)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data,
        x=[f"{h:02d}:00" for h in hours],
        y=day_order,
        colorscale='Blues',
        text=hover_text,
        hovertemplate='%{text}<extra></extra>',
        colorbar=dict(
            title=color_label,
            thickness=15,
            len=0.7
        )
    ))
    
    # Apply modern styling
    apply_modern_chart_style(fig, "⏰ Hourly Activity Pattern", height=400)
    
    fig.update_layout(
        xaxis=dict(
            title="Hour of Day",
            tickangle=45,
            tickmode='linear',
            tick0=0,
            dtick=2
        ),
        yaxis=dict(
            title="Day of Week",
            autorange='reversed'
        ),
        margin=dict(t=60, b=80, l=100, r=60)
    )
    
    return fig

def _create_day_part_analysis(df, value_col='Value'):
    """
    Create day part analysis showing revenue distribution across time segments
    
    Args:
        df: DataFrame with Date/Timestamp column
        value_col: Column name for revenue values
    
    Returns:
        Plotly figure with day part breakdown
    """
    if df is None or df.empty:
        return go.Figure().add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color='gray')
        )
    
    # Check for timestamp columns
    timestamp_cols = [col for col in df.columns if 'time' in col.lower() or 'date' in col.lower()]
    
    if not timestamp_cols:
        return go.Figure().add_annotation(
            text="⏰ No timestamp data available<br>Day part analysis requires time information",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color='gray')
        )
    
    # Use the first timestamp column
    time_col = timestamp_cols[0]
    df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
    df = df.dropna(subset=[time_col])
    
    if df.empty:
        return go.Figure().add_annotation(
            text="No valid timestamp data",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color='gray')
        )
    
    # Extract hour
    df['Hour'] = df[time_col].dt.hour
    
    # Define day parts
    def get_day_part(hour):
        if 0 <= hour < 6:
            return '🌙 Night (00-06)'
        elif 6 <= hour < 12:
            return '🌅 Morning (06-12)'
        elif 12 <= hour < 18:
            return '☀️ Afternoon (12-18)'
        else:
            return '🌆 Evening (18-24)'
    
    df['DayPart'] = df['Hour'].apply(get_day_part)
    
    # Aggregate by day part
    if value_col and value_col in df.columns:
        day_part_agg = df.groupby('DayPart').agg({
            value_col: 'sum'
        }).reset_index()
        day_part_agg['OrderCount'] = df.groupby('DayPart').size().values
        metric_col = value_col
    else:
        day_part_agg = df.groupby('DayPart').size().reset_index(name='OrderCount')
        metric_col = 'OrderCount'
    
    # Sort by time order
    day_part_order = ['🌙 Night (00-06)', '🌅 Morning (06-12)', '☀️ Afternoon (12-18)', '🌆 Evening (18-24)']
    day_part_agg['DayPart'] = pd.Categorical(day_part_agg['DayPart'], categories=day_part_order, ordered=True)
    day_part_agg = day_part_agg.sort_values('DayPart')
    
    # Calculate percentages
    total = day_part_agg[metric_col].sum()
    day_part_agg['Percentage'] = (day_part_agg[metric_col] / total * 100).round(1)
    
    # Create stacked bar chart with gradient colors
    colors = ['#34495E', '#F39C12', '#E74C3C', '#9B59B6']
    
    fig = go.Figure()
    
    for idx, row in day_part_agg.iterrows():
        fig.add_trace(go.Bar(
            x=[row[metric_col]],
            y=['Revenue Distribution'],
            name=row['DayPart'],
            orientation='h',
            marker=dict(color=colors[idx % len(colors)]),
            text=f"{row['Percentage']:.1f}%",
            textposition='inside',
            textfont=dict(size=14, color='white', weight='bold'),
            hovertemplate=(
                f"<b>{row['DayPart']}</b><br>" +
                f"Revenue: Rs. {row[metric_col]:,.0f}<br>" +
                f"Orders: {row['OrderCount']}<br>" +
                f"Share: {row['Percentage']:.1f}%<br>" +
                "<extra></extra>"
            )
        ))
    
    # Apply modern styling
    apply_modern_chart_style(fig, "🕐 Day Part Analysis", height=400)
    
    fig.update_layout(
        xaxis=dict(title="Revenue (Rs.)"),
        yaxis=dict(showticklabels=False),
        barmode='stack',
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='lightgray',
            borderwidth=1
        ),
        margin=dict(t=60, b=60, l=40, r=150)
    )
    
    return fig

def _create_revenue_comparison_chart(df, value_col, period_view='daily', comparison_type='previous_period'):
    """
    Create advanced revenue comparison chart with period-over-period analysis
    
    Args:
        df: DataFrame with Date and Value columns
        value_col: Column name for revenue values
        period_view: 'daily', 'weekly', or 'monthly'
        comparison_type: 'previous_period', 'last_year', or 'custom'
    
    Returns:
        Plotly figure with main chart and comparison chart
    """
    if df is None or df.empty:
        return go.Figure().add_annotation(
            text="No data available for revenue comparison",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color='gray')
        )
    
    # Check if required columns exist
    if 'Date' not in df.columns or not value_col:
        return go.Figure().add_annotation(
            text="Date or revenue data not available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color='gray')
        )
    
    # Ensure Date column is datetime
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    
    if df.empty:
        return go.Figure().add_annotation(
            text="No valid date data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color='gray')
        )
    
    # Sort by date
    df = df.sort_values('Date')
    
    # Aggregate based on period view
    if period_view == 'daily':
        current_data = df.groupby(df['Date'].dt.date)[value_col].sum().reset_index()
        current_data['Date'] = pd.to_datetime(current_data['Date'])
        period_label = "Daily"
        date_format = '%d-%b'
    elif period_view == 'weekly':
        current_data = df.groupby(df['Date'].dt.to_period('W').dt.start_time)[value_col].sum().reset_index()
        current_data.columns = ['Date', value_col]
        period_label = "Weekly"
        date_format = '%d-%b'
    else:  # monthly
        current_data = df.groupby(df['Date'].dt.to_period('M').dt.start_time)[value_col].sum().reset_index()
        current_data.columns = ['Date', value_col]
        period_label = "Monthly"
        date_format = '%b-%Y'
    
    current_data = current_data.sort_values('Date')
    
    # Calculate comparison period
    if comparison_type == 'previous_period':
        # Previous period of same length
        period_length = (current_data['Date'].max() - current_data['Date'].min()).days
        comparison_start = current_data['Date'].min() - pd.Timedelta(days=period_length + 1)
        comparison_end = current_data['Date'].min() - pd.Timedelta(days=1)
        comparison_label = "Previous Period"
    elif comparison_type == 'last_year':
        # Same period last year
        comparison_start = current_data['Date'].min() - pd.DateOffset(years=1)
        comparison_end = current_data['Date'].max() - pd.DateOffset(years=1)
        comparison_label = "Last Year"
    else:
        # Default to previous period
        period_length = (current_data['Date'].max() - current_data['Date'].min()).days
        comparison_start = current_data['Date'].min() - pd.Timedelta(days=period_length + 1)
        comparison_end = current_data['Date'].min() - pd.Timedelta(days=1)
        comparison_label = "Previous Period"
    
    # Get comparison period data
    comparison_df = df[(df['Date'] >= comparison_start) & (df['Date'] <= comparison_end)].copy()
    
    if not comparison_df.empty:
        # Aggregate comparison data
        if period_view == 'daily':
            comparison_data = comparison_df.groupby(comparison_df['Date'].dt.date)[value_col].sum().reset_index()
            comparison_data['Date'] = pd.to_datetime(comparison_data['Date'])
        elif period_view == 'weekly':
            comparison_data = comparison_df.groupby(comparison_df['Date'].dt.to_period('W').dt.start_time)[value_col].sum().reset_index()
            comparison_data.columns = ['Date', value_col]
        else:  # monthly
            comparison_data = comparison_df.groupby(comparison_df['Date'].dt.to_period('M').dt.start_time)[value_col].sum().reset_index()
            comparison_data.columns = ['Date', value_col]
        
        comparison_data = comparison_data.sort_values('Date')
        
        # Align comparison data with current period (shift dates)
        date_diff = current_data['Date'].min() - comparison_data['Date'].min()
        comparison_data['Aligned_Date'] = comparison_data['Date'] + date_diff
    else:
        comparison_data = pd.DataFrame()
    
    # Calculate statistics
    current_total = current_data[value_col].sum()
    current_avg = current_data[value_col].mean()
    current_peak = current_data[value_col].max()
    peak_date = current_data.loc[current_data[value_col].idxmax(), 'Date']
    
    if not comparison_data.empty:
        comparison_total = comparison_data[value_col].sum()
        change_pct = ((current_total - comparison_total) / comparison_total * 100) if comparison_total > 0 else 0
        change_color = '#2ECC71' if change_pct >= 0 else '#E74C3C'
        change_icon = '↑' if change_pct >= 0 else '↓'
    else:
        change_pct = 0
        comparison_total = 0
        change_color = '#6c757d'
        change_icon = '—'
    
    # Create figure with subplots (main chart + comparison mini chart)
    from plotly.subplots import make_subplots
    
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.75, 0.25],
        vertical_spacing=0.08,
        subplot_titles=(f"{period_label} Revenue Trend", "Period Comparison"),
        specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
    )
    
    # Main chart - Current period
    fig.add_trace(
        go.Scatter(
            x=current_data['Date'],
            y=current_data[value_col],
            name='Current Period',
            mode='lines+markers',
            line=dict(color='#2ECC71', width=3),
            marker=dict(size=6, color='#27AE60', line=dict(width=1, color='white')),
            fill='tozeroy',
            fillcolor='rgba(46, 204, 113, 0.1)',
            hovertemplate='<b>Current</b><br>%{x|' + date_format + '}<br>Rs. %{y:,.0f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Main chart - Comparison period (if available)
    if not comparison_data.empty:
        fig.add_trace(
            go.Scatter(
                x=comparison_data['Aligned_Date'],
                y=comparison_data[value_col],
                name=comparison_label,
                mode='lines',
                line=dict(color='#95A5A6', width=2, dash='dot'),
                opacity=0.6,
                hovertemplate='<b>' + comparison_label + '</b><br>%{x|' + date_format + '}<br>Rs. %{y:,.0f}<extra></extra>'
            ),
            row=1, col=1
        )
    
    # Add peak marker
    fig.add_trace(
        go.Scatter(
            x=[peak_date],
            y=[current_peak],
            mode='markers+text',
            marker=dict(size=12, color='#F39C12', symbol='star', line=dict(width=2, color='white')),
            text=['Peak'],
            textposition='top center',
            textfont=dict(size=10, color='#F39C12', family='Arial Black'),
            showlegend=False,
            hovertemplate='<b>Peak Day</b><br>%{x|' + date_format + '}<br>Rs. %{y:,.0f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Add weekend shading (if daily view)
    if period_view == 'daily':
        for date in current_data['Date']:
            if date.weekday() >= 5:  # Saturday or Sunday
                fig.add_vrect(
                    x0=date - pd.Timedelta(hours=12),
                    x1=date + pd.Timedelta(hours=12),
                    fillcolor='rgba(200, 200, 200, 0.1)',
                    layer='below',
                    line_width=0,
                    row=1, col=1
                )
    
    # Comparison mini chart - Bar comparison
    if not comparison_data.empty:
        comparison_bars = pd.DataFrame({
            'Period': [comparison_label, 'Current Period'],
            'Total': [comparison_total, current_total],
            'Color': ['#95A5A6', change_color]
        })
        
        fig.add_trace(
            go.Bar(
                x=comparison_bars['Period'],
                y=comparison_bars['Total'],
                marker=dict(color=comparison_bars['Color'], opacity=0.8, line=dict(width=1, color='white')),
                text=[f"Rs. {v/1e5:.1f}L" for v in comparison_bars['Total']],
                textposition='outside',
                textfont=dict(size=10, color='black'),
                showlegend=False,
                hovertemplate='<b>%{x}</b><br>Rs. %{y:,.0f}<extra></extra>'
            ),
            row=2, col=1
        )
    
    # Update layout
    fig.update_xaxes(
        title_text="Date",
        showgrid=True,
        gridcolor='rgba(200, 200, 200, 0.2)',
        tickformat=date_format,
        row=1, col=1
    )
    
    fig.update_yaxes(
        title_text="Revenue (Rs.)",
        showgrid=True,
        gridcolor='rgba(200, 200, 200, 0.2)',
        tickformat=".2s",
        row=1, col=1
    )
    
    fig.update_xaxes(
        title_text="",
        showgrid=False,
        row=2, col=1
    )
    
    fig.update_yaxes(
        title_text="Total Revenue",
        showgrid=True,
        gridcolor='rgba(200, 200, 200, 0.2)',
        tickformat=".2s",
        row=2, col=1
    )
    
    # Overall layout
    apply_modern_chart_style(fig, f"📊 {period_label} Revenue Comparison", height=650)
    
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='lightgray',
            borderwidth=1
        ),
        margin=dict(t=80, b=20, l=60, r=40),
        hovermode='x unified',
        annotations=[
            # Change percentage annotation
            dict(
                text=f"{change_icon} {abs(change_pct):.1f}%",
                xref='paper', yref='paper',
                x=0.02, y=0.98,
                showarrow=False,
                font=dict(size=24, color=change_color, family='Inter'),
                bgcolor='rgba(255,255,255,0.9)',
                bordercolor=change_color,
                borderwidth=2,
                borderpad=8
            )
        ]
    )
    
    return fig, {
        'current_total': current_total,
        'current_avg': current_avg,
        'current_peak': current_peak,
        'peak_date': peak_date,
        'change_pct': change_pct,
        'comparison_total': comparison_total
    }

# Data Table Callbacks

# Toggle Data Table Visibility
@app.callback(
    Output("data-table-collapse", "is_open"),
    Input("toggle-data-table", "n_clicks"),
    State("data-table-collapse", "is_open"),
)
def toggle_data_table(n, is_open):
    """Toggle visibility of data table section"""
    if n:
        return not is_open
    return is_open

# Export Selected Rows
@app.callback(
    Output('download-table-data', 'data'),
    Input('export-selected-btn', 'n_clicks'),
    Input('export-all-btn', 'n_clicks'),
    State('sales-data-table', 'selectedRows'),
    State('sales-data-table', 'rowData'),
    prevent_initial_call=True
)
def export_table_data(export_selected_clicks, export_all_clicks, selected_rows, all_rows):
    """Export selected or all rows to CSV"""
    
    if not ctx.triggered:
        return no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    try:
        if button_id == 'export-selected-btn':
            if not selected_rows or len(selected_rows) == 0:
                return no_update
            df_export = pd.DataFrame(selected_rows)
            filename = f"sales_data_selected_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        elif button_id == 'export-all-btn':
            if not all_rows:
                return no_update
            df_export = pd.DataFrame(all_rows)
            filename = f"sales_data_all_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        else:
            return no_update
        
        return dcc.send_data_frame(df_export.to_csv, filename, index=False)
    
    except Exception as e:
        print(f"Error exporting data: {str(e)}")
        return no_update

# Clear Filters
@app.callback(
    Output('sales-data-table', 'filterModel'),
    Input('clear-filters-btn', 'n_clicks'),
    prevent_initial_call=True
)
def clear_table_filters(n_clicks):
    """Clear all table filters"""
    if n_clicks:
        return {}
    return no_update

# Global Search
@app.callback(
    Output('sales-data-table', 'dashGridOptions'),
    Input('table-global-search', 'value'),
    State('sales-data-table', 'dashGridOptions'),
    prevent_initial_call=True
)
def update_global_search(search_value, current_options):
    """Update table with global search filter"""
    if search_value:
        updated_options = current_options.copy()
        updated_options['quickFilterText'] = search_value
        return updated_options
    else:
        updated_options = current_options.copy()
        if 'quickFilterText' in updated_options:
            del updated_options['quickFilterText']
        return updated_options

# Column Visibility Toggle
@app.callback(
    Output('sales-data-table', 'columnDefs'),
    Input('column-visibility-checklist', 'value'),
    State('username-input', 'value'),
    State('password-input', 'value'),
    State('date-range-picker', 'start_date'),
    State('date-range-picker', 'end_date'),
    prevent_initial_call=True
)
def update_column_visibility(visible_columns, username, password, start_date, end_date):
    """Update which columns are visible in the table"""
    
    if not visible_columns:
        return no_update
    
    # Get VALUE_COL from current data
    try:
        start_date_obj = pd.to_datetime(start_date)
        end_date_obj = pd.to_datetime(end_date)
        start_date_str = start_date_obj.strftime("%d-%m-%Y")
        end_date_str = end_date_obj.strftime("%d-%m-%Y")
        
        api_client = APIClient(username=username, password=password)
        response = api_client.get_sales_report(start_date=start_date_str, end_date=end_date_str)
        
        if response.get('success'):
            api_response = response.get('data', {})
            report_data = api_response.get('report_data', [])
            df = pd.DataFrame(report_data)
            
            column_mapping = {
                'SV': 'Value',
                'SQ': 'Qty',
                'comp_nm': 'Dealer Name',
                'category_name': 'Category',
                'state': 'State',
                'city': 'City',
                'meta_keyword': 'Product Name',
                'parent_category': 'Sub Category'
            }
            df = df.rename(columns={old: new for old, new in column_mapping.items() if old in df.columns})
            
            VALUE_COLS = [c for c in df.columns if c.startswith('Value') and c != 'Value']
            VALUE_COL = VALUE_COLS[0] if VALUE_COLS else ('Value' if 'Value' in df.columns else 'Value')
        else:
            VALUE_COL = 'Value'
    except:
        VALUE_COL = 'Value'
    
    # Define all column definitions
    all_columns = [
        {
            'headerName': 'Date',
            'field': 'Date',
            'filter': 'agDateColumnFilter',
            'sortable': True,
            'resizable': True,
            'width': 110,
            'checkboxSelection': True,
            'headerCheckboxSelection': True,
            'hide': 'Date' not in visible_columns
        },
        {
            'headerName': 'Order ID',
            'field': 'Order ID',
            'filter': 'agTextColumnFilter',
            'sortable': True,
            'resizable': True,
            'width': 120,
            'hide': 'Order ID' not in visible_columns
        },
        {
            'headerName': 'Dealer Name',
            'field': 'Dealer Name',
            'filter': 'agTextColumnFilter',
            'sortable': True,
            'resizable': True,
            'width': 200,
            'hide': 'Dealer Name' not in visible_columns
        },
        {
            'headerName': 'City',
            'field': 'City',
            'filter': 'agTextColumnFilter',
            'sortable': True,
            'resizable': True,
            'width': 130,
            'hide': 'City' not in visible_columns
        },
        {
            'headerName': 'State',
            'field': 'State',
            'filter': 'agTextColumnFilter',
            'sortable': True,
            'resizable': True,
            'width': 130,
            'hide': 'State' not in visible_columns
        },
        {
            'headerName': 'Category',
            'field': 'Category',
            'filter': 'agTextColumnFilter',
            'sortable': True,
            'resizable': True,
            'width': 150,
            'hide': 'Category' not in visible_columns
        },
        {
            'headerName': 'Product',
            'field': 'Product Name',
            'filter': 'agTextColumnFilter',
            'sortable': True,
            'resizable': True,
            'width': 250,
            'hide': 'Product Name' not in visible_columns
        },
        {
            'headerName': 'Quantity',
            'field': 'Qty',
            'filter': 'agNumberColumnFilter',
            'sortable': True,
            'resizable': True,
            'width': 100,
            'type': 'numericColumn',
            'valueFormatter': {'function': 'Number(params.value).toLocaleString()'},
            'hide': 'Qty' not in visible_columns
        },
        {
            'headerName': 'Revenue (₹)',
            'field': VALUE_COL,
            'filter': 'agNumberColumnFilter',
            'sortable': True,
            'resizable': True,
            'width': 130,
            'type': 'numericColumn',
            'valueFormatter': {'function': 'd3.format(",.2f")(params.value)'},
            'hide': VALUE_COL not in visible_columns
        },
    ]
    
    return all_columns

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Starting Dash Dashboard...")
    print("="*60)
    print("   URL: http://localhost:8050")
    print("   Press Ctrl+C to stop")
    print("="*60 + "\n")
    app.run(debug=True, port=8050)

# Export server for production (Vercel)
server = app.server
