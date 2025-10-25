import { useQuery } from '@tanstack/react-query';
import { Users, TrendingUp, AlertTriangle } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { BarChart } from '../components/charts/BarChart';
import { LineChart } from '../components/charts/LineChart';
import { segmentService } from '../services/api';

export function RFMSegmentation() {
  // Fetch segment data
  const { data: segments, isLoading } = useQuery({
    queryKey: ['rfm-segments'],
    queryFn: () => segmentService.getSegments('rfm').then(res => res.data),
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

  // Prepare bar chart data
  const barChartData = segments?.map((seg: any) => ({
    segment: seg.segment_name,
    customers: seg.customer_count
  })) || [];

  // Mock movement data (replace with API call if available)
//   const movementData = [
//     { month: 'Jan', Champions: 2300, Loyal: 3800, 'At Risk': 1100, 'New Customers': 1400 },
//     { month: 'Feb', Champions: 2400, Loyal: 3900, 'At Risk': 1150, 'New Customers': 1450 },
//     { month: 'Mar', Champions: 2450, Loyal: 3950, 'At Risk': 1180, 'New Customers': 1480 },
//     { month: 'Apr', Champions: 2480, Loyal: 3980, 'At Risk': 1190, 'New Customers': 1490 },
//     { month: 'May', Champions: 2500, Loyal: 4000, 'At Risk': 1200, 'New Customers': 1500 },
//   ];

//   // Mock customer data (replace with API call)
//   const customerScores = [
//     { id: 'CUS1001', name: 'Alice Johnson', recency: 5, frequency: 12, monetary: 25375, segment: 'Champions' },
//     { id: 'CUS1002', name: 'Bob Smith', recency: 25, frequency: 8, monetary: 8502, segment: 'Loyal' },
//     { id: 'CUS1003', name: 'Charlie Davis', recency: 45, frequency: 3, monetary: 2350, segment: 'Need Attention' },
//     { id: 'CUS1004', name: 'Diana Prince', recency: 60, frequency: 5, monetary: 3500, segment: 'At Risk' },
//     { id: 'CUS1005', name: 'Eve Adams', recency: 120, frequency: 2, monetary: 1200, segment: 'Hibernating' },
//   ];

  // Get segment colors
  const getSegmentColor = (segment: string) => {
    const colors: Record<string, string> = {
      'Champions': 'bg-blue-100 text-blue-700',
      'Loyal': 'bg-green-100 text-green-700',
      'At Risk': 'bg-red-100 text-red-700',
      'Need Attention': 'bg-orange-100 text-orange-700',
      'Hibernating': 'bg-gray-100 text-gray-700',
    };
    return colors[segment] || 'bg-gray-100 text-gray-700';
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
        <h1 className="text-3xl font-bold text-gray-900">RFM Segmentation Dashboard</h1>
        <p className="text-gray-600 mt-1">Customer value across different RFM segments</p>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-1 gap-6">
        {/* Left Column - Bar Chart */}
        <div className="lg:col-span-1">
          <BarChart
            title="RFM Segment Distribution"
            description="Customer count across segments"
            data={barChartData}
            dataKey="customers"
            xAxisKey="segment"
            color="#6366f1"
            valueFormatter={(value) => value.toLocaleString()}
          />
        </div>

        {/* Right Column - Performance Cards */}
        <div className="lg:col-span-2">
          <div className="mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Key Segment Performance</h2>
            <p className="text-sm text-gray-600">Revenue and customer distribution by segment</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {segments?.slice(0, 6).map((segment: any, index: number) => {
              const icons = [Users, TrendingUp, AlertTriangle, Users, TrendingUp, AlertTriangle];
              const colors = ['text-blue-600', 'text-green-600', 'text-red-600', 'text-purple-600', 'text-orange-600', 'text-gray-600'];
              const Icon = icons[index % icons.length];
              
              return (
                <Card key={segment.segment_name}>
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <div className="h-2 w-2 rounded-full bg-blue-600"></div>
                          <h3 className="text-sm font-semibold text-gray-900">{segment.segment_name}</h3>
                        </div>
                        <div className="space-y-1">
                          <p className="text-2xl font-bold text-blue-600">{segment.customer_count.toLocaleString()}</p>
                          <p className="text-xs text-gray-600">Customers</p>
                          <p className="text-xl font-bold text-pink-600 mt-2">{formatCurrency(segment.total_revenue)}</p>
                          <p className="text-xs text-gray-600">Revenue</p>
                          <p className="text-xs text-gray-500 mt-2">
                            Avg spend: {formatCurrency(segment.avg_revenue)} | Frequency: {segment.avg_frequency.toFixed(1)}x
                          </p>
                        </div>
                      </div>
                      <div className={`rounded-full p-3 bg-blue-50 ${colors[index % colors.length]}`}>
                        <Icon className="h-5 w-5" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </div>

     

      {/* Detailed Customer RFM Scores */}
     
    </div>
  );
}

