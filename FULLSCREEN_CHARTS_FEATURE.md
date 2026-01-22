# Fullscreen Charts Feature

## Overview
Added a fullscreen button to all major charts in the dashboard. Users can now click a button in the top-right corner of any chart to view it in a large modal popup.

## Features

### 1. Fullscreen Button
- **Location**: Top-right corner of each chart
- **Icon**: Bootstrap Icons fullscreen icon (`bi-arrows-fullscreen`)
- **Styling**: 
  - Semi-transparent by default (opacity: 0.7)
  - Becomes fully visible on hover
  - Smooth scale animation on hover and click
  - Blue accent color on hover (#6366f1)

### 2. Modal Popup
- **Size**: Extra large (95% of viewport width)
- **Content**: Chart displayed at larger size (75vh height)
- **Header**: Gradient background (purple to violet) with chart title
- **Close**: Standard modal close button (X)

### 3. Charts with Fullscreen Support

The following charts now have fullscreen capability:

#### Main Analytics Section
- **Geographic Map** - Interactive India map showing sales distribution
- **Top Dealers by Revenue** - Pie chart
- **Revenue by State** - Pie chart
- **Revenue by Category** - Bar chart
- **Top Cities by Revenue** - Bar chart
- **Revenue Trend Over Time** - Line chart (if date data available)
- **Revenue by Day of Week** - Bar chart (if date data available)

#### Comparison Section
- **Dealer Comparison** - Revenue vs Quantity bar chart
- **Cities by Revenue** - Bar chart
- **Category & Sub-Category Breakdown** - Sunburst chart

#### Activity Patterns Section (if date data available)
- **Activity Heatmap** - Day/hour heatmap
- **Hourly Activity Pattern** - Hourly distribution
- **Sales by Time of Day** - Time period analysis

#### Funnel Analysis Section
- **Sales Funnel** - Conversion funnel chart
- **Conversion Timeline** - Timeline chart (if date data available)

## Implementation Details

### Helper Function
```python
def create_chart_with_fullscreen(chart_component, chart_id, chart_title="Chart"):
    """
    Wrap a chart component with a fullscreen button
    
    Args:
        chart_component: The dcc.Graph component
        chart_id: Unique identifier for the chart
        chart_title: Title to display in fullscreen modal
    """
```

### Components Added
1. **Modal Component** - Added to `app.layout` for displaying fullscreen charts
2. **Store Component** - `fullscreen-chart-store` to manage chart state
3. **Callback** - Python callback to handle button clicks and open modal
4. **Clientside Callback** - JavaScript callback to clone and resize charts

### CSS Styling
Added to `assets/custom.css`:
- `.fullscreen-chart-btn` - Button styling with hover effects
- `#fullscreen-chart-modal` - Modal styling with gradient header
- Smooth transitions and animations

## User Experience

### Opening Fullscreen View
1. Hover over any chart
2. Click the fullscreen icon button in the top-right corner
3. Chart opens in a large modal with proper title
4. Chart automatically resizes to fill the modal space

### Closing Fullscreen View
1. Click the X button in the modal header, or
2. Click outside the modal, or
3. Press ESC key

## Technical Notes

### Auto-resize
The clientside callback automatically triggers Plotly's resize function when the chart is displayed in the modal, ensuring the chart properly fills the available space.

### Chart Cloning
Charts are cloned from their original location to the modal using JavaScript DOM manipulation, preserving all interactivity and data.

### Performance
- Minimal overhead as fullscreen functionality only activates on user interaction
- Efficient DOM cloning prevents duplicate data storage
- Smooth CSS transitions for professional feel

## Browser Compatibility
- Works on all modern browsers (Chrome, Firefox, Safari, Edge)
- Responsive on desktop and tablet devices
- Bootstrap Icons CDN ensures icon availability

## Future Enhancements
Possible improvements:
- Add download button in fullscreen mode
- Add print functionality
- Support for comparing multiple charts side-by-side
- Fullscreen slideshow mode for presentations
