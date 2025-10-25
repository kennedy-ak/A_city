import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/Layout';
import { Overview } from './pages/Overview';
import { RFMSegmentation } from './pages/RFMSegmentation';
import { KMeansClustering } from './pages/KMeansClustering';
import { ChurnPrediction } from './pages/ChurnPrediction';
import { CLVPrediction } from './pages/CLVPrediction';
import { ProductRecommendation } from './pages/ProductRecommendation';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

// Placeholder pages

const Settings = () => (
  <div className="flex items-center justify-center h-full">
    <div className="text-center">
      <h1 className="text-3xl font-bold text-gray-900 mb-4">Settings</h1>
      <p className="text-gray-600">Coming soon...</p>
    </div>
  </div>
);

const Help = () => (
  <div className="flex items-center justify-center h-full">
    <div className="text-center">
      <h1 className="text-3xl font-bold text-gray-900 mb-4">Help</h1>
      <p className="text-gray-600">Coming soon...</p>
    </div>
  </div>
);

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Overview />} />
            <Route path="rfm-segmentation" element={<RFMSegmentation />} />
            <Route path="kmeans-clustering" element={<KMeansClustering />} />
            <Route path="churn-prediction" element={<ChurnPrediction />} />
            <Route path="clv-prediction" element={<CLVPrediction />} />
            <Route path="product-recommendation" element={<ProductRecommendation />} />
            <Route path="settings" element={<Settings />} />
            <Route path="help" element={<Help />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
