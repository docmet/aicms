'use client';

import { useEffect, useState, use } from 'react';
import api from '@/lib/api';

interface ContentSection {
  id: string;
  section_type: string;
  content: string;
}

interface ServiceItem {
  name: string;
  description: string;
}

interface HeroContent {
  headline: string;
  subheadline: string;
}

interface ContactContent {
  email: string;
  phone: string;
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

  if (loading)
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  if (error || !data)
    return (
      <div className="min-h-screen flex items-center justify-center text-red-500 text-xl font-bold italic">
        Site not found.
      </div>
    );

  // Parse JSON content for certain sections
  const parseContent = (content: string, sectionType: string) => {
    try {
      if (sectionType === 'services' || sectionType === 'contact') {
        const parsed = JSON.parse(content);
        if (sectionType === 'services' && parsed.services) {
          return parsed.services;
        }
        return parsed;
      }
      return content;
    } catch {
      return content;
    }
  };

  // Parse hero content - supports both JSON and Markdown formats
  const parseHeroContent = (content: string): { headline: string; subheadline: string } => {
    try {
      // Try JSON format first
      const parsed = JSON.parse(content);
      if (parsed.headline) {
        return parsed;
      }
    } catch {
      // Not JSON, parse as Markdown
      const lines = content.split('\n').filter(line => line.trim());
      if (lines.length > 0) {
        // First line is headline (remove # if present)
        const headline = lines[0].replace(/^#+\s*/, '');
        // Rest is subheadline
        const subheadline = lines.slice(1).join(' ').trim();
        return { headline, subheadline };
      }
    }
    return { headline: 'Welcome', subheadline: '' };
  };

  return (
    <div className="min-h-screen" data-theme={data.theme_slug || 'default'}>
      {data.sections
        .filter((section) => section.content && section.content.trim().length > 0)
        .map((section) => {
          const parsedContent = parseContent(section.content, section.section_type);

          if (section.section_type === 'hero') {
            const heroContent = parseHeroContent(section.content);
            return (
              <section key={section.id} className="py-20 px-4 bg-primary-50 text-center">
                <div className="max-w-4xl mx-auto">
                  <h1 className="text-5xl font-bold mb-4 text-primary-900">
                    {heroContent.headline}
                  </h1>
                  <p className="text-xl text-primary-700">{heroContent.subheadline}</p>
                </div>
              </section>
            );
          }

          if (section.section_type === 'body' || section.section_type === 'main') {
            return (
              <section key={section.id} className="py-16 px-4 bg-white">
                <div className="max-w-4xl mx-auto">
                  <div className="prose prose-lg max-w-none">{section.content}</div>
                </div>
              </section>
            );
          }

          if (section.section_type === 'services') {
            const servicesContent = parsedContent as ServiceItem[];
            // Ensure it's an array before mapping
            if (!Array.isArray(servicesContent)) {
              console.error('Services content is not an array:', servicesContent);
              return null;
            }
            return (
              <section key={section.id} className="py-20 px-4 bg-white">
                <div className="max-w-4xl mx-auto">
                  <h2 className="text-4xl font-bold text-center mb-12">Our Services</h2>
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {servicesContent.map((service, index) => (
                      <div key={index} className="p-6 border rounded-lg bg-card">
                        <h3 className="text-xl font-semibold mb-2">{service.name}</h3>
                        <p className="text-muted-foreground">{service.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </section>
            );
          }

          if (section.section_type === 'contact') {
            const contactContent = parsedContent as ContactContent;
            return (
              <section key={section.id} className="py-20 px-4 bg-primary-50">
                <div className="max-w-4xl mx-auto text-center">
                  <h2 className="text-4xl font-bold mb-8">Contact Us</h2>
                  <div className="space-y-4">
                    <p className="text-lg">
                      <span className="font-semibold">Email:</span>{' '}
                      <a
                        href={`mailto:${contactContent.email}`}
                        className="text-primary-600 hover:underline"
                      >
                        {contactContent.email}
                      </a>
                    </p>
                    <p className="text-lg">
                      <span className="font-semibold">Phone:</span>{' '}
                      <a
                        href={`tel:${contactContent.phone}`}
                        className="text-primary-600 hover:underline"
                      >
                        {contactContent.phone}
                      </a>
                    </p>
                  </div>
                </div>
              </section>
            );
          }

          // Default section rendering
          return (
            <section key={section.id} className="py-20 px-4 bg-white">
              <div className="max-w-4xl mx-auto">
                <h2 className="text-4xl font-bold mb-6 capitalize text-center">
                  {section.section_type}
                </h2>
                <div className="prose prose-lg max-w-none text-center">{section.content}</div>
              </div>
            </section>
          );
        })
        .filter(Boolean)}
      <footer className="py-8 text-center border-t bg-muted">
        <p className="text-muted-foreground">Built with AI CMS - {data.name}</p>
      </footer>
    </div>
  );
}
