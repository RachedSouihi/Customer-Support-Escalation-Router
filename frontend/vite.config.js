import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // GitHub Pages deployment: replace 'YOUR_REPO_NAME' with your actual repo name
  // For local dev, base stays as '/'. For GitHub Pages, set to '/customer-support-escalation-router/' or your repo name
  base: process.env.GITHUB_PAGES === 'true' ? '/customer-support-escalation-router/' : '/',
})
