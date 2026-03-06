"use client";

import { use, useEffect, useState } from "react";

interface BlogPost {
  id: string;
  slug: string;
  title: string;
  excerpt: string | null;
  body: string;
  author_name: string | null;
  cover_image_url: string | null;
  tags: string[];
  published_at: string | null;
}

export default function BlogPostPage({
  params,
}: {
  params: Promise<{ site_slug: string; slug: string }>;
}) {
  const { site_slug, slug } = use(params);
  const [post, setPost] = useState<BlogPost | null>(null);
  const [siteName, setSiteName] = useState("");
  const [notFound, setNotFound] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/public/sites/${site_slug}`)
      .then((r) => r.json())
      .then((d) => setSiteName(d.name ?? site_slug))
      .catch(() => {});

    fetch(`/api/public/sites/${site_slug}/blog/${slug}`)
      .then((r) => {
        if (!r.ok) { setNotFound(true); return null; }
        return r.json();
      })
      .then((d) => { if (d) setPost(d); })
      .catch(() => setNotFound(true))
      .finally(() => setLoading(false));
  }, [site_slug, slug]);

  if (loading) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </main>
    );
  }

  if (notFound || !post) {
    return (
      <main className="min-h-screen flex flex-col items-center justify-center gap-4">
        <h1 className="text-3xl font-bold text-gray-900">Post not found</h1>
        <a href={`/${site_slug}/blog`} className="text-blue-600 hover:underline">
          &larr; Back to blog
        </a>
      </main>
    );
  }

  const dateStr = post.published_at
    ? new Date(post.published_at).toLocaleDateString("en-US", {
        year: "numeric", month: "long", day: "numeric",
      })
    : null;

  return (
    <main className="min-h-screen bg-white">
      <article className="max-w-3xl mx-auto px-6 py-20">
        {/* Breadcrumb */}
        <nav className="mb-8 flex gap-2 text-sm text-gray-400">
          <a href={`/${site_slug}`} className="hover:text-blue-600">{siteName}</a>
          <span>/</span>
          <a href={`/${site_slug}/blog`} className="hover:text-blue-600">Blog</a>
          <span>/</span>
          <span className="text-gray-600 truncate max-w-xs">{post.title}</span>
        </nav>

        {/* Tags */}
        {post.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
            {post.tags.map((tag) => (
              <span key={tag} className="text-xs font-semibold px-3 py-1 rounded-full bg-blue-50 text-blue-700">
                {tag}
              </span>
            ))}
          </div>
        )}

        {/* Title */}
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 leading-tight mb-6">
          {post.title}
        </h1>

        {/* Meta */}
        <div className="flex items-center gap-4 text-sm text-gray-400 mb-8 pb-8 border-b border-gray-100">
          {post.author_name && <span>By <strong className="text-gray-700">{post.author_name}</strong></span>}
          {dateStr && <span>{dateStr}</span>}
        </div>

        {/* Cover image */}
        {post.cover_image_url && (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={post.cover_image_url}
            alt=""
            className="w-full rounded-2xl object-cover mb-10"
            style={{ maxHeight: "480px" }}
          />
        )}

        {/* Body — render markdown-style paragraphs */}
        <div className="prose prose-lg max-w-none text-gray-700 leading-relaxed">
          {post.body.split("\n\n").map((para, i) =>
            para.startsWith("# ") ? (
              <h2 key={i} className="text-2xl font-bold text-gray-900 mt-10 mb-4">{para.slice(2)}</h2>
            ) : para.startsWith("## ") ? (
              <h3 key={i} className="text-xl font-bold text-gray-900 mt-8 mb-3">{para.slice(3)}</h3>
            ) : (
              <p key={i} className="mb-6">{para}</p>
            )
          )}
        </div>

        {/* Footer nav */}
        <div className="mt-16 pt-8 border-t border-gray-100">
          <a href={`/${site_slug}/blog`} className="text-blue-600 hover:underline font-medium">
            &larr; Back to blog
          </a>
        </div>
      </article>
    </main>
  );
}
