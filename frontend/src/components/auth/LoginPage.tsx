'use client';

import React from 'react';
import { useAuth } from '@/lib/auth/AuthProvider';
import { Button } from '@nextui-org/react';
import { LogIn, TrendingUp, BarChart3, Brain } from 'lucide-react';

export function LoginPage() {
  const { login } = useAuth();

  const features = [
    {
      icon: <BarChart3 className="h-8 w-8" />,
      title: 'Interactive Dashboards',
      description: 'Create and customize beautiful dashboards with real-time data visualization.',
    },
    {
      icon: <TrendingUp className="h-8 w-8" />,
      title: 'Advanced Analytics',
      description: 'Powerful analytics engine with drill-down capabilities and predictive insights.',
    },
    {
      icon: <Brain className="h-8 w-8" />,
      title: 'AI-Powered Queries',
      description: 'Ask questions in natural language and get instant SQL results and visualizations.',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-blue-900 dark:to-indigo-900">
      <div className="min-h-screen flex">
        {/* Left side - Features */}
        <div className="hidden lg:flex lg:w-1/2 xl:w-2/3 flex-col justify-center px-12">
          <div className="max-w-lg mx-auto">
            <div className="mb-12">
              <div className="flex items-center space-x-3 mb-6">
                <div className="bg-primary-600 rounded-xl p-3">
                  <BarChart3 className="h-8 w-8 text-white" />
                </div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                  Enterprise Reporting
                </h1>
              </div>
              <p className="text-xl text-gray-600 dark:text-gray-300">
                Comprehensive reporting and analytics platform with AI-powered insights
              </p>
            </div>

            <div className="space-y-8">
              {features.map((feature, index) => (
                <div key={index} className="flex items-start space-x-4">
                  <div className="bg-white dark:bg-gray-800 rounded-lg p-3 shadow-soft">
                    <div className="text-primary-600">{feature.icon}</div>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                      {feature.title}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-300">
                      {feature.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right side - Login */}
        <div className="w-full lg:w-1/2 xl:w-1/3 flex items-center justify-center px-6 lg:px-12">
          <div className="w-full max-w-md">
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-large p-8">
              <div className="text-center mb-8">
                <div className="bg-primary-100 dark:bg-primary-900/20 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <LogIn className="h-8 w-8 text-primary-600" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                  Welcome Back
                </h2>
                <p className="text-gray-600 dark:text-gray-300">
                  Sign in to access your enterprise dashboard
                </p>
              </div>

              <div className="space-y-6">
                <Button
                  onClick={login}
                  className="w-full bg-primary-600 hover:bg-primary-700 text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200"
                  size="lg"
                  startContent={<LogIn className="h-5 w-5" />}
                >
                  Sign in with Enterprise SSO
                </Button>

                <div className="text-center text-sm text-gray-500 dark:text-gray-400">
                  Secure authentication powered by Keycloak
                </div>
              </div>

              <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
                <div className="text-center text-xs text-gray-500 dark:text-gray-400">
                  <p>Enterprise Reporting Platform v1.0</p>
                  <p className="mt-1">Protected by enterprise security standards</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}