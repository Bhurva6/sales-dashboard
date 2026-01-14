# 📊 Enhanced Metric Cards - Magenta Style

## Overview

The dashboard now features **enhanced metric cards** with Magenta-style visual design, including:
- **Sparkline charts** showing 30-day trends
- **Period-over-period comparison** with color-coded change indicators
- **Gradient backgrounds** matching metric themes
- **Clean, modern layout** with consistent styling

## Features

### 1. Visual Components

Each enhanced metric card includes:

```
┌─────────────────────────────────────────┐
│ 💰 Revenue                      Card    │
│                                         │
│ Rs. 45.2L          ↑ 15.3%             │  ← Main value + Change badge
│                                         │
│     Sparkline Chart (30 days)          │  ← Mini trend chart
│  ─────────╱╲─────╱────────             │
│                                         │
│ 01-Jan → 31-Jan                        │  ← Date range
└─────────────────────────────────────────┘
```

### 2. Sparkline Charts

**Function**: `_create_sparkline(values, color)`

Creates a 60px-high mini chart with:
- **No axes or grid** - Clean, minimal design
- **Transparent background** - Blends with card
- **Area fill** - Light shading under the line
- **Line chart** - Shows trend over time
- **Hover disabled** - Decorative only

**Color Coding**:
- Revenue: Green (`#2ECC71`)
- Quantity: Blue (`#3498DB`)
- Orders: Red (`#E74C3C`)
- State: Purple (`#9B59B6`)
- City: Teal (`#1ABC9C`)
- Dealer: Orange (`#E67E22`)
- Categories: Dark Gray (`#34495E`)

### 3. Change Indicators

**Percentage Badge**:
```
↑ 15.3%   ← Green background, positive change
↓ 8.2%    ← Red background, negative change
→ 0.0%    ← Gray background, no change
```

**Colors**:
- **Positive**: Green (`#28a745`) - Growth from previous period
- **Negative**: Red (`#dc3545`) - Decline from previous period
- **Neutral**: Gray (`#6c757d`) - No change or no previous data

### 4. Gradient Backgrounds

Each metric card has a subtle gradient matching its theme:

```css
background: linear-gradient(135deg, 
    rgba(46, 204, 113, 0.1) 0%,    /* Light theme color */
    rgba(46, 204, 113, 0.02) 100%  /* Very light theme color */
)
```

**Gradient Colors by Metric**:
- **Revenue**: Green gradient (`rgba(46, 204, 113, ...)`)
- **Quantity**: Blue gradient (`rgba(52, 152, 219, ...)`)
- **Orders**: Red gradient (`rgba(231, 76, 60, ...)`)
- **State**: Purple gradient (`rgba(155, 89, 182, ...)`)
- **City**: Teal gradient (`rgba(26, 188, 156, ...)`)
- **Dealer**: Orange gradient (`rgba(230, 126, 34, ...)`)
- **Categories**: Dark gradient (`rgba(52, 73, 94, ...)`)

## Implementation Details

### Core Functions

#### 1. `_create_sparkline(values, color='#2ECC71')`

**Purpose**: Generate mini trend chart for metric cards

**Parameters**:
- `values`: List of numeric values (e.g., last 30 days)
- `color`: Hex color code for the line

**Returns**: Plotly `go.Figure` object

**Example**:
```python
sparkline = _create_sparkline([100, 120, 115, 140, 135], '#2ECC71')
```

**Features**:
- Height: 60px (fixed)
- Margins: 0px (all sides)
- Axes: Hidden
- Grid: Hidden
- Area fill: Light version of line color
- Hover: Disabled

#### 2. `_create_enhanced_metric_card(...)`

**Purpose**: Create complete metric card with all visual elements

