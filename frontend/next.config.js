/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    workerThreads: true,
    webpackBuildWorker: false
  }
}

module.exports = nextConfig
