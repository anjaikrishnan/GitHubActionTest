/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'standalone',
  
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_KEYCLOAK_URL: process.env.NEXT_PUBLIC_KEYCLOAK_URL,
    NEXT_PUBLIC_ANALYTICS_URL: process.env.NEXT_PUBLIC_ANALYTICS_URL,
  },

  // Enable experimental features
  experimental: {
    appDir: true,
  },

  // Image optimization
  images: {
    domains: [],
    unoptimized: true, // For Docker deployment
  },

  // Security headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
        ],
      },
    ];
  },

  // Webpack configuration
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    return config;
  },
};

module.exports = nextConfig;