import type { NextConfig } from "next";

const isProduction = process.env.NODE_ENV === "production";

const nextConfig: NextConfig = {
  // Static export for S3 hosting in production
  ...(isProduction && { output: "export" }),

  // Proxy API calls in local dev only (not used in static export)
  ...(!isProduction && {
    async rewrites() {
      return [
        {
          source: "/api/:path*",
          destination: "http://localhost:8000/api/:path*",
        },
      ];
    },
  }),
};

export default nextConfig;
