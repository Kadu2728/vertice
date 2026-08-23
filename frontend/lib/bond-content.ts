import type { BondType } from "./types";

interface BondTypeContent {
  displayName: string;
  intro: string;
  howItWorks: string;
  whoItsFor: string;
  simulationSupported: boolean;
}

export const BOND_TYPE_CONTENT: Record<BondType, BondTypeContent> = {
  LTN: {
    displayName: "Tesouro Prefixado",
    intro:
      "Título de renda fixa que promete um valor exato no vencimento — R$ 1.000,00 por unidade — definido no momento da compra.",
    howItWorks:
      "Não paga cupons no meio do caminho. O preço de negociação antes do vencimento sobe ou desce conforme a taxa de juros de mercado muda: se a taxa sobe depois da compra, o preço de hoje cai; se a taxa cai, o preço sobe. Quem carrega até o vencimento recebe o valor prometido de qualquer forma.",
    whoItsFor:
      "Faz sentido para quem sabe exatamente quando vai precisar do dinheiro e quer previsibilidade do valor final, aceitando que o preço de mercado pode oscilar antes disso.",
    simulationSupported: true,
  },
  "NTN-F": {
    displayName: "Tesouro Prefixado com Juros Semestrais",
    intro:
      "Mesma lógica do Tesouro Prefixado, mas paga cupons de juros a cada seis meses em vez de concentrar tudo no vencimento.",
    howItWorks:
      "O cupom semestral (10% ao ano, convenção padrão do Tesouro Direto) chega na conta do investidor duas vezes por ano, sujeito a Imposto de Renda no momento do pagamento. O preço de negociação reage à taxa de juros de mercado do mesmo jeito que o Tesouro Prefixado sem cupom.",
    whoItsFor:
      "Faz sentido para quem quer um fluxo de renda periódico em vez de esperar todo o valor no vencimento.",
    simulationSupported: true,
  },
  "NTN-B Principal": {
    displayName: "Tesouro IPCA+",
    intro:
      "Título corrigido pela inflação (IPCA) mais uma taxa de juros real fixada na compra — protege o poder de compra do valor investido.",
    howItWorks:
      "O valor de face é atualizado diariamente pela inflação oficial. Não paga cupons — tudo (correção monetária mais juros reais) é recebido de uma vez no vencimento.",
    whoItsFor: "Faz sentido para objetivos de longo prazo em que preservar o poder de compra importa mais do que ter renda periódica.",
    simulationSupported: false,
  },
  "NTN-B": {
    displayName: "Tesouro IPCA+ com Juros Semestrais",
    intro:
      "Mesma proteção contra inflação do Tesouro IPCA+, mas com pagamento de cupons de juros a cada seis meses (6% ao ano sobre o valor corrigido).",
    howItWorks:
      "O valor de face é corrigido diariamente pelo IPCA, e a cada seis meses uma parte dos juros reais é paga em dinheiro — o restante continua rendendo até o vencimento.",
    whoItsFor:
      "Faz sentido para quem quer proteção contra inflação de longo prazo com uma renda periódica no meio do caminho.",
    simulationSupported: false,
  },
  LFT: {
    displayName: "Tesouro Selic",
    intro:
      "Título pós-fixado que acompanha a taxa Selic diariamente — o título do Tesouro Direto com menor oscilação de preço no curto prazo.",
    howItWorks:
      "O valor de face é corrigido todo dia pela taxa Selic acumulada. O preço de negociação fica muito próximo desse valor corrigido o tempo todo, com um pequeno ágio ou deságio negociado no mercado secundário.",
    whoItsFor:
      "Faz sentido para reserva de emergência ou objetivos de curto prazo, onde previsibilidade de preço no dia a dia importa mais do que buscar o maior retorno possível.",
    simulationSupported: false,
  },
};
