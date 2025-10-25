# Frontend Dashboard Setup Guide

## 🎉 Dashboard Built Successfully!

Your modern customer intelligence dashboard is ready with:

✅ **Sidebar Navigation** - All pages accessible from the left sidebar  
✅ **Top Navbar** - Search and user profile  
✅ **Overview Dashboard** - Real-time metrics and charts  
✅ **shadcn/ui Components** - Beautiful, accessible UI  
✅ **API Integration** - Connected to your FastAPI backend  
✅ **Responsive Design** - Works on all screen sizes

## 🚀 Quick Start (Both Backend & Frontend)

### Step 1: Start the Backend API

Open a terminal and run:

```bash
cd backend
python run.py
```

✅ Backend will start at: **http://localhost:8000**  
✅ API Docs available at: **http://localhost:8000/docs**

### Step 2: Start the Frontend

Open a **new terminal** and run:

```bash
cd frontend
npm run dev
```

✅ Frontend will start at: **http://localhost:5173**

### Step 3: Open in Browser

Navigate to **http://localhost:5173** to see your dashboard!

## 📊 Dashboard Features

### Current Pages (✅ Implemented)

1. **Overview Dashboard** (`/`)
   - 4 metric cards (Total Customers, Revenue, Churn Rate, CLV)
   - 3 trend charts (Customers, Revenue, Churn)
   - Revenue by segment (donut chart)
   - Top product categories (bar chart)
   - Date filter and Filter button
   - Real-time data from backend API

### Coming Soon (Placeholder Pages)

2. **RFM Segmentation** - `/rfm-segmentation`
3. **K-Means Clustering** - `/kmeans-clustering`
4. **Churn Prediction** - `/churn-prediction`
5. **CLV Prediction** - `/clv-prediction`
6. **Product Recommendation** - `/product-recommendation`
7. **Settings** - `/settings`
8. **Help** - `/help`

## 🎨 Components Built

### Layout Components

- **Sidebar** - Navigation with icons and active states
- **Navbar** - Search bar, notifications, user profile
- **Layout** - Main layout wrapper

### UI Components (shadcn/ui)

- **Card** - Content containers
- **Button** - Various button variants
- **Select** - Dropdown selector
- **Avatar** - User profile picture
- **MetricCard** - Displays KPIs with icons and changes

### Chart Components (Recharts)

- **AreaChart** - Filled line charts
- **LineChart** - Line charts
- **BarChart** - Bar charts
- **DonutChart** - Donut/pie charts

All charts include:

- Tooltips
- Legends
- Responsive design
- Custom formatting

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/                 # shadcn/ui components
│   │   │   ├── card.tsx
│   │   │   ├── button.tsx
│   │   │   ├── select.tsx
│   │   │   └── avatar.tsx
│   │   ├── charts/             # Chart components
│   │   │   ├── AreaChart.tsx
│   │   │   ├── LineChart.tsx
│   │   │   ├── BarChart.tsx
│   │   │   └── DonutChart.tsx
│   │   ├── Layout.tsx         # Main layout
│   │   ├── Sidebar.tsx        # Left sidebar navigation
│   │   ├── Navbar.tsx         # Top navigation bar
│   │   └── MetricCard.tsx     # Metric display card
│   ├── pages/
│   │   └── Overview.tsx       # Dashboard page
│   ├── services/
│   │   └── api.ts             # API client & services
│   ├── lib/
│   │   └── utils.ts           # Utility functions
│   ├── App.tsx                # Main app component
│   └── main.tsx              # Entry point
├── package.json
├── vite.config.ts
├── tsconfig.json
└── README.md
```

## 🔧 Technology Stack

- **React 19** - Latest React version
- **TypeScript** - Type safety
- **Vite** - Lightning-fast build tool
- **Tailwind CSS v4** - Modern utility-first CSS
- **shadcn/ui** - Beautiful component library
- **React Query** - Data fetching & caching
- **Recharts** - Chart library
- **React Router v7** - Client-side routing
- **Axios** - HTTP client
- **Lucide React** - Icon library

## 🎯 How It Works

### Data Flow

```
Backend API (FastAPI)
    ↓
API Client (Axios)
    ↓
React Query (Caching)
    ↓
