"use client";

import React, { useState, useEffect } from "react";
import { useAuthStore } from "@/lib/store";
import { useRouter } from "next/navigation";
import DataTable from "@/components/DataTable";
import {
  RevenueLineChart,
  RevenueBarChart,
  RevenuePieChart,
  ComposedChartComponent,
} from "@/components/Charts";
import { ChartModal, ChartConfig } from "@/components/ChartModal";

// Sample data for demonstration
const revenueTrend = [
  { month: "Jan", revenue: 1200000 },
  { month: "Feb", revenue: 1500000 },
  { month: "Mar", revenue: 1100000 },
  { month: "Apr", revenue: 1800000 },
  { month: "May", revenue: 2100000 },
  { month: "Jun", revenue: 1700000 },
];
const categoryRevenue = [
  { category: "Electronics", revenue: 3200000 },
  { category: "Apparel", revenue: 2100000 },
  { category: "Home", revenue: 1800000 },
  { category: "Beauty", revenue: 900000 },
];
const dealerPerformance = [
  { dealer: "Dealer A", sales: 1200000 },
  { dealer: "Dealer B", sales: 900000 },
  { dealer: "Dealer C", sales: 1500000 },
  { dealer: "Dealer D", sales: 700000 },
];
const tableColumns = [
  { key: "dealer", label: "Dealer" },
  { key: "sales", label: "Sales (₹)" },
];
const composedData = [
  { name: "Jan", revenue: 1200000, quantity: 320 },
  { name: "Feb", revenue: 1500000, quantity: 410 },
  { name: "Mar", revenue: 1100000, quantity: 290 },
  { name: "Apr", revenue: 1800000, quantity: 500 },
  { name: "May", revenue: 2100000, quantity: 610 },
  { name: "Jun", revenue: 1700000, quantity: 430 },
];

export default function DashboardIndexPage() {
  const { isAuthenticated, username, userRole } = useAuthStore();
  const router = useRouter();

  // Chart modal state
  const [modalOpen, setModalOpen] = useState(false);
  const [modalConfig, setModalConfig] = useState<ChartConfig | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, router]);

  if (!isAuthenticated) {
    return <div>Redirecting to login...</div>;
  }

  // Handlers for opening chart modal
  const openChartModal = (config: ChartConfig) => {
    setModalConfig(config);
    setModalOpen(true);
  };

  return (
    <div className="p-6 md:p-10 bg-gray-50 min-h-screen">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-1">Dashboard</h1>
        <p className="text-gray-600 text-sm">
          Welcome, <span className="font-semibold">{username}</span> ({userRole})
        </p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
        {/* Revenue Trend Line Chart */}
        <div
          onClick={() =>
            openChartModal({
              type: "line",
              title: "Revenue Trend",
              data: revenueTrend,
              xKey: "month",
              yKey: "revenue",
            })
          }
          className="cursor-pointer"
        >
          <RevenueLineChart
            data={revenueTrend}
            xKey="month"
            yKey="revenue"
            title="Revenue Trend"
          />
        </div>
        {/* Revenue by Category Bar Chart */}
        <div
          onClick={() =>
            openChartModal({
              type: "bar",
              title: "Revenue by Category",
              data: categoryRevenue,
              xKey: "category",
              yKey: "revenue",
            })
          }
          className="cursor-pointer"
        >
          <RevenueBarChart
            data={categoryRevenue}
            xKey="category"
            yKey="revenue"
            title="Revenue by Category"
          />
        </div>
        {/* Dealer Performance Pie Chart */}
        <div
          onClick={() =>
            openChartModal({
              type: "pie",
              title: "Dealer Performance",
              data: dealerPerformance,
              xKey: "dealer",
              yKey: "sales",
            })
          }
          className="cursor-pointer"
        >
          <RevenuePieChart
            data={dealerPerformance}
            dataKey="sales"
            nameKey="dealer"
            title="Dealer Performance"
          />
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {/* Composed Chart Example */}
        <div
          onClick={() =>
            openChartModal({
              type: "composed",
              title: "Combined Revenue & Quantity",
              data: composedData,
              xKey: "name",
              yKey: "revenue", // required for ChartConfig
              barKey: "revenue",
              lineKey: "quantity",
            })
          }
          className="cursor-pointer"
        >
          <ComposedChartComponent
            data={composedData}
            xKey="name"
            barKey="revenue"
            lineKey="quantity"
            title="Combined Revenue & Quantity"
          />
        </div>
        {/* Data Table Example */}
        <DataTable
          columns={tableColumns}
          data={dealerPerformance}
          title="Dealer Sales Table"
        />
      </div>
      {/* Chart Modal */}
      <ChartModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        config={modalConfig}
      />
    </div>
  );
}
