import type { BondSeries, BondType } from "./types";

/**
 * Slugs seguem a nomenclatura oficial do Tesouro Direto, não a sigla ANBIMA
 * — "tesouro-ipca-2035" é o que uma pessoa procura no Google, não
 * "ntnb-2035". IPCA+ sem cupom (NTN-B Principal) e IPCA+ com cupom (NTN-B)
 * viram slugs diferentes porque são produtos diferentes na prateleira do
 * Tesouro Direto, mesmo tendo o mesmo ano de vencimento às vezes.
 */
const SLUG_PREFIX: Record<BondType, string> = {
  LTN: "tesouro-prefixado",
  "NTN-F": "tesouro-prefixado-juros-semestrais",
  "NTN-B Principal": "tesouro-ipca",
  "NTN-B": "tesouro-ipca-juros-semestrais",
  LFT: "tesouro-selic",
};

export function bondToSlug(bond: Pick<BondSeries, "bondType" | "maturityDate">): string {
  const year = bond.maturityDate.slice(0, 4);
  return `${SLUG_PREFIX[bond.bondType]}-${year}`;
}

export function findBondBySlug(bonds: BondSeries[], slug: string): BondSeries | undefined {
  return bonds.find((bond) => bondToSlug(bond) === slug);
}
