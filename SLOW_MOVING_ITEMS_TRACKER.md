# 📦 Slow-Moving Items Tracker - Feature Documentation

## Overview
The Slow-Moving Items Tracker is a powerful inventory management tool that identifies products with low sales velocity. It helps you optimize inventory by highlighting items that haven't sold recently.

## Features

### 1. **Date-Based Filtering**
   - **7 Days**: Items with no sales in the last week
   - **15 Days**: Items with no sales in the last 2 weeks
   - **30 Days**: Items with no sales in the last month (default)
   - **60 Days**: Items with no sales in the last 2 months
   - **90 Days**: Items with no sales in the last 3 months

### 2. **Key Metrics Displayed**

#### Summary Cards:
- **Slow-Moving Products**: Total count of products meeting the criteria
- **Avg Days Since Sale**: Average days since last sale
- **Total Revenue Impact**: Total revenue from these products
- **Total Units**: Total quantity sold

#### Product Analysis:
- **Days Since Last Sale**: Time elapsed since the last transaction
- **Last Sale Date**: When the product was last sold
- **Total Revenue**: Lifetime revenue for the product
- **Total Quantity**: Total units sold
- **Order Count**: Number of orders containing this product
- **Sales Velocity**: Average units sold per day

### 3. **Visualizations**

#### Top 20 Slow-Moving Products Chart
- Horizontal bar chart showing products with longest time since last sale
- Color-coded: Green (recent) → Orange (moderate) → Red (critical)
- Shows days since last sale for each product

#### Detailed Report Table
- Comprehensive table with all slow-moving items (up to 50)
- Sortable columns for easy analysis
- Includes all key metrics for informed decision-making

## How to Use

### Access the Tracker
1. Navigate to the **Dashboard** tab
2. Scroll down to find **"📦 Slow-Moving Items Tracker"**
3. The section appears only when date data is available

### Filter by Time Period
1. Select your desired time range using the radio buttons:
   - Click on **7 Days**, **15 Days**, **30 Days**, **60 Days**, or **90 Days**
2. The analysis updates automatically
3. Products with no sales in the selected period will be displayed

### Interpret Results

#### ✅ **No Slow-Moving Items**
If you see: "Great! No products found with no sales in the last X days"
- This means all products have recent sales
- Your inventory is moving well

#### ⚠️ **Slow-Moving Items Found**
Review the following:
1. **Days Since Last Sale**: Higher numbers indicate stagnant inventory
2. **Total Revenue**: Shows the monetary value locked in slow items
3. **Sales Velocity**: Low velocity indicates poor demand
4. **Order Count**: Few orders suggest limited customer interest

### Action Items Based on Results

#### For Products with 30+ Days Since Last Sale:
- Consider promotional campaigns
- Review pricing strategy
- Evaluate product placement
- Check with dealers about demand

#### For Products with 60+ Days Since Last Sale:
- Implement clearance sales
- Bundle with fast-moving items
- Reduce reorder quantities
- Consider discontinuation

#### For Products with 90+ Days Since Last Sale:
- Urgent clearance needed
- Evaluate product viability
- Reallocate inventory space
- Consider return to supplier

## Technical Details

### Data Requirements
- **Date column**: Required for time-based analysis
- **Product Name**: Required for product identification
- **Quantity**: Required for velocity calculations
- **Revenue**: Required for financial impact

### Calculation Methods

#### Sales Velocity
```
Sales Velocity = Total Quantity Sold / Date Range Days
```

#### Days Since Last Sale
```
Days Since Last Sale = Current Date - Last Sale Date
```

#### Average Order Value
```
Avg Order Value = Total Revenue / Order Count
```

### Performance
- Analyzes up to 50 slowest-moving products
- Real-time calculation based on selected date range
- Optimized for large datasets

## Integration with Other Features

### Works With:
- **Date Range Picker**: Uses selected date range for analysis
- **Hide Innovative Filter**: Respects dealer filtering
- **Refresh Data**: Updates with latest API data

### Combines Well With:
- **Top Products Table**: Compare fast vs slow movers
- **Revenue Trend**: Understand overall sales patterns
- **Geographic Map**: See regional slow-moving patterns

## Best Practices

### Regular Monitoring
- **Weekly**: Check 7-day filter for early warning signs
- **Monthly**: Review 30-day filter for inventory planning
- **Quarterly**: Analyze 90-day filter for strategic decisions

### Seasonal Considerations
- Adjust expectations during off-seasons
- Account for product lifecycles
- Consider promotional periods

### Inventory Optimization
- Use data to inform purchasing decisions
- Adjust stock levels based on velocity
- Focus resources on fast-moving items

## Troubleshooting

### "No data available"
- Check that date range is selected
- Verify API connection
- Ensure data contains Product Name and Date columns

### "Date or Product Name data not available"
- Data source may not include required fields
- Contact administrator for data structure review

### Empty results on all filters
- ✅ This is actually good news! All products have recent sales
- Try a longer time period if needed

## Future Enhancements (Roadmap)
- [ ] Export slow-moving report to Excel
- [ ] Email alerts for critical slow-movers
- [ ] Category-wise slow-moving analysis
- [ ] Dealer-wise slow-moving comparison
- [ ] Predictive analysis for future slow-movers
- [ ] Integration with inventory management systems

## Support
For questions or issues with the Slow-Moving Items Tracker, please refer to the main dashboard documentation or contact the development team.

---

**Last Updated**: January 18, 2026
**Version**: 1.0.0
**Status**: ✅ Active
