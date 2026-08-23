import type { BondSeries, Simulation } from "./types";

/**
 * Dado estático de demonstração — NENHUM valor aqui é calculado em
 * JavaScript. Os números foram gerados uma única vez com as regras reais
 * de tributação/custódia do backend (script Python descartável, não parte
 * do frontend) e colados como literais. O frontend nunca calcula número
 * financeiro (ADR-003) — nem para mock, para não abrir um precedente que
 * alguém reaproveite "temporariamente" depois.
 *
 * Substituir por `fetch` real em `POST /api/v1/simulations` e
 * `POST /api/v1/simulations/{id}/scenarios` assim que houver backend com
 * banco populado (ver docs/domain/fase-4-status.md).
 */

export const MOCK_ENGINE_VERSION = "2026.08.1";

export const MOCK_BONDS: BondSeries[] = [
  { id: "ltn-2029", bondType: "LTN", maturityDate: "2029-01-01", couponRateAnnual: null },
  { id: "ntnb-2035", bondType: "NTN-B", maturityDate: "2035-08-15", couponRateAnnual: "0.06" },
  { id: "lft-2027", bondType: "LFT", maturityDate: "2027-03-01", couponRateAnnual: null },
];

const SHOCK_STEPS = [-200, -150, -100, -50, 0, 50, 100, 150, 200] as const;
export type ShockBps = (typeof SHOCK_STEPS)[number];
export { SHOCK_STEPS };

interface ScenarioPoint {
  puReference: string;
  grossValueToday: string;
  taxes: { grossGain: string; iofAmount: string; irAmount: string; netGain: string };
  custodyFeeAmount: string;
  netValueToday: string;
}

const LTN_SCENARIOS: Record<ShockBps, ScenarioPoint> = {
  [-200]: { puReference: "1210.03", grossValueToday: "1612.69", taxes: { grossGain: "612.69", iofAmount: "0.00", irAmount: "107.22", netGain: "505.47" }, custodyFeeAmount: "5.27", netValueToday: "1500.20" },
  [-150]: { puReference: "1113.31", grossValueToday: "1483.78", taxes: { grossGain: "483.78", iofAmount: "0.00", irAmount: "84.66", netGain: "399.12" }, custodyFeeAmount: "4.85", netValueToday: "1394.27" },
  [-100]: { puReference: "1016.59", grossValueToday: "1354.88", taxes: { grossGain: "354.88", iofAmount: "0.00", irAmount: "62.10", netGain: "292.77" }, custodyFeeAmount: "4.42", netValueToday: "1288.35" },
  [-50]: { puReference: "919.87", grossValueToday: "1225.97", taxes: { grossGain: "225.97", iofAmount: "0.00", irAmount: "39.54", netGain: "186.43" }, custodyFeeAmount: "4.00", netValueToday: "1182.42" },
  [0]: { puReference: "823.15", grossValueToday: "1097.07", taxes: { grossGain: "97.07", iofAmount: "0.00", irAmount: "16.99", netGain: "80.08" }, custodyFeeAmount: "3.58", netValueToday: "1076.50" },
  [50]: { puReference: "726.43", grossValueToday: "968.16", taxes: { grossGain: "-31.84", iofAmount: "0.00", irAmount: "0.00", netGain: "-31.84" }, custodyFeeAmount: "3.16", netValueToday: "965.00" },
  [100]: { puReference: "629.71", grossValueToday: "839.25", taxes: { grossGain: "-160.75", iofAmount: "0.00", irAmount: "0.00", netGain: "-160.75" }, custodyFeeAmount: "2.74", netValueToday: "836.51" },
  [150]: { puReference: "532.99", grossValueToday: "710.35", taxes: { grossGain: "-289.65", iofAmount: "0.00", irAmount: "0.00", netGain: "-289.65" }, custodyFeeAmount: "2.32", netValueToday: "708.03" },
  [200]: { puReference: "436.27", grossValueToday: "581.44", taxes: { grossGain: "-418.56", iofAmount: "0.00", irAmount: "0.00", netGain: "-418.56" }, custodyFeeAmount: "1.90", netValueToday: "579.55" },
};

