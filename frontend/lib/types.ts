/**
 * Espelha os DTOs de backend/api/v1/schemas/{bonds,simulations}.py.
 * Números financeiros chegam como string (o backend serializa Decimal como
 * string para não perder precisão em JSON) — nunca convertidos para float
 * no frontend, só formatados para exibição (ver lib/format.ts).
 */

export type BondType = "LTN" | "NTN-F" | "NTN-B" | "NTN-B Principal" | "LFT";

export interface BondSeries {
  id: string;
  bondType: BondType;
  maturityDate: string; // ISO yyyy-mm-dd
  couponRateAnnual: string | null;
}

export interface TaxBreakdown {
  grossGain: string;
  iofAmount: string;
  irAmount: string;
  netGain: string;
}

export interface Simulation {
  id: string;
  bondSeriesId: string;
  bondType: BondType;
  purchaseDate: string;
  referenceDate: string;
  amountInvested: string;
  quantity: string;
  puPurchase: string;
  puReference: string;
  grossValueToday: string;
  daysHeld: number;
  taxes: TaxBreakdown;
  custodyFeeAmount: string;
  netValueToday: string;
  calculationEngineVersion: string;
}
