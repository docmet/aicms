import { NextRequest, NextResponse } from "next/server";

export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ site_slug: string }> }
) {
  const { site_slug } = await params;
  const domain = process.env.NEXT_PUBLIC_DOMAIN ?? "localhost";

  const content = `User-agent: *
Allow: /

Sitemap: https://${domain}/${site_slug}/sitemap.xml
`;

  return new NextResponse(content, {
    headers: {
      "Content-Type": "text/plain",
      "Cache-Control": "public, max-age=86400",
    },
  });
}
