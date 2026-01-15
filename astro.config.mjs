import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  // 重要：末尾にスラッシュを付けてください
  site: 'https://penan-japanese-news.vercel.app/',
  integrations: [sitemap()],
  output: 'static',
});
