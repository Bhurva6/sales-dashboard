'use client';

import React, { useEffect } from 'react';
import { useAuthStore } from '@/lib/store';
import { useRouter } from 'next/navigation';

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

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Welcome to the Dashboard</h1>
      <p>Logged in as: <strong>{username}</strong> ({userRole})</p>
      {/* Add your dashboard content here */}
    </div>
  );
}
