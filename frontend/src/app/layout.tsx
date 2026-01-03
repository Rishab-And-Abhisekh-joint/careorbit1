import type { Metadata, Viewport } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'CareOrbit - Multi-Agent Healthcare Coordination',
  description: 'AI-powered care coordination for patients with multiple chronic conditions. Powered by Microsoft Azure AI.',
  keywords: ['healthcare', 'AI', 'care coordination', 'chronic disease', 'medication management', 'Microsoft Azure'],
  authors: [{ name: 'CareOrbit Team' }],
  openGraph: {
    title: 'CareOrbit - Multi-Agent Healthcare Coordination',
    description: 'AI-powered care coordination for patients with multiple chronic conditions',
    type: 'website',
    locale: 'en_US',
  },
  robots: {
    index: true,
    follow: true,
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
  themeColor: '#0ea5e9',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className="min-h-screen bg-slate-950 text-slate-100 antialiased">
        {/* Skip to main content link for accessibility */}
        <a 
          href="#main-content" 
          className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 
                     bg-careorbit-500 text-white px-4 py-2 rounded-lg z-50"
        >
          Skip to main content
        </a>
        
        {/* Main App Container */}
        <div className="relative min-h-screen">
          {/* Animated background gradient */}
          <div className="fixed inset-0 -z-10 animated-bg opacity-50" />
          
          {/* Gradient orbs for visual interest */}
          <div className="fixed top-0 left-1/4 w-96 h-96 bg-careorbit-500/20 rounded-full blur-3xl -z-10" />
          <div className="fixed bottom-0 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl -z-10" />
          
          {children}
        </div>
        
        {/* Screen reader announcements container */}
        <div 
          id="sr-announcements" 
          className="sr-only" 
          role="status" 
          aria-live="polite" 
          aria-atomic="true"
        />
      </body>
    </html>
  );
}
