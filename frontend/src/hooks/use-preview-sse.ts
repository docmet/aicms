/**
 * Hook that opens a fetch-based SSE connection to the preview stream for a page.
 *
 * Uses fetch (not EventSource) so we can send the Authorization header.
 * Automatically reconnects after 3s on disconnect.
 * Calls onSectionsUpdated whenever the backend broadcasts a draft change.
 */

import { useEffect, useRef } from 'react';

export interface SSESection {
  id: string;
  section_type: string;
  content_draft: string | null;
  order: number;
  has_unpublished_changes: boolean;
}

interface UsePreviewSSEOptions {
  pageId: string | null | undefined;
  onSectionsUpdated: (sections: SSESection[]) => void;
  enabled?: boolean;
}

export function usePreviewSSE({ pageId, onSectionsUpdated, enabled = true }: UsePreviewSSEOptions) {
  const onUpdateRef = useRef(onSectionsUpdated);
  onUpdateRef.current = onSectionsUpdated;

  useEffect(() => {
    if (!pageId || !enabled) return;

    const controller = new AbortController();

    async function connect() {
      while (!controller.signal.aborted) {
        const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
        if (!token) break;

        try {
          const response = await fetch(`/api/preview/pages/${pageId}/stream`, {
            headers: { Authorization: `Bearer ${token}` },
            signal: controller.signal,
          });

          if (!response.ok || !response.body) {
            // Non-retryable (401, 404): stop
            if (response.status === 401 || response.status === 404) break;
            throw new Error(`SSE ${response.status}`);
          }

          const reader = response.body.getReader();
          const decoder = new TextDecoder();
          let buffer = '';

          while (!controller.signal.aborted) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() ?? '';

            for (const line of lines) {
              if (!line.startsWith('data: ')) continue;
              try {
                const data = JSON.parse(line.slice(6)) as { type: string; sections?: SSESection[] };
                if (data.type === 'sections_updated' && data.sections) {
                  onUpdateRef.current(data.sections);
                }
              } catch {
                // ignore malformed event
              }
            }
          }
        } catch {
          if (controller.signal.aborted) break;
        }

        // Wait before reconnecting
        await new Promise<void>((resolve) => {
          const t = setTimeout(resolve, 3000);
          controller.signal.addEventListener('abort', () => { clearTimeout(t); resolve(); });
        });
      }
    }

    connect();
    return () => controller.abort();
  }, [pageId, enabled]);
}
