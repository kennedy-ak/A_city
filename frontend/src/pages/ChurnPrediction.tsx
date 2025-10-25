import { useQuery } from '@tanstack/react-query';
import { Users, DollarSign, AlertTriangle, TrendingDown } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { BarChart } from '../components/charts/BarChart';
import { MetricCard } from '../components/MetricCard';
import { predictionService, analyticsService } from '../services/api';

// Helper function to get suggested actions
const getSuggestedAction = (riskLevel: string, segment: string) => {
  if (riskLevel === 'Critical') {
    return 'Offer exclusive discount and personalized support';
  } else if (riskLevel === 'High') {
    return 'Send loyalty reward and check-in call';
  } else if (riskLevel === 'Medium') {
    return 'Recommend related products and engage via email campaign';
  } else {
    return 'Ensure regular high-quality content and offers';
  }
};

export function ChurnPrediction() {
  // Fetch churn predictions
  const { data: churnData, isLoading } = useQuery({
    queryKey: ['churn-predictions'],
    queryFn: () => predictionService.getChurnPredictions({ limit: 100 }).then(res => res.data),
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

  // Fetch risk distribution for revenue at risk by category
  const { data: riskData } = useQuery({
    queryKey: ['risk-distribution'],
    queryFn: () => analyticsService.getRiskDistribution().then(res => res.data),
  });

  // Prepare revenue at risk data from churn predictions
  const revenueAtRiskData = churnData ? [
    { risk: 'Low', revenue: churnData.filter((c: any) => c.churn_risk_level === 'Low').reduce((sum: number, c: any) => sum + c.monetary, 0) },
    { risk: 'Medium', revenue: churnData.filter((c: any) => c.churn_risk_level === 'Medium').reduce((sum: number, c: any) => sum + c.monetary, 0) },
    { risk: 'High', revenue: churnData.filter((c: any) => c.churn_risk_level === 'High').reduce((sum: number, c: any) => sum + c.monetary, 0) },
    { risk: 'Critical', revenue: churnData.filter((c: any) => c.churn_risk_level === 'Critical').reduce((sum: number, c: any) => sum + c.monetary, 0) },
  ] : [];

  // Mock churn drivers (no API endpoint available)
  const churnDrivers = [
    { driver: 'Inconsistent Product Quality', impact: 85, description: 'Frequent complaints about product freshness and delivery damage.' },
    { driver: 'High Pricing', impact: 78, description: 'Competitor analysis shows prices are consistently above market average.' },
    { driver: 'Poor Customer Service', impact: 60, description: 'Slow response times and unresolved issues in support tickets.' },
    { driver: 'Lack of New Products', impact: 45, description: 'Customers seeking variety not found on the platform.' },
    { driver: 'Website Usability Issues', impact: 20, description: 'Reported difficulties in navigation and checkout process.' },
  ];

  // Prepare customers at risk from API data
  const customersAtRisk = churnData?.slice(0, 20).map((customer: any) => ({
    id: customer.customer_id,
    name: customer.customer_id, // Using ID as name since no name field in API
    probability: customer.churn_probability * 100,
    risk: customer.churn_risk_level,
    action: getSuggestedAction(customer.churn_risk_level, customer.rfm_segment)
  })) || [];

  // Get risk level color
  const getRiskColor = (risk: string) => {
    const colors: Record<string, string> = {
      'Low': 'bg-gray-100 text-gray-700',
      'Medium': 'bg-yellow-100 text-yellow-700',
      'High': 'bg-orange-100 text-orange-700',
      'Critical': 'bg-red-100 text-red-700',
    };
    return colors[risk] || 'bg-gray-100 text-gray-700';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Calculate metrics from churn data
  const criticalCustomers = churnData?.filter((c: any) => c.churn_risk_level === 'Critical').length || 350;
  const customersAtRiskCount = criticalCustomers || 1250;
  const totalRevenueAtRisk = churnData?.reduce((sum: number, c: any) => sum + (c.monetary || 0), 0) || 225000;
  console.log(criticalCustomers)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Churn Prediction Dashboard</h1>
        <p className="text-gray-600 mt-1">Early warning system for customer churn detection and prevention</p>
      </div>

      {/* Top Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Key Metrics */}
        <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-4">
          <MetricCard
            title="Customers at Risk"
            value={customersAtRiskCount.toLocaleString()}
            change="Potential customers who may churn"
            changeType="neutral"
            icon={Users}
            iconColor="text-red-600"
          />
          <MetricCard
            title="Total Revenue at Risk"
            value={formatCurrency(totalRevenueAtRisk)}
            change="Estimated revenue from customers at risk"
            changeType="neutral"
            icon={DollarSign}
            iconColor="text-orange-600"
          />
        </div>

        {/* Churn Risk Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base font-semibold">Churn Risk Distribution</CardTitle>
            <CardDescription>Overall breakdown of customers by risk category</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center h-full py-8">
              <div className="relative w-48 h-48">
                <svg className="transform -rotate-90 w-48 h-48">
                  <circle
                    cx="96"
                    cy="96"
                    r="84"
                    fill="none"
                    stroke="#e5e7eb"
                    strokeWidth="16"
                  />
                  <circle
                    cx="96"
                    cy="96"
                    r="84"
                    fill="none"
                    stroke="#ec4899"
                    strokeWidth="16"
                    strokeDasharray={`${55 * 5.27} ${100 * 5.27}`}
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-4xl font-bold text-gray-900">55%</span>
                  <span className="text-sm text-gray-600">Customers at Risk</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Middle Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue at Risk by Category */}
        {/* <Card>
          <CardHeader>
            <CardTitle className="text-base font-semibold">Revenue at Risk by Category</CardTitle>
            <CardDescription>Monetary value exposed to potential churn, by risk level</CardDescription>
          </CardHeader>
          <CardContent>
            <BarChart
              title=""
              data={revenueAtRiskData}
              dataKey="revenue"
              xAxisKey="risk"
              color="#ef4444"
              valueFormatter={formatCurrency}
            />
          </CardContent>
        </Card> */}

        {/* Top Churn Drivers */}
        {/* <Card>
          <CardHeader>
            <CardTitle className="text-base font-semibold">Top Churn Drivers</CardTitle>
            <CardDescription>Key factors influencing customer churn</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {churnDrivers.map((driver, index) => (
                <div key={index} className="flex items-start gap-3">
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-gray-900">{driver.driver}</span>
                      <span className="text-sm font-semibold text-red-600">{driver.impact}%</span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-red-500 transition-all"
                        style={{ width: `${driver.impact}%` }}
                      />
                    </div>
                    <p className="text-xs text-gray-600 mt-1">{driver.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card> */}
      </div>

      {/* Customers at Risk Table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base font-semibold">Customers at Risk</CardTitle>
          <CardDescription>Detailed list of customers with churn probability and recommended actions</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-900">Customer ID</th>
                  <th className="text-left py-3 px-4 letters-spacing:0.05em text-sm font-semibold text-gray-900">Name</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-900">Probability</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-900">Risk Level</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-900">Suggested Action</th>
                </tr>
              </thead>
              <tbody>
                {customersAtRisk.map((customer) => (
                  <tr key={customer.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4 text-sm text-gray-900">{customer.id}</td>
                    <td className="py-3 px-4 text-sm text-gray-900">{customer.name}</td>
                    <td className="py-3 px-4 text-sm text-gray-900 font-medium">{customer.probability.toFixed(1)}%</td>
                    <td className="py-3 px-4">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRiskColor(customer.risk)}`}>
                        {customer.risk}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-600">{customer.action}</td>
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

