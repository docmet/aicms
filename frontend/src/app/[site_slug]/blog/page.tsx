"use client";

import { use, useEffect, useState } from "react";

interface BlogPostSummary {
  id: string;
  slug: string;
  title: string;
  excerpt: string | null;
  author_name: string | null;
  cover_image_url: string | null;
  tags: string[];
  published_at: string | null;
}

export default function BlogIndexPage({
  params,
}: {
  params: Promise<{ site_slug: string }>;
}) {
  const { site_slug } = use(params);
  const [posts, setPosts] = useState<BlogPostSummary[]>([]);
  const [siteName, setSiteName] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch site info for the name
    fetch(`/api/public/sites/${site_slug}`)
      .then((r) => r.json())
      .then((d) => setSiteName(d.name ?? site_slug))
      .catch(() => {});

    fetch(`/api/public/sites/${site_slug}/blog`)
      .then((r) => (r.ok ? r.json() : []))
      .then(setPosts)
      .catch(() => setPosts([]))
      .finally(() => setLoading(false));
  }, [site_slug]);

  if (loading) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-white">
      <div className="max-w-4xl mx-auto px-6 py-20">
        <div className="mb-12">
          <a href={`/${site_slug}`} className="text-sm text-blue-600 hover:underline mb-4 inline-block">
            &larr; Back to {siteName}
          </a>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-3">Blog</h1>
          {posts.length > 0 && (
            <p className="text-gray-500">{posts.length} post{posts.length !== 1 ? "s" : ""}</p>
          )}
        </div>

        {posts.length === 0 ? (
          <p className="text-gray-400 text-lg">No posts published yet.</p>
        ) : (
          <div className="space-y-10">
            {posts.map((post) => (
              <article key={post.id} className="group">
                {post.cover_image_url && (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={post.cover_image_url}
                    alt=""
                    className="w-full h-64 object-cover rounded-2xl mb-6"
                  />
                )}
                <div className="flex flex-wrap gap-2 mb-3">
                  {post.tags.map((tag) => (
                    <span
                      key={tag}
                      className="text-xs font-semibold px-3 py-1 rounded-full bg-blue-50 text-blue-700"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
                  <a href={`/${site_slug}/blog/${post.slug}`}>{post.title}</a>
                </h2>
                {post.excerpt && (
                  <p className="text-gray-600 leading-relaxed mb-4">{post.excerpt}</p>
                )}
                <div className="flex items-center gap-4 text-sm text-gray-400">
                  {post.author_name && <span>{post.author_name}</span>}
                  {post.published_at && (
                    <span>
                      {new Date(post.published_at).toLocaleDateString("en-US", {
                        year: "numeric",
                        month: "long",
                        day: "numeric",
                      })}
                    </span>
                  )}
                  <a
                    href={`/${site_slug}/blog/${post.slug}`}
                    className="text-blue-600 font-medium hover:underline"
                  >
                    Read more &rarr;
                  </a>
                </div>
                <hr className="mt-10 border-gray-100" />
              </article>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
