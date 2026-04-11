/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  distDir: 'next-build',
  experimental: {
    workerThreads: true,
    webpackBuildWorker: false
  }
}

module.exports = nextConfig
