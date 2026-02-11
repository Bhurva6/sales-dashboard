'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { useDashboardStore, useAuthStore } from '@/lib/store';
import { formatDate, getQuickDateRange } from '@/lib/utils';
import { Menu, LogOut } from 'lucide-react';

interface HeaderProps {
  onToggleSidebar: () => void;
}

export default function Header({ onToggleSidebar }: HeaderProps) {
  const router = useRouter();
  const { logout } = useAuthStore();
  const dashboardMode = useDashboardStore((state) => state.dashboardMode);
  const setDashboardMode = useDashboardStore((state) => state.setDashboardMode);

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
      <div className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center gap-4">
          <button
            onClick={onToggleSidebar}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Toggle sidebar"
          >
            <Menu className="w-6 h-6 text-gray-700" />
          </button>

          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              <span className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                Orthopedic Implant Analytics
              </span>
            </h1>
            <p className="text-sm text-gray-600">Real-time Sales & Analytics Dashboard</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* Dashboard Toggle */}
          <div className="flex gap-2">
            <button
              onClick={() => setDashboardMode('avante')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                dashboardMode === 'avante'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              🏢 Avante Dashboard
            </button>
            <button
              onClick={() => setDashboardMode('iospl')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                dashboardMode === 'iospl'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              🛍️ IOSPL Dashboard
            </button>
          </div>

          {/* Logout Button */}
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 px-3 py-2 hover:bg-red-50 rounded-lg transition-colors text-red-600"
            aria-label="Logout"
          >
            <LogOut className="w-5 h-5" />
            <span className="text-sm font-medium">Logout</span>
          </button>
        </div>
      </div>
    </header>
  );
}
