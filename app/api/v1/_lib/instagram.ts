const IG_API = "https://i.instagram.com/api/v1";

const HEADERS: Record<string, string> = {
  "User-Agent":
    "Instagram 332.0.0.38.90 Android (33/13; 420dpi; 1080x2400; samsung; SM-G991B; o1s; exynos2100; en_US; 604247854)",
  "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
  "X-IG-App-ID": "567067343352427",
  "X-IG-Connection-Type": "WIFI",
  "X-IG-Capabilities": "3brTvx0=",
  Accept: "*/*",
  "Accept-Language": "en-US,en;q=0.9",
  "Sec-Fetch-Site": "same-origin",
  "Sec-Fetch-Mode": "cors",
  "Sec-Fetch-Dest": "empty",
};

function normalizeNumber(phone: string): string {
  let n = phone.replace(/[\s\-().]/g, "");
  if (!n.startsWith("+")) {
    n = "+" + n;
  }
  return n;
}

export async function lookupNumberToUsername(
  number: string
): Promise<
  | { username: string }
  | { error: string; status: number; debug?: string }
> {
  const normalized = normalizeNumber(number);
  const deviceId = crypto.randomUUID();

  try {
    const body = new URLSearchParams({
      query: normalized,
      device_id: deviceId,
      guid: crypto.randomUUID(),
      directly_sign_in: "true",
    });

    const res = await fetch(`${IG_API}/users/lookup/`, {
      method: "POST",
      headers: {
        ...HEADERS,
        "X-Device-ID": deviceId,
      },
      body: body.toString(),
    });

    const text = await res.text();
    let data: Record<string, unknown>;
    try {
      data = JSON.parse(text);
    } catch {
      return {
        error: "FETCH_FAILED",
        status: 424,
        debug: `Instagram returned non-JSON (HTTP ${res.status}): ${text.slice(0, 200)}`,
      };
    }

    if (res.status === 429 || data.spam || data.message === "rate_limit_error") {
      return { error: "RATE_LIMIT", status: 429, debug: `HTTP ${res.status}: ${text.slice(0, 300)}` };
    }

    // If not OK and not handled, show the raw response for debugging
    if (!res.ok) {
      return {
        error: "FETCH_FAILED",
        status: 424,
        debug: `HTTP ${res.status}: ${text.slice(0, 500)}`,
      };
    }

    // users/lookup can return the user object directly
    const user = data.user as Record<string, unknown> | undefined;
    if (user?.username) {
      return { username: String(user.username) };
    }

    // Sometimes it returns a pk/pk_v2 we can use to fetch the profile
    const userId = user?.pk ?? user?.pk_v2 ?? data.pk ?? data.pk_v2;
    if (userId) {
      try {
        const profileRes = await fetch(`${IG_API}/users/${userId}/info/`, {
          headers: HEADERS,
        });
        const profileText = await profileRes.text();
        const profileData = JSON.parse(profileText);
        if (profileData?.user?.username) {
          return { username: String(profileData.user.username) };
        }
        return {
          error: "FETCH_FAILED",
          status: 424,
          debug: `Got user_id ${userId} but profile lookup failed: ${profileText.slice(0, 200)}`,
        };
      } catch {
        return {
          error: "FETCH_FAILED",
          status: 424,
          debug: `Got user_id ${userId} but profile lookup errored`,
        };
      }
    }

    // Check if user not found
    if (
      data.message === "user_not_found" ||
      data.status === "fail" ||
      !res.ok
    ) {
      return {
        error: "No Instagram account found for this number.",
        status: 404,
        debug: text.slice(0, 300),
      };
    }

    return {
      error: "FETCH_FAILED",
      status: 424,
      debug: `Unexpected response: ${text.slice(0, 300)}`,
    };
  } catch (e) {
    return { error: "FETCH_FAILED", status: 424, debug: String(e) };
  }
}
