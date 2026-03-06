"use client";

import { useEffect, useRef } from "react";

type RenderMode = "text" | "markdown" | "html";

interface CustomContent {
  title?: string;
  content?: string;
  render_mode?: RenderMode;
}

function parseContent(raw: string): CustomContent {
  try {
    const parsed = JSON.parse(raw);
    return parsed as CustomContent;
  } catch {
    return { content: raw };
  }
}

/** Minimal safe markdown → React nodes (no external deps). */
function renderMarkdown(md: string) {
  const lines = md.split("\n");
  const nodes: React.ReactNode[] = [];
  let i = 0;

  const inlineStyle = (text: string): React.ReactNode[] => {
    // bold **text**, inline code `code`, links [label](url)
    const parts: React.ReactNode[] = [];
    const re = /(\*\*(.+?)\*\*|`(.+?)`|\[(.+?)\]\((.+?)\))/g;
    let last = 0;
    let m: RegExpExecArray | null;
    while ((m = re.exec(text)) !== null) {
      if (m.index > last) parts.push(text.slice(last, m.index));
      if (m[2]) parts.push(<strong key={m.index}>{m[2]}</strong>);
      else if (m[3]) parts.push(<code key={m.index} className="px-1 py-0.5 rounded text-sm bg-black/10 font-mono">{m[3]}</code>);
      else if (m[4] && m[5]) parts.push(<a key={m.index} href={m[5]} target="_blank" rel="noopener noreferrer" className="underline" style={{ color: "var(--color-primary)" }}>{m[4]}</a>);
      last = m.index + m[0].length;
    }
    if (last < text.length) parts.push(text.slice(last));
    return parts;
  };

  while (i < lines.length) {
    const line = lines[i];

    if (line.startsWith("### ")) {
      nodes.push(<h3 key={i} className="text-xl font-bold mt-6 mb-2" style={{ color: "var(--color-heading)", fontFamily: "var(--font-heading)" }}>{line.slice(4)}</h3>);
    } else if (line.startsWith("## ")) {
      nodes.push(<h2 key={i} className="text-2xl font-bold mt-8 mb-3" style={{ color: "var(--color-heading)", fontFamily: "var(--font-heading)" }}>{line.slice(3)}</h2>);
    } else if (line.startsWith("# ")) {
      nodes.push(<h1 key={i} className="text-4xl font-bold mt-8 mb-4" style={{ color: "var(--color-heading)", fontFamily: "var(--font-heading)" }}>{line.slice(2)}</h1>);
    } else if (line.startsWith("- ") || line.startsWith("* ")) {
      // Collect list items
      const items: string[] = [];
      while (i < lines.length && (lines[i].startsWith("- ") || lines[i].startsWith("* "))) {
        items.push(lines[i].slice(2));
        i++;
      }
      nodes.push(
        <ul key={`ul-${i}`} className="list-disc list-inside space-y-1 my-3">
          {items.map((item, j) => <li key={j}>{inlineStyle(item)}</li>)}
        </ul>
      );
      continue;
    } else if (/^\d+\. /.test(line)) {
      // Ordered list
      const items: string[] = [];
      while (i < lines.length && /^\d+\. /.test(lines[i])) {
        items.push(lines[i].replace(/^\d+\. /, ""));
        i++;
      }
      nodes.push(
        <ol key={`ol-${i}`} className="list-decimal list-inside space-y-1 my-3">
          {items.map((item, j) => <li key={j}>{inlineStyle(item)}</li>)}
        </ol>
      );
      continue;
    } else if (line.startsWith("---") || line.startsWith("***")) {
      nodes.push(<hr key={i} className="my-6 border-current opacity-20" />);
    } else if (line.trim() === "") {
      // blank line — spacer
      nodes.push(<div key={i} className="h-2" />);
    } else {
      nodes.push(<p key={i} className="leading-relaxed my-2">{inlineStyle(line)}</p>);
    }
    i++;
  }
  return nodes;
}

export function CustomSection({ content }: { content: string }) {
  const sectionRef = useRef<HTMLElement>(null);
  const data = parseContent(content);
  const mode = data.render_mode ?? "text";

  useEffect(() => {
    const el = sectionRef.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) el.classList.add("visible");
      },
      { threshold: 0.1 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <section
      ref={sectionRef}
      className="py-24 px-6 animate-on-scroll"
      style={{ background: "var(--color-bg)" }}
    >
      <div className="max-w-4xl mx-auto">
        {data.title && (
          <h2
            className="text-4xl md:text-5xl font-bold text-center mb-8"
            style={{
              color: "var(--color-heading)",
              fontFamily: "var(--font-heading)",
            }}
          >
            {data.title}
          </h2>
        )}
        {data.content && mode === "html" && (
          /* eslint-disable-next-line react/no-danger */
          <div
            className="prose max-w-none"
            style={{ color: "var(--color-text)" }}
            dangerouslySetInnerHTML={{ __html: data.content }}
          />
        )}
        {data.content && mode === "markdown" && (
          <div className="text-base leading-relaxed" style={{ color: "var(--color-text)" }}>
            {renderMarkdown(data.content)}
          </div>
        )}
        {data.content && mode === "text" && (
          <div
            className="text-lg leading-relaxed space-y-4"
            style={{ color: "var(--color-text)" }}
          >
            {data.content.split("\n").map((paragraph, i) => (
              <p key={i}>{paragraph}</p>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
