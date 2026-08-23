import { Suspense } from "react";
import { Simulator } from "@/components/simulation/simulator";

export default function Home() {
  return (
    <main className="mx-auto max-w-4xl px-6 py-14">
      <header className="mb-12">
        <p className="mb-2 font-mono text-xs tracking-widest text-muted-foreground uppercase">
          Simulador
        </p>
        <h1 className="font-heading text-3xl font-medium">VÉRTICE</h1>
        <p className="mt-2 max-w-[52ch] text-muted-foreground">
          Por que seu título mudou de valor, e quanto você recebe se vender
          hoje em vez de esperar o vencimento.
        </p>
      </header>

      <Suspense>
        <Simulator />
      </Suspense>
    </main>
  );
}
