# Zero Sales Products Tracker

## Overview
This feature identifies products that have had **zero sales** during the selected time period. Unlike the Slow-Moving Items Tracker (which shows products with low sales velocity), this tracker specifically highlights products that haven't sold at all, helping you identify potential dead stock and take corrective action.

## Purpose
- **Inventory Optimization**: Identify products that may need promotional efforts or should be phased out
- **Category Analysis**: See which product categories have the most unsold items
- **Historical Context**: View when these products last sold (if ever)
- **Action Planning**: Export data for inventory reviews and decision-making

## Key Features

### 1. **Comprehensive Product Catalog**
- Fetches historical data (1 year) to identify all products in your catalog
- Compares against sales in the selected date range
- Shows products that exist in your system but haven't sold during the period

### 2. **Summary Metrics**
Three key cards display:
- **Products with Zero Sales**: Total count of unsold products
- **Categories Affected**: Number of product categories impacted
- **Avg Days Since Last Sale**: Average time elapsed since these products last sold

### 3. **Category Distribution Chart**
- Bar chart showing zero-sales products grouped by category
- Color-coded by intensity (darker red = more products)
- Helps identify which categories need attention

### 4. **Detailed Product List**
Table showing:
- Product Name
- Category
- Last Sale Date (from historical data)
- Days Since Last Sale

### 5. **Filtering Options**
- **Filter by Category**: Focus on specific product categories (multi-select)
- **Sort By**: 
  - Product Name (A-Z)
  - Category (grouped view)
  - Last Sale Date (oldest first)

### 6. **Export Capability**
- Download complete report as CSV
- Includes all zero-sales products with their details
- Timestamped filename for record-keeping

## How It Works

### Data Collection Process
1. **Current Period Sales**: Fetches sales data for the selected date range
2. **Historical Catalog**: Retrieves sales data from the past year to build a complete product catalog
3. **Comparison**: Identifies products in the catalog that don't appear in current period sales
4. **Enrichment**: Adds last sale date and days since last sale from historical data

### Technical Implementation
```python
# Pseudo-code flow:
1. Fetch sales for selected period (start_date to end_date)
2. Fetch historical sales (1 year ago to end_date)
3. Extract all unique products from historical data
4. Identify products NOT in current period sales
5. Add category and last sale date information
6. Display with filters and visualizations
```

## Use Cases

### 1. **Monthly Inventory Review**
- Set date range to last month
- Identify products with zero sales
- Plan promotions or clearance

### 2. **Seasonal Analysis**
- Set date range to a specific season
- Find products that didn't sell during peak season
- Consider inventory adjustments

### 3. **Category Performance**
- Filter by specific categories
- Compare zero-sales rates across categories
- Identify underperforming product lines

### 4. **Dead Stock Identification**
- Look for products with 90+ days since last sale
- Review for potential phase-out
- Consider replacement products

## Visual Indicators
- **Red Theme**: Danger color scheme to highlight critical attention needed
- **Border**: Red border on the card to emphasize urgency
- **Charts**: Color-coded intensity (more products = darker red)

## Differences from Slow-Moving Tracker

| Feature | Zero Sales Tracker | Slow-Moving Tracker |
|---------|-------------------|---------------------|
| **Focus** | Products with NO sales | Products with LOW sales velocity |
| **Threshold** | Exactly 0 sales | Configurable days since last sale |
| **Data Required** | Historical catalog needed | Only current period data |
| **Use Case** | Dead stock identification | Velocity optimization |
| **Urgency** | High (complete lack of movement) | Medium (slow movement) |

## Best Practices

### 1. **Regular Monitoring**
- Check weekly for recent periods (last 7-30 days)
- Monthly review for longer trends

### 2. **Category Focus**
- Start with high-value categories
- Review seasonal products appropriately

### 3. **Action Steps**
When you find zero-sales products:
- **Immediate**: Check if product is still active/relevant
- **Short-term**: Plan promotional campaigns
- **Long-term**: Consider phasing out or replacing

### 4. **Combine with Other Trackers**
- Use with Slow-Moving Tracker for complete picture
- Cross-reference with Cross-Selling Analysis for bundle opportunities

## Example Workflow

```
1. Select Date Range: Last Quarter (Oct 1 - Dec 31)
2. View Summary: 45 products with zero sales across 8 categories
3. Filter: Select "Orthopedic Implants" category
4. Sort by: Last Sale Date (to see oldest first)
5. Review: Products haven't sold in 120+ days
6. Action: Download report and plan clearance promotion
7. Follow-up: Check again after promotion period
```

## Limitations
- Requires historical data (1 year) to build product catalog
- Products added recently may show as zero-sales (expected)
- Doesn't account for products removed from catalog
- Relies on API historical data availability

## Benefits
1. ✅ **Proactive Inventory Management**: Catch dead stock early
2. ✅ **Category Insights**: Understand which product lines struggle
3. ✅ **Data-Driven Decisions**: Export reports for planning meetings
4. ✅ **Complementary Analysis**: Works alongside other trackers
5. ✅ **Historical Context**: Know when products last moved

## Tips for Success
- 📊 **Check regularly**: Don't wait for annual reviews
- 🎯 **Set goals**: Define acceptable zero-sales thresholds by category
- 📈 **Track trends**: Monitor if zero-sales products are increasing
- 💡 **Take action**: Use insights to drive promotional plans
- 🔄 **Review results**: After actions, verify impact in next period
