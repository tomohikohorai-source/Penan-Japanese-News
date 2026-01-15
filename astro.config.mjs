import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  // あなたのURL。末尾のスラッシュはなしで設定してみましょう。
  site: 'https://penan-japanese-news.vercel.app',
  integrations: [sitemap()],
  output: 'static',
});
