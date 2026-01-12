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
                    html.H5("🔐 API Login", className="card-title"),
                    
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
                    
                    html.Hr(),
                    
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
            api_client = APIClient(username=username, password=password)
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
        
        # Check if date data is available
        has_date_data = 'Date' in df.columns
        
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
                            dcc.Graph(figure=_create_dealer_pie(df, VALUE_COL, limit=10), config={'displayModeBar': True})
                        ])
                    ])
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=_create_state_pie(df, VALUE_COL), config={'displayModeBar': True})
                        ])
                    ])
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=_create_category_bar(df, VALUE_COL), config={'displayModeBar': True})
                        ])
                    ])
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=_create_city_bar(df, VALUE_COL), config={'displayModeBar': True})
                        ])
                    ])
                ], width=3),
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
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=_create_dealer_comparison(df, VALUE_COL, QTY_COL), config={'displayModeBar': True})
                        ])
                    ])
                ], width=4),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=_create_city_bar(df, VALUE_COL), config={'displayModeBar': True})
                        ])
                    ])
                ], width=4),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=_create_category_sunburst(df, VALUE_COL), config={'displayModeBar': True})
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
    
    # Custom color palette
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9']
    
    fig = px.pie(
        dealer_data,
        values=value_col,
        names='Dealer Name',
        title=f"🏆 Top {limit} Dealers by Revenue",
        color_discrete_sequence=colors[:len(dealer_data)]
    )
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Revenue: Rs. %{value:,.0f}<br>Share: %{percent}<extra></extra>',
        marker=dict(line=dict(color='white', width=2)),
        pull=[0.05 if i == 0 else 0 for i in range(len(dealer_data))]  # Pull out the top slice
    )
    fig.update_layout(
        height=450,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        ),
        font=dict(size=12, family="Arial, sans-serif"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=50, b=100, l=20, r=20)
    )
    return fig

def _create_state_pie(df, value_col):
    """Create state revenue pie chart"""
    if not value_col or 'State' not in df.columns:
        return go.Figure().add_annotation(text="No data")
    
    state_data = df.groupby('State')[value_col].sum().reset_index()
    state_data = state_data.sort_values(value_col, ascending=False).head(10)
    
    # Custom color palette for states
    colors = ['#E74C3C', '#3498DB', '#2ECC71', '#F39C12', '#9B59B6', '#1ABC9C', '#E67E22', '#34495E', '#16A085', '#27AE60']
    
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
        pull=[0.03 if i < 3 else 0 for i in range(len(state_data))]  # Pull out top 3 slices
    )
    fig.update_layout(
        height=450,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        ),
        font=dict(size=12, family="Arial, sans-serif"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=50, b=100, l=20, r=20)
    )
    return fig