**Parameters**:
- `icon`: Emoji or icon (e.g., "💰")
- `label`: Metric name (e.g., "Revenue")
- `current_value`: Formatted current value (e.g., "Rs. 45.2L")
- `previous_value`: Numeric previous period value
- `trend_values`: List of daily values for sparkline
- `color`: Theme color hex code
- `gradient_start`: Start color for gradient
- `gradient_end`: End color for gradient
- `date_range_text`: Date range description

**Returns**: `dbc.Card` component

**Example**:
```python
card = _create_enhanced_metric_card(
    icon="💰",
    label="Revenue",
    current_value="Rs. 45.2L",
    previous_value=39200000,
    trend_values=[100000, 120000, 115000, ...],
    color='#2ECC71',
    gradient_start='rgba(46, 204, 113, 0.1)',
    gradient_end='rgba(46, 204, 113, 0.02)',
    date_range_text="01-Jan → 31-Jan"
)
```

### Data Calculation

#### Previous Period Calculation

```python
# Calculate period duration
start_date_obj = pd.to_datetime(start_date)
end_date_obj = pd.to_datetime(end_date)
period_duration = (end_date_obj - start_date_obj).days

# Calculate previous period dates
prev_start_date = start_date_obj - pd.Timedelta(days=period_duration + 1)
prev_end_date = start_date_obj - pd.Timedelta(days=1)

# Fetch previous period data
prev_response = api_client.get_sales_report(
    start_date=prev_start_date.strftime("%d-%m-%Y"),
    end_date=prev_end_date.strftime("%d-%m-%Y")
)
```

**Example**:
- **Current Period**: Jan 1 - Jan 31 (31 days)
- **Previous Period**: Dec 1 - Dec 31 (31 days)

#### Trend Data Calculation

```python
# Get last 30 days of daily data
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df_with_date = df.dropna(subset=['Date'])
    
    # Group by date and aggregate
    daily_data = df_with_date.groupby(df_with_date['Date'].dt.date).agg({
        'Value': 'sum',
        'Qty': 'sum'
    }).reset_index()
    
    daily_data['orders'] = df_with_date.groupby(
        df_with_date['Date'].dt.date
    ).size().values
    
    # Take last 30 days
    daily_data = daily_data.tail(30)
    
    revenue_trend = daily_data['Value'].tolist()
    quantity_trend = daily_data['Qty'].tolist()
    orders_trend = daily_data['orders'].tolist()
```

#### Percentage Change Calculation

```python
# Extract numeric value from formatted string
current_numeric = float(
    str(current_value)
    .replace('Rs. ', '')
    .replace('L', '')
    .replace('K', '')
    .replace(',', '')
    .replace('\n', ' ')
    .split()[0]
)

# Adjust for K/L suffixes
if 'L' in str(current_value):
    current_numeric *= 100000
elif 'K' in str(current_value):
    current_numeric *= 1000

# Calculate percentage change
pct_change = ((current_numeric - previous_value) / previous_value) * 100
```

## Card Layout Structure

### HTML Structure

```html
<div class="card">
  <div class="card-body" style="background: linear-gradient(...)">
    <!-- Top Row: Icon + Label -->
    <div style="display: flex; align-items: center">
      <span style="font-size: 24px">💰</span>
      <span class="text-muted" style="font-size: 14px">Revenue</span>
    </div>
    
    <!-- Middle Row: Value + Change Badge -->
    <div style="display: flex; justify-content: space-between">
      <div>
        <h2 class="fw-bold">Rs. 45.2L</h2>
      </div>
      <div>
        <span style="color: #28a745; background: #28a74515">
          ↑ 15.3%
        </span>
      </div>
    </div>
    
    <!-- Bottom Row: Sparkline Chart -->
    <dcc.Graph figure={sparkline} style="height: 60px" />
    
    <!-- Date Range Text -->
    <small class="text-muted">01-Jan → 31-Jan</small>
  </div>
</div>
```

### CSS Styling

**Card Container**:
```css
border: none;
box-shadow: 0 2px 4px rgba(0,0,0,0.05);
transition: transform 0.2s, box-shadow 0.2s;
```

