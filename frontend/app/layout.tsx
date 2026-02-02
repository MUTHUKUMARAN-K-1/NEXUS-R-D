import { ReactNode } from 'react';
import './globals.css';
import Providers from './providers';

export const metadata = {
  title: 'NEXUS-R&D | Recursive Innovation Intelligence',
  description: 'From Patents to Profits: Autonomous Discovery of Tomorrow\'s Innovations',
  keywords: ['AI', 'Research', 'Innovation', 'Patent Analysis', 'Market Intelligence'],
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="icon" href="/favicon.ico" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body className="antialiased">
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
