import { 
  AreaChart as RechartsAreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  type TooltipProps
} from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';

interface AreaChartProps {
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

export function AreaChart({ 
  title, 
  description, 
  data, 
  dataKey, 
  xAxisKey,
  color = "#8b5cf6",
  valueFormatter
}: AreaChartProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base font-semibold">{title}</CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <RechartsAreaChart data={data}>
            <defs>
              <linearGradient id={`gradient-${color}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={color} stopOpacity={0.3}/>
                <stop offset="95%" stopColor={color} stopOpacity={0}/>
              </linearGradient>
            </defs>
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
            <Area 
              type="monotone" 
              dataKey={dataKey} 
              stroke={color} 
              strokeWidth={2}
              fill={`url(#gradient-${color})`}
            />
          </RechartsAreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

