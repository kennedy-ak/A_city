import { 
  PieChart, 
  Pie, 
  Cell, 
  ResponsiveContainer, 
  Legend,
  Tooltip,
  type TooltipProps
} from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';

interface DonutChartProps {
  title: string;
  description?: string;
  data: any[];
  nameKey: string;
  valueKey: string;
  valueFormatter?: (value: number) => string;
}

const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f97316', '#10b981', '#6366f1'];

// const CustomTooltip = ({ 
//   active?: boolean, 
//   payload?: any[],
//   valueFormatter
// }: TooltipProps<any, any> & { valueFormatter?: (value: number) => string }) => {
//   if (active && payload && payload.length) {
//     return (
//       <div className="rounded-lg border bg-white p-3 shadow-lg">
//         <p className="text-sm font-medium text-gray-900">{payload[0].name}</p>
//         <p className="text-sm text-gray-600">
//           {valueFormatter ? valueFormatter(payload[0].value) : payload[0].value}
//         </p>
//       </div>
//     );
//   }
//   return null;
// };

const CustomTooltip = ({ 
    active, 
    payload,
    valueFormatter
  }: {
    active?: boolean;
    payload?: any[];
    valueFormatter?: (value: number) => string;
  }) => {
    if (active && payload && payload.length) {
      return (
        <div className="rounded-lg border bg-white p-3 shadow-lg">
          <p className="text-sm font-medium text-gray-900">
            {valueFormatter ? valueFormatter(payload[0].value) : payload[0].value}
          </p>
        </div>
      );
    }
    return null;
  };

export function DonutChart({ 
  title, 
  description, 
  data, 
  nameKey, 
  valueKey,
  valueFormatter
}: DonutChartProps) {
  const chartData = data.map((item, index) => ({
    name: item[nameKey],
    value: item[valueKey],
    color: COLORS[index % COLORS.length]
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base font-semibold">{title}</CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={90}
              paddingAngle={2}
              dataKey="value"
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip valueFormatter={valueFormatter} />} />
            <Legend 
              verticalAlign="bottom" 
              height={36}
              iconType="circle"
              formatter={(value) => <span className="text-sm text-gray-700">{value}</span>}
            />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

