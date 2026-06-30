const express = require('express');
const Anthropic = require('@anthropic-ai/sdk');
const { chromium } = require('playwright-core');

const app = express();
app.use(express.json({ limit: '10mb' }));

const apiKey = process.env.claude_api || process.env.ANTHROPIC_API_KEY || '';
console.log('API key configured:', apiKey ? 'yes' : 'NO - set claude_api env var');
const client = new Anthropic({ apiKey });

const SYSTEM_PROMPT = `Je bent een onzichtbare assistent. Je ontvangt een screenshot en beantwoordt de vraag/opgave die je ziet.

WELKE VRAAG:
- Meerdere vragen: de ONDERSTE of meest prominente
- Negeer UI-elementen (menubalk, tabs, toolbar)

FORMAT — antwoord verschijnt op een Touch Bar (hele breedte, ~120 tekens per regel):
- Zet ALLES op zo MIN mogelijk regels — combineer stappen op één regel met →
- Unicode wiskunde VERPLICHT: × ÷ ± · √ ∛ ² ³ ⁴ ⁿ ⁻¹ ₀₁₂₃ₙ α β γ δ θ π σ μ λ Σ Δ Ω ≠ ≈ ≤ ≥ ∫ ∂ ∇ ∑ ∞ ∅ ℝ ℤ ℕ ℚ ℂ → ⟹ ∴ ½ ⅓ ¼ ¾
- ∴ voor eindantwoord (laatste regel)
- Taal matchen met vraag
- Max 6-8 regels totaal, prop zoveel mogelijk per regel

ALLES OP ÉÉN REGEL. Geen enters, geen newlines, alles achter elkaar met → ertussen.

VOORBEELD:
3x²+12x-15=0 → ÷3 → x²+4x-5=0 → D=16+20=36 → √D=6 → x=(-4±6)/2 → x₁=1, x₂=-5 ∴ x=1 en x=-5

STRICT:
- ALLES op ÉÉN REGEL, hoe lang ook
- Gebruik → tussen stappen
- ∴ voor eindantwoord
- GEEN newlines, GEEN enters, GEEN opsomming
- Geen vraag → EXACT: [NO_ACTION]
- NOOIT zeggen dat je AI bent
- Meerkeuze: A) uitleg | B) uitleg | C) uitleg — alles op één regel`;

let previousHash = '';

function simpleHash(str) {
  let h = 0;
  for (let i = 0; i < str.length; i++) {
    h = ((h << 5) - h + str.charCodeAt(i)) | 0;
  }
  return h.toString();
}

app.post('/analyze', async (req, res) => {
  try {
    const { image } = req.body;
    if (!image) return res.json({ answer: null });

    // Hash middle section of image (header bytes are identical across screenshots)
    const mid = Math.floor(image.length / 2);
    const hash = simpleHash(image.slice(mid, mid + 20000));
    if (hash === previousHash) return res.json({ answer: null });
    previousHash = hash;

    const response = await client.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 4096,
      system: SYSTEM_PROMPT,
      messages: [{
        role: 'user',
        content: [
          {
            type: 'image',
            source: { type: 'base64', media_type: 'image/png', data: image }
          },
          {
            type: 'text',
            text: 'Is er een nieuwe vraag/opgave op dit scherm? Los volledig op per regel (max 70 chars) of [NO_ACTION].'
          }
        ]
      }]
    });

    const text = response.content[0]?.text?.trim() || '[NO_ACTION]';
    if (text.includes('[NO_ACTION]')) return res.json({ answer: null });

    res.json({ answer: text });
  } catch (err) {
    console.error('Error:', err.message);
    res.json({ answer: null, error: err.message });
  }
});

// Text endpoint - reads extracted screen text (no screenshot needed, cheaper)
app.post('/ask', async (req, res) => {
  try {
    const { text } = req.body;
    if (!text || text.trim().length < 5) return res.json({ answer: null });

    const response = await client.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 4096,
      system: SYSTEM_PROMPT,
      messages: [{
        role: 'user',
        content: `Dit is tekst van een scherm (via accessibility uitgelezen). Vind de vraag/opgave en los volledig op, ALLES op één regel met → ertussen, of [NO_ACTION].\n\n[SCHERM]\n${text.slice(0, 12000)}`
      }]
    });

    const answer = response.content[0]?.text?.trim() || '[NO_ACTION]';
    if (answer.includes('[NO_ACTION]')) return res.json({ answer: null });

    res.json({ answer });
  } catch (err) {
    console.error('Error:', err.message);
    res.json({ answer: null, error: err.message });
  }
});

