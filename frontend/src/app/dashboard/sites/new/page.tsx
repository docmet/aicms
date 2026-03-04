'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import api from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import Link from 'next/link';

export default function NewSitePage() {
  const [name, setName] = useState('');
  const [slug, setSlug] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const router = useRouter();
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const response = await api.post('/sites/', {
        name,
        slug,
        theme_slug: 'default',
      });

      toast({
        title: 'Success',
        description: 'Your new site has been created.',
      });

      router.push(`/dashboard/sites/${response.data.id}`);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      console.error('Failed to create site', error);
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to create site.',
        variant: 'destructive',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Auto-generate slug from name
  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newName = e.target.value;
    setName(newName);
    if (!slug || slug === newName.toLowerCase().replace(/ /g, '-').replace(/[^\w-]+/g, '')) {
      setSlug(newName.toLowerCase().replace(/ /g, '-').replace(/[^\w-]+/g, ''));
    }
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="sm" asChild>
          <Link href="/dashboard">Back</Link>
        </Button>
        <h1 className="text-3xl font-bold text-gray-900">Create New Site</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Site Details</CardTitle>
          <CardDescription>
            Give your new landing page a name and a unique URL slug.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Site Name</Label>
              <Input
                id="name"
                placeholder="My Awesome Landing Page"
                value={name}
                onChange={handleNameChange}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="slug">URL Slug</Label>
              <div className="flex items-center gap-2">
                <Input
                  id="slug"
                  placeholder="my-site"
                  value={slug}
                  onChange={(e) => setSlug(e.target.value.toLowerCase().replace(/ /g, '-'))}
                  required
                />
                <span className="text-sm text-gray-500 whitespace-nowrap">
                  .aicms.docmet.systems
                </span>
              </div>
              <p className="text-xs text-gray-400">
                Only lowercase letters, numbers, and hyphens are allowed.
              </p>
            </div>
            <div className="pt-4 flex justify-end">
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Creating...' : 'Create Site'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
