'use client';

import { useEffect, useState, use } from 'react';

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
        // Public endpoint to get site by slug - use direct fetch to avoid auth
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/public/sites/${site_slug}`);
        if (!response.ok) {
          throw new Error('Site not found');
        }
        const data = await response.json();
        console.log('Site data:', data);
        setData(data);
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
    <div className="min-h-screen" data-theme={data.theme_slug || 'default'}>
      <div className="text-center py-4 bg-gray-100 text-sm">
        Debug: Theme = {data.theme_slug}, Site = {data.name}
      </div>
      <pre className="p-4 bg-gray-100 text-xs">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
}
