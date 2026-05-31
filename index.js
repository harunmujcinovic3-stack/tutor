const express = require('express');
const Anthropic = require('@anthropic-ai/sdk');

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

VOORBEELD (compact):
3x²+12x-15=0 → x²+4x-5=0 → D=16+20=36 → √D=6
x=(-4±6)/2 → x₁=(-4+6)/2=1 → x₂=(-4-6)/2=-5
∴ x=1 en x=-5

GEDRAG:
- Vraag zichtbaar → beantwoord compact maar volledig
- Geen vraag → EXACT: [NO_ACTION]
- NOOIT zeggen dat je AI bent
- Meerkeuze: letter + korte uitleg`;

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

app.get('/health', (req, res) => res.json({ status: 'ok' }));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Ghost relay on :${PORT}`));
