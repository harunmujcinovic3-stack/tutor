const IG_BASE = "https://i.instagram.com/api/v1";

const IG_HEADERS = {
  "User-Agent":
    "Instagram 332.0.0.38.90 Android (33/13; 420dpi; 1080x2400; samsung; SM-G991B; o1s; exynos2100; en_US; 604247854)",
  "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
  "X-IG-App-ID": "567067343352427",
  "X-IG-Connection-Type": "WIFI",
  Accept: "*/*",
  "Accept-Language": "en-US,en;q=0.9",
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
): Promise<{ username: string } | { error: string; status: number }> {
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
    const res = await fetch(`${IG_BASE}/address_book/link/`, {
      method: "POST",
      headers: IG_HEADERS,
      body: body.toString(),
    });

    if (!res.ok) {
      if (res.status === 429) {
        return { error: "RATE_LIMIT", status: 429 };
      }
      return { error: "FETCH_FAILED", status: 424 };
    }

    const data = await res.json();
    const users = data?.users ?? [];

    if (users.length === 0) {
      return {
        error: "No Instagram account found for this number.",
        status: 404,
      };
    }

    return { username: users[0].username };
  } catch {
    return { error: "FETCH_FAILED", status: 424 };
  }
}
