import { NextRequest, NextResponse } from "next/server";

export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ site_slug: string }> }
) {
  const { site_slug } = await params;
  const baseUrl = `https://${process.env.NEXT_PUBLIC_DOMAIN ?? "localhost"}`;

  let pages: { slug: string }[] = [];
  try {
    const internalUrl =
      process.env.INTERNAL_API_URL ?? "http://backend:8000/api";
    const res = await fetch(`${internalUrl}/public/sites/${site_slug}`, {
      next: { revalidate: 60 },
    });
    if (res.ok) {
      const data = (await res.json()) as { pages?: { slug: string }[] };
      pages = data.pages ?? [];
    }
  } catch {
    // Return minimal sitemap on error
  }

  const homepageSlug = pages[0]?.slug;
  const urls = pages.map((p) => {
    const loc =
      p.slug === homepageSlug
        ? `${baseUrl}/${site_slug}`
        : `${baseUrl}/${site_slug}/${p.slug}`;
    return `  <url><loc>${loc}</loc></url>`;
  });

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.join("\n")}
</urlset>`;

  return new NextResponse(xml, {
    headers: {
      "Content-Type": "application/xml",
      "Cache-Control": "public, max-age=3600",
    },
  });
}
