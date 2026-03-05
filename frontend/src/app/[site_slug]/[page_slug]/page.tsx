"use client";

import { use } from "react";
import { SiteRenderer } from "../SiteRenderer";

export default function PublicSitePageBySlug({
  params,
}: {
  params: Promise<{ site_slug: string; page_slug: string }>;
}) {
  const { site_slug, page_slug } = use(params);
  return <SiteRenderer siteSlug={site_slug} pageSlug={page_slug} />;
}
