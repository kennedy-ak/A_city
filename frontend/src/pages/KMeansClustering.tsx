import { useQuery } from '@tanstack/react-query';
import { TrendingUp, Users, AlertCircle, Filter } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { DonutChart } from '../components/charts/DonutChart';
import { Button } from '../components/ui/button';
import { segmentService } from '../services/api';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';

export function KMeansClustering() {
  // Fetch K-Means segments
  const { data: clusters, isLoading } = useQuery({
    queryKey: ['kmeans-clusters'],
    queryFn: () => segmentService.getSegments('kmeans').then(res => res.data),
  });

  // Mock scatter plot data (replace with API call)
  const scatterData = [
    { x: 1000, y: 15, cluster: 'High-Value Loyalists' },
    { x: 1500, y: 20, cluster: 'High-Value Loyalists' },
    { x: 2000, y: 25, cluster: 'High-Value Loyalists' },
    { x: 2500, y: 18, cluster: 'High-Value Loyalists' },
    { x: 500, y: 8, cluster: 'New Engagers' },
    { x: 600, y: 6, cluster: 'New Engagers' },
    { x: 700, y: 10, cluster: 'New Engagers' },
    { x: 300, y: 2, cluster: 'Dormant Wakables' },
    { x: 400, y: 3, cluster: 'Dormant Wakables' },
    { x: 350, y: 1, cluster: 'Dormant Wakables' },
  ];

  // Prepare donut chart data
  const revenueData = clusters?.map(cluster => ({
    segment: cluster.segment_name,
    revenue: cluster.total_revenue
  })) || [];

  // Mock customer details (replace with API call)
  const customerDetails = [
    { id: 'AMB-2023-001', cluster: 'HV-L', lastPurchase: '2025-05-25', spend: 4235 },
    { id: 'AMB-2023-002', cluster: 'NE-L', lastPurchase: '2025-03-28', spend: 832 },
    { id: 'AMB-2023-003', cluster: 'DW-L', lastPurchase: '2025-01-15', spend: 1632 },
    { id: 'AMB-2023-004', cluster: 'DW-R', lastPurchase: '2024-11-03', spend: 752 },
    { id: 'AMB-2023-005', cluster: 'HV-L', lastPurchase: '2025-05-27', spend: 5126 },
    { id: 'AMB-2023-006', cluster: 'CS-R', lastPurchase: '2025-01-01', spend: 385 },
    { id: 'AMB-2023-007', cluster: 'HV-L', lastPurchase: '2025-04-12', spend: 4850 },
    { id: 'AMB-2023-008', cluster: 'NE-L', lastPurchase: '2025-02-18', spend: 1260 },
    { id: 'AMB-2023-009', cluster: 'DW-L', lastPurchase: '2024-12-08', spend: 825 },
  ];

  // Cluster colors
  const clusterColors: Record<string, string> = {
    'High-Value Loyalists': '#3b82f6',
    'New Engagers': '#8b5cf6',
    'Dormant Wakables': '#ec4899',
    'Churn Risk': '#ef4444',
  };

  const formatCurrency = (value: number) => {
    if (value >= 1000000) {
      return `₦${(value / 1000000).toFixed(1)}M`;
    }
    if (value >= 1000) {
      return `₦${(value / 1000).toFixed(0)}K`;
    }
    return `₦${value.toLocaleString()}`;
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
        <h1 className="text-3xl font-bold text-gray-900">K-Means Clustering Analysis</h1>
        <p className="text-gray-600 mt-1">
          Data-driven insights into customer behavior by segmenting them into distinct clusters based on purchase patterns and engagement metrics
        </p>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Scatter Plot */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-base font-semibold">Customer Cluster Scatter Plot</CardTitle>
              <CardDescription>Clustering customer segments based on spend and purchase frequency</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis
                    type="number"
                    dataKey="x"
                    name="Total Spend"
                    tick={{ fontSize: 12 }}
                    stroke="#9ca3af"
                    label={{ value: 'Total Spend ($)', position: 'bottom', offset: 0 }}
                  />
                  <YAxis
                    type="number"
                    dataKey="y"
                    name="Purchase Frequency"
                    tick={{ fontSize: 12 }}
                    stroke="#9ca3af"
                    label={{ value: 'Purchase Frequency', angle: -90, position: 'left' }}
                  />
                  <Tooltip
                    cursor={{ strokeDasharray: '3 3' }}
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        return (
                          <div className="rounded-lg border bg-white p-3 shadow-lg">
                            <p className="text-sm font-medium text-gray-900">{payload[0].payload.cluster}</p>
                            <p className="text-xs text-gray-600">Spend: ${payload[0].value}</p>
                            <p className="text-xs text-gray-600">Frequency: {payload[1].value}</p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  {Object.keys(clusterColors).map((cluster) => (
                    <Scatter
                      key={cluster}
                      name={cluster}
                      data={scatterData.filter(d => d.cluster === cluster)}
                      fill={clusterColors[cluster]}
                    >
                      {scatterData.filter(d => d.cluster === cluster).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={clusterColors[cluster]} />
                      ))}
                    </Scatter>
                  ))}
                </ScatterChart>
              </ResponsiveContainer>
              <div className="flex items-center justify-center gap-6 mt-4">
                {Object.entries(clusterColors).map(([cluster, color]) => (
                  <div key={cluster} className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }}></div>
                    <span className="text-xs text-gray-600">{cluster}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Donut Chart */}
        <div className="lg:col-span-1">
          <Card className="h-full">
            <CardHeader>
              <CardTitle className="text-base font-semibold">Revenue Contribution by Cluster</CardTitle>
              <CardDescription>Breakdown of total revenue attributed to each customer segment</CardDescription>
            </CardHeader>
            <CardContent>
              <DonutChart
                title=""
                data={revenueData}
                nameKey="segment"
                valueKey="revenue"
                valueFormatter={formatCurrency}
              />
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Cluster Profiles */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Cluster Profiles</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* High-Value Loyalists */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-start gap-3">
                <div className="rounded-full p-2 bg-blue-50">
                  <TrendingUp className="h-5 w-5 text-blue-600" />
                </div>
                <div className="flex-1">
                  <h3 className="text-sm font-semibold text-gray-900 mb-2">High-Value Loyalists</h3>
                  <p className="text-xs text-gray-600 leading-relaxed">
                    These customers are your most valuable, characterized by high spending and 
                    repeat purchases. Focus on retaining them through VIP programs and personalized offers.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* New Engagers */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-start gap-3">
                <div className="rounded-full p-2 bg-pink-50">
                  <Users className="h-5 w-5 text-pink-600" />
                </div>
                <div className="flex-1">
                  <h3 className="text-sm font-semibold text-gray-900 mb-2">New Engagers</h3>
                  <p className="text-xs text-gray-600 leading-relaxed">
                    Recently acquired customers with moderate spending and good activity. 
                    Nurture them with targeted campaigns to increase engagement.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Dormant Wakables */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-start gap-3">
                <div className="rounded-full p-2 bg-orange-50">
                  <AlertCircle className="h-5 w-5 text-orange-600" />
                </div>
                <div className="flex-1">
                  <h3 className="text-sm font-semibold text-gray-900 mb-2">Dormant Wakables</h3>
                  <p className="text-xs text-gray-600 leading-relaxed">
                    Customers who were once active but have since decreased activity. 
                    They might be at risk of churning, so reactivation campaigns are essential.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Customer Details Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-base font-semibold">Customer Details by Cluster</CardTitle>
              <CardDescription>View and filter individual customer data based on their assigned cluster</CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm">
                <Filter className="h-4 w-4 mr-2" />
                Filter
              </Button>
              <Button variant="outline" size="sm">
                Export
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-900">Customer ID</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-900">Cluster ID</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-900">Last Purchase Date</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-gray-900">Spend</th>
                </tr>
              </thead>
              <tbody>
                {customerDetails.map((customer) => (
                  <tr key={customer.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4 text-sm text-gray-900">{customer.id}</td>
                    <td className="py-3 px-4 text-sm">
                      <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-50 text-blue-700">
                        {customer.cluster}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-600">{customer.lastPurchase}</td>
                    <td className="py-3 px-4 text-sm text-gray-900 text-right">${customer.spend.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

