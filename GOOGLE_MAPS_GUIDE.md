# 🗺️ Google Maps Integration Guide

## ✅ Changes Implemented

### 1. **Dash Leaflet Integration**
Your dashboard now uses **Dash Leaflet** to display an interactive Google Maps-style map with:
- 🗺️ OpenStreetMap tiles (Google Maps visual style)
- 📍 Color-coded markers based on sales performance
- 💬 Interactive popups with detailed information
- 🎨 Professional CartoDB Voyager tiles (light theme)
- 🔍 Zoom controls and scale indicator

### 2. **Color-Coded Markers**
Markers change color based on market share:
- 🔴 **Red**: ≥15% market share (Top performers)
- 🟠 **Orange**: 10-15% market share (Strong performers)
- 🟡 **Yellow**: 5-10% market share (Good performers)
- 🟢 **Green**: 2-5% market share (Average performers)
- 🔵 **Blue**: <2% market share (Small markets)

### 3. **Interactive Features**
- **Click markers** to see detailed popup with:
  - Location name
  - Revenue/Quantity/Orders value
  - Market share percentage
- **Hover** for quick tooltips with location names
- **Pan & Zoom** for navigation
- **Scale control** for distance reference

## 📦 Installation Steps

### Step 1: Install dash-leaflet
```bash
pip install dash-leaflet==1.0.15
```

### Step 2: Restart your application
```bash
python app.py
```

## 🎨 Map Tile Options

You can customize the map appearance by changing the TileLayer URL:

### Current (CartoDB Voyager - Light):
```python
url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
```

### Alternative Options:

#### 1. **OpenStreetMap (Default)**
```python
url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
```

#### 2. **CartoDB Dark Matter (Dark Theme)**
```python
url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
```

#### 3. **CartoDB Positron (Minimalist Light)**
```python
url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
```

#### 4. **Stamen Terrain (Topographic)**
```python
url="https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png"
```

#### 5. **Esri World Street Map**
```python
url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}"
```

## 🔑 Using Google Maps (Premium Option)

If you want to use **actual Google Maps** instead of OpenStreetMap:

### Option A: Google Maps Embed API (Iframe - Simple)
```python
# In your layout, replace the Leaflet map with:
html.Iframe(
    src="https://www.google.com/maps/embed/v1/view?key=YOUR_API_KEY&center=20.5937,78.9629&zoom=5",
    style={'width': '100%', 'height': '600px', 'border': 'none', 'borderRadius': '10px'}
)
```

### Option B: Google Maps JavaScript API (Advanced)
1. Get API key from [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Maps JavaScript API
3. Use `dash-google-maps` library or custom JavaScript

**Note**: Google Maps requires billing setup and API key, while Leaflet is free!

## 🚀 Features Comparison

| Feature | Dash Leaflet (Current) | Google Maps |
|---------|----------------------|-------------|
| Cost | ✅ Free | 💰 Paid (after free tier) |
| Setup | ✅ No API key needed | ❌ Requires API key |
| Customization | ✅ Full control | ⚠️ Limited |
| Markers | ✅ Custom colors/icons | ✅ Custom |
| Performance | ✅ Fast | ✅ Fast |
| Visual Quality | ✅ Professional | ✅ Premium |

## 🎯 Current Implementation Features

### ✅ What's Working:
1. **Interactive markers** with color-coding
2. **Popups** with sales data
3. **Tooltips** on hover
4. **Pan and zoom** controls
5. **Responsive design**
6. **Fast performance** (no API limits)

### 🔧 Customization Options:

#### Change Marker Icons:
```python
icon={
    "iconUrl": "https://cdn-icons-png.flaticon.com/512/447/447031.png",  # Custom icon
    "iconSize": [30, 30],
    "iconAnchor": [15, 30],
}
```

#### Add Heatmap Layer:
```python
# Install: pip install dash-leaflet-plugins
from dash_leaflet import plugins

# Add to map:
plugins.HeatmapLayer(
    positions=[[lat1, lon1], [lat2, lon2], ...],
    intensit y=0.8,
    radius=25
)
```

#### Add Circle Markers (Size-based):
```python
dl.Circle(
    center=[lat, lon],
    radius=value * 1000,  # Size based on value
    color='#3b82f6',
    fillOpacity=0.5
)
```

## 🐛 Troubleshooting

### Issue: Map not loading
**Solution**: Ensure dash-leaflet is installed:
```bash
pip install dash-leaflet==1.0.15
```

### Issue: Markers not showing
**Solution**: Check that coordinates are valid in `CITY_COORDS` or `STATE_COORDS` dictionaries.

### Issue: Slow performance
**Solution**: 
- Limit markers to top 50 locations (already implemented)
- Use marker clustering for large datasets:
```python
from dash_leaflet import plugins
plugins.MarkerClusterGroup(children=markers)
```

### Issue: Tiles not loading
**Solution**: Check internet connection or try alternative tile provider.

## 📊 Advanced Features (Optional)

### 1. Add Search Box:
```bash
pip install dash-leaflet-search
```

```python
from dash_leaflet import plugins
plugins.Search(position="topleft")
```

### 2. Add Drawing Tools:
```python
dl.FeatureGroup([
    dl.EditControl(
        draw=dict(
            polyline=False,
            polygon=True,
            circle=True,
            marker=True,
            rectangle=True
        )
    )
])
```

### 3. Add Geolocation:
```python
dl.LocateControl(
    position="topleft",
    strings={"title": "Show my location"}
)
```

## 🎨 Styling Tips

### Card Background:
Currently using `#ffffff` (white). For dark theme:
```python
style={
    'background': '#0f172a',  # Dark navy
    'borderRadius': '10px',
    'padding': '10px',
    'boxShadow': '0 10px 25px rgba(0,0,0,0.3)'
}
```

### Map Container:
Add border and shadow for better visual separation:
```python
style={
    'width': '100%',
    'height': '600px',
    'borderRadius': '10px',
    'border': '2px solid #e5e7eb',
    'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
}
```

## 📝 Next Steps

1. **Install dash-leaflet**: `pip install dash-leaflet==1.0.15`
2. **Restart your app**: The map should now display with Google Maps-style tiles
3. **Test interactivity**: Click markers to see popups
4. **Customize** (optional): Change tiles, colors, or add features

## 🆘 Need Help?

- **Dash Leaflet Docs**: https://www.dash-leaflet.com/
- **Leaflet.js Docs**: https://leafletjs.com/
- **Map Tiles**: https://leaflet-extras.github.io/leaflet-providers/preview/

Your map is now ready with a professional Google Maps-style interface! 🎉
