'use client';

import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
  ComposedChart,
} from 'recharts';
import { X, Maximize2, Settings } from 'lucide-react';

const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#f97316', '#eab308', '#84cc16', '#22c55e', '#14b8a6', '#06b6d4'];

const formatIndianNumber = (value: number): string => {
  if (value >= 10000000) return `₹${(value / 10000000).toFixed(2)}Cr`;
  if (value >= 100000) return `₹${(value / 100000).toFixed(2)}L`;
  if (value >= 1000) return `₹${(value / 1000).toFixed(1)}K`;
  return `₹${value.toFixed(0)}`;
};

const formatTooltipValue = (value: number): string => {
  return `₹${value.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
};

export type ChartType = 'bar' | 'horizontalBar' | 'line' | 'area' | 'pie' | 'donut' | 'composed';

export interface ChartConfig {
  type: ChartType;
  title: string;
  data: any[];
  xKey: string;
  yKey: string;
  dataKey?: string;
  nameKey?: string;
  barKey?: string;
  lineKey?: string;
  availableKeys?: string[];
}

interface ChartModalProps {
  isOpen: boolean;
  onClose: () => void;
  config: ChartConfig | null;
}

export const ChartModal: React.FC<ChartModalProps> = ({ isOpen, onClose, config }) => {
  const [selectedXKey, setSelectedXKey] = useState<string>('');
  const [selectedYKey, setSelectedYKey] = useState<string>('');
  const [showSettings, setShowSettings] = useState(false);

  useEffect(() => {
    if (config) {
      setSelectedXKey(config.xKey || config.nameKey || '');
      setSelectedYKey(config.yKey || config.dataKey || config.barKey || '');
    }
  }, [config]);

  // Close on Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen || !config) return null;

  // Get available keys from data
  const availableKeys = config.data.length > 0 
    ? Object.keys(config.data[0]).filter(key => key !== 'id' && key !== '_id')
    : [];

  const numericKeys = availableKeys.filter(key => 
    typeof config.data[0][key] === 'number'
  );

  const stringKeys = availableKeys.filter(key => 
    typeof config.data[0][key] === 'string'
  );

  const renderChart = () => {
    const { type, data } = config;
    const xKey = selectedXKey || config.xKey || config.nameKey || 'name';
    const yKey = selectedYKey || config.yKey || config.dataKey || 'value';

    switch (type) {
      case 'bar':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 100 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis 
                dataKey={xKey} 
                tick={{ fill: '#374151', fontSize: 12 }} 
                angle={-45} 
                textAnchor="end" 
                interval={0}
              />
              <YAxis tickFormatter={formatIndianNumber} tick={{ fill: '#374151', fontSize: 12 }} />
              <Tooltip formatter={(value: number) => formatTooltipValue(value)} />
              <Legend />
              <Bar dataKey={yKey} fill="#6366f1" radius={[4, 4, 0, 0]} name={yKey}>
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        );

      case 'horizontalBar':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} layout="vertical" margin={{ top: 20, right: 30, left: 150, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis type="number" tickFormatter={formatIndianNumber} tick={{ fill: '#374151', fontSize: 12 }} />
              <YAxis type="category" dataKey={xKey} tick={{ fill: '#374151', fontSize: 12 }} width={140} />
              <Tooltip formatter={(value: number) => formatTooltipValue(value)} />
              <Legend />
              <Bar dataKey={yKey} fill="#6366f1" radius={[0, 4, 4, 0]} name={yKey}>
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        );

      case 'line':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey={xKey} tick={{ fill: '#374151', fontSize: 12 }} />
              <YAxis tickFormatter={formatIndianNumber} tick={{ fill: '#374151', fontSize: 12 }} />
              <Tooltip formatter={(value: number) => formatTooltipValue(value)} />
              <Legend />
              <Line type="monotone" dataKey={yKey} stroke="#6366f1" strokeWidth={3} dot={{ r: 5 }} name={yKey} />
            </LineChart>
          </ResponsiveContainer>
        );

      case 'area':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey={xKey} tick={{ fill: '#374151', fontSize: 12 }} />
              <YAxis tickFormatter={formatIndianNumber} tick={{ fill: '#374151', fontSize: 12 }} />
              <Tooltip formatter={(value: number) => formatTooltipValue(value)} />
              <Legend />
              <defs>
                <linearGradient id="fullscreenGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <Area type="monotone" dataKey={yKey} stroke="#6366f1" fill="url(#fullscreenGradient)" strokeWidth={2} name={yKey} />
            </AreaChart>
          </ResponsiveContainer>
        );

      case 'pie':
      case 'donut':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie 
                data={data} 
                dataKey={yKey} 
                nameKey={xKey} 
                cx="50%" 
                cy="50%" 
                innerRadius={type === 'donut' ? 80 : 0}
                outerRadius={180} 
                paddingAngle={2}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                labelLine={{ stroke: '#374151' }}
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value: number) => formatTooltipValue(value)} />
              <Legend layout="vertical" align="right" verticalAlign="middle" />
            </PieChart>
          </ResponsiveContainer>
        );

      case 'composed':
        const barKey = config.barKey || selectedYKey || 'revenue';
        const lineKey = config.lineKey || 'quantity';
        return (
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={data} margin={{ top: 20, right: 60, left: 20, bottom: 100 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey={xKey} tick={{ fill: '#374151', fontSize: 12 }} angle={-45} textAnchor="end" />
              <YAxis yAxisId="left" tickFormatter={formatIndianNumber} tick={{ fill: '#374151', fontSize: 12 }} />
              <YAxis yAxisId="right" orientation="right" tick={{ fill: '#374151', fontSize: 12 }} />
              <Tooltip formatter={(value: number, name: string) => [name === barKey ? formatTooltipValue(value) : value.toLocaleString(), name]} />
              <Legend />
              <Bar yAxisId="left" dataKey={barKey} fill="#6366f1" radius={[4, 4, 0, 0]} name="Revenue" />
              <Line yAxisId="right" type="monotone" dataKey={lineKey} stroke="#f97316" strokeWidth={3} name="Quantity" />
            </ComposedChart>
          </ResponsiveContainer>
        );

      default:
        return <div className="text-center text-gray-500">Unsupported chart type</div>;
    }
  };

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-75"
      onClick={onClose}
    >
      <div 
        className="bg-white rounded-2xl shadow-2xl w-[95vw] h-[90vh] max-w-7xl flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <Maximize2 className="w-5 h-5 text-indigo-600" />
            <h2 className="text-xl font-bold text-gray-900">{config.title}</h2>
          </div>
          <div className="flex items-center gap-2">
            {/* Settings Toggle */}
            <button
              onClick={() => setShowSettings(!showSettings)}
              className={`p-2 rounded-lg transition-colors ${showSettings ? 'bg-indigo-100 text-indigo-600' : 'hover:bg-gray-100 text-gray-600'}`}
              title="Chart Settings"
            >
              <Settings className="w-5 h-5" />
            </button>
            {/* Close Button */}
            <button
              onClick={onClose}
              className="p-2 hover:bg-red-100 rounded-lg transition-colors text-red-600"
              title="Close (Esc)"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Settings Panel */}
        {showSettings && (
          <div className="p-4 bg-gray-50 border-b border-gray-200">
            <div className="flex flex-wrap gap-4">
              {/* X-Axis / Name Key Selector */}
              <div className="flex items-center gap-2">
                <label className="text-sm font-medium text-gray-700">
                  {config.type === 'pie' || config.type === 'donut' ? 'Category Field:' : 'X-Axis:'}
                </label>
                <select
                  value={selectedXKey}
                  onChange={(e) => setSelectedXKey(e.target.value)}
                  className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                >
                  {stringKeys.map(key => (
                    <option key={key} value={key}>{key}</option>
                  ))}
                </select>
              </div>

              {/* Y-Axis / Value Key Selector */}
              <div className="flex items-center gap-2">
                <label className="text-sm font-medium text-gray-700">
                  {config.type === 'pie' || config.type === 'donut' ? 'Value Field:' : 'Y-Axis:'}
                </label>
                <select
                  value={selectedYKey}
                  onChange={(e) => setSelectedYKey(e.target.value)}
                  className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                >
                  {numericKeys.map(key => (
                    <option key={key} value={key}>{key}</option>
                  ))}
                </select>
              </div>

              {/* Data Count Info */}
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <span>📊 {config.data.length} data points</span>
              </div>
            </div>
          </div>
        )}

        {/* Chart Area */}
        <div className="flex-1 p-6 min-h-0">
          {renderChart()}
        </div>

        {/* Footer with instructions */}
        <div className="p-3 border-t border-gray-200 bg-gray-50 text-center">
          <span className="text-xs text-gray-500">
            Press <kbd className="px-1.5 py-0.5 bg-gray-200 rounded text-gray-700 font-mono">Esc</kbd> or click outside to close • 
            Click <Settings className="w-3 h-3 inline mx-1" /> to change chart variables
          </span>
        </div>
      </div>
    </div>
  );
};

// Clickable wrapper for charts
export const ClickableChartWrapper: React.FC<{
  children: React.ReactNode;
  onClick: () => void;
  title?: string;
}> = ({ children, onClick, title }) => (
  <div 
    className="relative cursor-pointer group"
    onClick={onClick}
    title={title || 'Click to expand'}
  >
    {children}
    {/* Expand overlay on hover */}
    <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-5 transition-all duration-200 rounded-lg pointer-events-none flex items-center justify-center">
      <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 bg-white px-3 py-1.5 rounded-full shadow-lg flex items-center gap-2 text-sm font-medium text-indigo-600">
        <Maximize2 className="w-4 h-4" />
        Click to expand
      </div>
    </div>
  </div>
);

export default ChartModal;
