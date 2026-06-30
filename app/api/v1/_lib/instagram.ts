const IG_WEB = "https://www.instagram.com";
const IG_API = "https://i.instagram.com/api/v1";

const ANDROID_UA =
  "Instagram 332.0.0.38.90 Android (33/13; 420dpi; 1080x2400; samsung; SM-G991B; o1s; exynos2100; en_US; 604247854)";

function normalizeNumber(phone: string): string {
  let n = phone.replace(/[\s\-().]/g, "");
  if (!n.startsWith("+")) {
    n = "+" + n;
  }
  return n;
}

async function getCsrfToken(): Promise<string | null> {
  try {
    const res = await fetch(`${IG_WEB}/accounts/login/`, {
      headers: { "User-Agent": ANDROID_UA },
    });
    const cookies = res.headers.get("set-cookie") ?? "";
    const match = cookies.match(/csrftoken=([^;]+)/);
    return match ? match[1] : null;
  } catch {
    return null;
  }
}

export async function lookupNumberToUsername(
  number: string
): Promise<
  | { username: string; masked?: boolean }
  | { error: string; status: number; debug?: string }
> {
  const normalized = normalizeNumber(number);
  const csrf = await getCsrfToken();

  if (!csrf) {
    return { error: "FETCH_FAILED", status: 424, debug: "Could not get CSRF token from Instagram" };
  }

  // Step 1: Send the phone number to account recovery to check if it exists
  try {
    const body = new URLSearchParams({
      query: normalized,
      device_id: crypto.randomUUID(),
      guid: crypto.randomUUID(),
    });

    const res = await fetch(`${IG_API}/users/lookup/`, {
      method: "POST",
      headers: {
        "User-Agent": ANDROID_UA,
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": csrf,
        Cookie: `csrftoken=${csrf}`,
      },
      body: body.toString(),
    });

    const data = await res.json();

    if (!res.ok) {
      if (res.status === 429) return { error: "RATE_LIMIT", status: 429 };
      if (data?.message === "user_not_found" || data?.status === "fail") {
        return { error: "No Instagram account found for this number.", status: 404 };
      }
      return { error: "FETCH_FAILED", status: 424, debug: JSON.stringify(data) };
    }

    // The lookup response may contain obfuscated contact info
    // Try to extract username from the response
    if (data?.user?.username) {
      return { username: data.user.username };
    }

    // If we get an obfuscated email/phone but no username, use the user_id to get profile
    const userId = data?.user?.pk ?? data?.user?.pk_v2;
    if (userId) {
      const profileRes = await fetch(`${IG_API}/users/${userId}/info/`, {
        headers: {
          "User-Agent": ANDROID_UA,
          "X-CSRFToken": csrf,
          Cookie: `csrftoken=${csrf}`,
        },
      });

      if (profileRes.ok) {
        const profileData = await profileRes.json();
        if (profileData?.user?.username) {
          return { username: profileData.user.username };
        }
      }
    }

    // Return whatever obfuscated info we got
    const obfuscated = data?.obfuscated_phone ?? data?.user?.obfuscated_phone;
    if (obfuscated) {
      return {
        error: "Account exists but username is masked. Found phone: " + obfuscated,
        status: 404,
      };
    }

    return { error: "FETCH_FAILED", status: 424, debug: JSON.stringify(data) };
  } catch (e) {
    return { error: "FETCH_FAILED", status: 424, debug: String(e) };
  }
}
