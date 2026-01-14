# Quick Test Guide - My Charts Feature

## How to Test the New Feature

### 1. Start the Dashboard
```bash
cd /Users/bhurvasharma/dashboard
python app.py
```
Then open http://localhost:8050 in your browser.

### 2. Test Chart Saving

**Step 1: Create a Custom Chart**
- You should see two tabs at the top: "Dashboard" and "My Charts"
- Stay on the "Dashboard" tab
- Scroll down to find "➕ Create Custom Chart" button
- Click it to expand the Custom Chart Builder

**Step 2: Configure the Chart**
- Select X-axis: "State" (or any other option)
- Select Y-axis: "Sum of Revenue"
- Select Chart Type: "Bar Chart"
- Leave other settings as default or customize
- Click "Generate Chart" button
- You should see a preview of the chart

**Step 3: Save the Chart**
- In the "Chart Name" field, type: "My First Saved Chart"
- Click "💾 Save Chart" button
- You should see a green success message: "✅ Chart 'My First Saved Chart' saved successfully! Switch to 'My Charts' tab to view it."

### 3. Test Chart Display

**Step 1: View Saved Charts**
- Click on the "My Charts" tab at the top
- You should see your saved chart displayed in a card
- The card shows:
  - Chart name: "My First Saved Chart"
  - Timestamp of when it was saved
  - The actual chart with current data
  - A "🗑️ Delete" button

**Step 2: Test Dynamic Updates**
- In the left sidebar, change the date range
- Notice the chart automatically updates with new data
- Try checking/unchecking "Hide 'Innovative Ortho Surgicals'" checkbox
- The chart should update accordingly

### 4. Test Multiple Charts

**Create More Charts:**
1. Go back to "Dashboard" tab
2. Create another chart with different settings:
   - X-axis: "Dealer Name"
   - Y-axis: "Sum of Quantity"
   - Chart Type: "Pie Chart"
   - Name it: "Top Dealers by Quantity"
3. Save it
4. Create a third chart:
   - X-axis: "City"
   - Y-axis: "Count of Orders"
   - Chart Type: "Horizontal Bar"
   - Name it: "Orders by City"
5. Save it

**View All Charts:**
- Go to "My Charts" tab
- You should see all 3 charts in a 2-column grid layout
- Each chart should have its own card with delete button

### 5. Test Chart Deletion

**Delete a Chart:**
- On "My Charts" tab, find one of your saved charts
- Click the "🗑️ Delete" button below it
- The chart should immediately disappear from the page
- The remaining charts should still be visible

### 6. Test Persistence

**Test Browser Refresh:**
1. While on "My Charts" tab with saved charts visible
2. Press Ctrl+R (or Cmd+R on Mac) to refresh the page
3. After page reloads, go back to "My Charts" tab
4. Your saved charts should still be there!

**Test Browser Close/Reopen:**
1. Note the charts you have saved
2. Close the browser completely
3. Reopen browser and go to http://localhost:8050
4. Navigate to "My Charts" tab
5. Your charts should still be there!

### 7. Test Error Handling

**Test Empty Chart Name:**
1. Go to Dashboard tab
2. Open Custom Chart Builder
3. Configure a chart but leave "Chart Name" field empty
4. Click "💾 Save Chart"
5. You should see a warning message

**Test No Saved Charts:**
1. Delete all your saved charts (click delete button on each)
2. "My Charts" tab should show a friendly message:
   - "No Saved Charts Yet"
   - Instructions on how to create charts

### 8. Expected Behavior Summary

✅ **Charts persist across page refreshes**  
✅ **Charts persist across browser sessions**  
✅ **Charts update with current date range**  
✅ **Charts can be deleted instantly**  
✅ **Multiple charts display in grid layout**  
✅ **Clear error messages for invalid inputs**  
✅ **Smooth tab navigation**  
✅ **Sidebar accessible from both tabs**  

## Common Issues & Solutions

### Issue: Charts don't appear after saving
**Solution:** Make sure to click the "My Charts" tab to see saved charts. They won't appear on the Dashboard tab.

### Issue: Charts show "No data available"
**Solution:** Ensure you have selected a valid date range in the sidebar and that the API is returning data.

### Issue: Storage doesn't persist
**Solution:** Check browser console for errors. Make sure cookies/storage are enabled in browser settings.

### Issue: Delete button doesn't work
**Solution:** Check browser console for JavaScript errors. Refresh the page and try again.

## Browser Console Testing

For advanced testing, open browser console (F12) and run:

```javascript
// View saved charts
console.log(JSON.parse(window.storage.get('my-saved-charts', false)))

// Clear all saved charts (for testing)
window.storage.set('my-saved-charts', '[]', false)

// Manually add a chart (for testing)
const testChart = {
  name: "Test Chart",
  x_axis: "State",
  y_axis: "Sum of Revenue",
  chart_type: "Bar Chart",
  agg_type: "Sum",
  top_n: 10,
  sort_desc: true,
  timestamp: new Date().toISOString(),
  unique_id: "test_" + Date.now()
};
let charts = JSON.parse(window.storage.get('my-saved-charts', false) || '[]');
charts.push(testChart);
window.storage.set('my-saved-charts', JSON.stringify(charts), false);
```

## Success Criteria

The feature is working correctly if:

1. ✅ You can save multiple charts with different configurations
2. ✅ Saved charts appear on the "My Charts" tab
3. ✅ Charts update when you change the date range
4. ✅ You can delete charts individually
5. ✅ Charts persist after browser refresh
6. ✅ Charts persist after closing and reopening browser
7. ✅ Error messages appear for invalid inputs
8. ✅ No JavaScript errors in browser console

Enjoy your new persistent chart storage feature! 🎉
