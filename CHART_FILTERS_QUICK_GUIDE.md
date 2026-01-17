# 🎯 Quick Guide: Using Chart Filters

## Overview
Every chart in the dashboard now has a multiselect dropdown filter that lets you focus on specific data points.

## How to Use

### Step 1: Load the Dashboard
- The dashboard loads with all data visible
- All charts show complete datasets

### Step 2: Filter a Chart
1. Look at any chart's header (top section)
2. Click the dropdown below the chart title
3. Select one or more items from the list
4. The chart updates instantly

### Step 3: Clear Filters
- Click the "×" next to any selected item to remove it
- Or click the dropdown and deselect items
- Or refresh the dashboard to reset everything

## Available Filters

### 📊 Main Analytics Row

| Chart | Filter Type | What It Does |
|-------|-------------|--------------|
| **💼 Top Dealers by Revenue** | Dealers | Select specific dealers to view their revenue contribution |
| **🗺️ Revenue by State** | States | Focus on selected states only |
| **📂 Revenue by Category** | Categories | Compare specific product categories |
| **🏙️ Top Cities by Revenue** | Cities | Analyze selected cities |

### 📈 Second Analytics Row

| Chart | Filter Type | What It Does |
|-------|-------------|--------------|
| **💼 Dealer Comparison** | Dealers | Compare revenue & quantity for selected dealers |
| **🏙️ Cities by Revenue** | Cities | Independent city filter for this chart |
| **📊 Category Hierarchy** | Categories | Drill down into specific category branches |

## Tips & Tricks

### ✨ Best Practices

1. **Start Broad, Then Narrow**
   - View all data first
   - Identify interesting patterns
   - Filter to investigate specific areas

2. **Compare Subsets**
   - Select 2-3 dealers to compare performance
   - Choose specific regions for regional analysis
   - Pick related categories for category comparison

3. **Use Multiple Charts**
   - Each chart has independent filters
   - Filter dealers in one chart, cities in another
   - Build your custom view

### 🔍 Search Feature
- Type in the dropdown to search
- Quickly find items in long lists
- Example: Type "Mum" to find "Mumbai"

### 📱 Mobile Friendly
- Dropdowns work great on tablets
- Touch-optimized interface
- Scrollable option lists

## Common Use Cases

### Scenario 1: Regional Deep-Dive
```
Goal: Analyze Maharashtra region

Steps:
1. In "Revenue by State" → Select Maharashtra
2. In "Top Cities" → Select Mumbai, Pune, Nagpur
3. In "Top Dealers" → See which dealers operate there
4. Result: Complete regional picture
```

### Scenario 2: Dealer Performance Analysis
```
Goal: Compare top 3 dealers

Steps:
1. View "Top Dealers" chart (unfiltered)
2. Note the top 3 dealers
3. In "Dealer Comparison" → Select those 3 dealers
4. In "Revenue by Category" → Select all to see what they sell
5. Result: Detailed dealer comparison
```

### Scenario 3: Product Category Focus
```
Goal: Understand Hip & Knee Implants sales

Steps:
1. In "Revenue by Category" → Select "Hip" and "Knee" categories
2. In "Category Hierarchy" → Select same categories for drill-down
3. In "Top Cities" → See which cities buy these products
4. In "Top States" → See regional distribution
5. Result: Complete category analysis
```

### Scenario 4: City-Specific Analysis
```
Goal: Focus on Delhi market

Steps:
1. In "Top Cities" → Select Delhi
2. In "Top Dealers" → See active dealers in Delhi
3. In "Revenue by Category" → See popular categories
4. Result: City-specific insights
```

## Visual Guide

### Before Filtering
```
Chart Header
├── 💼 Top Dealers by Revenue
└── [Select dealers...] ▼    ← Click here
```

### After Selecting Items
```
Chart Header
├── 💼 Top Dealers by Revenue
└── [ABC Surgical × | XYZ Implants × | ...] ▼
         ↑              ↑
    Remove item    Remove item
```

### Searching in Dropdown
```
Type: "surg"
Results:
✓ ABC Surgical
✓ Orthopedic Surgicals
✓ Modern Surgical
```

## Keyboard Shortcuts

- **↑/↓ Arrow Keys**: Navigate through dropdown options
- **Enter**: Select highlighted option
- **Escape**: Close dropdown
- **Backspace**: Remove last selected item
- **Type to Search**: Start typing to filter options

## Troubleshooting

### ❓ Chart shows "No data available"
**Solution**: You might have filtered out all data. Clear some selections.

### ❓ Dropdown is empty
**Solution**: Wait for dashboard to load completely. The dropdowns populate after data loads.

### ❓ Selections don't affect chart
**Solution**: The chart might be loading. Wait a moment for the update to complete.

### ❓ Want to reset everything
**Solution**: Click the "🔄 Refresh Data" button in the sidebar. This reloads all data and clears all filters.

## Performance Notes

- ⚡ **Fast**: Filters work instantly on already-loaded data
- 🔄 **No API Calls**: Filtering doesn't trigger new data fetches
- 💾 **Memory Efficient**: Uses client-side filtering
- 🎯 **Optimized**: Large datasets filtered smoothly

## Advanced Features

### Multi-Chart Analysis
You can use different filters on each chart simultaneously:

```
Setup:
- Dealers Chart: Filter to "Top 5"
- Cities Chart: Filter to "Metros"
- Categories Chart: Filter to "High-value"
- States Chart: Show all

Result: Custom dashboard view showing top dealers
in metro cities selling high-value products, with
complete state-wise distribution.
```

### Comparison Mode
Use duplicate charts with different filters:

```
Left Chart: Filter Region A
Right Chart: Filter Region B
Compare: Side-by-side regional comparison
```

## Remember

✅ **Independent Filters**: Each chart's filter only affects that chart
✅ **No Data Loss**: Filtering is temporary - data is not deleted
✅ **Instant Updates**: Charts update immediately when you change filters
✅ **Flexible Analysis**: Mix and match filters for custom insights
✅ **Reset Anytime**: Refresh dashboard to start over

---

**Pro Tip**: Bookmark your dashboard URL after setting up filters for quick access to your custom view!

**Need Help?** Try the examples above or experiment with different filter combinations to discover insights!
