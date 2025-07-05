// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config

import {themes as prismThemes} from 'prism-react-renderer';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'DGEMC',
  tagline: 'Rolland Auda, La Condamine, Quito, 2025-2026',
  favicon: 'img/droit.svg',

  // Set the production url of your site here
  url: 'https://profauda.fr',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/dgemc25/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'rollauda', // Usually your GitHub org/user name.
  projectName: 'dgemc25', // Usually your repo name.
  trailingSlash: false, 

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'fr',
    locales: ['fr'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: false, // Désactive la documentation par défaut
        blog: {
          showReadingTime: true,
          feedOptions: {
            type: ['rss', 'atom'],
            xslt: true,
          },
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl: undefined,
          // Useful options to enforce blogging best practices
          onInlineTags: 'warn',
          onInlineAuthors: 'warn',
          onUntruncatedBlogPosts: 'warn',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  plugins: [
    [
      '@docusaurus/plugin-content-docs',
      {
        id: 'docs',
        path: 'docs',
        routeBasePath: 'docs',
        sidebarPath: require.resolve('./sidebars.js'),
      },
    ],
    [
      '@docusaurus/plugin-content-docs',
      {
        id: 'activites',
        path: 'activites',
        routeBasePath: 'activites',
        sidebarPath: require.resolve('./sidebars.js'),
      },
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/docusaurus-social-card.jpg',
      navbar: {
        title: 'dgemc-conda',
        logo: {
          alt: 'dgemc',
          src: 'img/justice.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Leçons',
            docsPluginId: 'docs',
          },
          {
            to: '/activites/intro', // Pointe vers le fichier intro.md
            label: 'Activités', 
            position: 'left',
            activeBaseRegex: `/activites/`, // Pour mettre en surbrillance l'élément actif
          },
          {
            href: 'https://www.profauda.fr/',
            label: 'Accueil-Auda',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        copyright: `©Rolland Auda, 2025-2026. Construit avec Docusaurus.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
    }),
};

export default config;
