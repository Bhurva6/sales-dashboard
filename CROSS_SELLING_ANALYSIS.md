# Cross-Selling Analysis Feature

## Overview
The Cross-Selling Analysis section helps identify product relationships and discover which items are frequently purchased together. This feature is **visible by default** on the dashboard as soon as it loads.

## Features

### 1. **Analysis Types**
- **By Product**: Analyze product-to-product associations
- **By Category**: Discover category-level cross-selling patterns
- **By Dealer**: Identify dealer-specific buying patterns

### 2. **Advanced Filters**
- **Category Filter**: Multi-select to focus on specific product categories
- **Dealer Filter**: Multi-select to analyze specific dealers
- **Minimum Support**: Set threshold (1-100%) for association frequency
- **Minimum Confidence**: Set threshold (1-100%) for association strength
- **Top N Associations**: Limit results to top N strongest associations (5-50)

### 3. **Visualizations**

#### Summary Cards
- **Associations Found**: Total number of product associations discovered
- **Average Confidence**: Mean confidence level across all associations
- **Average Support**: Mean support level across all associations
- **Top Item**: Most frequently associated product

#### Network/Sankey Diagram
- Interactive flow diagram showing product relationships
- Color-coded by confidence level:
  - 🟢 Green: High confidence (≥50%)
  - 🔵 Blue: Medium confidence (30-49%)
  - 🟡 Yellow: Low confidence (<30%)
- Hover to see detailed association metrics

#### Bar Chart
- Top 15 associations by confidence
- Color-coded by support level
- Easy-to-read horizontal layout

#### Scatter Plot
- Support vs Confidence analysis
- Bubble size represents frequency
- Helps identify strong and reliable associations

#### Data Table
- Comprehensive list of all association rules
- Sortable and filterable columns
- Shows:
  - Item A and Item B (associated products)
  - Confidence percentage
  - Support percentage
  - Co-occurrence frequency
  - Revenue for both items

### 4. **Action Buttons**
- **Download Report**: Export association rules as CSV
- **Reset Filters**: Clear all filters and return to defaults

## How to Use

1. **Select Analysis Type**: Choose between Product, Category, or Dealer analysis
2. **Apply Filters**: Optionally filter by category, dealer, or set thresholds
3. **Adjust Thresholds**: 
   - Increase support to find more common associations
   - Increase confidence to find stronger relationships
4. **Interpret Results**:
   - High confidence = Strong association (if A is bought, B is likely bought)
   - High support = Frequent association (A and B are often bought together)
5. **Take Action**: Use insights to create product bundles, recommendations, or promotions

## Metrics Explained

### Support
- **Definition**: How frequently items appear together
- **Formula**: (Transactions with both items) / (Total transactions)
- **Example**: 10% support means 10 out of 100 transactions contain both items

### Confidence
- **Definition**: How often Item B is bought when Item A is bought
- **Formula**: (Transactions with both A and B) / (Transactions with A)
- **Example**: 60% confidence (A→B) means when A is bought, B is bought 60% of the time

### Frequency
- **Definition**: Absolute count of times items appear together
- **Example**: Frequency of 25 means these items appeared together in 25 orders

## Business Applications

1. **Product Bundling**: Create bundles of frequently associated items
2. **Cross-Sell Recommendations**: Suggest Item B when customer buys Item A
3. **Store Layout**: Place associated items near each other
4. **Inventory Planning**: Stock associated items together
5. **Marketing Campaigns**: Promote complementary products together
6. **Pricing Strategy**: Offer discounts on product combinations

## Tips for Best Results

- **Start with low thresholds** (5% support, 10% confidence) to discover patterns
- **Increase thresholds gradually** to filter out weak associations
- **Compare different time periods** to identify seasonal patterns
- **Analyze by dealer** to discover region-specific preferences
- **Use category-level analysis** for strategic insights
- **Export reports** for deeper analysis in Excel/BI tools

## Technical Notes

- Analysis runs automatically when dashboard loads
- Results update when filters change
- Requires Order ID and Product Name columns in data
- Handles missing data gracefully
- Performance optimized for datasets up to 100K transactions

## Default Settings

- Analysis Type: **Product**
- Minimum Support: **5%**
- Minimum Confidence: **10%**
- Top N Associations: **10**
- Category Filter: **All Categories**
- Dealer Filter: **All Dealers**
