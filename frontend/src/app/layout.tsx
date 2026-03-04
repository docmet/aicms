import { AuthProviderWrapper } from '@/components/auth-provider-wrapper';
import './globals.css';

export const metadata = {
  title: 'AI CMS',
  description: 'AI-powered Content Management System',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <AuthProviderWrapper>
          {children}
        </AuthProviderWrapper>
      </body>
    </html>
  )
}