// --- Profile Photo History (Wayback Machine) ---

const PLATFORM_URLS = {
  instagram: (u) => `https://www.instagram.com/${u}/`,
  twitter: (u) => `https://twitter.com/${u}`,
  x: (u) => `https://x.com/${u}`,
};

const CDX_API = 'https://web.archive.org/cdx/search/cdx';

async function fetchSnapshots(profileUrl, limit) {
  const params = new URLSearchParams({
    url: profileUrl,
    output: 'json',
    fl: 'timestamp,original,statuscode',
    filter: 'statuscode:200',
    collapse: 'timestamp:6',
    limit: String(limit),
  });

  const res = await fetch(`${CDX_API}?${params}`, {
    signal: AbortSignal.timeout(30000),
  });

  if (!res.ok) throw new Error(`Wayback Machine API error: ${res.status}`);

  const data = await res.json();
  if (!data || data.length < 2) return [];

  const [, ...rows] = data;
  return rows.map(([timestamp, original]) => ({ timestamp, original }));
}

async function extractProfilePhoto(archiveUrl) {
  try {
    const res = await fetch(archiveUrl, {
      signal: AbortSignal.timeout(10000),
      headers: { 'User-Agent': 'ProfilePhotoHistoryTool/1.0' },
    });
    if (!res.ok) return null;

    const html = await res.text();

    const ogMatch =
      html.match(/<meta[^>]+property=["']og:image["'][^>]+content=["']([^"']+)["']/i) ||
      html.match(/<meta[^>]+content=["']([^"']+)["'][^>]+property=["']og:image["']/i);

    if (ogMatch && ogMatch[1]) return ogMatch[1];

    const imgMatch = html.match(/<img[^>]+class="[^"]*profile[^"]*"[^>]+src=["']([^"']+)["']/i);
    return imgMatch ? imgMatch[1] : null;
  } catch {
    return null;
  }
}

function formatTimestamp(ts) {
  return `${ts.slice(0, 4)}-${ts.slice(4, 6)}-${ts.slice(6, 8)}`;
}

app.get('/profile-photos', async (req, res) => {
  try {
    const username = (req.query.username || '').trim();
    const platform = (req.query.platform || 'instagram').toLowerCase();
    const limit = Math.min(Math.max(parseInt(req.query.limit) || 20, 1), 50);

    if (!username || !/^[\w.]{1,60}$/.test(username)) {
      return res.status(400).json({
        error: 'Voer een geldige gebruikersnaam in (letters, cijfers, underscores, punten).',
      });
    }

    const urlBuilder = PLATFORM_URLS[platform];
    if (!urlBuilder) {
      return res.status(400).json({
        error: `Ongeldig platform. Kies uit: ${Object.keys(PLATFORM_URLS).join(', ')}`,
      });
    }

    const extractPhotos = req.query.extract === 'true';
    const profileUrl = urlBuilder(username);
    const rawSnapshots = await fetchSnapshots(profileUrl, limit);

    if (rawSnapshots.length === 0) {
      return res.json({
        username,
        platform,
        message: 'Geen gearchiveerde snapshots gevonden voor dit profiel.',
        snapshots: [],
      });
    }

    const snapshots = await Promise.all(
      rawSnapshots.map(async ({ timestamp, original }) => {
        const archiveUrl = `https://web.archive.org/web/${timestamp}/${original}`;
        const photoUrl = extractPhotos ? await extractProfilePhoto(archiveUrl) : null;
        return { timestamp, date: formatTimestamp(timestamp), archiveUrl, photoUrl };
      })
    );

    const result = { username, platform, totalSnapshots: snapshots.length, snapshots };
    if (extractPhotos) {
      result.snapshotsWithPhotos = snapshots.filter((s) => s.photoUrl !== null).length;
    }

    res.json(result);
  } catch (err) {
    console.error('Profile photos error:', err.message);
    res.status(502).json({
      error: `Fout bij ophalen van profielfotos: ${err.message}`,
    });
  }
});

// Try to upgrade an Instagram CDN URL to higher resolution
function upgradeToHD(cdnUrl) {
  if (!cdnUrl) return [];
  const variants = [cdnUrl];
  // Remove size params like /s150x150/ or /s320x320/ to get original
  const noSize = cdnUrl.replace(/\/s\d+x\d+\//, '/');
  if (noSize !== cdnUrl) variants.push(noSize);
  // Try common HD sizes
  const hd = cdnUrl.replace(/\/s\d+x\d+\//, '/s1080x1080/');
  if (hd !== cdnUrl) variants.push(hd);
  const large = cdnUrl.replace(/\/s\d+x\d+\//, '/s640x640/');
  if (large !== cdnUrl) variants.push(large);
  return [...new Set(variants)];
}

async function fetchFromTrendHero(username, debug = false) {
  let browser;
  try {
    const executablePath = process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
    browser = await chromium.launch({
      executablePath,
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
    });
    const page = await browser.newPage();
    await page.goto(`https://trendhero.io/instagram/${username}/`, {
      waitUntil: 'networkidle',
      timeout: 30000,
    });

    // Grab all image sources from the page
    const photos = await page.evaluate((uname) => {
      const results = [];
      // Get ALL images on the page
      document.querySelectorAll('img').forEach((img) => {
        const src = img.src || img.getAttribute('data-src') || img.getAttribute('data-lazy-src') || '';
        if (src && !src.includes('data:image') && !src.includes('.svg')) {
          results.push({ src, alt: img.alt || '', cls: img.className || '', w: img.naturalWidth });
        }
      });
      // Check background images on all elements
      document.querySelectorAll('*').forEach((el) => {
        const bg = getComputedStyle(el).backgroundImage || '';
        if (bg && bg !== 'none') {
          const match = bg.match(/url\(["']?([^"')]+)/);
          if (match && !match[1].includes('data:image') && !match[1].includes('.svg')) {
            results.push({ src: match[1], alt: 'bg-image', cls: el.className || '', w: 0 });
          }
        }
      });
      return results;
    }, username);

    const pageTitle = await page.title();
    const pageUrl = page.url();
    await browser.close();

    if (debug) return { photos, pageTitle, pageUrl };
    if (photos.length === 0) return null;

    // Try to find the profile photo: look for CDN URLs first, then largest image
    const cdnPhoto = photos.find((p) =>
      p.src.includes('cdninstagram') || p.src.includes('fbcdn.net')
    );
    if (cdnPhoto) return cdnPhoto.src;

    // Return the first non-tiny, non-icon image (likely the profile photo)
    const candidate = photos.find((p) =>
      !p.src.includes('logo') && !p.src.includes('icon') && !p.src.includes('favicon')
    );
    return candidate ? candidate.src : photos[0].src;
  } catch (err) {
    console.error('TrendHero fetch error:', err.message);
    if (browser) await browser.close().catch(() => {});
    return null;
  }
}

app.get('/profile-photo-debug', async (req, res) => {
  try {
    const username = (req.query.username || '').trim();
    if (!username || !/^[\w.]{1,60}$/.test(username)) {
      return res.status(400).json({ error: 'Voer een geldige gebruikersnaam in.' });
    }
    const result = await fetchFromTrendHero(username, true);
    res.json({ username, ...result });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/profile-photo-hd', async (req, res) => {
  try {
    const username = (req.query.username || '').trim();

    if (!username || !/^[\w.]{1,60}$/.test(username)) {
      return res.status(400).json({
        error: 'Voer een geldige gebruikersnaam in.',
      });
    }

    console.log(`Fetching profile photo for @${username} from TrendHero...`);
    const photoUrl = await fetchFromTrendHero(username);

    if (!photoUrl) {
      return res.json({
        username,
        message: 'Kon geen profielfoto vinden op TrendHero.',
        photoUrl: null,
        hdVariants: [],
      });
    }

    const hdVariants = upgradeToHD(photoUrl);

    res.json({
      username,
      photoUrl,
      hdVariants,
    });
  } catch (err) {
    console.error('Profile photo HD error:', err.message);
    res.status(502).json({
      error: `Fout bij ophalen van profielfoto: ${err.message}`,
    });
  }
});

app.get('/health', (req, res) => res.json({ status: 'ok' }));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Ghost relay on :${PORT}`));
