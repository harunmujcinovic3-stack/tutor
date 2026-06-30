export function errorResponse(
  status: number,
  code: string,
  message: string,
  headers?: Record<string, string>
) {
  return Response.json(
    { status: "error", error: { code, message } },
    { status, headers }
  );
}

export const ERRORS = {
  MISSING_KEY: () =>
    errorResponse(401, "MISSING_KEY", "No API key was provided."),
  INVALID_KEY: () =>
    errorResponse(403, "INVALID_KEY", "The key does not exist."),
  KEY_DISABLED: () =>
    errorResponse(403, "KEY_DISABLED", "The key has been disabled."),
  KEY_EXPIRED: () =>
    errorResponse(403, "KEY_EXPIRED", "The subscription has ended."),
  ENDPOINT_NOT_ALLOWED: () =>
    errorResponse(
      403,
      "ENDPOINT_NOT_ALLOWED",
      "Your plan does not include this endpoint."
    ),
  RATE_LIMIT_EXCEEDED: (retryAfter: number) =>
    errorResponse(
      429,
      "RATE_LIMIT_EXCEEDED",
      "Rate limit reached; see Retry-After.",
      { "Retry-After": String(retryAfter) }
    ),
  NOT_FOUND: (msg = "The requested resource was not found.") =>
    errorResponse(404, "NOT_FOUND", msg),
  FETCH_FAILED: () =>
    errorResponse(
      424,
      "FETCH_FAILED",
      "Upstream request to Instagram failed; retry."
    ),
  BAD_REQUEST: (msg: string) => errorResponse(400, "BAD_REQUEST", msg),
} as const;
