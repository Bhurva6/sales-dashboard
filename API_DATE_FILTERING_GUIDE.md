# API Date Filtering Guide

## Overview
The dashboard now sends date-filtered requests to the API based on the selected time period. All data displayed is filtered at the API level using the appropriate start and end dates.

## How It Works

### Time Period Selection
Users can select one of four time periods from the sidebar:
- **Today**: Current date only
- **This Week**: Monday of current week to today
- **This Month**: 1st of current month to today
- **This Year**: January 1st of current year to today

### Date Calculation (`get_date_range` method)

Located in `api_client.py`, the `APIClient` class includes a helper method that calculates the appropriate date range:

```python
def get_date_range(self, period: str = "year") -> tuple:
    """
    Get start and end dates based on the period
    
    Args:
        period: One of 'today', 'week', 'month', 'year'
    
    Returns:
        Tuple of (start_date, end_date) in DD-MM-YYYY format
    """
```

### Date Format
All dates are sent to the API in **DD-MM-YYYY** format (as required by the API):
- Example: `01-01-2026` for January 1, 2026

### API Request Body

When `get_sales_report()` is called with a period parameter, it sends:

```json
{
    "action": "get_sales_report",
    "startdate": "DD-MM-YYYY",
    "enddate": "DD-MM-YYYY"
}
```

**Example for "This Week":**
```json
{
    "action": "get_sales_report",
    "startdate": "30-12-2025",
    "enddate": "02-01-2026"
}
```

## Implementation Details

### api_client.py Changes

1. **New `get_date_range` method**: Calculates start/end dates based on period
   - Returns tuple of dates in DD-MM-YYYY format
   - Handles: today, week, month, year periods

2. **Updated `get_sales_report` method**: Now accepts period parameter
   - `period`: Optional parameter for time period filtering
   - If period is provided, calculates dates automatically
   - Maintains backward compatibility with explicit date parameters

### dashboard.py Changes

1. **Moved time period selector to sidebar** for better UX
2. **New `load_data_by_period` function**: Fetches data for selected period
3. **Period-based caching**: Separate cache for each period to avoid data mixing
4. **Simplified key metrics section**: No need for client-side filtering

## Usage Example

### From Dashboard UI
```
User selects: "This Week" from sidebar
↓
Dashboard calls: load_data_by_period("week")
↓
Which calls: fetch_dashboard_data(period="week")
↓
Which calls: api_client.get_sales_report(period="week")
↓
Which calls: get_date_range("week")
↓
API receives dates and filters data server-side
```

### From Code
```python
# Get date range for a specific period
start_date, end_date = api_client.get_date_range("month")
# Returns: ("01-01-2026", "02-01-2026")

# Fetch data for the period
result = api_client.get_sales_report(period="today")

# Or use explicit dates
result = api_client.get_sales_report(
    start_date="01-12-2025",
    end_date="31-12-2025"
)
```

## Period Calculations

### Today
- Start: Current date at 00:00
- End: Current date (until now)
- Example: `02-01-2026` to `02-01-2026`

### This Week
- Start: Monday of current week at 00:00
- End: Today
- Example: `30-12-2025` (Mon) to `02-01-2026` (Thu)

### This Month
- Start: 1st of current month
- End: Today
- Example: `01-01-2026` to `02-01-2026`

### This Year
- Start: January 1st of current year
- End: Today
- Example: `01-01-2026` to `02-01-2026`

## API Response Handling

The API filters data server-side and returns only records within the date range. The dashboard:

1. Receives filtered data from API
2. Converts to DataFrame
3. Caches with period-specific key
4. Displays metrics and charts

## Benefits

✅ **Server-side filtering** - Only relevant data is transferred  
✅ **Reduced bandwidth** - Smaller API responses  
✅ **Better performance** - Less data to process  
✅ **Accurate metrics** - Timestamps handled at API level  
✅ **User-friendly** - Simple period selector in sidebar  

## Testing

To test different time periods:

1. **Today**: Select "Today" - should show only today's transactions
2. **This Week**: Select "This Week" - metrics should match last 7 days
3. **This Month**: Select "This Month" - metrics should match Jan 1 to today
4. **This Year**: Select "This Year" - metrics should show all 2026 data

Check the browser console or terminal for debug output showing the dates sent to the API.

## Notes

- Dates are calculated in the user's local timezone (server timezone)
- Week starts on Monday (ISO 8601 standard)
- All filters are applied at the API level
- Caching is per-period to ensure data consistency
- Refresh button clears all period caches
