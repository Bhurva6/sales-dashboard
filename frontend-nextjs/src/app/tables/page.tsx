'use client';

import React, { useState, useEffect } from 'react';
import { useDashboardStore } from '@/lib/store';
import Layout from '@/components/Layout';
import DataTable from '@/components/DataTable';
import { formatIndianNumber } from '@/lib/utils';

export default function TablesPage() {
  const { dashboardMode, startDate, endDate } = useDashboardStore();
  const [loading, setLoading] = useState(false);
  const [salesData, setSalesData] = useState<any[]>([]);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        // Mock data - replace with actual API call
        const mockData = [
          {
            id: 1,
            date: '2024-01-15',
            dealer: 'Dealer A',
            state: 'Maharashtra',
            city: 'Mumbai',
            product: 'Hip Implant',
            category: 'Orthopedic Implants',
            quantity: 5,
            value: 125000,
          },
          {
            id: 2,
            date: '2024-01-16',
            dealer: 'Dealer B',
            state: 'Karnataka',
            city: 'Bangalore',
            product: 'Knee Implant',
            category: 'Orthopedic Implants',
            quantity: 3,
            value: 87000,
          },
          {
            id: 3,
            date: '2024-01-17',
            dealer: 'Dealer C',
            state: 'Delhi',
            city: 'Delhi',
            product: 'Spine Implant',
            category: 'Surgical Instruments',
            quantity: 2,
            value: 65000,
          },
        ];
        setSalesData(mockData);
      } catch (error) {
        console.error('Error loading data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [startDate, endDate, dashboardMode]);

  const columns = [
    { key: 'date', label: 'Date' },
    { key: 'dealer', label: 'Dealer Name' },
    { key: 'state', label: 'State' },
    { key: 'city', label: 'City' },
    { key: 'product', label: 'Product' },
    { key: 'category', label: 'Category' },
    { key: 'quantity', label: 'Quantity' },
    { key: 'value', label: 'Value (₹)' },
  ];

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Sales Data Tables</h1>
          <p className="text-gray-600 mt-2">Comprehensive view of all transactions</p>
        </div>

        <DataTable
          columns={columns}
          data={salesData}
          loading={loading}
          title="Sales Transactions"
        />
      </div>
    </Layout>
  );
}
