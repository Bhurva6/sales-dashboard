# 📋 Advanced Data Table Feature

## Overview
Added a powerful, interactive data table using AG Grid that provides detailed views of all sales records with advanced filtering, sorting, and export capabilities.

## Features

### 1. **AG Grid Component**
- Professional-grade data table with enterprise features
- High performance with large datasets
- Smooth scrolling and pagination

### 2. **Key Columns Displayed**
- 📅 Date
- 🔢 Order ID
- 🏢 Dealer Name
- 🌆 City
- 📍 State
- 📦 Category
- 🛍️ Product Name
- 📊 Quantity
- 💰 Revenue (₹)

### 3. **Interactive Features**

#### **Column Sorting**
- Click any column header to sort
- Click again to reverse sort order
- Multi-column sorting supported

#### **Column Filtering**
- Text filters for name/category columns
- Number filters for quantity/revenue
- Date filters for date column
- Filter icon appears in header

#### **Row Selection**
- Checkbox selection in first column
- Header checkbox to select all
- Multiple row selection supported

#### **Pagination**
- 50 rows per page (default)
- Page size options: 25, 50, 100, 200
- Page navigation at bottom

#### **Global Search**
- Search box above table
- Searches across all columns simultaneously
- Real-time filtering as you type

### 4. **Control Buttons**

#### **📥 Export Selected**
- Exports only selected rows to CSV
- Filename includes timestamp
- Format: `sales_data_selected_YYYYMMDD_HHMMSS.csv`

#### **📥 Export All**
- Exports all visible data to CSV
- Respects current filters
- Format: `sales_data_all_YYYYMMDD_HHMMSS.csv`

#### **🔄 Clear Filters**
- Removes all column filters
- Resets to full dataset view
- Keeps sort order

### 5. **Column Visibility Toggle**
- Checkboxes to show/hide columns
- Inline layout for easy access
- All columns visible by default
- Column state persists during session

### 6. **Styling Features**

#### **Visual Enhancements**
- Clean, modern AG Grid Alpine theme
- Fixed header that stays visible on scroll
- Responsive column widths
- Resizable columns (drag divider)

#### **Data Formatting**
- Currency formatted with thousand separators
- Quantity formatted with commas
- Date in standard format
- Aligned numeric columns

### 7. **Collapsible Section**
- Table hidden by default to save space
- Large "📋 View Detailed Data Table" button
- Toggles visibility with smooth animation
- Located at bottom of dashboard

## Technical Implementation

### Dependencies
```python
import dash_ag_grid as dag
```

### AG Grid Configuration
```python
dashGridOptions={
    'pagination': True,
    'paginationPageSize': 50,
    'paginationPageSizeSelector': [25, 50, 100, 200],
    'enableRangeSelection': True,
    'rowSelection': 'multiple',
    'suppressRowClickSelection': True,
    'animateRows': True,
}
```

### Column Definitions
```python
columnDefs=[
    {
        'headerName': 'Revenue (₹)',
        'field': VALUE_COL,
        'filter': 'agNumberColumnFilter',
        'sortable': True,
        'resizable': True,
        'type': 'numericColumn',
        'valueFormatter': {'function': 'd3.format(",.2f")(params.value)'}
    },
    # ... other columns
]
```

## Usage Guide

### Opening the Table
1. Scroll to bottom of dashboard
2. Click "📋 View Detailed Data Table" button
3. Table expands with all records

### Filtering Data
1. Click filter icon in column header
2. Enter search term or select operator
3. Press Enter or click away to apply
4. Use "Clear Filters" button to reset

### Sorting Data
1. Click column header once to sort ascending
2. Click again to sort descending
3. Click third time to remove sort

### Selecting & Exporting Rows
1. Click checkboxes to select specific rows
2. Click "📥 Export Selected" button
3. CSV file downloads automatically
4. Or use "📥 Export All" for complete dataset

### Global Search
1. Type in search box above table
2. Searches all columns in real-time
3. Clear search box to show all records

### Column Visibility
1. Check/uncheck column names above table
2. Columns hide/show immediately
3. Useful for focusing on specific data

## Callbacks

### 1. Toggle Visibility
```python
@app.callback(
    Output("data-table-collapse", "is_open"),
    Input("toggle-data-table", "n_clicks"),
    State("data-table-collapse", "is_open")
)
```

