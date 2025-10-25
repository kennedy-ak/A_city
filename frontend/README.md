# Afrimash Customer Intelligence Dashboard

Modern React + TypeScript dashboard for customer analytics and intelligence.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The app will be available at **http://localhost:5173**

## 📋 Prerequisites

Make sure the backend API is running:

```bash
cd ../backend
python run.py
```

The backend should be running at **http://localhost:8000**

## 🎨 Features

- **Overview Dashboard** - Real-time metrics and KPIs
- **Customer Segmentation** - RFM and K-Means clustering
- **Predictive Analytics** - Churn and CLV predictions
- **Product Recommendations** - AI-powered suggestions
- **Interactive Charts** - Area, line, bar, and donut charts
- **Responsive Design** - Works on all devices

## 🛠️ Tech Stack

- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI components
- **React Query** - Data fetching
- **Recharts** - Charts
- **React Router** - Navigation
- **Axios** - HTTP client

## 📁 Project Structure

```
src/
├── components/
│   ├── ui/              # shadcn/ui components
│   ├── charts/          # Chart components
│   ├── Layout.tsx       # Main layout
│   ├── Sidebar.tsx      # Navigation sidebar
│   ├── Navbar.tsx       # Top navigation
│   └── MetricCard.tsx   # Metric display card
├── pages/
│   └── Overview.tsx     # Dashboard page
├── services/
│   └── api.ts           # API client & services
├── lib/
│   └── utils.ts         # Utility functions
├── App.tsx              # Main app component
└── main.tsx            # Entry point
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
```

For production:

```env
VITE_API_URL=https://your-api-domain.com
```

## 📊 Available Pages

- `/` - Overview Dashboard
- `/rfm-segmentation` - RFM Segmentation Analysis
- `/kmeans-clustering` - K-Means Clustering
- `/churn-prediction` - Churn Prediction
- `/clv-prediction` - Customer Lifetime Value
- `/product-recommendation` - Product Recommendations
- `/settings` - Settings
- `/help` - Help & Support

## 🎨 Customization

### Adding New Pages

1. Create a new component in `src/pages/`
2. Add route in `src/App.tsx`
3. Add navigation item in `src/components/Sidebar.tsx`

### Adding New Charts

Import chart components from `src/components/charts/`:

```tsx
import { AreaChart } from "@/components/charts/AreaChart";
import { BarChart } from "@/components/charts/BarChart";
import { DonutChart } from "@/components/charts/DonutChart";
import { LineChart } from "@/components/charts/LineChart";
```

### Styling

This project uses Tailwind CSS. Modify styles directly in components using Tailwind classes.

## 📦 Building for Production

```bash
npm run build
```

The optimized build will be in the `dist/` folder.

### Preview Production Build

```bash
npm run preview
```

## 🐛 Troubleshooting

### API Connection Issues

- Verify backend is running at `http://localhost:8000`
- Check CORS settings in backend (`backend/app/api/main.py`)
- Ensure `.env` file has correct API URL

### Module Not Found Errors

- Restart the dev server: `npm run dev`
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`

### Type Errors

- Update TypeScript: `npm install -D typescript@latest`
- Clear TypeScript cache: Delete `.tsbuildinfo` files

## 📝 Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## 🤝 Contributing

1. Create a new branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📄 License

Copyright © 2025 Afrimash

---

Built with ❤️ using React + TypeScript + Vite
