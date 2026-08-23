"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { Slider } from "@/components/ui/slider";
import { ApiError, createScenario, createSimulation, getSimulation, listBonds } from "@/lib/api";
import { formatCurrencyBRL, formatDateBR, formatSignedCurrencyBRL } from "@/lib/format";
import type { BondSeries, Simulation } from "@/lib/types";
import { ShareButton } from "./share-button";
import { Waterfall } from "./waterfall";

// Datas com cotação real ingerida (Fase 3) — fixas até existir um job de
// ingestão diário rodando de verdade e um seletor de data no formulário.
const PURCHASE_DATE = "2025-01-02";
const REFERENCE_DATE = "2026-08-21";

const SUPPORTED_TYPES = new Set(["LTN", "NTN-F"]);

const BOND_TYPE_LABELS: Record<string, string> = {
  LTN: "Tesouro Prefixado",
  "NTN-F": "Tesouro Prefixado com juros semestrais",
};

function bondLabel(bond: BondSeries): string {
  return `${BOND_TYPE_LABELS[bond.bondType] ?? bond.bondType} ${bond.maturityDate.slice(0, 4)}`;
}

type Status = "loading-bonds" | "idle" | "simulating" | "simulated" | "error";

export function Simulator({ initialBondId }: { initialBondId?: string } = {}) {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [bonds, setBonds] = useState<BondSeries[]>([]);
  const [bondId, setBondId] = useState<string>(initialBondId ?? "");
  const [amount, setAmount] = useState("1000,00");
  const [shockBps, setShockBps] = useState(0);
  const [simulation, setSimulation] = useState<Simulation | null>(null);
  const [status, setStatus] = useState<Status>("loading-bonds");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listBonds()
      .then((all) => {
        const supported = all.filter((b) => SUPPORTED_TYPES.has(b.bondType));
        setBonds(supported);
        setBondId((current) => current || initialBondId || supported[0]?.id || "");
        setStatus("idle");
      })
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.detail : "Não foi possível carregar os títulos.");
        setStatus("error");
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // um link compartilhado carrega a simulação real do servidor pelo id
  useEffect(() => {
    const sharedId = searchParams.get("sim");
    if (!sharedId) return;
    const sharedShock = Math.round(Number(searchParams.get("shock") ?? "0") / 50) * 50;
    getSimulation(sharedId)
      // POST /scenarios não persiste o cenário na simulação base (ver
      // docs/domain/fase-4-status.md) — se o link foi compartilhado com um
      // choque ativo, reaplica aqui pra restaurar exatamente o que a
      // pessoa que compartilhou estava vendo.
      .then((sim) => (sharedShock !== 0 ? createScenario(sim.id, sharedShock) : sim))
      .then((sim) => {
        setSimulation(sim);
        setBondId(sim.bondSeriesId);
        setAmount(sim.amountInvested);
        setShockBps(sharedShock);
        setStatus("simulated");
      })
      .catch((err: unknown) => {
        setError(
          err instanceof ApiError
            ? "Essa simulação não existe mais — o servidor de desenvolvimento reinicia do zero."
            : "Não foi possível carregar a simulação compartilhada.",
        );
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleSimular() {
    const normalizedAmount = amount.replace(/\./g, "").replace(",", ".");
    setStatus("simulating");
    setError(null);
    try {
      const sim = await createSimulation({
        bondSeriesId: bondId,
        purchaseDate: PURCHASE_DATE,
        amountInvested: normalizedAmount,
        referenceDate: REFERENCE_DATE,
      });
      setSimulation(sim);
      setShockBps(0);
      setStatus("simulated");
      router.replace(`?sim=${sim.id}`, { scroll: false });
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Não foi possível simular agora.");
      setStatus("error");
    }
  }

  async function handleShockChange(value: number[]) {
    const nearest = Math.round(value[0] / 50) * 50;
    setShockBps(nearest);
    if (!simulation) return;
    try {
      const updated = await createScenario(simulation.id, nearest);
      setSimulation(updated);
      router.replace(`?sim=${simulation.id}&shock=${nearest}`, { scroll: false });
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Não foi possível recalcular o cenário.");
    }
  }

  function handleBondOrAmountChange(nextBondId: string, nextAmount: string) {
    setBondId(nextBondId);
    setAmount(nextAmount);
    setSimulation(null);
    setStatus("idle");
    setError(null);
  }

  return (
    <div className="grid gap-10 md:grid-cols-[320px_1fr]">
      <section className="space-y-6">
        <div className="grid gap-1.5">
          <Label htmlFor="bond">Título</Label>
          <Select
            value={bondId}
            disabled={status === "loading-bonds" || bonds.length === 0}
            onValueChange={(value) => handleBondOrAmountChange(value, amount)}
          >
            <SelectTrigger id="bond" className="w-full">
              <SelectValue placeholder={status === "loading-bonds" ? "Carregando…" : "Escolha um título"} />
            </SelectTrigger>
            <SelectContent>
              {bonds.map((bond) => (
                <SelectItem key={bond.id} value={bond.id}>
                  {bondLabel(bond)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="grid gap-1.5">
          <Label htmlFor="amount">Valor investido</Label>
          <div className="relative">
            <span className="pointer-events-none absolute top-1/2 left-3 -translate-y-1/2 font-mono text-sm text-muted-foreground">
              R$
            </span>
            <Input
              id="amount"
              inputMode="decimal"
              className="pl-9 tabular"
              value={amount}
              onChange={(e) => handleBondOrAmountChange(bondId, e.target.value)}
            />
          </div>
        </div>

        <p className="text-sm text-muted-foreground">
          Comprado em {formatDateBR(PURCHASE_DATE)}, mantido até hoje
          {" "}({formatDateBR(REFERENCE_DATE)}).
        </p>

        <Button
          onClick={handleSimular}
          disabled={!bondId || status === "simulating" || status === "loading-bonds"}
          className="w-full"
        >
          {status === "simulating" ? "Simulando…" : "Simular"}
        </Button>

        {error && <p className="text-sm text-negative">{error}</p>}
      </section>

      <section aria-live="polite" className="min-w-0">
        {simulation ? (
          <ResultLedger
            simulation={simulation}
            shockBps={shockBps}
            onShockChange={handleShockChange}
          />
        ) : (
          <EmptyState />
        )}
      </section>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex h-full min-h-[280px] flex-col items-center justify-center rounded-md border border-dashed border-border px-6 text-center">
      <p className="max-w-[38ch] text-muted-foreground">
        Escolha um título e um valor, depois simule — o resultado aparece
        aqui, com a decomposição completa do que mudou desde a compra.
      </p>
    </div>
  );
}

function ResultLedger({
  simulation,
  shockBps,
  onShockChange,
}: {
  simulation: Simulation;
  shockBps: number;
  onShockChange: (value: number[]) => void;
}) {
  const diff = Number(simulation.netValueToday) - Number(simulation.amountInvested);

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="mb-1 text-sm text-muted-foreground">Valor líquido hoje</p>
          <p className="tabular font-mono text-4xl font-semibold">
            {formatCurrencyBRL(simulation.netValueToday)}
          </p>
          <p
            className={`tabular mt-1 font-mono text-sm ${diff >= 0 ? "text-positive" : "text-negative"}`}
          >
            {diff >= 0 ? "+" : "−"}
            {formatCurrencyBRL(String(Math.abs(diff)))} desde o investimento
          </p>
        </div>
        <ShareButton simulationId={simulation.id} shockBps={shockBps} />
      </div>

      <div>
        <Waterfall simulation={simulation} />
      </div>

      <div className="max-w-md">
        <Separator className="mb-4" />
        <dl className="space-y-2 text-sm">
          <Row label="Valor bruto hoje" value={formatCurrencyBRL(simulation.grossValueToday)} />
          <Row
            label="IOF"
            value={formatSignedCurrencyBRL(`-${simulation.taxes.iofAmount}`)}
            tone="negative"
          />
          <Row
            label="IR"
            value={formatSignedCurrencyBRL(`-${simulation.taxes.irAmount}`)}
            tone="negative"
          />
          <Row
            label="Custódia B3"
            value={formatSignedCurrencyBRL(`-${simulation.custodyFeeAmount}`)}
            tone="negative"
          />
        </dl>
        <Separator className="my-4" />
        <div className="flex items-center gap-2">
          <Badge
            variant="outline"
            className="border-accent font-mono text-[0.65rem] tracking-wide text-primary uppercase"
          >
            Motor {simulation.calculationEngineVersion} · {formatDateBR(simulation.referenceDate)}
          </Badge>
        </div>
      </div>

      <div className="max-w-md">
        <Label className="mb-3 block">Cenário — choque de taxa</Label>
        <div className="mb-2 flex justify-between font-mono text-xs text-muted-foreground">
          <span>−200bps</span>
          <span className={shockBps !== 0 ? "text-primary" : undefined}>
            {shockBps > 0 ? "+" : shockBps < 0 ? "−" : ""}
            {Math.abs(shockBps)}bps
          </span>
          <span>+200bps</span>
        </div>
        <Slider
          value={[shockBps]}
          min={-200}
          max={200}
          step={50}
          onValueChange={onShockChange}
        />
      </div>
    </div>
  );
}

function Row({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone?: "negative";
}) {
  return (
    <div className="flex items-baseline justify-between">
      <dt className="text-muted-foreground">{label}</dt>
      <dd className={`tabular font-mono font-medium ${tone === "negative" ? "text-negative" : ""}`}>
        {value}
      </dd>
    </div>
  );
}