**Card Body**:
```css
background: linear-gradient(135deg, [gradient_start] 0%, [gradient_end] 100%);
border-radius: 8px;
```

**Change Badge**:
```css
font-size: 14px;
font-weight: bold;
color: [change_color];
background-color: [change_color]15;  /* 15 = opacity hex */
padding: 4px 8px;
border-radius: 4px;
border: 1px solid [change_color]40;  /* 40 = opacity hex */
```

## Metrics Enhanced

### 1. Revenue Card
- **Icon**: 💰
- **Color**: Green (`#2ECC71`)
- **Trend**: Daily revenue sum
- **Comparison**: Previous period total revenue

### 2. Total Quantity Card
- **Icon**: 📦
- **Color**: Blue (`#3498DB`)
- **Trend**: Daily quantity sum
- **Comparison**: Previous period total quantity

### 3. Orders Card
- **Icon**: 📊
- **Color**: Red (`#E74C3C`)
- **Trend**: Daily order count
- **Comparison**: Previous period order count

### 4. Top State Card
- **Icon**: 🗺️
- **Color**: Purple (`#9B59B6`)
- **Trend**: Daily state order counts
- **Comparison**: Previous period state orders

### 5. Top City Card
- **Icon**: 🏙️
- **Color**: Teal (`#1ABC9C`)
- **Trend**: Daily city order counts
- **Comparison**: Previous period city orders

### 6. Top Dealer Card
- **Icon**: 🤝
- **Color**: Orange (`#E67E22`)
- **Trend**: Daily dealer order counts
- **Comparison**: Previous period dealer orders

### 7. Categories Card
- **Icon**: 📂
- **Color**: Dark Gray (`#34495E`)
- **Trend**: Daily unique category counts
- **Comparison**: Previous period category count

### 8. Most Sold Item Card (Static)
- **Icon**: 🏆
- **Color**: Gold gradient
- **Special**: No sparkline, just displays top product name

## Usage Examples

### Basic Usage

The enhanced metric cards are automatically created in the main dashboard callback:

```python
@app.callback(
    Output('main-content', 'children'),
    ...
)
def update_dashboard(...):
    # ... fetch data ...
    
    # Create enhanced metric card
    revenue_card = _create_enhanced_metric_card(
        icon="💰",
        label="Revenue",
        current_value=format_inr(revenue),
        previous_value=prev_revenue,
        trend_values=revenue_trend,
        color='#2ECC71',
        gradient_start='rgba(46, 204, 113, 0.1)',
        gradient_end='rgba(46, 204, 113, 0.02)',
        date_range_text=f"{start_date_str} → {end_date_str}"
    )
    
    return html.Div([
        dbc.Row([
            dbc.Col(revenue_card, width=3),
            # ... more cards ...
        ])
    ])
```

### Custom Sparkline

To create a standalone sparkline:

```python
# Sample data: last 30 days of revenue
trend_data = [
    1000000, 1100000, 1050000, 1200000, 1150000,
    1300000, 1250000, 1400000, 1350000, 1500000,
    # ... 30 values total
]

# Create sparkline
fig = _create_sparkline(trend_data, color='#2ECC71')

# Use in layout
dcc.Graph(
    figure=fig,
    config={'displayModeBar': False, 'staticPlot': True},
    style={'height': '60px'}
)
```

## Visual Examples

### Positive Growth Scenario

```
┌─────────────────────────────────────────┐
│ 💰 Revenue                              │
│                                         │
│ Rs. 52.8L          ↑ 22.5%             │
│                                         │
│     ╱────────╱───────╱────────          │
│  ──         ╱               ──          │
│                                         │
│ 01-Jan → 31-Jan                        │
└─────────────────────────────────────────┘
```

### Negative Decline Scenario

