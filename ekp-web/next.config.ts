import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  async rewrites() {
    return [
      {
        source: '/api/backend/:path*',
        destination: 'http://ai-service:8000/api/:path*',
      },
    ];
  },
};

export default nextConfig;
