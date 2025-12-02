const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    NEXT_PUBLIC_INSTITUTION: 'banreservas',
    NEXT_PUBLIC_ENVIRONMENT: 'development'
  }
}
module.exports = nextConfig
