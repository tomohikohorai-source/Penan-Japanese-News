import { defineConfig } from 'astro/config';
import vercel from '@astrojs/vercel/serverless';

export default defineConfig({
  output: 'hybrid', // ページは静的、ログインはサーバーで処理
  adapter: vercel(),
});
