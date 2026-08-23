"use client";

import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { Simulation } from "@/lib/types";
import { formatCurrencyBRL } from "@/lib/format";

interface WaterfallStep {
  label: string;
  delta: number;
  isAnchor: boolean;
}

function buildSteps(sim: Simulation): WaterfallStep[] {
  return [
    { label: "Investido", delta: Number(sim.amountInvested), isAnchor: true },
    { label: "Ganho bruto", delta: Number(sim.taxes.grossGain), isAnchor: false },
    { label: "IOF", delta: -Number(sim.taxes.iofAmount), isAnchor: false },
    { label: "IR", delta: -Number(sim.taxes.irAmount), isAnchor: false },
    { label: "Custódia", delta: -Number(sim.custodyFeeAmount), isAnchor: false },
    { label: "Líquido hoje", delta: Number(sim.netValueToday), isAnchor: true },
  ];
}

interface ChartRow {
  label: string;
  base: number;
  value: number;
  delta: number;
  isAnchor: boolean;
}

function buildRows(steps: WaterfallStep[]): ChartRow[] {
  let running = 0;
  const rows: ChartRow[] = [];
  for (const step of steps) {
    if (step.isAnchor) {
      rows.push({ label: step.label, base: 0, value: step.delta, delta: step.delta, isAnchor: true });
      running = step.delta;
      continue;
    }
    const start = step.delta >= 0 ? running : running + step.delta;
    const height = Math.abs(step.delta);
    rows.push({ label: step.label, base: start, value: height, delta: step.delta, isAnchor: false });
    running += step.delta;
  }
  return rows;
}

function barColor(row: ChartRow): string {
  if (row.isAnchor) return "var(--primary)";
  return row.delta >= 0 ? "var(--positive)" : "var(--negative)";
}

export function Waterfall({ simulation }: { simulation: Simulation }) {
  const rows = buildRows(buildSteps(simulation));

  return (
    <div className="h-64 w-full min-w-0">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={rows} margin={{ top: 8, right: 8, left: 8, bottom: 0 }} barGap={4}>
          <XAxis
            dataKey="label"
            tick={{ fill: "var(--muted-foreground)", fontSize: 11, fontFamily: "var(--font-mono)" }}
            axisLine={{ stroke: "var(--border)" }}
            tickLine={false}
          />
          <YAxis hide domain={[0, (max: number) => max * 1.15]} />
          <Tooltip
            cursor={{ fill: "var(--accent)", opacity: 0.15 }}
            contentStyle={{
              background: "var(--card)",
              border: "1px solid var(--border)",
              borderRadius: 2,
              fontFamily: "var(--font-mono)",
              fontSize: 12,
            }}
            labelStyle={{ color: "var(--muted-foreground)" }}
            formatter={(_value, _name, item) => {
              const row = (item as { payload?: ChartRow } | undefined)?.payload;
              const sign = row && !row.isAnchor ? (row.delta >= 0 ? "+" : "−") : "";
              return [`${sign}${formatCurrencyBRL(String(Math.abs(row?.delta ?? 0)))}`, ""];
            }}
          />
          {/* base invisível — empurra a barra visível até a altura certa, técnica padrão de waterfall no Recharts */}
          <Bar dataKey="base" stackId="wf" fill="transparent" isAnimationActive={false} />
          <Bar dataKey="value" stackId="wf" radius={[1, 1, 0, 0]} isAnimationActive={false}>
            {rows.map((row) => (
              <Cell key={row.label} fill={barColor(row)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
