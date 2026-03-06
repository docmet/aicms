'use client';

import Link from 'next/link';
import { Check, Zap } from 'lucide-react';

const WHAT_YOU_CAN_DO = [
  'Create and manage sites & pages',
  'Write and publish content sections',
  'Apply themes and preview changes',
  'Build entire sites from a single prompt',
];

const EXAMPLE_PROMPTS = [
  'Build me a homepage for my bakery called "Flour & Co."',
  'Add a testimonials section with 3 real-sounding reviews',
  'Change the theme to dark and publish the page',
  'Rewrite the hero headline to be more punchy',
  'Create an About page and fill it in',
];

export default function HelpPage() {
  return (
    <div className="space-y-8 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Help & Getting Started</h1>
        <p className="text-sm text-gray-500 mt-0.5">How to connect MyStorey to your AI tools</p>
      </div>

      {/* What you can do */}
      <div className="bg-white border border-gray-200 rounded-2xl p-6 space-y-4">
        <h2 className="text-sm font-semibold text-gray-900">What you can do with AI</h2>
        <ul className="space-y-2.5">
          {WHAT_YOU_CAN_DO.map((label) => (
            <li key={label} className="flex items-center gap-2.5 text-sm text-gray-600">
              <Check size={14} className="text-violet-500 flex-shrink-0" />
              {label}
            </li>
          ))}
        </ul>
      </div>

      {/* Connect */}
      <div className="bg-white border border-gray-200 rounded-2xl p-6 space-y-4">
        <h2 className="text-sm font-semibold text-gray-900">Connect your AI tool</h2>
        <p className="text-sm text-gray-500">
          MyStorey uses the{' '}
          <span className="font-medium text-gray-700">Model Context Protocol (MCP)</span> — a
          standard that lets AI assistants like ChatGPT and Claude talk directly to your sites.
        </p>
        <ol className="space-y-3">
          {[
            <>
              Go to{' '}
              <Link
                href="/dashboard/mcp"
                className="font-medium text-violet-600 hover:text-violet-700 underline underline-offset-2"
              >
                AI Tools
              </Link>{' '}
              in the sidebar.
            </>,
            'Click "Connect" next to ChatGPT, Claude, or Perplexity.',
            'Follow the one-click OAuth flow — no tokens to copy.',
            'Start chatting. Your AI can now build and edit your sites.',
          ].map((step, i) => (
            <li key={i} className="flex gap-3 text-sm text-gray-600">
              <span className="shrink-0 w-5 h-5 rounded-full bg-violet-100 text-violet-700 flex items-center justify-center text-[11px] font-bold mt-0.5">
                {i + 1}
              </span>
              <span>{step}</span>
            </li>
          ))}
        </ol>
      </div>

      {/* Example prompts */}
      <div className="bg-white border border-gray-200 rounded-2xl p-6 space-y-4">
        <h2 className="text-sm font-semibold text-gray-900">Example prompts to try</h2>
        <ul className="space-y-2">
          {EXAMPLE_PROMPTS.map((p) => (
            <li
              key={p}
              className="flex items-start gap-2.5 text-sm text-gray-600 bg-gray-50 border border-gray-100 rounded-lg px-3.5 py-2.5"
            >
              <Zap size={13} className="text-violet-400 mt-0.5 flex-shrink-0" />
              &ldquo;{p}&rdquo;
            </li>
          ))}
        </ul>
      </div>

      {/* Tips */}
      <div className="bg-violet-50 border border-violet-100 rounded-2xl p-6 space-y-3">
        <h2 className="text-sm font-semibold text-violet-900">Tips for best results</h2>
        <ul className="space-y-2">
          {[
            'Tell the AI your business name, industry, and vibe upfront.',
            'Ask it to publish after each round of changes so you see them live.',
            'You can edit sections manually in the dashboard after AI builds them.',
            'Use the version history to revert if something goes wrong.',
          ].map((tip) => (
            <li key={tip} className="flex items-start gap-2 text-sm text-violet-800">
              <Check size={13} className="text-violet-500 mt-0.5 flex-shrink-0" />
              {tip}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
