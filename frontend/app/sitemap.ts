import type { MetadataRoute } from "next";
import { listBonds } from "@/lib/api";
import { bondToSlug } from "@/lib/slugs";

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  // se a API estiver fora do ar na hora de gerar o sitemap, ainda assim
  // devolve pelo menos a home — sitemap parcial é melhor que build quebrado
  const bonds = await listBonds().catch(() => []);

  const bondEntries: MetadataRoute.Sitemap = bonds.map((bond) => ({
    url: `${BASE_URL}/${bondToSlug(bond)}`,
    lastModified: new Date(),
    changeFrequency: "daily",
    priority: 0.8,
  }));

  return [
    { url: BASE_URL, lastModified: new Date(), changeFrequency: "daily", priority: 1 },
    ...bondEntries,
  ];
}
