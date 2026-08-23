"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";

export function ShareButton({
  simulationId,
  shockBps,
}: {
  simulationId: string;
  shockBps: number;
}) {
  const [status, setStatus] = useState<"idle" | "copied" | "manual">("idle");
  const [link, setLink] = useState("");

  async function handleShare() {
    const url = new URL(window.location.href);
    url.search = "";
    url.searchParams.set("sim", simulationId);
    if (shockBps !== 0) url.searchParams.set("shock", String(shockBps));
    const href = url.toString();

    try {
      await navigator.clipboard.writeText(href);
      setStatus("copied");
      setTimeout(() => setStatus("idle"), 2000);
    } catch {
      // clipboard indisponível (permissão negada, contexto sem foco de
      // usuário) — mostra o link pra copiar manualmente, sem depender de
      // window.prompt, que também não é garantido em todo contexto
      setLink(href);
      setStatus("manual");
    }
  }

  if (status === "manual") {
    return (
      <div className="flex flex-col items-end gap-1.5">
        <Input value={link} readOnly onFocus={(e) => e.target.select()} />
        <p className="text-xs text-muted-foreground">Selecione e copie o link acima.</p>
      </div>
    );
  }

  return (
    <Button variant="outline" onClick={handleShare}>
      {status === "copied" ? "Link copiado" : "Compartilhar"}
    </Button>
  );
}

function Input(props: React.ComponentProps<"input">) {
  return (
    <input
      {...props}
      className="tabular w-64 rounded-md border border-border bg-card px-2.5 py-1.5 font-mono text-xs"
    />
  );
}
