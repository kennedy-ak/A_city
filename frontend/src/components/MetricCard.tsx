import { Card, CardContent } from './ui/card';
import type { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
  icon: LucideIcon;
  iconColor?: string;
}

export function MetricCard({ 
  title, 
  value, 
  change, 
  changeType = 'neutral',
  icon: Icon,
  iconColor = 'text-blue-600'
}: MetricCardProps) {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <div className="mt-2 flex items-baseline gap-2">
              <p className="text-3xl font-bold text-gray-900">{value}</p>
              {change && (
                <span
                  className={cn(
                    "text-sm font-medium",
                    changeType === 'positive' && "text-green-600",
                    changeType === 'negative' && "text-red-600",
                    changeType === 'neutral' && "text-gray-600"
                  )}
                >
                  {change}
                </span>
              )}
            </div>
          </div>
          <div className={cn("rounded-full p-3 bg-blue-50", iconColor)}>
            <Icon className="h-6 w-6" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

