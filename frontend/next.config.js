/** @type {import('next').NextConfig} */
const nextConfig = {
    images: {
        // domains: ['images.unsplash.com'],
        remotePatterns: [
            {
              hostname: 'images.unsplash.com',
              protocol: 'https',
            },
        ],
    },
}

module.exports = nextConfig
