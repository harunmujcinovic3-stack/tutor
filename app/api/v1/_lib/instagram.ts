function normalizeNumber(phone: string): string {
  let n = phone.replace(/[\s\-().]/g, "");
  if (!n.startsWith("+")) {
    n = "+" + n;
  }
  return n;
}

async function getWebCsrf(): Promise<{ csrf: string; cookies: string } | null> {
  try {
    const res = await fetch("https://www.instagram.com/accounts/login/", {
      method: "GET",
      headers: {
        "User-Agent":
          "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
      },
      redirect: "manual",
    });

    const rawCookies = res.headers.getSetCookie?.() ?? [];
    const cookieStr = rawCookies.join("; ");
    const csrfMatch = cookieStr.match(/csrftoken=([^;]+)/);

    if (!csrfMatch) {
      const body = await res.text();
      const bodyMatch = body.match(/"csrf_token":"([^"]+)"/);
      if (bodyMatch) {
        return { csrf: bodyMatch[1], cookies: cookieStr };
      }
      return null;
    }

    return { csrf: csrfMatch[1], cookies: cookieStr };
  } catch {
    return null;
  }
}

export async function lookupNumberToUsername(
  number: string
): Promise<
  | { username: string }
  | { error: string; status: number; debug?: string }
> {
  const normalized = normalizeNumber(number);

  const session = await getWebCsrf();
  if (!session) {
    return { error: "FETCH_FAILED", status: 424, debug: "Could not get CSRF token" };
  }

  const browserUA =
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36";

  try {
    const body = new URLSearchParams({
      email_or_phone_or_username: normalized,
      recaptcha_challenge_field: "",
      flow: "",
      app_id: "",
      source_account_id: "",
    });

    const res = await fetch(
      "https://www.instagram.com/api/v1/web/accounts/account_recovery_send_ajax/",
      {
        method: "POST",
        headers: {
          "User-Agent": browserUA,
          "Content-Type": "application/x-www-form-urlencoded",
          "X-CSRFToken": session.csrf,
          "X-Requested-With": "XMLHttpRequest",
          "X-IG-App-ID": "936619743392459",
          Referer: "https://www.instagram.com/accounts/password/reset/",
          Origin: "https://www.instagram.com",
          Cookie: session.cookies,
          "Sec-Fetch-Site": "same-origin",
          "Sec-Fetch-Mode": "cors",
          "Sec-Fetch-Dest": "empty",
        },
        body: body.toString(),
      }
    );

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

    // The recovery response contains contact_point which is the masked email/phone
    // and sometimes reveals the username
    if (data.status === "ok") {
      const contactPoint = data.contact_point as string | undefined;
      return {
        error: "Account found! Recovery sent to: " + (contactPoint ?? "unknown"),
        status: 200,
        debug: text.slice(0, 500),
      };
    }

    if (!res.ok) {
      return {
        error: "FETCH_FAILED",
        status: 424,
        debug: `HTTP ${res.status}: ${text.slice(0, 500)}`,
      };
    }

    return {
      error: "FETCH_FAILED",
      status: 424,
      debug: `Unexpected: ${text.slice(0, 500)}`,
    };
  } catch (e) {
    return { error: "FETCH_FAILED", status: 424, debug: String(e) };
  }
}
