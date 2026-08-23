import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
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

export default function DesignTokensPage() {
  return (
    <main className="mx-auto max-w-3xl px-6 py-16">
      <p className="mb-2 font-mono text-xs tracking-widest text-muted-foreground uppercase">
        Fase 5.1 — Verificação
      </p>
      <h1 className="mb-2 font-heading text-3xl font-medium">
        Tokens e primitivos
      </h1>
      <p className="mb-12 max-w-[60ch] text-muted-foreground">
        Papel de Ofício, selo dourado — os componentes shadcn abaixo já
        herdam a paleta e a tipografia aprovadas na Fase 5.0, sem edição
        componente a componente.
      </p>

      <section className="mb-12">
        <h2 className="mb-4 font-heading text-lg font-medium">Botões</h2>
        <div className="flex flex-wrap items-center gap-3">
          <Button>Simular</Button>
          <Button variant="secondary">Comparar cenário</Button>
          <Button variant="outline">Compartilhar</Button>
          <Button variant="ghost">Editar</Button>
          <Button variant="destructive">Excluir simulação</Button>
          <Button variant="link">Ver metodologia</Button>
        </div>
      </section>

      <section className="mb-12">
        <h2 className="mb-4 font-heading text-lg font-medium">
          Formulário de simulação
        </h2>
        <div className="grid max-w-sm gap-4">
          <div className="grid gap-1.5">
            <Label htmlFor="bond">Título</Label>
            <Select defaultValue="ltn-2029">
              <SelectTrigger id="bond" className="w-full">
                <SelectValue placeholder="Escolha um título" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ltn-2029">Tesouro Prefixado 2029</SelectItem>
                <SelectItem value="ntnb-2035">Tesouro IPCA+ 2035</SelectItem>
                <SelectItem value="lft-2027">Tesouro Selic 2027</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor="amount">Valor investido</Label>
            <Input id="amount" inputMode="decimal" defaultValue="1.000,00" />
          </div>
        </div>
      </section>

      <section className="mb-12">
        <h2 className="mb-4 font-heading text-lg font-medium">
          Cenário — choque de taxa
        </h2>
        <div className="max-w-sm space-y-3">
          <div className="flex justify-between font-mono text-xs text-muted-foreground">
            <span>−200bps</span>
            <span className="text-primary">+50bps</span>
            <span>+200bps</span>
          </div>
          <Slider defaultValue={[125]} min={0} max={200} step={12.5} />
        </div>
      </section>

      <section className="mb-12">
        <h2 className="mb-4 font-heading text-lg font-medium">
          Lançamento — resultado da simulação
        </h2>
        <Card className="max-w-sm gap-4 py-5">
          <CardHeader className="gap-1">
            <CardDescription>Valor líquido hoje</CardDescription>
            <CardTitle className="tabular font-mono text-3xl font-semibold">
              R$ 1.198,30
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-0">
            <Separator className="mb-3" />
            <dl className="space-y-2 text-sm">
              <div className="flex items-baseline justify-between">
                <dt className="text-muted-foreground">Impacto da taxa</dt>
                <dd className="tabular font-mono font-medium text-negative">
                  −R$ 42,10
                </dd>
              </div>
              <div className="flex items-baseline justify-between">
                <dt className="text-muted-foreground">Impacto do IPCA</dt>
                <dd className="tabular font-mono font-medium text-positive">
                  +R$ 87,60
                </dd>
              </div>
              <div className="flex items-baseline justify-between">
                <dt className="text-muted-foreground">IR + custódia</dt>
                <dd className="tabular font-mono font-medium text-negative">
                  −R$ 38,20
                </dd>
              </div>
            </dl>
            <Separator className="my-3" />
            <div className="flex items-center gap-2">
              <Badge
                variant="outline"
                className="border-accent font-mono text-[0.65rem] tracking-wide text-primary uppercase"
              >
                Motor v2026.08.1 · 21 ago
              </Badge>
            </div>
          </CardContent>
        </Card>
      </section>

      <section>
        <h2 className="mb-4 font-heading text-lg font-medium">Paleta</h2>
        <div className="flex flex-wrap gap-3">
          {[
            ["tinta", "bg-background border border-border"],
            ["selo", "bg-primary"],
            ["selo abatido", "bg-accent"],
            ["papel", "bg-foreground"],
            ["lacre", "bg-negative"],
            ["verdete", "bg-positive"],
          ].map(([label, cls]) => (
            <div key={label} className="w-24">
              <div className={`h-12 w-full rounded-md ${cls}`} />
              <p className="mt-1.5 text-xs text-muted-foreground">{label}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
