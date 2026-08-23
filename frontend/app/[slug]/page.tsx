import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Suspense } from "react";
import { Simulator } from "@/components/simulation/simulator";
import { getBondQuotes, listBonds } from "@/lib/api";
import { BOND_TYPE_CONTENT } from "@/lib/bond-content";
import { formatDateBR, formatPercent } from "@/lib/format";
import { findBondBySlug } from "@/lib/slugs";
import type { BondSeries } from "@/lib/types";

// Renderizado sob demanda (SSR por requisição), não pré-gerado no build —
// gerar estático exigiria o backend disponível na hora do build do
// frontend, um acoplamento que não existe hoje entre deploy do Vercel e
// deploy do Render. SSR entrega o mesmo HTML já renderizado pro crawler,
// só que na hora da requisição em vez de antecipado.
const REVALIDATE_SECONDS = 3600;

async function getBondForSlug(slug: string): Promise<BondSeries | undefined> {
  const bonds = await listBonds({ next: { revalidate: REVALIDATE_SECONDS } });
  return findBondBySlug(bonds, slug);
}

interface PageProps {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const bond = await getBondForSlug(slug);
  if (!bond) return {};

  const content = BOND_TYPE_CONTENT[bond.bondType];
  const year = bond.maturityDate.slice(0, 4);
  const title = `${content.displayName} ${year}`;

  return {
    title,
    description: content.intro,
    alternates: { canonical: `/${slug}` },
    openGraph: { title, description: content.intro, type: "website" },
  };
}

export default async function BondPage({ params }: PageProps) {
  const { slug } = await params;
  const bond = await getBondForSlug(slug);
  if (!bond) notFound();

  const content = BOND_TYPE_CONTENT[bond.bondType];
  const year = bond.maturityDate.slice(0, 4);
  const quotes = await getBondQuotes(bond.id, 1, {
    next: { revalidate: REVALIDATE_SECONDS },
  }).catch(() => []);
  const latest = quotes[0];

  return (
    <main className="mx-auto max-w-4xl px-6 py-14">
      <header className="mb-10">
        <p className="mb-2 font-mono text-xs tracking-widest text-muted-foreground uppercase">
          {bond.bondType} · vencimento {formatDateBR(bond.maturityDate)}
        </p>
        <h1 className="font-heading text-3xl font-medium">
          {content.displayName} {year}
        </h1>
        <p className="mt-3 max-w-[60ch] text-muted-foreground">{content.intro}</p>
        {latest && (
          <p className="tabular mt-4 font-mono text-sm text-primary">
            Taxa indicativa em {formatDateBR(latest.quoteDate)}:{" "}
            {formatPercent(latest.referenceRateAnnual)} a.a.
          </p>
        )}
      </header>

      <section className="mb-12 max-w-[65ch] space-y-4 text-sm text-muted-foreground">
        <p>{content.howItWorks}</p>
        <p>{content.whoItsFor}</p>
      </section>

      {content.simulationSupported ? (
        <Suspense>
          <Simulator initialBondId={bond.id} />
        </Suspense>
      ) : (
        <div className="rounded-md border border-dashed border-border p-6 text-center text-muted-foreground">
          Simulação para {content.displayName} ainda não está disponível — em desenvolvimento.
        </div>
      )}
    </main>
  );
}
