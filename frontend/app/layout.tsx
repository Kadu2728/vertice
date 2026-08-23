import type { Metadata } from "next";
import { Fraunces, IBM_Plex_Mono, Source_Sans_3 } from "next/font/google";
import "./globals.css";

// Papel de Ofício — Fraunces carrega a autoridade do lançamento (display,
// uso restrito); Source Sans 3 é o texto corrido; IBM Plex Mono é onde todo
// número financeiro vive — algarismos tabulares, essencial para a coluna de
// valores do livro-razão (ver docs/design/direcao-a.md).
const fraunces = Fraunces({
  variable: "--font-fraunces",
  subsets: ["latin"],
  weight: ["500", "600"],
});

const sourceSans = Source_Sans_3({
  variable: "--font-source-sans",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

const plexMono = IBM_Plex_Mono({
  variable: "--font-plex-mono",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: { default: "VÉRTICE", template: "%s — VÉRTICE" },
  description: "Simulação e explicação de marcação a mercado de títulos públicos brasileiros.",
  openGraph: {
    siteName: "VÉRTICE",
    locale: "pt_BR",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      <body
        className={`${fraunces.variable} ${sourceSans.variable} ${plexMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
