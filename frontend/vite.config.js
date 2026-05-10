import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [react()],
    // For local dev, base stays '/'. For GitHub Pages, set VITE_GITHUB_PAGES=true.
     base: env.GITHUB_PAGES === 'true' ? '/Customer-Support-Escalation-Router/' : '/',
  }
})