const NTNB_SCENARIOS: Record<ShockBps, ScenarioPoint> = {
  [-200]: { puReference: "4217.47", grossValueToday: "1721.35", taxes: { grossGain: "721.35", iofAmount: "0.00", irAmount: "126.24", netGain: "595.11" }, custodyFeeAmount: "5.62", netValueToday: "1589.49" },
  [-150]: { puReference: "3790.70", grossValueToday: "1547.16", taxes: { grossGain: "547.16", iofAmount: "0.00", irAmount: "95.75", netGain: "451.41" }, custodyFeeAmount: "5.05", netValueToday: "1446.36" },
  [-100]: { puReference: "3363.94", grossValueToday: "1372.98", taxes: { grossGain: "372.98", iofAmount: "0.00", irAmount: "65.27", netGain: "307.71" }, custodyFeeAmount: "4.48", netValueToday: "1303.22" },
  [-50]: { puReference: "2937.17", grossValueToday: "1198.80", taxes: { grossGain: "198.80", iofAmount: "0.00", irAmount: "34.79", netGain: "164.01" }, custodyFeeAmount: "3.91", netValueToday: "1160.09" },
  [0]: { puReference: "2510.40", grossValueToday: "1024.61", taxes: { grossGain: "24.61", iofAmount: "0.00", irAmount: "4.31", netGain: "20.30" }, custodyFeeAmount: "3.35", netValueToday: "1016.96" },
  [50]: { puReference: "2083.63", grossValueToday: "850.43", taxes: { grossGain: "-149.57", iofAmount: "0.00", irAmount: "0.00", netGain: "-149.57" }, custodyFeeAmount: "2.78", netValueToday: "847.65" },
  [100]: { puReference: "1656.86", grossValueToday: "676.24", taxes: { grossGain: "-323.76", iofAmount: "0.00", irAmount: "0.00", netGain: "-323.76" }, custodyFeeAmount: "2.21", netValueToday: "674.03" },
  [150]: { puReference: "1230.10", grossValueToday: "502.06", taxes: { grossGain: "-497.94", iofAmount: "0.00", irAmount: "0.00", netGain: "-497.94" }, custodyFeeAmount: "1.64", netValueToday: "500.42" },
  [200]: { puReference: "803.33", grossValueToday: "327.88", taxes: { grossGain: "-672.12", iofAmount: "0.00", irAmount: "0.00", netGain: "-672.12" }, custodyFeeAmount: "1.07", netValueToday: "326.80" },
};

const LFT_SCENARIOS: Record<ShockBps, ScenarioPoint> = {
  [-200]: { puReference: "15069.46", grossValueToday: "1037.82", taxes: { grossGain: "37.82", iofAmount: "0.00", irAmount: "7.56", netGain: "30.26" }, custodyFeeAmount: "0.00", netValueToday: "1030.26" },
  [-150]: { puReference: "15024.79", grossValueToday: "1034.74", taxes: { grossGain: "34.74", iofAmount: "0.00", irAmount: "6.95", netGain: "27.79" }, custodyFeeAmount: "0.00", netValueToday: "1027.79" },
  [-100]: { puReference: "14980.11", grossValueToday: "1031.67", taxes: { grossGain: "31.67", iofAmount: "0.00", irAmount: "6.33", netGain: "25.33" }, custodyFeeAmount: "0.00", netValueToday: "1025.33" },
  [-50]: { puReference: "14935.44", grossValueToday: "1028.59", taxes: { grossGain: "28.59", iofAmount: "0.00", irAmount: "5.72", netGain: "22.87" }, custodyFeeAmount: "0.00", netValueToday: "1022.87" },
  [0]: { puReference: "14890.77", grossValueToday: "1025.51", taxes: { grossGain: "25.51", iofAmount: "0.00", irAmount: "5.10", netGain: "20.41" }, custodyFeeAmount: "0.00", netValueToday: "1020.41" },
  [50]: { puReference: "14846.10", grossValueToday: "1022.44", taxes: { grossGain: "22.44", iofAmount: "0.00", irAmount: "4.49", netGain: "17.95" }, custodyFeeAmount: "0.00", netValueToday: "1017.95" },
  [100]: { puReference: "14801.43", grossValueToday: "1019.36", taxes: { grossGain: "19.36", iofAmount: "0.00", irAmount: "3.87", netGain: "15.49" }, custodyFeeAmount: "0.00", netValueToday: "1015.49" },
  [150]: { puReference: "14756.75", grossValueToday: "1016.28", taxes: { grossGain: "16.28", iofAmount: "0.00", irAmount: "3.26", netGain: "13.03" }, custodyFeeAmount: "0.00", netValueToday: "1013.03" },
  [200]: { puReference: "14712.08", grossValueToday: "1013.21", taxes: { grossGain: "13.21", iofAmount: "0.00", irAmount: "2.64", netGain: "10.57" }, custodyFeeAmount: "0.00", netValueToday: "1010.57" },
};

const SCENARIOS_BY_BOND: Record<string, Record<ShockBps, ScenarioPoint>> = {
  "ltn-2029": LTN_SCENARIOS,
  "ntnb-2035": NTNB_SCENARIOS,
  "lft-2027": LFT_SCENARIOS,
};

const BASE_INPUT: Record<string, { quantity: string; puPurchase: string; purchaseDate: string; daysHeld: number }> = {
  "ltn-2029": { quantity: "1.332764687067", puPurchase: "750.32", purchaseDate: "2025-01-02", daysHeld: 596 },
  "ntnb-2035": { quantity: "0.408146606261", puPurchase: "2450.10", purchaseDate: "2025-01-02", daysHeld: 596 },
  "lft-2027": { quantity: "0.068869100501", puPurchase: "14520.30", purchaseDate: "2025-10-25", daysHeld: 300 },
};

