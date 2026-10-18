/** @type {import('next').NextConfig} */
const nextConfig = {
  async redirects() {
    return [
      {
        source: "/collaboration-heatmap",
        destination: "/heatmap",
        permanent: true,
      },
    ];
  },
};

export default nextConfig;
