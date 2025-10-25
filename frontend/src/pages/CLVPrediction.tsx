import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { TrendingUp, Search } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { BarChart } from '../components/charts/BarChart';
import { LineChart } from '../components/charts/LineChart';
import { predictionService, analyticsService } from '../services/api';

export function CLVPrediction() {
  const [searchQuery, setSearchQuery] = useState('');
  const [lookupResult, setLookupResult] = useState<any>(null);

  // Fetch CLV predictions
  const { data: clvData, isLoading } = useQuery({
    queryKey: ['clv-predictions'],
    queryFn: () => predictionService.getCLVPredictions({ limit: 100 }).then(res => res.data),
  });

  // Fetch CLV distribution data
  const { data: clvDistribution } = useQuery({
    queryKey: ['clv-distribution'],
    queryFn: () => analyticsService.getCLVDistribution().then(res => res.data),
  });

  // Format currency
  const formatCurrency = (value: number) => {
    if (value >= 1000000) {
      return `₦${(value / 1000000).toFixed(1)}M`;
    }
    if (value >= 1000) {
      return `₦${(value / 1000).toFixed(0)}K`;
    }
    return `₦${value.toLocaleString()}`;
  };

  // Prepare CLV distribution data from API
  const clvDistributionData = clvDistribution?.data?.map((item: any) => ({
    range: formatCurrency(item.bin_start),
    count: item.count
  })) || [];

  // Mock revenue forecast data
  const revenueForecastData = [
    { month: 'Jan', actual: 80000, forecasted: null },
    { month: 'Feb', actual: 85000, forecasted: null },
    { month: 'Mar', actual: 90000, forecasted: null },
    { month: 'Apr', actual: 95000, forecasted: null },
    { month: 'May', actual: 100000, forecasted: null },
    { month: 'Jun', actual: 105000, forecasted: null },
    { month: 'Jul', actual: 110000, forecasted: null },
    { month: 'Aug', actual: 115000, forecasted: null },
    { month: 'Sep', actual: null, forecasted: 120000 },
    { month: 'Oct', actual: null, forecasted: 125000 },
    { month: 'Nov', actual: null, forecasted: 130000 },
    { month: 'Dec', actual: null, forecasted: 135000 },
  ];

  // Mock spending allocation
  const spendingAllocation = [
    { category: 'Acquisition', percentage: 40, color: 'bg-blue-500' },
    { category: 'Retention', percentage: 30, color: 'bg-pink-500' },
    { category: 'Upselling/Cross-selling', percentage: 20, color: 'bg-purple-500' },
    { category: 'Brand Loyalty Programs', percentage: 10, color: 'bg-orange-500' },
  ];

  // Mock customer segments
  const customerSegments = [
    {
      title: 'VIP Customers',
      description: 'Highest value, most loyal customers',
      clv: '₦1250K',
      count: 70,
      share: '35%',
      trend: '+9.3%'
    },
    {
      title: 'High Value',
      description: 'Consistent spenders with high potential',
      clv: '₦780K',
      count: 180,
      share: '28%',
      trend: '+5.2%'
    },
    {
      title: 'Mid Value',
      description: 'Regular customers with moderate spending',
      clv: '₦320K',
      count: 420,
      share: '22%',
      trend: '+2.1%'
    },
    {
      title: 'Low Value',
      description: 'New or infrequent customers, high churn risk',
      clv: '₦85K',
      count: 650,
      share: '15%',
      trend: '-1.5%'
    },
  ];

  const handleLookup = () => {
    // Lookup customer from CLV data
    const found = clvData?.find((c: any) => 
      c.customer_id.toLowerCase().includes(searchQuery.toLowerCase())
    );
    
    if (found) {
      setLookupResult({
        customerId: found.customer_id,
        predictedCLV: formatCurrency(found.predicted_clv),
        tier: found.clv_category,
        retentionRisk: found.churn_probability < 0.3 ? 'Low' : found.churn_probability < 0.6 ? 'Medium' : 'High'
      });
    } else {
      setLookupResult({
        customerId: 'Not Found',
        predictedCLV: 'N/A',
        tier: 'N/A',
        retentionRisk: 'N/A'
      });
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Customer Lifetime Value (CLV) Prediction</h1>
        <p className="text-gray-600 mt-1">Forecast customer value and optimize marketing spend</p>
      </div>

      {/* Customer Segmentation Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {customerSegments.map((segment, index) => (
          <Card key={index}>
            <CardContent className="p-6">
              <div className="flex items-start justify-between mb-2">
                <h3 className="text-sm font-semibold text-gray-900">{segment.title}</h3>
                <span className="text-xs font-medium text-green-600">{segment.trend}</span>
              </div>
              <p className="text-xs text-gray-600 mb-4">{segment.description}</p>
              <div className="space-y-2">
                <div>
                  <p className="text-2xl font-bold text-purple-600">{segment.clv}</p>
                  <p className="text-xs text-gray-600">Predicted CLV</p>
                </div>
                <div className="flex items-center justify-between pt-2 border-t border-gray-200">
                  <div>
                    <p className="text-sm font-semibold text-gray-900">{segment.count}</p>
                    <p className="text-xs text-gray-600">Customers</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold text-gray-900">{segment.share}</p>
                    <p className="text-xs text-gray-600">Share</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* CLV Distribution */}
        <div className="lg:col-span-1">
          <BarChart
            title="Predicted CLV Score Distribution"
            description="Frequency of customers across different CLV score ranges"
            data={clvDistributionData}
            dataKey="count"
            xAxisKey="range"
            color="#8b5cf6"
            valueFormatter={(value) => value.toLocaleString()}
          />
        </div>

        {/* Revenue Forecast */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-base font-semibold">Revenue Forecast</CardTitle>
              <CardDescription>Historical and projected monthly revenue trends</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-80">
                <LineChart
                  title=""
                  data={revenueForecastData}
                  dataKey="actual"
                  xAxisKey="month"
                  color="#3b82f6"
                  valueFormatter={(value) => value ? formatCurrency(value) : ''}
                />
              </div>
              <div className="flex items-center justify-center gap-4 mt-4">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-blue-600"></div>
                  <span className="text-xs text-gray-600">Actual Revenue</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 border-2 border-red-500"></div>
                  <span className="text-xs text-gray-600">Forecasted Revenue</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Bottom Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Spending Allocation */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base font-semibold">Recommended Spending Allocation</CardTitle>
            <CardDescription>Optimized budget allocation for different customer segments</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {spendingAllocation.map((item, index) => (
                <div key={index}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-900">{item.category}</span>
                    <span className="text-sm font-semibold text-gray-700">{item.percentage}%</span>
                  </div>
                  <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${item.color} transition-all`}
                      style={{ width: `${item.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Individual CLV Lookup */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base font-semibold">Individual CLV Lookup</CardTitle>
            <CardDescription>Search for a customer to view their predicted Lifetime Value</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Enter Customer ID or Email"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full h-10 pl-10 pr-4 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                <Button className="bg-purple-600 hover:bg-purple-700" onClick={handleLookup}>
                  Lookup CLV
                </Button>
              </div>

              {lookupResult && (
                <div className="mt-4 p-4 bg-purple-50 rounded-lg border border-purple-200">
                  <h4 className="text-sm font-semibold text-gray-900 mb-3">Customer Details</h4>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-600">Customer ID:</span>
                      <span className="text-xs font-medium text-gray-900">{lookupResult.customerId}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-600">Predicted CLV:</span>
                      <span className="text-xs font-semibold text-purple-600">{lookupResult.predictedCLV}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-600">Tier:</span>
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-700">
                        {lookupResult.tier}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-600">Retention Risk:</span>
                      <span className="text-xs font-medium text-green-600">{lookupResult.retentionRisk}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

