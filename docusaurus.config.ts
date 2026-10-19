import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'Code Design Note',
  tagline: 'Self-Index 레포에서 정리한 설계 지식과 코딩 규약',

  url: 'https://happysnail06.github.io',
  baseUrl: '/code-design-note/',
  organizationName: 'happysnail06',
  projectName: 'code-design-note',
  trailingSlash: true,

  // A broken cross-link between topics fails the build instead of shipping a dead link
  onBrokenLinks: 'throw',

  // .md files are plain CommonMark, so `{...}` and `<...>` in prose need no escaping
  markdown: {
    format: 'detect',
    hooks: {
      onBrokenMarkdownLinks: 'throw',
    },
  },

  i18n: {
    defaultLocale: 'ko',
    locales: ['ko'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          // The docs are the whole site, so they are served from the root
          routeBasePath: '/',
          sidebarPath: './sidebars.ts',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    announcementBar: {
      id: 'self-index-credit',
      content: '이 문서는 <strong><a href="https://github.com/augustinLib/Self-Index">augustinLib/Self-Index</a></strong>의 코드와 설계를 분석한 학습 노트입니다. 원본 코드와 설계의 크레딧은 Self-Index 저자와 기여자에게 있습니다.',
      isCloseable: false,
    },
    colorMode: {
      respectPrefersColorScheme: true,
    },
    docs: {
      sidebar: {
        hideable: true,
      },
    },
    tableOfContents: {
      minHeadingLevel: 2,
      maxHeadingLevel: 3,
    },
    navbar: {
      title: 'Code Design Note',
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docsSidebar',
          position: 'left',
          label: 'Docs',
        },
        {
          href: 'https://github.com/augustinLib/Self-Index',
          label: '원본 · Self-Index',
          position: 'right',
        },
        {
          href: 'https://github.com/happysnail06/code-design-note',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {label: '개요', to: '/'},
            {label: '먼저 알아 둘 개념', to: '/concepts'},
            {label: '코딩 규약', to: '/coding-convention'},
          ],
        },
        {
          title: '원본',
          items: [{label: 'augustinLib/Self-Index', href: 'https://github.com/augustinLib/Self-Index'}],
        },
      ],
      copyright: '원본 코드와 설계: <a href="https://github.com/augustinLib/Self-Index">Self-Index 저자 및 기여자</a> · 분석 기준: <a href="https://github.com/augustinLib/Self-Index/tree/9c6fade">9c6fade</a>',
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