def _create_category_bar(df, value_col):
    """Create category revenue bar chart"""
    if not value_col or 'Category' not in df.columns:
        return go.Figure().add_annotation(text="No data")
    
    cat_data = df.groupby('Category')[value_col].sum().reset_index()
    cat_data = cat_data.sort_values(value_col, ascending=True)
    
    # Custom gradient colors
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9']
    
    fig = px.bar(
        cat_data,
        x=value_col,
        y='Category',
        orientation='h',
        title="📂 Revenue by Category",
        color=value_col,
        color_continuous_scale='Blues'
    )
    fig.update_traces(
        text=[f"Rs. {x/1e5:.1f}L" for x in cat_data[value_col]],
        textposition='outside',
        textfont=dict(size=10, color='black'),
        hovertemplate='<b>%{y}</b><br>Revenue: Rs. %{x:,.0f}<extra></extra>',
        marker=dict(
            line=dict(color='white', width=1),
            opacity=0.8
        )
    )
    fig.update_xaxes(
        tickformat=',.0f',
        showgrid=True,
        gridcolor='lightgray',
        gridwidth=0.5
    )
    fig.update_yaxes(
        tickfont=dict(size=11),
        showgrid=False
    )
    fig.update_layout(
        height=450,
        showlegend=False,
        coloraxis_showscale=False,
        font=dict(size=12, family="Arial, sans-serif"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
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
        line=dict(color='#FF6B6B', width=3, dash='dash'),
        fill='tozeroy',
        fillcolor='rgba(255, 107, 107, 0.1)'
    ))
    
    # Add actual revenue line with markers
    fig.add_trace(go.Scatter(
        x=daily_revenue['Date'],
        y=daily_revenue[value_col],
        mode='lines+markers',
        name='Daily Revenue',
        line=dict(color='#2ECC71', width=2),
        marker=dict(size=6, color='#27AE60', line=dict(width=1, color='white'))
    ))
    
    # Update layout
    fig.update_layout(
        title="📈 Revenue Trend Over Time",
        xaxis_title="Date",
        yaxis_title="Revenue (Rs.)",
        height=400,
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
        font=dict(size=12, family="Arial, sans-serif"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=60, b=40, l=60, r=40)
    )
    
    # Format y-axis as Indian currency
    fig.update_yaxes(
        tickformat=".2f",
        tickprefix="Rs. ",
        ticksuffix="",
        tickvals=[1e5, 1e6, 1e7, 1e8, 1e9],
        ticktext=["0.1L", "1L", "10L", "1Cr", "10Cr"],
        showgrid=True,
        gridcolor='lightgray',
        gridwidth=0.5
    )
    
    # Format x-axis
    fig.update_xaxes(
        showgrid=True,
        gridcolor='lightgray',
        gridwidth=0.5,
        tickformat='%d-%b'
    )
    
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
        marker_color='#3498DB',
        opacity=0.8,
        hovertemplate='<b>%{y}</b><br>Revenue: Rs. %{x:,.0f}<extra></extra>'
    ))
    
    # Add quantity bars on secondary y-axis
    fig.add_trace(go.Bar(
        x=dealer_data[qty_col],
        y=dealer_data['Dealer Name'],
        name='Quantity',
        orientation='h',
        marker_color='#E74C3C',
        opacity=0.8,
        xaxis='x2',
        hovertemplate='<b>%{y}</b><br>Quantity: %{x:,.0f}<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        title="🏪 Top 10 Dealers - Revenue vs Quantity",
        xaxis=dict(
            title="Revenue (Rs.)",
            tickformat=".2f",
            tickprefix="Rs. ",
            ticksuffix="",
            tickvals=[1e5, 1e6, 1e7, 1e8, 1e9],
            ticktext=["0.1L", "1L", "10L", "1Cr", "10Cr"],
            showgrid=True,
            gridcolor='lightgray',
            gridwidth=0.5
        ),
        xaxis2=dict(
            title="Quantity",
            overlaying='x',
            side='top',
            showgrid=False
        ),
        yaxis=dict(
            title="Dealer Name",
            tickfont=dict(size=10),
            showgrid=False
        ),
        height=500,
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
        font=dict(size=12, family="Arial, sans-serif"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
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
        color_continuous_scale=['#E8F4F8', '#3498DB']
    )
    
    # Update traces
    fig.update_traces(
        text=text_values,
        textposition='outside',
        textfont=dict(size=9, color='black'),
        hovertemplate='<b>%{x}</b><br>Revenue: Rs. %{y:,.0f}<extra></extra>',
        marker=dict(
            line=dict(color='white', width=1),
            opacity=0.9
        )
    )
    fig.update_layout(
        height=450,
        showlegend=False,
        coloraxis_showscale=False,
        font=dict(size=12, family="Arial, sans-serif"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=50, b=60, l=40, r=40)
    )
    
    # Format y-axis
    fig.update_yaxes(
        tickformat=".2f",
        tickprefix="Rs. ",
        ticksuffix="",
        tickvals=[1e5, 1e6, 1e7, 1e8, 1e9],
        ticktext=["0.1L", "1L", "10L", "1Cr", "10Cr"],
        showgrid=True,
        gridcolor='lightgray',
        gridwidth=0.5
    )
    
    # Format x-axis
    fig.update_xaxes(
        tickangle=45,
        tickfont=dict(size=10),
        showgrid=False
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
        color_continuous_scale=['#FFF5E1', '#FF6B6B', '#E74C3C'],
        title="📊 Category & Sub-Category Breakdown"
    )
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>Revenue: Rs. %{value:,.0f}<br>Parent: %{parent}<extra></extra>',
        textinfo='label+percent entry',
        textfont=dict(size=11)
    )
    fig.update_layout(
        height=550,
        font=dict(size=12, family="Arial, sans-serif"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=60, b=20, l=20, r=20)
    )
    
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
        color_continuous_scale=['#FFF9C4', '#FFC107', '#FF9800']
    )
    
    # Update layout
    fig.update_layout(
        height=400,
        showlegend=False,
        coloraxis_showscale=False,
        font=dict(size=12, family="Arial, sans-serif"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=50, b=40, l=40, r=40)
    )
    
    # Update traces
    fig.update_traces(
        text=[f"Rs. {x/1e5:.1f}L" for x in weekday_data[value_col]],
        textposition='outside',
        textfont=dict(size=9, color='black'),
        hovertemplate='<b>%{x}</b><br>Revenue: Rs. %{y:,.0f}<extra></extra>',
        marker=dict(
            line=dict(color='white', width=1),
            opacity=0.9
        )
    )
    
    # Format y-axis as Lakhs
    fig.update_yaxes(
        tickformat=".2f",
        tickprefix="Rs. ",
        ticksuffix="",
        tickvals=[1e5, 1e6, 1e7, 1e8, 1e9],
        ticktext=["0.1L", "1L", "10L", "1Cr", "10Cr"],
        showgrid=True,
        gridcolor='lightgray',
        gridwidth=0.5
    )
    
    # Format x-axis
    fig.update_xaxes(
        showgrid=False,
        tickfont=dict(size=11)
    )
    
    return fig

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
