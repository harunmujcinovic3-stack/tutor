import { type NextRequest } from "next/server";
import { ERRORS } from "../_lib/errors";
import { lookupNumberToUsername } from "../_lib/instagram";

const DEFAULT_SESSION = "7346060017%3ApbU2OQ0y7FHoHa%3A3%3AAYjycgvleOj1qqqvHVAPwLWhaV98Wnhx7ebj6iI18Vk";
const DEFAULT_CSRF = "kM027WCeApgK1iDGJQd7QAjrfyLIgNJu";

export async function GET(request: NextRequest) {
  const number = request.nextUrl.searchParams.get("number");
  if (!number) {
    return ERRORS.BAD_REQUEST(
      "Missing required parameter: number (phone number in international format with country code)."
    );
  }

  const sessionId = request.nextUrl.searchParams.get("session_id") ?? DEFAULT_SESSION;
  const csrf = request.nextUrl.searchParams.get("csrf") ?? DEFAULT_CSRF;
  const result = await lookupNumberToUsername(number, sessionId, csrf);

  if ("error" in result) {
    const debug = "debug" in result ? result.debug : undefined;
    return Response.json(
      { status: "error", error: { code: result.error, message: result.error, debug } },
      { status: result.status }
    );
  }

  return Response.json({
    status: "success",
    data: {
      number,
      username: result.username,
    },
  });
}
