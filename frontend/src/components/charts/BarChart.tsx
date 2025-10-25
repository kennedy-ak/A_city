import { 
  BarChart as RechartsBarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  type TooltipProps
} from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';

interface BarChartProps {
  title: string;
  description?: string;
  data: any[];
  dataKey: string;
  xAxisKey: string;
  color?: string;
  valueFormatter?: (value: number) => string;
}

// const CustomTooltip = ({ 
//   active, 
//   payload,
//   valueFormatter
// }: TooltipProps<any, any> & { valueFormatter?: (value: number) => string }) => {
//   if (active && payload && payload.length) {
//     return (
//       <div className="rounded-lg border bg-white p-3 shadow-lg">
//         <p className="text-sm font-medium text-gray-900">
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

export function BarChart({ 
  title, 
  description, 
  data, 
  dataKey, 
  xAxisKey,
  color = "#6366f1",
  valueFormatter
}: BarChartProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base font-semibold">{title}</CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <RechartsBarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis 
              dataKey={xAxisKey} 
              tick={{ fontSize: 12 }}
              stroke="#9ca3af"
            />
            <YAxis 
              tick={{ fontSize: 12 }}
              stroke="#9ca3af"
            />
            <Tooltip content={<CustomTooltip valueFormatter={valueFormatter} />} />
            <Bar 
              dataKey={dataKey} 
              fill={color}
              radius={[4, 4, 0, 0]}
            />
          </RechartsBarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

