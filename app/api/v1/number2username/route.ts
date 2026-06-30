import { type NextRequest } from "next/server";
import { ERRORS } from "../_lib/errors";
import { lookupNumberToUsername } from "../_lib/instagram";

const CSRF = "7pdGU1g5we4eyoR4mt9iQqwmSdvVy96X";

const COOKIES = [
  `csrftoken=${CSRF}`,
  "sessionid=74861310130%3AhMkpRtFRFW8K9A%3A8%3AAYh7QuoaV2q2QShMIIawElW8fsoU1fWPXDRHr45FSQ",
  "ds_user_id=74861310130",
  "datr=JYZHaJTLnaEU-YtJk6u7nD2i",
  "ig_did=321E854A-C949-4704-8209-DCB38CED63F5",
  "mid=aEeGJQAEAAFWf88U14LDzGp5Kfqb",
  "ps_l=1",
  "ps_n=1",
  "rur=NCG\\05474861310130\\0541814393532:01ff92589325a0bde018c8d317213e68529f85378b28a592286da7929cca567ef72a8b82",
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
