import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

const DATA_FILE = path.join(process.cwd(), "data", "waitlist.json");

function ensureDataFile() {
  const dir = path.dirname(DATA_FILE);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  if (!fs.existsSync(DATA_FILE)) {
    fs.writeFileSync(DATA_FILE, JSON.stringify([], null, 2));
  }
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const email = (body.email ?? "").trim().toLowerCase();
    const name = (body.name ?? "").trim();

    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return NextResponse.json(
        { error: "Voer een geldig e-mailadres in." },
        { status: 400 }
      );
    }

    if (!name) {
      return NextResponse.json(
        { error: "Voer je naam in." },
        { status: 400 }
      );
    }

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
  } catch {
    return NextResponse.json(
      { error: "Er ging iets mis. Probeer het opnieuw." },
      { status: 500 }
    );
  }
}

export async function GET() {
  try {
    ensureDataFile();
    const raw = fs.readFileSync(DATA_FILE, "utf-8");
    const list = JSON.parse(raw);
    return NextResponse.json({ count: list.length, entries: list });
  } catch {
    return NextResponse.json({ error: "Kon wachtlijst niet laden." }, { status: 500 });
  }
}
