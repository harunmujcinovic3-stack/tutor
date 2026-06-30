import { type NextRequest } from "next/server";
import { ERRORS } from "../_lib/errors";
import { lookupEmailToUsername } from "../_lib/instagram";

export async function GET(request: NextRequest) {
  const email = request.nextUrl.searchParams.get("email");
  if (!email) {
    return ERRORS.BAD_REQUEST(
      "Missing required parameter: email (the email address to look up)."
    );
  }

  const result = await lookupEmailToUsername(email);

  if ("error" in result) {
    const debug = "debug" in result ? result.debug : undefined;
    return Response.json(
      { status: "error", error: { code: result.error, message: result.error, debug } },
      { status: result.status }
    );
  }

  return Response.json({
    status: "success",
    data: { email, username: result.username },
  });
}
