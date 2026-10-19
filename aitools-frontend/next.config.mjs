/** @type {import('next').NextConfig} */
const nextConfig = {
  // Proxy les appels API vers le backend FastAPI
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
