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
  number: string,
  sessionId: string,
  csrfToken: string
): Promise<
  | { username: string }
  | { error: string; status: number; debug?: string }
> {
  const normalized = normalizeNumber(number);

  const contacts = JSON.stringify({
    contacts: [
      {
        phone_numbers: [normalized],
        first_name: "Lookup",
        last_name: "",
      },
    ],
  });

  const body = new URLSearchParams({
    contacts: contacts,
    phone_id: crypto.randomUUID(),
    module: "find_friends_contacts",
  });

  try {
    const decodedSession = decodeURIComponent(sessionId);
    const dsUserId = decodedSession.split(":")[0];

    const res = await fetch(`${IG_API}/address_book/link/`, {
      method: "POST",
      headers: {
        ...HEADERS,
        "X-CSRFToken": csrfToken,
        Cookie: `sessionid=${decodedSession}; ds_user_id=${dsUserId}; csrftoken=${csrfToken}; rur=NHA`,
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
        debug: `Non-JSON (HTTP ${res.status}): ${text.slice(0, 300)}`,
      };
    }

    if (res.status === 429 || data.spam || data.message === "rate_limit_error") {
      return { error: "RATE_LIMIT", status: 429, debug: `HTTP ${res.status}: ${text.slice(0, 300)}` };
    }

    if (!res.ok) {
      return {
        error: "FETCH_FAILED",
        status: 424,
        debug: `HTTP ${res.status}: ${text.slice(0, 500)}`,
      };
    }

    const users = (data.users ?? []) as Array<Record<string, unknown>>;

    if (users.length === 0) {
      return {
        error: "No Instagram account found for this number.",
        status: 404,
        debug: text.slice(0, 300),
      };
    }

    return { username: String(users[0].username) };
  } catch (e) {
    return { error: "FETCH_FAILED", status: 424, debug: String(e) };
  }
}