```
┌─────────────────────────────────────────┐
│ 📦 Total Quantity                       │
│                                         │
│ 8.2K               ↓ 12.3%             │
│                                         │
│  ────╲                                  │
│       ╲─────╲──────╲──────             │
│                                         │
│ 01-Jan → 31-Jan                        │
└─────────────────────────────────────────┘
```

### No Previous Data Scenario

```
┌─────────────────────────────────────────┐
│ 📊 Orders                               │
│                                         │
│ 1,245              → 0.0%              │
│                                         │
│     ─────╱╲─────╱────────╱─            │
│  ──                                     │
│                                         │
│ 01-Jan → 31-Jan                        │
└─────────────────────────────────────────┘
```

## Responsive Behavior

### Desktop (>1200px)
- 4 cards per row
- Full sparkline visibility
- Large text and badges

### Tablet (768px - 1200px)
- 2 cards per row
- Full sparkline visibility
- Medium text and badges

### Mobile (<768px)
- 1 card per row
- Stacked layout
- Sparklines may be hidden on very small screens

## Performance Considerations

### Data Fetching
- **Previous period data** fetched separately (1 additional API call)
- **Trend data** calculated from current dataset (no extra API calls)
- **Caching**: Consider implementing caching for previous period data

### Rendering
- **Sparklines** use static plot mode (no interactive overhead)
- **DisplayModeBar** disabled (faster rendering)
- **Hover** disabled (no event listeners)

### Optimization Tips
1. **Limit trend data** to 30 days maximum
2. **Use daily aggregation** instead of hourly
3. **Disable animations** on sparklines
4. **Cache previous period** results

## Troubleshooting

### Issue: Sparkline not showing

**Solution**: Check if `trend_values` has data:
```python
if len(trend_values) == 0:
    print("No trend data available")
```

### Issue: Percentage change incorrect

**Solution**: Verify numeric extraction:
```python
print(f"Current: {current_value}")
print(f"Previous: {previous_value}")
print(f"Change: {pct_change}%")
```

### Issue: Previous period data missing

**Solution**: Check API response:
```python
if prev_response.get('success'):
    print(f"Previous data: {len(prev_df)} rows")
else:
    print(f"API Error: {prev_response.get('message')}")
```

### Issue: Gradient not visible

**Solution**: Check opacity values (should be very light):
```python
gradient_start='rgba(46, 204, 113, 0.1)'   # 10% opacity
gradient_end='rgba(46, 204, 113, 0.02)'     # 2% opacity
```

## Color Reference

### Theme Colors

| Metric | Color Name | Hex Code | RGB |
|--------|-----------|----------|-----|
| Revenue | Green | `#2ECC71` | rgb(46, 204, 113) |
| Quantity | Blue | `#3498DB` | rgb(52, 152, 219) |
| Orders | Red | `#E74C3C` | rgb(231, 76, 60) |
| State | Purple | `#9B59B6` | rgb(155, 89, 182) |
| City | Teal | `#1ABC9C` | rgb(26, 188, 156) |
| Dealer | Orange | `#E67E22` | rgb(230, 126, 34) |
| Categories | Dark Gray | `#34495E` | rgb(52, 73, 94) |

### Change Indicator Colors

| Status | Color Name | Hex Code | Usage |
|--------|-----------|----------|-------|
| Positive | Success Green | `#28a745` | Growth/increase |
| Negative | Danger Red | `#dc3545` | Decline/decrease |
| Neutral | Secondary Gray | `#6c757d` | No change |

## Summary

✅ **8 enhanced metric cards** with Magenta-style design
✅ **Sparkline charts** showing 30-day trends
✅ **Period-over-period comparison** with color-coded badges
✅ **Gradient backgrounds** matching metric themes
✅ **Automatic calculation** of trends and changes
✅ **Responsive layout** for all screen sizes
✅ **Clean, modern UI** with consistent styling

The enhanced metric cards provide a professional, data-rich overview that helps users quickly understand:
- Current performance
- Trends over time
- Comparison to previous period
- Visual indicators of growth or decline
