import { type NextRequest } from "next/server";
import { ERRORS } from "../_lib/errors";
import { lookupNumberToUsername } from "../_lib/instagram";

const CSRF = "kM027WCeApgK1iDGJQd7QAjrfyLIgNJu";

const COOKIES = [
  `csrftoken=${CSRF}`,
  "sessionid=7346060017%3ApbU2OQ0y7FHoHa%3A3%3AAYjycgvleOj1qqqvHVAPwLWhaV98Wnhx7ebj6iI18Vk",
  "ds_user_id=7346060017",
  "datr=JYZHaJTLnaEU-YtJk6u7nD2i",
  "ig_did=321E854A-C949-4704-8209-DCB38CED63F5",
  "mid=aEeGJQAEAAFWf88U14LDzGp5Kfqb",
  "ps_l=1",
  "ps_n=1",
  'rur="LDC\\0547346060017\\0541814391993:01ffe612d3bfb5f30176525b169be9fbff3a1825354ca658667d5c6f121f78c2a16dffe0"',
].join("; ");

export async function GET(request: NextRequest) {
  const number = request.nextUrl.searchParams.get("number");
  if (!number) {
    return ERRORS.BAD_REQUEST(
      "Missing required parameter: number (phone number in international format with country code)."
    );
  }

  const result = await lookupNumberToUsername(number, COOKIES, CSRF);

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
