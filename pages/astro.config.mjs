import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://jyje.github.io',
  base: '/hermes-agent-helm',
  integrations: [
    starlight({
      title: 'jyje/hermes-agent-helm',
      description: 'Community-powered Helm chart for running Hermes Agent on Kubernetes.',
      locales: {
        root: { label: 'English', lang: 'en' },
        ko: { label: '한국어', lang: 'ko' },
      },
      defaultLocale: 'root',
      customCss: ['./src/styles/custom.css'],
      components: {
        Head: './src/components/SiteHead.astro',
        SiteTitle: './src/components/SiteTitle.astro',
        ThemeProvider: './src/components/LightThemeProvider.astro',
        ThemeSelect: './src/components/NoThemeSelect.astro',
        SocialIcons: './src/components/GitHubStars.astro',
        Sidebar: './src/components/GeneratedSidebar.astro',
      },
      social: [{
        icon: 'github',
        label: 'GitHub repository',
        href: 'https://github.com/jyje/hermes-agent-helm',
      }],
    }),
  ],
});
