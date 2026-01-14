# ⚡ Quick Reference - Modern Theme

## 🚀 Quick Start
```bash
# Run the dashboard
python app.py

# Open in browser
http://localhost:8050
```

---

## 🎨 Color Palette (COLORS Dictionary)

| Name | Hex | Usage |
|------|-----|-------|
| `primary` | `#6366f1` | Primary actions, main elements |
| `secondary` | `#8b5cf6` | Secondary actions, accents |
| `success` | `#10b981` | Success states, positive metrics |
| `danger` | `#ef4444` | Errors, negative changes |
| `warning` | `#f59e0b` | Warnings, attention needed |
| `info` | `#3b82f6` | Information, neutral actions |
| `light` | `#f9fafb` | Light backgrounds |
| `dark` | `#1f2937` | Dark text, headings |

---

## 📝 Typography

**Font Family**: Inter (Google Fonts)  
**Weights**: 300, 400, 500, 600, 700, 800  
**Sizes**: 11px (body), 14px (headings), 18px (titles)

---

## 📊 All 16 Charts

| Chart | Function | Status |
|-------|----------|--------|
| Dealer Pie | `_create_dealer_pie()` | ✅ |
| State Pie | `_create_state_pie()` | ✅ |
| Category Bar | `_create_category_bar()` | ✅ |
| Revenue Trend | `_create_revenue_trend()` | ✅ |
| Dealer Comparison | `_create_dealer_comparison()` | ✅ |
| City Bar | `_create_city_bar()` | ✅ |
| Category Sunburst | `_create_category_sunburst()` | ✅ |
| Weekday Pattern | `_create_weekday_pattern()` | ✅ |
| Sales Funnel | `_create_sales_funnel()` | ✅ |
| Conversion Timeline | `_create_conversion_timeline()` | ✅ |
| Activity Heatmap | `_create_activity_heatmap()` | ✅ |
| Hourly Heatmap | `_create_hourly_heatmap()` | ✅ |
| Day Part Analysis | `_create_day_part_analysis()` | ✅ |
| India Map | `_create_india_map()` | ✅ |
| Revenue Comparison | `_create_revenue_comparison_chart()` | ✅ |
| Custom Chart | `_create_custom_chart()` | ✅ |

---

## 🛠️ Helper Function

```python
apply_modern_chart_style(fig, title="Chart Title", height=400)
```

**What it does**:
- Sets Inter font family
- Makes backgrounds transparent
- Adds subtle gridlines
- Applies consistent margins
- Sets modern layout

---

## ✏️ Creating New Charts

```python
def _create_my_new_chart(df, value_col):
    # 1. Create figure
    fig = px.bar(df, x='category', y=value_col)
    
    # 2. Customize (optional)
    fig.update_traces(marker_color=COLORS['primary'])
    
    # 3. Apply modern style (required!)
    apply_modern_chart_style(fig, "My Chart Title", height=400)
    
    # 4. Add layout tweaks (optional)
    fig.update_layout(margin=dict(t=60, b=40))
    
    return fig
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `app.py` | Main application (4,300+ lines) |
| `/assets/custom.css` | Custom styling (500+ lines) |
| `THEME_COMPLETE_SUMMARY.md` | Full summary |
| `CHART_STYLING_COMPLETE.md` | Chart update details |
| `QUICK_START_THEME.md` | User guide |

---

## 🔍 Common Tasks

### Change Theme Color
```python
# In app.py, edit COLORS dictionary
COLORS = {
    'primary': '#YOUR_COLOR',  # Change this!
    # ... rest stays same
}
```

### Adjust Chart Height
```python
apply_modern_chart_style(fig, "Title", height=500)  # Default: 400
```

### Customize Single Chart
```python
# After apply_modern_chart_style()
fig.update_layout(
    showlegend=False,
    margin=dict(t=80, b=20)
)
```

### Add Custom Colors to Chart
```python
fig.update_traces(
    marker_color=[COLORS['primary'], COLORS['secondary'], COLORS['success']]
)
```

---

## 🐛 Troubleshooting

### Charts not showing?
- Check browser console (F12)
- Verify `python app.py` runs without errors
- Clear browser cache

### Wrong font displaying?
- Check if Google Fonts is loading
- Verify `/assets/custom.css` exists
- Check network tab for font download

### Colors not updating?
- Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
- Check COLORS dictionary is defined
- Verify chart uses COLORS['key'] syntax

---

## 📚 Documentation Quick Links

| Document | Use Case |
|----------|----------|
| `QUICK_START_THEME.md` | 5-minute overview |
| `THEME_UPDATE_GUIDE.md` | Complete technical guide |
| `DESIGN_SYSTEM_REFERENCE.md` | Colors, fonts, components |
| `CHART_UPDATES_VISUAL_GUIDE.md` | Before/after examples |
| `THEME_COMPLETE_SUMMARY.md` | Executive summary |

---

## ✅ Status

**Theme Version**: 2.0  
**Charts Updated**: 16/16 ✅  
**Syntax Errors**: 0 ✅  
**Documentation**: Complete ✅  
**Ready to Deploy**: YES ✅  

---

## 📞 Need Help?

1. Check `THEME_UPDATE_GUIDE.md` for detailed info
2. Review `CHART_UPDATES_VISUAL_GUIDE.md` for examples
3. Look at existing chart functions in `app.py`
4. Test in browser and check console for errors

---

**Last Updated**: January 14, 2026  
**Quick Access**: Keep this file open while working!
