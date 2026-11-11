export function formatDate(value: string | null): string {
  if (!value) return "—";
  return new Date(value).toLocaleString("en-GB", { dateStyle: "medium", timeStyle: "short" });
}

function pad(n: number): string {
  return String(n).padStart(2, "0");
}

export function toLocalInput(date: Date): string {
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

export function defaultCloseInput(days = 14): string {
  const d = new Date();
  d.setDate(d.getDate() + days);
  d.setHours(18, 0, 0, 0);
  return toLocalInput(d);
}

export function localInputToIso(value: string): string {
  return new Date(value).toISOString();
}

export function formatScore(value: number | null): string {
  if (value === null) return "—";
  return (Math.round(value * 10) / 10 + 0).toFixed(1);
}

export function formatGap(value: number | null): string {
  if (value === null) return "—";
  const rounded = Math.round(value * 10) / 10 + 0;
  return `${rounded > 0 ? "+" : ""}${rounded.toFixed(1)}`;
}
