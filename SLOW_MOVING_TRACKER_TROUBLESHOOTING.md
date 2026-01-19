# Slow-Moving Items Tracker - Troubleshooting Guide

## Issue: Tracker Not Visible on Dashboard

### Recent Fixes Applied:

#### 1. **Added Date Column Mapping** ✅
The tracker requires a 'Date' column to function. Added mappings for common date field names from the API:
- `date` → `Date`
- `order_date` → `Date`
- `created_at` → `Date`
- `sale_date` → `Date`

#### 2. **Added Debug Logging** ✅
Added console logging to help identify issues:
- Prints whether date data is available
- Shows sample date values if available
- Lists all column names if date column is missing

### How to Check if Tracker Should Appear:

1. **Open Browser Console** (F12 or Right-click → Inspect → Console)

2. **Look for these messages after loading dashboard:**
   ```
   Has date data: True  ← Should be True for tracker to appear
   Date column sample: [date values]
   ```

3. **If you see:**
   ```
   Has date data: False
   Available columns: [list of columns]
   ```
   Then the API is not providing date information in a recognizable format.

### Visibility Conditions:

The Slow-Moving Items Tracker will **ONLY** show if:
- ✅ Date range is selected in sidebar
- ✅ Data is successfully fetched from API
- ✅ DataFrame contains a 'Date' column
- ✅ At least one row of data exists

### Manual Check Steps:

#### Step 1: Verify Date Range
- Check that start and end dates are selected in the sidebar
- Default should be: Current month start → Today

#### Step 2: Check Browser Console
```
DASH UPDATE TRIGGERED
   Range: [start] to [end]
   Data fetched: [X] rows
   Available columns: [list]
   Has date data: True/False  ← KEY LINE
```

#### Step 3: Scroll Down Dashboard
The tracker appears:
- **After**: Activity Patterns section
- **After**: Funnel and Conversion Analysis  
- **Before**: Custom Chart Builder
- Look for: "📦 Slow-Moving Items Tracker" heading

### Common Issues & Solutions:

#### Issue 1: "Has date data: False"
**Cause**: API doesn't return date field or uses different field name

**Solution**: 
1. Check console for "Available columns:" output
2. Find the date field name in the API response
3. Add it to `column_mapping` dictionary in `app.py` (around line 360)

Example:
```python
column_mapping = {
    # ...existing mappings...
    'your_date_field': 'Date',  # Add this line
}
```

#### Issue 2: Tracker visible but shows "No data available"
**Cause**: Date column exists but contains invalid dates

**Solution**: Check date format in API response. Should be parseable by pandas.

#### Issue 3: Entire dashboard not loading
**Cause**: Error in callback execution

**Solution**: Check browser console for Python error messages

### Testing the Tracker:

1. **Select Date Range**: Use sidebar date picker or quick select buttons
2. **Wait for Load**: Watch for loading spinner to complete
3. **Scroll Down**: Past all charts to find the tracker section
4. **Adjust Filter**: Try different day ranges (7, 15, 30, 60, 90 days)

### Expected Location on Page:

```
┌─────────────────────────────────┐
│ Metric Cards (Revenue, etc.)    │
├─────────────────────────────────┤
│ Geographic Map                   │
├─────────────────────────────────┤
│ Analytics Charts                 │
├─────────────────────────────────┤
│ Revenue Trend                    │
├─────────────────────────────────┤
│ Activity Patterns                │
├─────────────────────────────────┤
│ Funnel Analysis                  │
├─────────────────────────────────┤
│ 📦 SLOW-MOVING ITEMS TRACKER    │ ← SHOULD APPEAR HERE
├─────────────────────────────────┤
│ Custom Chart Builder             │
├─────────────────────────────────┤
│ Data Table                       │
└─────────────────────────────────┘
```

### Quick Diagnostic Command:

After page loads, run in browser console:
```javascript
// Check if tracker div exists
document.getElementById('slow-moving-items-content')
// Should return: <div id="slow-moving-items-content">...</div>
// If null, the section wasn't rendered (date data missing)
```

### API Response Check:

To verify API includes date data:
1. Open Network tab in browser dev tools
2. Find the API call to sales report endpoint
3. Check response JSON for date fields
4. Common field names:
   - `date`
   - `order_date`
   - `created_at`
   - `sale_date`
   - `transaction_date`

### Still Not Showing?

If the tracker still doesn't appear after these checks:

1. **Restart the Dashboard**:
   ```bash
   # Stop the app (Ctrl+C)
   python app.py  # or python3 app.py
   ```

2. **Clear Browser Cache**:
   - Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)

3. **Check for Errors**:
   - Terminal where app is running
   - Browser console (F12)

4. **Verify Section Exists in Code**:
   - Search for "Slow-Moving Items Tracker" in app.py
   - Should be around line 994-1026

### Getting Help:

If issue persists, provide:
1. Browser console output (especially "Has date data:" line)
2. List of columns from "Available columns:" output
3. Sample API response (if possible)
4. Screenshot of dashboard (showing what's visible)

---

**Last Updated**: January 18, 2026
**File**: app.py (lines 994-1026 for layout, 2159-2384 for callback)
