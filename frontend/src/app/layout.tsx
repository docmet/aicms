import type { Metadata } from "next";
import { Inter, Sora } from "next/font/google";
import "./globals.css";
import { AuthProviderWrapper } from "@/components/auth-provider-wrapper";

// Inter: clean body font used everywhere
const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

// Sora: expressive headline font for public site sections
const sora = Sora({
  subsets: ["latin"],
  weight: ["400", "600", "700", "800"],
  variable: "--font-sora",
  display: "swap",
});

export const metadata: Metadata = {
  title: "AI CMS",
  description: "Build and edit stunning websites with your own AI tools.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${sora.variable}`}>
      <body className={inter.className}>
        <AuthProviderWrapper>{children}</AuthProviderWrapper>
      </body>
    </html>
  );
}
