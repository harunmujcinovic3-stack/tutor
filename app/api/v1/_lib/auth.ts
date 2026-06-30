import { type NextRequest } from "next/server";
import { ERRORS } from "./errors";

export function extractApiKey(request: NextRequest): string | null {
  const header = request.headers.get("x-api-key");
  if (header) return header;

  const key =
    request.nextUrl.searchParams.get("key") ??
    request.nextUrl.searchParams.get("api_key");
  return key;
}

export async function validateApiKey(
  request: NextRequest
): Promise<Response | null> {
  const key = extractApiKey(request);
  if (!key) return ERRORS.MISSING_KEY();

  // TODO: validate key against your database/store
  // For now, accept any non-empty key
  // Replace this with actual key validation:
  //   const keyRecord = await db.apiKeys.findByKey(key);
  //   if (!keyRecord) return ERRORS.INVALID_KEY();
  //   if (keyRecord.disabled) return ERRORS.KEY_DISABLED();
  //   if (keyRecord.expired) return ERRORS.KEY_EXPIRED();
  //   if (!keyRecord.allowedEndpoints.includes('number2username'))
  //     return ERRORS.ENDPOINT_NOT_ALLOWED();

  return null;
}