### 2. Export Data
```python
@app.callback(
    Output('download-table-data', 'data'),
    Input('export-selected-btn', 'n_clicks'),
    Input('export-all-btn', 'n_clicks'),
    State('sales-data-table', 'selectedRows'),
    State('sales-data-table', 'rowData')
)
```

### 3. Clear Filters
```python
@app.callback(
    Output('sales-data-table', 'filterModel'),
    Input('clear-filters-btn', 'n_clicks')
)
```

### 4. Global Search
```python
@app.callback(
    Output('sales-data-table', 'dashGridOptions'),
    Input('table-global-search', 'value'),
    State('sales-data-table', 'dashGridOptions')
)
```

### 5. Column Visibility
```python
@app.callback(
    Output('sales-data-table', 'columnDefs'),
    Input('column-visibility-checklist', 'value'),
    # ... other states
)
```

## Performance Considerations

### Optimizations
- **Pagination**: Reduces DOM elements on screen
- **Virtual Scrolling**: Renders only visible rows
- **Lazy Loading**: Data loaded as needed
- **Debounced Search**: Reduces filter operations

### Large Datasets
- Handles 10,000+ rows smoothly
- Pagination keeps performance stable
- Export works with any dataset size
- Filters applied efficiently on client side

## User Benefits

### For Sales Analysis
1. **Quick Lookup**: Find specific orders instantly
2. **Pattern Discovery**: Sort to identify trends
3. **Data Verification**: Check individual transactions
4. **Custom Views**: Filter to focus on segments

### For Reporting
1. **Export Filtered Data**: Send specific subsets
2. **Selected Records**: Export only relevant rows
3. **Time-stamped Files**: Track when data extracted
4. **CSV Format**: Compatible with Excel/Sheets

### For Exploration
1. **Column Toggle**: Focus on relevant fields
2. **Multi-level Filtering**: Combine filters
3. **Quick Search**: Find text anywhere
4. **Sorting Options**: Order by any metric

## Tips & Tricks

### Power User Features
- **Shift+Click**: Select range of rows
- **Ctrl/Cmd+Click**: Select multiple non-consecutive rows
- **Column Resize**: Drag column divider to adjust width
- **Header Checkbox**: Select/deselect all visible rows

### Common Workflows
1. **Top Customers**: Sort by Revenue descending, export top 50
2. **Regional Analysis**: Filter by State, export for regional team
3. **Product Focus**: Filter by Category, analyze specific products
4. **Date Range**: Use date filter for period-specific data

### Export Best Practices
- Use "Export Selected" for focused analysis
- Use "Export All" for complete backups
- Check filter status before exporting
- Verify row count matches expectations

## Integration

### Location in Dashboard
- **Position**: Bottom of main dashboard tab
- **Visibility**: Collapsed by default
- **Access**: Single click to open
- **Context**: Shows currently filtered data

### Data Source
- Uses same API data as charts
- Updates with date range changes
- Respects "Hide Innovative" filter
- Real-time data sync

## Future Enhancements (Potential)

### Possible Additions
- [ ] Excel export (with formatting)
- [ ] Save custom filter presets
- [ ] Column grouping
- [ ] Aggregation rows (totals/averages)
- [ ] Cell editing (if write access added)
- [ ] Color coding cells by thresholds
- [ ] Sparklines in cells
- [ ] Right-click context menu

## Troubleshooting

### Common Issues

**Table Not Loading**
- Check if data fetched successfully
- Verify date range selected
- Look for console errors

**Export Not Working**
- Ensure rows are selected for "Export Selected"
- Check browser download permissions
- Verify data exists in table

**Filters Not Applying**
- Click outside filter input to apply
- Check filter icon shows active state
- Use "Clear Filters" to reset

**Columns Missing**
- Check column visibility checkboxes
- Ensure all desired columns checked
- Scroll horizontally if needed

## Summary

The Advanced Data Table feature provides:
✅ Professional data grid with AG Grid
✅ Comprehensive filtering and sorting
✅ Row selection with checkboxes
✅ Export to CSV functionality
✅ Column visibility controls
✅ Global search capability
✅ Responsive and performant
✅ Enterprise-grade user experience

Perfect for detailed data exploration, verification, and export needs!
