import type { BondSeries, BondType, Simulation, TaxBreakdown } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    public status: number,
    public problemType: string,
    public detail: string,
  ) {
    super(detail);
  }
}

/** Corpo de erro RFC 7807 que api/errors.py devolve — ver docs/00-discovery.md §6. */
interface ProblemDetail {
  type: string;
  title: string;
  status: number;
  detail: string;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...init?.headers },
    });
  } catch {
    throw new ApiError(0, "urn:vertice:error:network", "Não foi possível falar com o servidor.");
  }

  if (!response.ok) {
    const problem = (await response.json().catch(() => null)) as ProblemDetail | null;
    throw new ApiError(
      response.status,
      problem?.type ?? "urn:vertice:error:unknown",
      problem?.detail ?? `Erro ${response.status}`,
    );
  }

  return response.json() as Promise<T>;
}

interface BondSeriesResponseDto {
  id: string;
  bond_type: BondType;
  maturity_date: string;
  coupon_rate_annual: string | null;
}

function mapBond(dto: BondSeriesResponseDto): BondSeries {
  return {
    id: dto.id,
    bondType: dto.bond_type,
    maturityDate: dto.maturity_date,
    couponRateAnnual: dto.coupon_rate_annual,
  };
}

interface SimulationResponseDto {
  id: string;
  bond_series_id: string;
  bond_type: BondType;
  purchase_date: string;
  reference_date: string;
  amount_invested: string;
  quantity: string;
  pu_purchase: string;
  pu_reference: string;
  gross_value_today: string;
  days_held: number;
  taxes: {
    gross_gain: string;
    iof_amount: string;
    ir_amount: string;
    net_gain: string;
  };
  custody_fee_amount: string;
  net_value_today: string;
  calculation_engine_version: string;
}

function mapSimulation(dto: SimulationResponseDto): Simulation {
  const taxes: TaxBreakdown = {
    grossGain: dto.taxes.gross_gain,
    iofAmount: dto.taxes.iof_amount,
    irAmount: dto.taxes.ir_amount,
    netGain: dto.taxes.net_gain,
  };
  return {
    id: dto.id,
    bondSeriesId: dto.bond_series_id,
    bondType: dto.bond_type,
    purchaseDate: dto.purchase_date,
    referenceDate: dto.reference_date,
    amountInvested: dto.amount_invested,
    quantity: dto.quantity,
    puPurchase: dto.pu_purchase,
    puReference: dto.pu_reference,
    grossValueToday: dto.gross_value_today,
    daysHeld: dto.days_held,
    taxes,
    custodyFeeAmount: dto.custody_fee_amount,
    netValueToday: dto.net_value_today,
    calculationEngineVersion: dto.calculation_engine_version,
  };
}

export async function listBonds(init?: RequestInit): Promise<BondSeries[]> {
  const dtos = await request<BondSeriesResponseDto[]>("/api/v1/bonds", init);
  return dtos.map(mapBond);
}

interface BondQuoteResponseDto {
  quote_date: string;
  reference_rate_annual: string;
}

export interface BondQuote {
  quoteDate: string;
  referenceRateAnnual: string;
}

export async function getBondQuotes(
  bondId: string,
  limit = 1,
  init?: RequestInit,
): Promise<BondQuote[]> {
  const dtos = await request<BondQuoteResponseDto[]>(
    `/api/v1/bonds/${bondId}/quotes?limit=${limit}`,
    init,
  );
  return dtos.map((dto) => ({ quoteDate: dto.quote_date, referenceRateAnnual: dto.reference_rate_annual }));
}

export async function createSimulation(params: {
  bondSeriesId: string;
  purchaseDate: string;
  amountInvested: string;
  referenceDate?: string;
}): Promise<Simulation> {
  const dto = await request<SimulationResponseDto>("/api/v1/simulations", {
    method: "POST",
    body: JSON.stringify({
      bond_series_id: params.bondSeriesId,
      purchase_date: params.purchaseDate,
      amount_invested: params.amountInvested,
      reference_date: params.referenceDate ?? null,
    }),
  });
  return mapSimulation(dto);
}

export async function getSimulation(simulationId: string): Promise<Simulation> {
  const dto = await request<SimulationResponseDto>(`/api/v1/simulations/${simulationId}`);
  return mapSimulation(dto);
}

export async function createScenario(
  simulationId: string,
  shockBps: number,
): Promise<Simulation> {
  const dto = await request<SimulationResponseDto>(
    `/api/v1/simulations/${simulationId}/scenarios`,
    { method: "POST", body: JSON.stringify({ shock_bps: shockBps }) },
  );
  return mapSimulation(dto);
}
