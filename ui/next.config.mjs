/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    // In Docker Compose, use service name 'backend'; fallback to localhost for local dev
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://backend:8002';
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/:path*`
      }
    ];
  },
}

export default nextConfig;
