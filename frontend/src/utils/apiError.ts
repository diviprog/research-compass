/**
 * Format API error detail for display.
 * FastAPI returns 422 with detail as array of validation errors; 400/401 use a string.
 */
export function formatApiErrorDetail(responseData: unknown): string {
  if (responseData == null) return 'Request failed. Please try again.';
  const d = responseData as { detail?: string | Array<{ loc?: unknown[]; msg?: string }> };
  const detail = d.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail) && detail.length > 0) {
    const first = detail[0];
    const msg = first?.msg ?? (first as { msg?: string }).msg;
    const loc = first?.loc;
    if (msg) {
      const field = Array.isArray(loc) ? loc[loc.length - 1] : null;
      return field ? `${String(field)}: ${msg}` : msg;
    }
  }
  return 'Request failed. Please try again.';
}
