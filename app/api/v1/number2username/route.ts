import { type NextRequest } from "next/server";
import { ERRORS } from "../_lib/errors";
import { lookupNumberToUsername } from "../_lib/instagram";

export async function GET(request: NextRequest) {
  const number = request.nextUrl.searchParams.get("number");
  if (!number) {
    return ERRORS.BAD_REQUEST(
      "Missing required parameter: number (phone number in international format with country code)."
    );
  }

  const result = await lookupNumberToUsername(number);

  if ("error" in result) {
    const debug = "debug" in result ? result.debug : undefined;
    if (result.error === "RATE_LIMIT") return ERRORS.RATE_LIMIT_EXCEEDED(60);
    if (result.error === "FETCH_FAILED") {
      return Response.json(
        { status: "error", error: { code: "FETCH_FAILED", message: "Upstream request to Instagram failed; retry.", debug } },
        { status: 424 }
      );
    }
    return ERRORS.NOT_FOUND(result.error);
  }

  return Response.json({
    status: "success",
    data: {
      number,
      username: result.username,
    },
  });
}
