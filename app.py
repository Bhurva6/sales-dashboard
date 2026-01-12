"""
Dash-based Orthopedic Implant Analytics Dashboard
Replaces Streamlit with Dash for better state management and reactive updates
"""

import dash
from dash import dcc, html, Input, Output, State, callback, ctx
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from api_client import APIClient
from datetime import datetime, timedelta
import json
import os

# Initialize Dash app with Bootstrap theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

# App title
app.title = "Orthopedic Implant Analytics Dashboard"

# Get current month start and today
today = datetime.now()
month_start = today.replace(day=1)

# Initialize API client
api_client = APIClient()

# Color scheme
COLORS = {
    'primary': '#0066cc',
    'secondary': '#6c757d',
    'success': '#28a745',
    'danger': '#dc3544',
    'warning': '#ffc107',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'dark': '#343a40'
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

# App layout
app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='session-store', storage_type='session'),
    
    # Header
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("📊 Orthopedic Implant Analytics Dashboard", className="mb-0"),
                html.P("Real-time Sales & Analytics - Powered by Dash", className="text-muted small")
            ], className="py-3")
        ], width=12)
    ], className="mb-4 border-bottom"),
    
    # Sidebar + Main Content
    dbc.Row([
        # Sidebar
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("📅 Date Range", className="card-title"),
                    
                    dcc.DatePickerRange(
                        id='date-range-picker',
                        start_date=month_start,
                        end_date=today,
                        display_format='DD-MM-YYYY',
                        className="mb-3",
                        style={'width': '100%'}
                    ),
                    
                    html.Hr(),
                    
                    html.H5("🔧 Controls", className="card-title"),
                    
                    dbc.Checkbox(
                        id='hide-innovative-check',
                        label="Hide 'Innovative Ortho Surgicals'",
                        value=False,
                        className="mb-2"
                    ),
                    
                    dbc.Button(
                        "🔄 Refresh Data",
                        id='refresh-btn',
                        color="info",
                        className="w-100 mb-2",
                        n_clicks=0
                    ),
                    
                    html.Hr(),
                    
                    html.Div([
                        html.P("Data Status:", className="small mb-1 fw-bold"),
                        html.Div(id='data-status', className="alert alert-info py-2 small")
                    ])
                ])
            ], className="sticky-top")
        ], width=3),
        
        # Main Content
        dbc.Col([
            dcc.Loading(id='main-loading', children=[
                html.Div(id='main-content')
            ], type='default', fullscreen=False)
        ], width=9)
    ], className="g-3"),
    
], fluid=True, className="py-4")

