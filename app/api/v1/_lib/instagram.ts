const IG_API = "https://i.instagram.com/api/v1";
const IG_WEB = "https://www.instagram.com/api/v1";

const MOBILE_HEADERS: Record<string, string> = {
  "User-Agent":
    "Instagram 332.0.0.38.90 Android (33/13; 420dpi; 1080x2400; samsung; SM-G991B; o1s; exynos2100; en_US; 604247854)",
  "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
  "X-IG-App-ID": "567067343352427",
  "X-IG-Connection-Type": "WIFI",
  "X-IG-Capabilities": "3brTvx0=",
  Accept: "*/*",
  "Accept-Language": "en-US,en;q=0.9",
};

const WEB_HEADERS: Record<string, string> = {
  "User-Agent":
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
  "Content-Type": "application/x-www-form-urlencoded",
  "X-IG-App-ID": "936619743392459",
  "X-Requested-With": "XMLHttpRequest",
  Origin: "https://www.instagram.com",
  Referer: "https://www.instagram.com/",
  Accept: "*/*",
  "Accept-Language": "en-US,en;q=0.9",
  "Sec-Fetch-Site": "same-origin",
  "Sec-Fetch-Mode": "cors",
  "Sec-Fetch-Dest": "empty",
};

function normalizeNumber(phone: string): string {
  let n = phone.replace(/[\s\-().]/g, "");
  if (!n.startsWith("+")) n = "+" + n;
  return n;
}

type LookupResult =
  | { username: string }
  | { error: string; status: number; debug?: string };

async function tryFetch(
  url: string,
  headers: Record<string, string>,
  body: string
): Promise<{ ok: boolean; status: number; text: string; json?: Record<string, unknown> }> {
  try {
    const res = await fetch(url, { method: "POST", headers, body });
    const text = await res.text();
    let json: Record<string, unknown> | undefined;
    try { json = JSON.parse(text); } catch {}
    return { ok: res.ok, status: res.status, text, json };
  } catch (e) {
    return { ok: false, status: 0, text: String(e) };
  }
}

// Strategy 1: users/lookup (no auth needed, password reset flow)
export async function lookupByQuery(query: string): Promise<LookupResult> {
  const body = new URLSearchParams({
    query,
    device_id: crypto.randomUUID(),
    waterfall_id: crypto.randomUUID(),
    directly_sign_in: "true",
  }).toString();

  const res = await tryFetch(`${IG_API}/users/lookup/`, MOBILE_HEADERS, body);

  if (res.status === 429) {
    return { error: "RATE_LIMIT", status: 429, debug: `HTTP 429: ${res.text.slice(0, 200)}` };
  }
  if (!res.json || res.json.status === "fail") {
    return { error: "LOOKUP_FAILED", status: 424, debug: `HTTP ${res.status}: ${res.text.slice(0, 300)}` };
  }

  const user = res.json.user as Record<string, unknown> | undefined;
  if (user?.username) return { username: String(user.username) };

  const pk = user?.pk ?? user?.pk_v2;
  if (pk) {
    const profileRes = await tryFetch(
      `${IG_API}/users/${pk}/info/`,
      { ...MOBILE_HEADERS, "Content-Type": "" },
      ""
    );
    if (profileRes.json?.user) {
      const u = profileRes.json.user as Record<string, unknown>;
      if (u.username) return { username: String(u.username) };
    }
    return { error: "LOOKUP_FAILED", status: 424, debug: `Got pk ${pk}, profile lookup: ${profileRes.text.slice(0, 200)}` };
  }

  return {
    error: "NOT_FOUND",
    status: 404,
    debug: `Response: ${res.text.slice(0, 300)}`,
  };
}

// Strategy 2: check_email (web, registration flow — confirms email exists)
export async function checkEmail(email: string): Promise<LookupResult> {
  const body = new URLSearchParams({ email }).toString();
  const res = await tryFetch(
    `${IG_WEB}/web/accounts/check_email/`,
    { ...WEB_HEADERS, Referer: "https://www.instagram.com/accounts/emailsignup/" },
    body
  );

  if (res.status === 429) {
    return { error: "RATE_LIMIT", status: 429, debug: `HTTP 429` };
  }
  if (!res.json) {
    return { error: "FETCH_FAILED", status: 424, debug: `HTTP ${res.status}: ${res.text.slice(0, 200)}` };
  }

  const available = res.json.available as boolean | undefined;
  if (available === false) {
    // Email is taken = account exists. Try users/lookup to get the username.
    return lookupByQuery(email);
  }
  if (available === true) {
    return { error: "No Instagram account found for this email.", status: 404 };
  }

  return { error: "FETCH_FAILED", status: 424, debug: `Unexpected: ${res.text.slice(0, 300)}` };
}

// Strategy 3: contact sync (needs session cookie)
export async function contactSync(
  phoneNumber: string,
  cookies: string,
  csrfToken: string
): Promise<LookupResult> {
  const normalized = normalizeNumber(phoneNumber);

  const contacts = JSON.stringify({
    contacts: [{ phone_numbers: [normalized], first_name: "Lookup", last_name: "" }],
  });

  const body = new URLSearchParams({
    contacts,
    phone_id: crypto.randomUUID(),
    module: "find_friends_contacts",
  }).toString();

  const res = await tryFetch(`${IG_WEB}/address_book/link/`, {
    ...WEB_HEADERS,
    "X-CSRFToken": csrfToken,
    Cookie: cookies,
  }, body);

  if (res.status === 429) {
    return { error: "RATE_LIMIT", status: 429, debug: `HTTP 429: ${res.text.slice(0, 200)}` };
  }
  if (!res.ok || !res.json) {
    return { error: "FETCH_FAILED", status: 424, debug: `HTTP ${res.status}: ${res.text.slice(0, 300)}` };
  }

  const users = (res.json.users ?? []) as Array<Record<string, unknown>>;
  if (users.length === 0) {
    return { error: "No Instagram account found for this number.", status: 404, debug: res.text.slice(0, 200) };
  }

  return { username: String(users[0].username) };
}

// Main lookup: tries multiple strategies
export async function lookupNumberToUsername(number: string): Promise<LookupResult> {
  return lookupByQuery(normalizeNumber(number));
}

export async function lookupEmailToUsername(email: string): Promise<LookupResult> {
  // Try check_email first (web, lighter rate limits)
  const checkResult = await checkEmail(email);
  if ("username" in checkResult) return checkResult;

  // Fallback: direct lookup
  if (checkResult.status !== 404) {
    const lookupResult = await lookupByQuery(email);
    if ("username" in lookupResult) return lookupResult;
  }

  return checkResult;
}
