'use client';

import { useEffect, useState, use } from 'react';
import api from '@/lib/api';

interface ContentSection {
  id: string;
  section_type: string;
  content: string;
}

interface SiteData {
  name: string;
  theme_slug: string;
  sections: ContentSection[];
}

export default function PublicSitePage({ params }: { params: Promise<{ site_slug: string }> }) {
  const { site_slug } = use(params);
  const [data, setData] = useState<SiteData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    const fetchSite = async () => {
      try {
        // Public endpoint to get site by slug
        const response = await api.get(`/public/sites/${site_slug}`);
        setData(response.data);
      } catch (err) {
        console.error('Failed to fetch site', err);
        setError(true);
      } finally {
        setLoading(false);
      }
    };
    fetchSite();
  }, [site_slug]);

  if (loading) return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  if (error || !data) return <div className="min-h-screen flex items-center justify-center text-red-500 text-xl font-bold italic">Site not found.</div>;

  return (
    <div className="min-h-screen" data-theme={data.theme_slug}>
      {data.sections.map((section) => (
        <section
          key={section.id}
          className={`py-20 px-4 ${
            section.section_type === 'hero' ? 'bg-primary-50 text-center' : 'bg-white'
          }`}
        >
          <div className="max-w-4xl mx-auto">
            <h2 className="text-4xl font-bold mb-6 capitalize">{section.section_type}</h2>
            <div className="prose prose-lg max-w-none whitespace-pre-wrap">
              {section.content}
            </div>
          </div>
        </section>
      ))}
      <footer className="py-8 text-center text-gray-400 border-t">
        <p>Built with AI CMS - {data.name}</p>
      </footer>
    </div>
  );
}
