import { NextRequest, NextResponse } from "next/server";
import { timingSafeEqual } from "crypto";
import fs from "fs";
import path from "path";

const DATA_FILE = path.join(process.cwd(), "data", "waitlist.json");

const MAX_NAME_LENGTH = 100;
const MAX_EMAIL_LENGTH = 254; // RFC 5321 maximum

// --- Simple in-memory rate limiter (per IP) ---------------------------------
// Not durable across restarts or multiple instances, but stops trivial spam of
// the unauthenticated write endpoint from a single source.
const RATE_LIMIT_WINDOW_MS = 60_000;
const RATE_LIMIT_MAX = 5;
const hits = new Map<string, { count: number; resetAt: number }>();

function isRateLimited(ip: string): boolean {
  const now = Date.now();
  const entry = hits.get(ip);
  if (!entry || now > entry.resetAt) {
    hits.set(ip, { count: 1, resetAt: now + RATE_LIMIT_WINDOW_MS });
    return false;
  }
  entry.count += 1;
  return entry.count > RATE_LIMIT_MAX;
}

function clientIp(req: NextRequest): string {
  // Next removed req.ip; derive from the standard forwarding header instead.
  const fwd = req.headers.get("x-forwarded-for");
  return fwd?.split(",")[0]?.trim() || "unknown";
}

// --- Serialize writes to avoid the read-modify-write race -------------------
let writeChain: Promise<unknown> = Promise.resolve();
function withLock<T>(fn: () => Promise<T>): Promise<T> {
  const run = writeChain.then(fn, fn);
  // Keep the chain alive even if a step rejects.
  writeChain = run.then(
    () => undefined,
    () => undefined
  );
  return run;
}

function ensureDataFile() {
  const dir = path.dirname(DATA_FILE);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  if (!fs.existsSync(DATA_FILE)) {
    fs.writeFileSync(DATA_FILE, JSON.stringify([], null, 2));
  }
}

function safeEqual(a: string, b: string): boolean {
  const bufA = Buffer.from(a);
  const bufB = Buffer.from(b);
  if (bufA.length !== bufB.length) return false;
  return timingSafeEqual(bufA, bufB);
}

export async function POST(req: NextRequest) {
  try {
    if (isRateLimited(clientIp(req))) {
      return NextResponse.json(
        { error: "Te veel verzoeken. Probeer het later opnieuw." },
        { status: 429 }
      );
    }

    const body = await req.json();
    const email = (body.email ?? "").trim().toLowerCase();
    const name = (body.name ?? "").trim();

    if (
      !email ||
      email.length > MAX_EMAIL_LENGTH ||
      !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
    ) {
      return NextResponse.json(
        { error: "Voer een geldig e-mailadres in." },
        { status: 400 }
      );
    }

    if (!name || name.length > MAX_NAME_LENGTH) {
      return NextResponse.json(
        { error: "Voer je naam in." },
        { status: 400 }
      );
    }

    return await withLock(async () => {
      ensureDataFile();

      const raw = fs.readFileSync(DATA_FILE, "utf-8");
      const list: { email: string; name: string; createdAt: string }[] =
        JSON.parse(raw);

      if (list.some((entry) => entry.email === email)) {
        return NextResponse.json(
          { error: "Dit e-mailadres staat al op de wachtlijst." },
          { status: 409 }
        );
      }

      list.push({ email, name, createdAt: new Date().toISOString() });
      fs.writeFileSync(DATA_FILE, JSON.stringify(list, null, 2));

      return NextResponse.json({ ok: true }, { status: 201 });
    });
  } catch {
    return NextResponse.json(
      { error: "Er ging iets mis. Probeer het opnieuw." },
      { status: 500 }
    );
  }
}

// Reading the waitlist exposes personal data of every signup, so it must never
// be public. Require a bearer token that matches WAITLIST_ADMIN_TOKEN; if the
// token is not configured, deny access entirely.
export async function GET(req: NextRequest) {
  const configured = process.env.WAITLIST_ADMIN_TOKEN;
  const provided = req.headers.get("authorization")?.replace(/^Bearer\s+/i, "");

  if (!configured || !provided || !safeEqual(provided, configured)) {
    return NextResponse.json({ error: "Niet geautoriseerd." }, { status: 401 });
  }

  try {
    ensureDataFile();
    const raw = fs.readFileSync(DATA_FILE, "utf-8");
    const list = JSON.parse(raw);
    return NextResponse.json({ count: list.length, entries: list });
  } catch {
    return NextResponse.json(
      { error: "Kon wachtlijst niet laden." },
      { status: 500 }
    );
  }
}
