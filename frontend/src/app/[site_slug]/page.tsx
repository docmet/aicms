"use client";

import { use } from "react";
import { SiteRenderer } from "./SiteRenderer";

export default function PublicSitePage({
  params,
}: {
  params: Promise<{ site_slug: string }>;
}) {
  const { site_slug } = use(params);
  return <SiteRenderer siteSlug={site_slug} />;
}