# Main content callback
@app.callback(
    Output('main-content', 'children'),
    Output('data-status', 'children'),
    Input('date-range-picker', 'start_date'),
    Input('date-range-picker', 'end_date'),
    Input('refresh-btn', 'n_clicks'),
    Input('hide-innovative-check', 'value'),
    prevent_initial_call=False
)
def update_dashboard(start_date, end_date, refresh_clicks, hide_innovative):
    """Update entire dashboard when dates change or refresh is clicked"""
    
    if not start_date or not end_date:
        return dbc.Alert("Please select date range", color="warning"), "No date range"
    
    try:
        # Convert dates to DD-MM-YYYY format
        start_date_obj = pd.to_datetime(start_date)
        end_date_obj = pd.to_datetime(end_date)
        start_date_str = start_date_obj.strftime("%d-%m-%Y")
        end_date_str = end_date_obj.strftime("%d-%m-%Y")
        
        print(f"\n📊 DASH UPDATE TRIGGERED")
        print(f"   Range: {start_date_str} to {end_date_str}")
        print(f"   Hide Innovative: {hide_innovative}")
        print(f"   Refresh clicks: {refresh_clicks}")
        
        # Fetch data from API
        print("   Fetching from API...")
        try:
            response = api_client.get_sales_report(
                start_date=start_date_str,
                end_date=end_date_str
            )
            
            if not response.get('success'):
                status_text = f"❌ API Error: {response.get('message', 'Unknown error')} | {datetime.now().strftime('%H:%M:%S')}"
                return dbc.Alert(f"Failed to fetch data: {response.get('message')}", color="danger"), status_text
            
            # Extract data from response
            api_response = response.get('data', {})
            report_data = api_response.get('report_data', [])
            
            if not report_data:
                status_text = f"❌ No data | {datetime.now().strftime('%H:%M:%S')}"
                return dbc.Alert("No data available for this date range", color="warning"), status_text
            
            # Convert to DataFrame
            df = pd.DataFrame(report_data)
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            status_text = f"❌ Error: {str(e)} | {datetime.now().strftime('%H:%M:%S')}"
            return dbc.Alert(f"Error fetching data: {str(e)}", color="danger"), status_text
        
        if df is None or df.empty:
            status_text = f"❌ No data | {datetime.now().strftime('%H:%M:%S')}"
            return dbc.Alert("No data available for this date range", color="warning"), status_text
        
        print(f"   ✅ Data fetched: {len(df)} rows")
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
            'id': 'Order ID'
        }
        
        # Rename columns that exist in the dataframe
        rename_dict = {old: new for old, new in column_mapping.items() if old in df.columns}
        if rename_dict:
            df = df.rename(columns=rename_dict)
            print(f"   Column mapping applied: {rename_dict}")
        
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
        
        # Most sold item
        if QTY_COL and QTY_COL in df.columns:
            prod_cols = ['Product Name', 'Item Name', 'Sub Category']
            prod_col = next((c for c in prod_cols if c in df.columns), None)
            most_sold = df.groupby(prod_col)[QTY_COL].sum().idxmax() if prod_col else "N/A"
        else:
            most_sold = "N/A"
        
        # Top locations
        most_state = df['State'].value_counts().idxmax() if 'State' in df.columns else "N/A"
        state_count = df['State'].value_counts().max() if 'State' in df.columns else 0
        
        most_city = df['City'].value_counts().idxmax() if 'City' in df.columns else "N/A"
        city_count = df['City'].value_counts().max() if 'City' in df.columns else 0
        
        most_dealer = df['Dealer Name'].value_counts().idxmax() if 'Dealer Name' in df.columns else "N/A"
        dealer_count = df['Dealer Name'].value_counts().max() if 'Dealer Name' in df.columns else 0
        
        category_count = df['Category'].nunique() if 'Category' in df.columns else 0
        
        # Build dashboard content
        metrics_content = html.Div([
            # First row of metrics
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("💰 Revenue", className="text-muted mb-2"),
                            html.H2(format_inr(revenue), className="text-primary fw-bold"),
                            html.Small(f"{start_date_str} → {end_date_str}", className="text-muted")
                        ])
                    ])
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("📦 Total Qty", className="text-muted mb-2"),
                            html.H2(format_qty(quantity), className="text-success fw-bold"),
                            html.Small(f"{start_date_str} → {end_date_str}", className="text-muted")
                        ])
                    ])
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("🏆 Most Sold", className="text-muted mb-2"),
                            html.H5(most_sold[:18], className="text-info fw-bold"),
                            html.Small("Top item by quantity", className="text-muted")
                        ])
                    ])
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("📊 Orders", className="text-muted mb-2"),
                            html.H2(f"{total_orders:,}", className="text-warning fw-bold"),
                            html.Small(f"{start_date_str} → {end_date_str}", className="text-muted")
                        ])
                    ])
                ], width=3),
            ], className="mb-4 g-2"),
            
            # Second row of metrics
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("🗺️ Top State", className="text-muted mb-2"),
                            html.H3(most_state, className="text-primary fw-bold"),
                            html.Small(f"{state_count} orders", className="text-muted")
                        ])
                    ])
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("🏙️ Top City", className="text-muted mb-2"),
                            html.H3(most_city, className="text-success fw-bold"),
                            html.Small(f"{city_count} orders", className="text-muted")
                        ])
                    ])
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("🤝 Top Dealer", className="text-muted mb-2"),
                            html.H4(most_dealer[:14], className="text-info fw-bold"),
                            html.Small(f"{dealer_count} orders", className="text-muted")
                        ])
                    ])
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("📂 Categories", className="text-muted mb-2"),
                            html.H2(f"{category_count}", className="text-warning fw-bold"),
                            html.Small("Unique categories", className="text-muted")
                        ])
                    ])
                ], width=3),
            ], className="mb-4 g-2"),
            
            html.Hr(className="my-4"),
            
            # Charts
            html.H4("📈 Analytics", className="mb-4 fw-bold"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=_create_dealer_pie(df, VALUE_COL, limit=10))
                        ])
                    ])
                ], width=4),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=_create_state_pie(df, VALUE_COL))
                        ])
                    ])
                ], width=4),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=_create_category_bar(df, VALUE_COL))
                        ])
                    ])
                ], width=4),
            ], className="g-2 mb-4"),
        ])
        
        # Status text
        status_text = f"✅ {len(df):,} records | Last updated: {datetime.now().strftime('%H:%M:%S')}"
        
        return metrics_content, status_text
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        status_text = f"❌ Error | {datetime.now().strftime('%H:%M:%S')}"
        return dbc.Alert(f"Error: {str(e)}", color="danger"), status_text

# Chart creation functions
def _create_dealer_pie(df, value_col, limit=10):
    """Create dealer revenue pie chart"""
    if not value_col or 'Dealer Name' not in df.columns:
        return go.Figure().add_annotation(text="No data")
    
    dealer_data = df.groupby('Dealer Name')[value_col].sum().reset_index()
    dealer_data = dealer_data.sort_values(value_col, ascending=False).head(limit)
    
    fig = px.pie(
        dealer_data,
        values=value_col,
        names='Dealer Name',
        title=f"Top {limit} Dealers by Revenue"
    )
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Rs. %{value:,.0f}<br>%{percent}<extra></extra>'
    )
    fig.update_layout(height=400, showlegend=False)
    return fig

def _create_state_pie(df, value_col):
    """Create state revenue pie chart"""
    if not value_col or 'State' not in df.columns:
        return go.Figure().add_annotation(text="No data")
    
    state_data = df.groupby('State')[value_col].sum().reset_index()
    state_data = state_data.sort_values(value_col, ascending=False).head(10)
    
    fig = px.pie(
        state_data,
        values=value_col,
        names='State',
        title="Top 10 States by Revenue"
    )
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Rs. %{value:,.0f}<br>%{percent}<extra></extra>'
    )
    fig.update_layout(height=400, showlegend=False)
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
        title="Revenue by Category",
        labels={value_col: 'Revenue'}
    )
    fig.update_traces(
        text=[f"Rs. {x/1e5:.2f}L" for x in cat_data[value_col]],
        textposition='outside'
    )
    fig.update_xaxes(tickformat=',.0f')
    fig.update_layout(height=400, showlegend=False)
    return fig

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Starting Dash Dashboard...")
    print("="*60)
    print("   URL: http://localhost:8050")
    print("   Press Ctrl+C to stop")
    print("="*60 + "\n")
    app.run_server(debug=True, port=8050)

# Export server for production (Vercel)
server = app.server
