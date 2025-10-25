import { useQuery } from '@tanstack/react-query';
import { Sparkles } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Select } from '../components/ui/select';
import { customerService, recommendationService } from '../services/api';

export function ProductRecommendation() {
  // Fetch first 4 customers for recommendations
  const { data: customersData } = useQuery({
    queryKey: ['customers-preview'],
    queryFn: () => customerService.getCustomers({ page: 1, page_size: 4 }).then(res => res.data),
  });

  // Fetch recommendations for each customer
  const customerIds = customersData?.customers.map((c: any) => c.customer_id) || [];
  
  const { data: recommendationsData, isLoading } = useQuery({
    queryKey: ['recommendations-batch', customerIds],
    queryFn: async () => {
      const recs = await Promise.all(
        customerIds.map(async (id: string) => {
          try {
            const res = await recommendationService.getRecommendations(id);
            return { customerId: id, ...res.data };
          } catch {
            return { customerId: id, recommendations: [], total_recommendations: 0 };
          }
        })
      );
      console.log(recs)
      return recs;
    },
    enabled: customerIds.length > 0,
  });

  // Prepare recommendations data
  const recommendations = recommendationsData?.map((rec: any) => ({
    customerId: rec.customer_id,
    customerName: rec.customer_id, // Using ID as name
    products: rec.recommendations?.slice(0, 5).map((r: any) => r.category) || [],
    confidence: rec.recommendations?.length > 0 
      ? rec.recommendations.reduce((sum: number, r: any) => sum + r.confidence, 0) / rec.recommendations.length * 100
      : 0
  })) || [];

  // Mock insights
  const insights = [
    {
      icon: '📈',
      text: 'High-Yield Maize Seeds and Organic Fertilizer are top cross-sell pairs this quarter, with a 70% joint purchase rate.'
    },
    {
      icon: '🛒',
      text: 'Customers purchasing Livestock Feed also frequently buy Veterinary Medicine Kits, indicating a strong bundled opportunity.'
    },
    {
      icon: '⭐',
      text: 'Over 80% of current recommendations have a confidence score above 90%, ensuring high relevance and potential conversion.'
    },
  ];

  // Get confidence badge color
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 90) return 'bg-green-100 text-green-700';
    if (confidence >= 80) return 'bg-blue-100 text-blue-700';
    if (confidence >= 70) return 'bg-yellow-100 text-yellow-700';
    return 'bg-gray-100 text-gray-700';
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
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Product Recommendation Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Identify personalized product recommendations and cross-sell opportunities to enhance customer engagement and sales
          </p>
        </div>
        {/* <div className="flex items-center gap-3">
          <Button className="bg-purple-600 hover:bg-purple-700">
            <Sparkles className="h-4 w-4 mr-2" />
            Generate New Campaign
          </Button>
          <Select defaultValue="all">
            <option value="all">All Recommendations</option>
            <option value="high">High Confidence</option>
            <option value="medium">Medium Confidence</option>
          </Select>
        </div> */}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Section - Recommendations */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-base font-semibold">Personalized Product Recommendations</CardTitle>
              <CardDescription>Top 5 product recommendations for each customer</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recommendations.map((rec) => (
                  <div key={rec.customerId} className="border border-gray-200 rounded-lg p-4 hover:border-purple-300 transition-colors">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="text-sm font-semibold text-gray-900">{rec.customerId}</h3>
                        <p className="text-xs text-gray-600">{rec.customerName}</p>
                      </div>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getConfidenceColor(rec.confidence)}`}>
                        {rec.confidence.toFixed(1)}%
                      </span>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {rec.products.map((product, index) => (
                        <div key={index} className="flex items-center gap-2 text-sm text-gray-700">
                          <div className="h-2 w-2 rounded-full bg-blue-600"></div>
                          <span>{product}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Section - Cross-Sell Heatmap */}
        {/* <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="text-base font-semibold">Cross-Sell Opportunity Heatmap</CardTitle>
              <CardDescription>Identifies categories frequently purchased together</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {['Seeds', 'Fertilizers', 'Tools', 'Livestock Feed', 'Farm Machinery'].map((category, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">{category}</p>
                    </div>
                    <div className="flex gap-1">
                      {[...Array(5)].map((_, i) => (
                        <div
                          key={i}
                          className="h-4 w-4 rounded"
                          style={{
                            backgroundColor: `rgba(139, 92, 246, ${0.2 + (i * 0.15)})`
                          }}
                        />
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div> */}
      </div>

      {/* Recommendation Insights */}
      {/* <Card>
        <CardHeader>
          <CardTitle className="text-base font-semibold">Recommendation Insights</CardTitle>
          <CardDescription>Key trends and actionable observations</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {insights.map((insight, index) => (
              <div key={index} className="flex items-start gap-3 p-4 bg-gray-50 rounded-lg">
                <span className="text-2xl">{insight.icon}</span>
                <p className="text-sm text-gray-700 leading-relaxed">{insight.text}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card> */}
    </div>
  );
}

