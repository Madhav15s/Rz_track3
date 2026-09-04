export function formatPaiseToINR(paise: number | undefined | null, compact = false): string {
  if (paise === undefined || paise === null || isNaN(paise)) return '₹0';
  const rupees = paise / 100;
  
  if (compact) {
    if (Math.abs(rupees) >= 10000000) {
      return `₹${(rupees / 10000000).toFixed(2)} Cr`;
    }
    if (Math.abs(rupees) >= 100000) {
      return `₹${(rupees / 100000).toFixed(2)} L`;
    }
    if (Math.abs(rupees) >= 1000) {
      return `₹${(rupees / 1000).toFixed(1)}k`;
    }
  }

  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(rupees);
}

export function formatPercentage(rate: number | undefined | null, showSign = false): string {
  if (rate === undefined || rate === null || isNaN(rate)) return '0%';
  const pct = (rate * 100).toFixed(1);
  if (showSign && rate > 0) return `+${pct}%`;
  return `${pct}%`;
}

export function formatTimestamp(seconds: number | undefined | null): string {
  if (!seconds) return '—';
  // Handle both seconds (unix timestamp) and milliseconds
  const ms = seconds < 10000000000 ? seconds * 1000 : seconds;
  const date = new Date(ms);
  return date.toLocaleTimeString('en-IN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });
}

export function formatDateTime(seconds: number | undefined | null): string {
  if (!seconds) return '—';
  const ms = seconds < 10000000000 ? seconds * 1000 : seconds;
  const date = new Date(ms);
  return date.toLocaleString('en-IN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });
}
