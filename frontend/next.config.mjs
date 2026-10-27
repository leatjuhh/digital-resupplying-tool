/** @type {import('next').NextConfig} */
const nextConfig = {
  // TypeScript-fouten mogen de productie-build blokkeren (R10.2). De eerder
  // aanwezige `typescript.ignoreBuildErrors: true` is verwijderd nadat de
  // openstaande typefouten zijn opgelost; `strict` in tsconfig.json wordt zo
  // ook bij de build daadwerkelijk gehandhaafd.
  images: {
    unoptimized: true,
  },
}

export default nextConfig