Components (Display)
```

### API Integration

The dashboard automatically fetches data from these endpoints:

- `GET /api/metrics` - Business metrics
- `GET /api/analytics/revenue-trend` - Revenue data
- `GET /api/analytics/segment-distribution` - Segment data
- `GET /api/analytics/risk-distribution` - Risk data
- `GET /api/analytics/revenue-by-segment` - Revenue by segment

All API calls are:

- Cached for 5 minutes
- Automatically retried on failure
- Handled with loading states

## 🎨 Customizing the Dashboard

### Adding a New Page

1. Create a new page component:

```tsx
// src/pages/NewPage.tsx
export function NewPage() {
  return (
    <div>
      <h1>New Page</h1>
    </div>
  );
}
```

2. Add route in `App.tsx`:

```tsx
import { NewPage } from "./pages/NewPage";

// In Routes:
<Route path="new-page" element={<NewPage />} />;
```

3. Add to sidebar in `Sidebar.tsx`:

```tsx
{ name: 'New Page', href: '/new-page', icon: YourIcon }
```

### Adding a New Metric Card

```tsx
<MetricCard
  title="Your Metric"
  value="1,234"
  change="↑ 5.2%"
  changeType="positive"
  icon={YourIcon}
  iconColor="text-blue-600"
/>
```

### Adding a New Chart

```tsx
<AreaChart
  title="Your Chart"
  description="Chart description"
  data={yourData}
  dataKey="value"
  xAxisKey="date"
  color="#3b82f6"
/>
```

## 🎨 Styling

### Using Tailwind CSS

The project uses Tailwind CSS v4. Style components directly:

```tsx
<div className="flex items-center gap-4 p-6 rounded-lg bg-white shadow-sm">
  <h2 className="text-2xl font-bold text-gray-900">Title</h2>
</div>
```

### Color Palette

The dashboard uses these primary colors:

- **Blue**: `#3b82f6` - Primary actions
- **Purple**: `#8b5cf6` - Accent color
- **Pink**: `#ec4899` - Highlights
- **Red**: `#ef4444` - Warnings/Negative
- **Green**: `#10b981` - Success/Positive

## 🐛 Troubleshooting

### Backend Not Responding

**Issue:** Charts showing no data or loading forever

**Solution:**

1. Make sure backend is running: `cd backend && python run.py`
2. Check backend URL in browser: http://localhost:8000
3. Verify API docs work: http://localhost:8000/docs

### CORS Errors

**Issue:** "CORS policy" error in browser console

**Solution:**
Backend is already configured for `localhost:5173` and `localhost:3000`.  
If using different port, update `backend/app/api/main.py`:

```python
allow_origins=["http://localhost:YOUR_PORT"]
```

### Module Not Found Errors

**Solution:**

```bash
cd frontend
rm -rf node_modules
npm install
npm run dev
```

### Port Already in Use

**Solution:**

```bash
# Frontend (default 5173)
# Vite will automatically use next available port

# Backend (port 8000)
# Edit backend/run.py to change port
```

## 📊 Sample Data

The dashboard displays real data from your backend. To see different data:

1. **Update CSV files** in project root:

   - `rfm_with_predictions.csv`
   - `transactions_clean.csv`
   - `product_recommendations.csv`

2. **Restart backend** to reload data

## 🚀 Next Steps

### Immediate

1. ✅ Both servers are running
2. ✅ Open http://localhost:5173
3. ✅ Explore the dashboard

### Build Other Pages

Follow the `REACT_INTEGRATION.md` guide in the backend folder to build:

- Customer list with filters
- Customer detail profiles
- RFM segmentation view
- Churn prediction tables
- CLV analysis charts

### Deploy to Production

**Frontend:**

```bash
npm run build
# Deploy dist/ folder to Vercel, Netlify, etc.
```

**Backend:**
See `backend/README.md` for deployment options

## 💡 Tips

1. **Hot Reload** - Changes auto-refresh the browser
2. **Component Library** - Use shadcn/ui for consistent design
3. **Type Safety** - TypeScript prevents bugs
4. **Data Caching** - React Query caches API responses
5. **Responsive** - Dashboard works on mobile devices

## 📚 Resources

- **Tailwind Docs**: https://tailwindcss.com/docs
- **shadcn/ui**: https://ui.shadcn.com/
- **React Query**: https://tanstack.com/query/latest
- **Recharts**: https://recharts.org/
- **Lucide Icons**: https://lucide.dev/

## ✨ Success!

Your dashboard is now:

- ✅ Running at http://localhost:5173
- ✅ Connected to backend API
- ✅ Displaying real-time metrics
- ✅ Using modern UI components
- ✅ Fully responsive

**Enjoy building your customer intelligence platform! 🚀**
