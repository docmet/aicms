import type { Metadata } from 'next';
import { WordPressLanding } from './WordPressLanding';

export const metadata: Metadata = {
  title: 'Control WordPress with AI | MyStorey',
  description:
    'Stop clicking through the WP admin. Tell Claude or ChatGPT what to write — and it writes it directly to your WordPress site.',
  openGraph: {
    title: 'Control WordPress with AI | MyStorey',
    description:
      'Stop clicking through the WP admin. Tell Claude or ChatGPT what to write — and it writes it directly to your WordPress site.',
    images: ['/og-wordpress.png'],
  },
};

export default function WordPressPage() {
  return <WordPressLanding />;
}
