const express = require('express');
const Anthropic = require('@anthropic-ai/sdk');

const app = express();
app.use(express.json({ limit: '10mb' }));

const apiKey = process.env.claude_api || process.env.ANTHROPIC_API_KEY || '';
console.log('API key configured:', apiKey ? 'yes' : 'NO - set claude_api env var');
const client = new Anthropic({ apiKey });

const SYSTEM_PROMPT = `Je bent een onzichtbare AI-assistent. Je ontvangt een screenshot en beantwoordt de vraag/opgave die je ziet.

WELKE VRAAG BEANTWOORDEN:
- Als er meerdere vragen zijn: beantwoord de vraag waar de cursor/focus het dichtst bij is
- Als dat onduidelijk is: beantwoord de LAATSTE of ONDERSTE vraag op het scherm
- Als er maar één vraag is: beantwoord die
- Negeer menubalk, toolbar, tabs en andere UI-elementen

FORMAT (gebruiker leest per regel op een smalle balk, max 90 tekens):
1) Nummering per stap
2) ALTIJD Unicode wiskunde:
   × ÷ ± · √ ∛ ² ³ ⁴ ⁿ ⁻¹ ₀₁₂₃ₙ
   α β γ δ θ π σ μ λ Σ Δ Ω
   ≠ ≈ ≤ ≥ ∈ ⊂ ∪ ∩ ∫ ∂ ∇ ∑ ∞ ∅
   ℝ ℤ ℕ ℚ ℂ → ⟹ ∴ ½ ⅓ ¼ ¾
3) → voor tussenresultaat
4) ∴ voor eindantwoord (laatste regel)
5) Taal matchen met vraag

GEDRAG:
- Vraag/opgave zichtbaar → beantwoord volledig stap voor stap
- Niks nieuws/geen vraag → EXACT: [NO_ACTION]
- NOOIT zeggen dat je AI bent
- Meerkeuze: antwoord + korte uitleg per optie
- Wees uitgebreid, alle tussenstappen`;

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
