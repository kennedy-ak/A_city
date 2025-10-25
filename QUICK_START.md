# 🚀 Quick Start Guide

## Start Your Dashboard in 3 Steps

### Step 1️⃣: Start Backend API

Open **Terminal 1** and run:

```bash
cd backend
python run.py
```

You should see:

```
🚀 Starting Afrimash Customer Intelligence API
📍 Server: http://0.0.0.0:8000
📚 Docs: http://localhost:8000/docs
```

✅ Backend running at: **http://localhost:8000**

---

### Step 2️⃣: Start Frontend Dashboard

Open **Terminal 2** (keep Terminal 1 running) and run:

```bash
cd frontend
npm run dev
```

You should see:

```
VITE v7.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

✅ Frontend running at: **http://localhost:5173**

---

### Step 3️⃣: Open Dashboard

Open your browser and navigate to:

## 🌐 **http://localhost:5173**

---

## 🎨 What You'll See

Your dashboard with:

### Top Section

- **Search bar** for customers
- **Notification bell** icon
- **User avatar** (top right)

### Left Sidebar

- 📊 Overview (active)
- 👥 RFM Segmentation
- 🔀 K-Means Clustering
- 📉 Churn Prediction
- 💰 CLV Prediction
- 🛍️ Product Recommendation
- ⚙️ Settings (bottom)
- ❓ Help (bottom)

### Main Dashboard

**4 Metric Cards:**

1. 👥 Total Active Customers
2. 💵 Total Revenue
3. 📊 Overall Churn Rate
4. 💎 Total Predicted CLV

**5 Charts:**

1. Active Customers Trend (purple area chart)
2. Revenue Trend (pink area chart)
3. Churn Rate Trend (red area chart)
4. Revenue Share by Segment (donut chart)
5. Top Product Categories (bar chart)

**Controls:**

- Date range selector (Last 30 Days)
- Filter button

---

## ✅ Checklist

Before starting:

- [ ] Backend CSV files exist in project root
- [ ] Python virtual environment activated
- [ ] Node.js and npm installed
- [ ] Two terminal windows available

After starting:

- [ ] Backend shows "ready" message
- [ ] Frontend shows Vite dev server URL
- [ ] No error messages in either terminal
- [ ] Browser shows dashboard

---

## 🐛 Troubleshooting

### Backend won't start

```bash
cd backend
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
python run.py
```

### Frontend won't start

```bash
cd frontend
rm -rf node_modules
npm install
npm run dev
```

### Dashboard shows "loading" forever

- Check backend is running at http://localhost:8000
- Visit http://localhost:8000/api/metrics in browser
- Check browser console for errors (F12)

### Port already in use

- Backend: Edit `backend/run.py` to change port
- Frontend: Vite auto-uses next available port

---

## 📚 Full Documentation

- **Frontend Setup**: `FRONTEND_SETUP.md`
- **Dashboard Complete**: `DASHBOARD_COMPLETE.md`
- **Backend API**: `BACKEND_QUICKSTART.md`
- **React Integration**: `backend/REACT_INTEGRATION.md`

---

## 🎉 Success!

Once both servers are running and you see the dashboard:

✅ **Backend API** serving data  
✅ **Frontend Dashboard** displaying metrics  
✅ **Charts** showing real data  
✅ **Navigation** working smoothly

**Your customer intelligence platform is LIVE! 🚀**

---

## 💡 Quick Tips

1. **Changes auto-reload** - Edit code and see updates instantly
2. **API docs available** at http://localhost:8000/docs
3. **Data cached** for 5 minutes for performance
4. **Fully responsive** - Try it on mobile!

---

**Need help?** Check the detailed guides in the documentation files listed above.

**Happy analyzing! 📊✨**
