/**
 * In-memory access token store. The access token is intentionally NOT persisted
 * to localStorage (XSS hardening); it lives only in memory and is re-obtained
 * via the HttpOnly refresh-token cookie on page load / on 401.
 */
let accessToken: string | null = null;
const listeners = new Set<(token: string | null) => void>();

export function getAccessToken() {
  return accessToken;
}

export function setAccessToken(token: string | null) {
  accessToken = token;
  listeners.forEach((l) => l(token));
}

export function onTokenChange(cb: (token: string | null) => void) {
  listeners.add(cb);
  return () => listeners.delete(cb);
}
