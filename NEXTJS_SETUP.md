# Next.js Frontend - Setup & Integration Guide

## 🚀 Overview

This is a modern **Next.js 14** frontend for your Orthopedic Implant Analytics Dashboard, replacing the Dash application with a faster, more reliable chart rendering system using **Recharts**.

### Key Features
- ✅ **Modern React 18** with TypeScript
- ✅ **Recharts** for beautiful, responsive charts
- ✅ **Tailwind CSS** for styling
- ✅ **Zustand** for state management
- ✅ **Zero React Children Errors** - Proper serialization
- ✅ **Server-side rendering** with Next.js
- ✅ **Responsive Design** - Mobile friendly
- ✅ **Authentication UI** - Ready for login integration

---

## 📋 Installation & Setup

### 1. Install Dependencies
```bash
cd /Users/bhurvasharma/dashboard/frontend-nextjs
npm install
```

### 2. Environment Configuration
Already configured in `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:5000
```

### 3. Start Development Server
```bash
npm run dev
```

Then open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🏗️ Project Structure

```
frontend-nextjs/
├── src/
│   ├── app/
│   │   ├── page.tsx              # Main dashboard
│   │   ├── login/page.tsx        # Login page
│   │   ├── tables/page.tsx       # Data tables
│   │   ├── dashboard/page.tsx    # Dashboard route
│   │   └── layout.tsx            # Root layout
│   ├── components/
│   │   ├── Charts.tsx            # Recharts components
│   │   ├── DataTable.tsx         # Data table component
│   │   ├── Layout.tsx            # Main layout wrapper
│   │   ├── Header.tsx            # Top header
│   │   └── Sidebar.tsx           # Sidebar with controls
│   └── lib/
│       ├── api.ts                # API client
│       ├── store.ts              # Zustand stores
│       └── utils.ts              # Utility functions
├── public/                        # Static assets
├── .env.local                    # Environment variables
├── next.config.ts                # Next.js config
├── package.json                  # Dependencies
└── tsconfig.json                 # TypeScript config
```

---

## 🔌 Backend Integration

### Flask Backend Setup

Your Python Flask app needs to serve this Next.js frontend. Here's how to integrate:

#### 1. Update `app.py` to serve the Next.js frontend:

```python
# Add to your Flask app (app.py)
import os
from flask import send_from_directory

# After your existing Dash app setup
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve Next.js frontend"""
    frontend_build = os.path.join(os.path.dirname(__file__), 'frontend-nextjs/out')
    
    if path != '' and os.path.exists(os.path.join(frontend_build, path)):
        return send_from_directory(frontend_build, path)
    else:
        return send_from_directory(frontend_build, 'index.html')

# CORS configuration for API requests
from flask_cors import CORS
CORS(app)
```

#### 2. Build the Next.js frontend for production:

```bash
cd frontend-nextjs
npm run build
```

#### 3. Update Python requirements if needed:

```bash
pip install flask-cors
```

---

## 🔗 API Integration Examples

### Making API calls from the frontend

The API client is ready in `src/lib/api.ts`. Here's how to use it:

```typescript
import { dashboardAPI } from '@/lib/api';

// Get sales report
const salesData = await dashboardAPI.getSalesReport('01-01-2024', '31-01-2024', false);

// Get dealer performance
const dealerPerf = await dashboardAPI.getDealerPerformance('01-01-2024', '31-01-2024', false);

// Get dashboard stats
const stats = await dashboardAPI.getDashboardStats('01-01-2024', '31-01-2024', false);
```

---

## 📊 Charts Available

The frontend includes these chart types:

1. **RevenueLineChart** - Time series data
2. **RevenueBarChart** - Categorical comparison
3. **RevenuePieChart** - Distribution charts
4. **HeatmapChart** - 2D data visualization

### Example usage:
```tsx
import { RevenueLineChart } from '@/components/Charts';

<RevenueLineChart
  data={chartData}
  title="Revenue Trend"
  xKey="date"
  yKey="revenue"
  loading={loading}
/>
```

---

## 🛠️ Backend API Endpoints Required

Your Flask backend should provide these endpoints:

```
GET  /api/avante/sales?start_date=DD-MM-YYYY&end_date=DD-MM-YYYY
GET  /api/avante/stats?start_date=DD-MM-YYYY&end_date=DD-MM-YYYY
GET  /api/avante/dealer-performance?start_date=DD-MM-YYYY&end_date=DD-MM-YYYY
GET  /api/avante/state-performance?start_date=DD-MM-YYYY&end_date=DD-MM-YYYY
GET  /api/avante/category-performance?start_date=DD-MM-YYYY&end_date=DD-MM-YYYY
GET  /api/avante/city-performance?start_date=DD-MM-YYYY&end_date=DD-MM-YYYY

GET  /api/iospl/sales?start_date=DD-MM-YYYY&end_date=DD-MM-YYYY
GET  /api/iospl/stats?start_date=DD-MM-YYYY&end_date=DD-MM-YYYY
GET  /api/iospl/dealer-performance?start_date=DD-MM-YYYY&end_date=DD-MM-YYYY
...and similar for IOSPL
```

Each endpoint should return JSON data compatible with the chart components.

---

## 🚀 Deployment

### Vercel (Recommended)
```bash
npm install -g vercel
vercel --prod
```

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY . .
RUN npm install
RUN npm run build
CMD ["npm", "start"]
```

### Environment Variables for Production
Update your `.env.production.local`:
```
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

---

## 📝 Development Notes

- **Charts are rendered with Recharts** - No Dash/React children errors
- **State managed with Zustand** - Lightweight and performant
- **TypeScript** - Full type safety
- **Tailwind CSS** - Utility-first styling
- **All components are client-side** - Use `'use client'` directive

---

## 🐛 Troubleshooting

### Port 3000 already in use
```bash
lsof -i :3000
kill -9 <PID>
```

### API not connecting
1. Check `NEXT_PUBLIC_API_URL` in `.env.local`
2. Ensure Flask backend is running on port 5000
3. Check CORS is enabled in Flask app

### Charts not rendering
- Check browser console for errors
- Verify data format matches chart requirements
- Ensure data has required keys (xKey, yKey, etc)

---

## 📚 Additional Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Recharts Documentation](https://recharts.org)
- [Tailwind CSS](https://tailwindcss.com)
- [Zustand](https://github.com/pmndrs/zustand)

---

## ✅ Next Steps

1. ✅ Update your Flask backend to serve this frontend
2. ✅ Create the required API endpoints (if not already existing)
3. ✅ Test the integration locally
4. ✅ Build for production: `npm run build`
5. ✅ Deploy to your preferred platform

---

**Happy coding! 🎉**
