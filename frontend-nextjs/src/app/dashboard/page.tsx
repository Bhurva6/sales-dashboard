'use client';

import React, { useEffect } from 'react';
import { useAuthStore } from '@/lib/store';
import { useRouter } from 'next/navigation';
import DashboardPage from '@/app/page';

export default function DashboardIndexPage() {
  const { isAuthenticated, username, userRole } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    console.log('Dashboard Auth State:', { isAuthenticated, username, userRole });
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, username, userRole, router]);

  if (!isAuthenticated) {
    return <div>Redirecting to login...</div>;
  }

  return <DashboardPage />;
}
