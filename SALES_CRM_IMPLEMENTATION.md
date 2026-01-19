# Sales CRM Feature - Implementation Summary

## Overview
A comprehensive Sales CRM (Customer Relationship Management) tabular view has been added to the dashboard, providing detailed transaction-level insights with the following columns:

## CRM Table Columns

### Columns with API Data (Populated):
1. **Transaction ID** - Generated from Order ID or auto-generated
2. **Date** - Transaction date from API
3. **Month** - Extracted from transaction date
4. **Year** - Extracted from transaction date
5. **Quarter** - Calculated from transaction date (Q1, Q2, Q3, Q4)
6. **Dealer** - Dealer/Company name from API
7. **State** - State information from API
8. **City** - City information from API
9. **Product** - Product name from API
10. **Product Family** - Category/Sub-category from API
11. **Quantity** - Sales quantity from API
12. **Revenue** - Sales value from API
13. **Unit Price** - Calculated as Revenue/Quantity

### Columns Awaiting API Data:
14. **Executive** - Sales executive information (not available in current API)
15. **Payment Status** - Payment status (not available in current API)
16. **Days Overdue** - Payment overdue days (not available in current API)
17. **Interest Amount** - Interest on overdue payments (not available in current API)

## Features Implemented

### 1. Interactive Filters
- **Dealer Filter**: Multi-select dropdown to filter by specific dealers
- **State Filter**: Multi-select dropdown to filter by states
- **Product Family Filter**: Multi-select dropdown to filter by product categories
- **Payment Status Filter**: Dropdown for payment status (feature ready for when API data is available)
- **Search Input**: Global search across all fields

### 2. Summary Statistics Cards
At the top of the CRM section, four summary cards display:
- Total Transactions count
- Total Revenue (formatted in Indian currency)
- Total Quantity (formatted in Indian notation)
- Unique Dealers count

### 3. Advanced Data Grid
- **AG Grid Implementation**: Professional data grid with:
  - Column sorting
  - Column filtering
  - Resizable columns
  - Pinned first column (Transaction ID)
  - Row selection with checkboxes
  - Pagination (25, 50, 100, 200, 500 rows per page)
  - Cell text selection
  - Range selection for copying data
  - Horizontal scrolling for all columns

### 4. Export Functionality
- **Export Button**: Downloads filtered CRM data as CSV
- Includes all visible columns and respects applied filters
- Filename format: `sales_crm_[start_date]_[end_date].csv`

### 5. Clear Filters
- One-click button to reset all filters to default values

## Technical Implementation

### Location in Code
- **UI Section**: Added before the "Custom Chart Builder" section (~line 1260)
- **Callback Functions**: Added after cross-selling callbacks (~line 3350)

### Callbacks Created
1. **update_crm_table**: Main callback to populate CRM table with filtered data
2. **clear_crm_filters**: Reset all filters
3. **export_crm_data**: Export table data to CSV

### Data Mapping
The callback maps API response fields to CRM columns:
```python
- 'id' or 'Order ID' → Transaction ID
- 'date' or 'order_date' → Date, Month, Year, Quarter
- 'comp_nm' → Dealer
- 'state' → State
- 'city' → City
- 'meta_keyword' → Product
- 'category_name' → Product Family
- 'SQ' → Quantity
- 'SV' → Revenue
- Calculated: Revenue/Quantity → Unit Price
```

### Placeholder Handling
For fields not available in the API, the system displays:
**"Awaiting API updation for data"**

This makes it clear to users which data points are pending API integration.

## User Experience

### Visual Design
- Modern card-based layout with shadow effects
- Color-coded badges for date range and transaction count
- Icon indicators (💼) for easy section identification
- Responsive grid that adapts to screen size

### Data Presentation
- Revenue formatted in Indian notation (Lakhs/Crores)
- Quantity formatted appropriately (K/Lakh/Crore)
- Dates in YYYY-MM-DD format for consistency
- Numeric values right-aligned in columns

### Performance
- Pagination limits initial load to 50 rows
- Filters applied on backend before rendering
- Efficient AG Grid rendering for smooth scrolling

## Future Enhancements
When API data becomes available for the following fields, the system will automatically populate them:
1. Executive/Sales Rep information
2. Payment Status (Paid/Pending/Overdue)
3. Days Overdue calculation
4. Interest Amount calculation

The payment status filter is already implemented and will become functional once API data is available.

## Usage Instructions

1. **Navigate to Sales CRM Section**: Scroll down past the analytics charts
2. **Apply Filters**: Use dropdowns to filter by Dealer, State, or Product Family
3. **Search**: Use the search box to find specific transactions
4. **Sort Data**: Click column headers to sort
5. **Select Rows**: Use checkboxes to select specific transactions
6. **Export Data**: Click "Export CRM Data" to download filtered results
7. **Clear Filters**: Click "Clear Filters" to reset all selections

## Notes
- Date range selector at the top of the dashboard controls the CRM data range
- "Hide Innovative" checkbox (if enabled) also applies to CRM data
- All transactions are displayed by default; use filters to narrow down results
