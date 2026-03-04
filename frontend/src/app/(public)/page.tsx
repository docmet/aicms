import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">AI CMS</h1>
          <p className="text-xl text-gray-600 mb-8">AI-powered Content Management System</p>
          <div className="space-x-4">
            <Link href="/register">
              <Button size="lg">Get Started</Button>
            </Link>
            <Link href="/login">
              <Button variant="outline" size="lg">
                Sign In
              </Button>
            </Link>
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          <Card>
            <CardHeader>
              <CardTitle>Easy to Use</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                Simple and intuitive interface for managing your website content with AI assistance.
              </CardDescription>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Beautiful Themes</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                Choose from multiple professionally designed themes to make your site stand out.
              </CardDescription>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>AI Powered</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                Leverage AI to help create, edit, and optimize your content effortlessly.
              </CardDescription>
            </CardContent>
          </Card>
        </div>

        <div className="text-center mt-16">
          <p className="text-gray-600">
            Ready to create your site?{' '}
            <Link href="/register" className="text-blue-600 hover:underline">
              Get started now
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
