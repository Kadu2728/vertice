/**
 * Só formatação de exibição — nunca deriva um novo valor financeiro.
 * O número em si sempre vem pronto do backend (string, para não perder
 * precisão do Decimal em JSON); aqui só decide como ele aparece na tela.
 */

const currencyFormatter = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
});

export function formatCurrencyBRL(value: string): string {
  return currencyFormatter.format(Number(value));
}

export function formatSignedCurrencyBRL(value: string): string {
  const n = Number(value);
  const formatted = currencyFormatter.format(Math.abs(n));
  if (n === 0) return formatted;
  return n < 0 ? `−${formatted}` : `+${formatted}`;
}

export function formatDateBR(isoDate: string): string {
  const [year, month, day] = isoDate.split("-");
  return `${day}/${month}/${year}`;
}

export function formatPercent(fraction: string, digits = 2): string {
  return `${(Number(fraction) * 100).toFixed(digits)}%`;
}
