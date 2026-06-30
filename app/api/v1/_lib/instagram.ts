const IG_API = "https://www.instagram.com/api/v1";

function normalizeNumber(phone: string): string {
  let n = phone.replace(/[\s\-().]/g, "");
  if (!n.startsWith("+")) {
    n = "+" + n;
  }
  return n;
}

export async function lookupNumberToUsername(
  number: string,
  cookies: string,
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
    const res = await fetch(`${IG_API}/address_book/link/`, {
      method: "POST",
      headers: {
        "User-Agent":
          "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-CSRFToken": csrfToken,
        "X-IG-App-ID": "936619743392459",
        "X-Requested-With": "XMLHttpRequest",
        "X-ASBD-ID": "129477",
        "X-IG-WWW-Claim": "0",
        Origin: "https://www.instagram.com",
        Referer: "https://www.instagram.com/",
        Accept: "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        Cookie: cookies,
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