export const MOCK_REFERENCE_DATE = "2026-08-21";

const REFERENCE_AMOUNT = 1000;

/**
 * Escala proporcional de exibição — não é cálculo financeiro (não aplica
 * taxa, faixa de IR nem fórmula de precificação, só multiplica valores já
 * computados pela mesma razão que "R$ 1.000 → R$ 2.000 é o dobro"). Existe
 * só para o campo de valor investido do mock parecer reativo. Caveat
 * conhecido: a isenção de custódia da LFT (R$ 10.000 fixos) não escala
 * linearmente — o mock não reproduz esse detalhe fora de R$ 1.000; a API
 * real (domain/taxation/custody.py) já trata isso corretamente.
 */
function scale(value: string, factor: number): string {
  return (Number(value) * factor).toFixed(2);
}

export function buildMockSimulation(bondSeriesId: string, amountInvested: string, shockBps: ShockBps = 0): Simulation {
  const bond = MOCK_BONDS.find((b) => b.id === bondSeriesId) ?? MOCK_BONDS[0];
  const scenario = SCENARIOS_BY_BOND[bond.id][shockBps];
  const input = BASE_INPUT[bond.id];
  const factor = (Number(amountInvested) || REFERENCE_AMOUNT) / REFERENCE_AMOUNT;

  return {
    id: `mock-${bond.id}`,
    bondSeriesId: bond.id,
    bondType: bond.bondType,
    purchaseDate: input.purchaseDate,
    referenceDate: MOCK_REFERENCE_DATE,
    amountInvested,
    quantity: (Number(input.quantity) * factor).toFixed(6),
    puPurchase: input.puPurchase,
    puReference: scenario.puReference,
    grossValueToday: scale(scenario.grossValueToday, factor),
    daysHeld: input.daysHeld,
    taxes: {
      grossGain: scale(scenario.taxes.grossGain, factor),
      iofAmount: scale(scenario.taxes.iofAmount, factor),
      irAmount: scale(scenario.taxes.irAmount, factor),
      netGain: scale(scenario.taxes.netGain, factor),
    },
    custodyFeeAmount: scale(scenario.custodyFeeAmount, factor),
    netValueToday: scale(scenario.netValueToday, factor),
    calculationEngineVersion: MOCK_ENGINE_VERSION,
  };
}

/**
 * "Valor líquido no vencimento" só é um número determinístico de verdade
 * para título prefixado sem cupom: o valor de face (R$ 1.000 por PU) não
 * depende de taxa de mercado nem de indexador futuro. Para NTN-B/LFT, o
 * valor no vencimento depende de IPCA/Selic que ainda não aconteceram —
 * mostrar um número ali seria projetar, não calcular. Para NTN-F, depende
 * de tratar cada cupom futuro com o IR da época em que cai, o que o motor
 * ainda não decompõe (ver docs/domain/fase-4-status.md). Por isso só a LTN
 * tem esse dado aqui — as outras mostram um estado "não disponível"
 * honesto em vez de inventar um número.
 */
interface MaturityPoint {
  grossValueAtMaturity: string;
  taxes: { grossGain: string; iofAmount: string; irAmount: string; netGain: string };
  custodyFeeAmount: string;
  netValueAtMaturity: string;
  daysToMaturity: number;
}

const MATURITY_BY_BOND: Partial<Record<string, MaturityPoint>> = {
  "ltn-2029": {
    grossValueAtMaturity: "1332.76",
    taxes: { grossGain: "332.76", iofAmount: "0.00", irAmount: "49.91", netGain: "282.85" },
    custodyFeeAmount: "10.66",
    netValueAtMaturity: "1272.19",
    daysToMaturity: 1460,
  },
};

export interface MaturityComparison {
  grossValueAtMaturity: string;
  taxes: { grossGain: string; iofAmount: string; irAmount: string; netGain: string };
  custodyFeeAmount: string;
  netValueAtMaturity: string;
  daysToMaturity: number;
}

export function getMockMaturityValue(
  bondSeriesId: string,
  amountInvested: string,
): MaturityComparison | null {
  const base = MATURITY_BY_BOND[bondSeriesId];
  if (!base) return null;
  const factor = (Number(amountInvested) || REFERENCE_AMOUNT) / REFERENCE_AMOUNT;
  return {
    grossValueAtMaturity: scale(base.grossValueAtMaturity, factor),
    taxes: {
      grossGain: scale(base.taxes.grossGain, factor),
      iofAmount: scale(base.taxes.iofAmount, factor),
      irAmount: scale(base.taxes.irAmount, factor),
      netGain: scale(base.taxes.netGain, factor),
    },
    custodyFeeAmount: scale(base.custodyFeeAmount, factor),
    netValueAtMaturity: scale(base.netValueAtMaturity, factor),
    daysToMaturity: base.daysToMaturity,
  };
}
