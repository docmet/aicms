import { NextRequest, NextResponse } from "next/server";

interface BlogPost {
  slug: string;
  title: string;
  excerpt: string | null;
  author_name: string | null;
  published_at: string | null;
}

export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ site_slug: string }> }
) {
  const { site_slug } = await params;
  const internalUrl = process.env.INTERNAL_API_URL ?? "http://backend:8000/api";
  const domain = process.env.NEXT_PUBLIC_DOMAIN ?? "localhost";
  const baseUrl = `https://${domain}`;

  let siteName = site_slug;
  let posts: BlogPost[] = [];

  try {
    const [siteRes, blogRes] = await Promise.all([
      fetch(`${internalUrl}/public/sites/${site_slug}`, { next: { revalidate: 60 } }),
      fetch(`${internalUrl}/public/sites/${site_slug}/blog`, { next: { revalidate: 60 } }),
    ]);

    if (siteRes.ok) {
      const siteData = (await siteRes.json()) as { name?: string };
      siteName = siteData.name ?? site_slug;
    }
    if (blogRes.ok) {
      posts = (await blogRes.json()) as BlogPost[];
    }
  } catch {
    // Return empty feed on error
  }

  const items = posts
    .map((post) => {
      const pubDate = post.published_at
        ? new Date(post.published_at).toUTCString()
        : "";
      const link = `${baseUrl}/${site_slug}/blog/${post.slug}`;
      const desc = post.excerpt ?? "";
      return `
    <item>
      <title><![CDATA[${post.title}]]></title>
      <link>${link}</link>
      <guid isPermaLink="true">${link}</guid>
      ${pubDate ? `<pubDate>${pubDate}</pubDate>` : ""}
      ${post.author_name ? `<author>${post.author_name}</author>` : ""}
      ${desc ? `<description><![CDATA[${desc}]]></description>` : ""}
    </item>`;
    })
    .join("");

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title><![CDATA[${siteName}]]></title>
    <link>${baseUrl}/${site_slug}</link>
    <description><![CDATA[Blog posts from ${siteName}]]></description>
    <language>en</language>
    <atom:link href="${baseUrl}/${site_slug}/feed.xml" rel="self" type="application/rss+xml"/>
    ${items}
  </channel>
</rss>`;

  return new NextResponse(xml, {
    headers: {
      "Content-Type": "application/rss+xml; charset=utf-8",
      "Cache-Control": "public, max-age=3600, stale-while-revalidate=86400",
    },
  });
}
