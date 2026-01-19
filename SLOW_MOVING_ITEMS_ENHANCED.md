# Slow-Moving Items Tracker - Enhanced Features

## Overview
The Slow-Moving Items Tracker has been upgraded with advanced date-based filtering capabilities and enhanced visualization options.

## New Features Implemented

### 1. **Enhanced Filter Controls**

#### Inactivity Period Filter
- Select products with no sales in the last 7, 15, 30, 60, or 90 days
- Default: 30 days

#### Category Filter
- Multi-select dropdown to filter by product categories
- Auto-populated from available data
- Shows "All Categories" when no selection made

#### Dealer Filter  
- Multi-select dropdown to filter by dealer names
- Auto-populated from available data
- Shows "All Dealers" when no selection made

#### Sort Options
Four sorting criteria available:
- **Days Since Last Sale** (default) - Shows products with longest inactivity
- **Total Revenue** - Shows slow-moving items sorted by revenue impact
- **Total Quantity** - Shows slow-moving items by quantity sold
- **Sales Velocity** - Shows items by sales velocity (units/day)

#### Additional Filters
- **Show Top N Items** - Control how many items to display (10-100, step 10)
- **Minimum Revenue** - Optional filter to show only items above certain revenue threshold

### 2. **Enhanced Visualizations**

#### Summary Cards
Four key metrics displayed at the top:
- 📦 **Slow-Moving Products Count** - Total number of slow-moving items
- 📅 **Avg Days Since Sale** - Average days of inactivity
- 💰 **Total Revenue Impact** - Combined revenue of all slow-moving items
- 📉 **Total Units** - Combined quantity of slow-moving items

#### Dynamic Bar Chart
- Horizontal bar chart showing top N slow-moving products
- Color-coded gradient from green (better) to red (worse)
- Automatically adjusts based on selected sort criteria
- Shows days, revenue, quantity, or velocity based on selection

#### Category Distribution Pie Chart
- Donut chart showing slow-moving items breakdown by category
- Only displays when category data is available
- Shows percentage and revenue for each category

#### Detailed Data Table
- Comprehensive table with all relevant metrics
- Columns include:
  - Product Name
  - Category (if available)
  - Days Since Last Sale
  - Last Sale Date
  - Total Revenue
  - Total Quantity
  - Order Count
  - Sales Velocity (units/day)
- Scrollable for large datasets
- Shows "Displaying X of Y" records

### 3. **Action Buttons**

#### Download Report Button
- Downloads complete slow-moving items analysis as CSV
- Includes all filtered data (not just top N displayed)
- Filename format: `slow_moving_items_YYYYMMDD_HHMMSS.csv`
- Uses current filter settings at time of download

#### Reset Filters Button
- One-click reset of all filters to default values
- Resets to:
  - Category: All Categories
  - Dealer: All Dealers
  - Sort By: Days Since Last Sale
  - Top N: 20
  - Minimum Revenue: None
  - Days Filter: 30

### 4. **Date-Based Intelligence**

The tracker now leverages the main dashboard's date range picker:
- Analyzes sales data within the selected date range
- Calculates "Days Since Last Sale" relative to end date
- Shows date range badge in card header
- Only appears when valid date data is available

## Usage Guide

### Basic Usage
1. Select date range using the main date picker (sidebar)
2. Navigate to "Slow-Moving Items Tracker" section
3. Adjust "Inactivity Period" (default: 30 days)
4. View results automatically

### Advanced Filtering
1. Use **Category Filter** to focus on specific product categories
2. Use **Dealer Filter** to analyze specific dealers' slow-moving items
3. Change **Sort By** to view items from different perspectives:
   - Sort by Revenue to see which slow items have highest revenue impact
   - Sort by Quantity to see which items have most units unsold
   - Sort by Velocity to identify truly stagnant products
4. Adjust **Show Top N** to see more or fewer items
5. Set **Minimum Revenue** to focus on higher-value items only

### Downloading Reports
1. Apply desired filters
2. Click "Download Report" button
3. CSV file will download with complete filtered dataset
4. Open in Excel/Sheets for further analysis

### Resetting Filters
- Click "Reset Filters" to return all settings to defaults
- Useful when you want to start fresh analysis

## Technical Details

### Data Processing
- Fetches data from API based on selected date range
- Groups sales by product name
- Calculates metrics:
  - Total Revenue per product
  - Total Quantity per product
  - First Sale Date
  - Last Sale Date
  - Order Count
  - Days Since Last Sale (end_date - last_sale_date)
  - Sales Velocity (total_quantity / date_range_days)
  - Average Order Value (total_revenue / order_count)

### Filtering Logic
1. Products are identified as "slow-moving" if: `Days Since Last Sale >= Selected Days Filter`
2. Category and Dealer filters are applied on top
3. Minimum Revenue filter (if set) further narrows results
4. Results are sorted by selected criteria
5. Top N items are displayed in visualizations

### Performance Optimization
- Filter options (categories, dealers) populated dynamically from data
- Uses pandas for efficient data aggregation
- Leverages existing chart_data_store for download functionality

## Callback Structure

### Main Callback: `update_slow_moving_items`
**Inputs:**
- slow-moving-days-filter
- slow-moving-category-filter
- slow-moving-dealer-filter
- slow-moving-sort-by
- slow-moving-top-n
- slow-moving-min-revenue
- username-input
- password-input
- date-range-picker (start_date, end_date)
- hide-innovative-check

**Outputs:**
- slow-moving-items-content (main visualization)
- slow-moving-category-filter options
- slow-moving-dealer-filter options

### Reset Callback: `reset_slow_moving_filters`
**Input:** slow-moving-reset-btn clicks

**Outputs:** Resets all filter values to defaults

### Download Callback: `download_slow_moving_report`
**Input:** slow-moving-download-btn clicks

**Output:** CSV file download

## Future Enhancements (Potential)

1. **Email Alerts** - Send alerts when critical items become slow-moving
2. **Trend Analysis** - Show if slow-moving status is improving or worsening
3. **Recommendations** - AI-powered suggestions for clearing slow-moving inventory
4. **Comparison Mode** - Compare slow-moving items across different date ranges
5. **Export Options** - Add PDF and Excel export with charts
6. **Custom Thresholds** - Allow users to define custom velocity thresholds
7. **Dealer Performance** - Show which dealers have most slow-moving items

## Troubleshooting

### Tracker Not Showing
- Ensure date range is selected
- Verify date data is available in API response
- Check that 'Date' field is present in data

### No Results
- Try reducing the "Inactivity Period" (e.g., from 30 to 15 days)
- Remove category/dealer filters
- Check if date range includes sufficient historical data

### Download Not Working
- Ensure filters are applied and results are visible
- Check browser's download settings
- Verify chart-data-store has data

## Best Practices

1. **Regular Monitoring** - Check slow-moving items weekly or bi-weekly
2. **Category Focus** - Filter by category for targeted inventory management
3. **Revenue Priority** - Sort by revenue to address high-value items first
4. **Velocity Analysis** - Use velocity sort to identify truly stagnant products
5. **Historical Comparison** - Use different date ranges to see trends
6. **Export Data** - Download reports for offline analysis and sharing

## Version History

### v2.0 - Enhanced (Current)
- Added category and dealer filters
- Added multiple sort options
- Added configurable top N display
- Added minimum revenue filter
- Enhanced visualizations with category pie chart
- Added CSV download functionality
- Added reset filters button
- Improved UI with better spacing and icons

### v1.0 - Initial
- Basic slow-moving items tracking
- Simple days filter (7, 15, 30, 60, 90)
- Basic bar chart visualization
- Summary cards
