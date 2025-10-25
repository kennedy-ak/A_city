import { useQuery } from '@tanstack/react-query';
import { Users, DollarSign, TrendingDown, TrendingUp, Filter } from 'lucide-react';
import { MetricCard } from '../components/MetricCard';
import { AreaChart } from '../components/charts/AreaChart';
import { DonutChart } from '../components/charts/DonutChart';
// import { BarChart } from '../components/charts/BarChart';
import { Button } from '../components/ui/button';
import { Select } from '../components/ui/select';
import { metricsService, analyticsService } from '../services/api';

export function Overview() {
  // Fetch data
  const { data: metrics, isLoading: metricsLoading } = useQuery({
    queryKey: ['metrics'],
    queryFn: () => metricsService.getBusinessMetrics().then(res => res.data),
  });

  const { data: revenueTrendData } = useQuery({
    queryKey: ['revenue-trend'],
    queryFn: () => analyticsService.getRevenueTrend().then(res => res.data),
  });

  const { data: segmentData } = useQuery({
    queryKey: ['segment-distribution'],
    queryFn: () => analyticsService.getSegmentDistribution().then(res => res.data),
  });

  const { data: riskData } = useQuery({
    queryKey: ['risk-distribution'],
    queryFn: () => analyticsService.getRiskDistribution().then(res => res.data),
  });

  const { data: revenueBySegmentData } = useQuery({
    queryKey: ['revenue-by-segment'],
    queryFn: () => analyticsService.getRevenueBySegment().then(res => res.data),
  });

  // Format currency
  const formatCurrency = (value: number) => {
    if (value >= 1000000) {
      return `₦${(value / 1000000).toFixed(1)}M`;
    }
    return `₦${value.toLocaleString()}`;
  };

  // Format percentage
  const formatPercentage = (value: number) => `${value.toFixed(1)}%`;

  // Mock data for categories (replace with API call if available)
  // const categoryData = [
  //   { category: 'Seeds', value: 135 },
  //   { category: 'Fertilizers', value: 98 },
  //   { category: 'Tools', value: 87 },
  //   { category: 'Pesticides', value: 76 },
  //   { category: 'Irrigation', value: 65 },
  // ];

  if (metricsLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Customer Overview</h1>
        </div>
        <div className="flex items-center gap-3">
          <Select defaultValue="30">
            <option value="7">Last 7 Days</option>
            <option value="30">Last 30 Days</option>
            <option value="90">Last 90 Days</option>
            <option value="365">Last Year</option>
          </Select>
          <Button variant="outline">
            <Filter className="h-4 w-4 mr-2" />
            Filter
          </Button>
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
        <MetricCard
          title="Total Active Customers"
          value={metrics?.total_customers.toLocaleString() || '0'}
          change={`↑ ${((metrics?.active_customers || 0) / (metrics?.total_customers || 1) * 100).toFixed(1)}% vs. last month`}
          changeType="positive"
          icon={Users}
          iconColor="text-blue-600"
        />
        <MetricCard
          title="Total Revenue"
          value={formatCurrency(metrics?.total_revenue || 0)}
          change={`Forecasted: ${formatCurrency(metrics?.predicted_clv || 0)} (↑2.8% growth)`}
          changeType="positive"
          icon={DollarSign}
          iconColor="text-green-600"
        />
        <MetricCard
          title="Overall Churn Rate"
          value={formatPercentage(metrics?.churn_rate || 0)}
          change={`↓ ${(100 - (metrics?.churn_rate || 0)).toFixed(1)}% vs. last month`}
          changeType="negative"
          icon={TrendingDown}
          iconColor="text-red-600"
        />
        <MetricCard
          title="Total Predicted CLV"
          value={formatCurrency(metrics?.predicted_clv || 0)}
          change={`↑ 5.2% vs. previous period`}
          changeType="positive"
          icon={TrendingUp}
          iconColor="text-purple-600"
        />
      </div>

      {/* Charts Row 1 - Trends */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <AreaChart
          title="Active Customers Trend"
          description="Monthly active customer count"
          data={segmentData?.data || []}
          dataKey="count"
          xAxisKey="segment"
          color="#8b5cf6"
          valueFormatter={(value) => value.toLocaleString()}
        />
        <AreaChart
          title="Revenue Trend"
          description="Actual vs. Forecasted monthly revenue"
          data={revenueTrendData?.data || []}
          dataKey="revenue"
          xAxisKey="month"
          color="#ec4899"
          valueFormatter={formatCurrency}
        />
        <AreaChart
          title="Churn Rate Trend"
          description="Monthly customer churn rate percentage"
          data={riskData?.data || []}
          dataKey="count"
          xAxisKey="risk_level"
          color="#ef4444"
          valueFormatter={(value) => `${value}%`}
        />
      </div>

      {/* Charts Row 2 - Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <DonutChart
          title="Revenue Share by Segment"
          description="Distribution of revenue across customer segments"
          data={revenueBySegmentData?.data || []}
          nameKey="segment"
          valueKey="revenue"
          valueFormatter={formatCurrency}
        />
        {/* <BarChart
          title="Most Frequently Purchased Categories"
          description="Top product categories by purchase volume"
          data={categoryData}
          dataKey="value"
          xAxisKey="category"
          color="#6366f1"
          valueFormatter={(value) => value.toLocaleString()}
        /> */}
      </div>
    </div>
  );
}

