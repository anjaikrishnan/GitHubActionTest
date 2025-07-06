'use client';

import React from 'react';
import { useAuth } from '@/lib/auth/AuthProvider';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { LoginPage } from '@/components/auth/LoginPage';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { DashboardHome } from '@/components/dashboard/DashboardHome';

export default function HomePage() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  return (
    <DashboardLayout>
      <DashboardHome />
    </DashboardLayout>
  );
}