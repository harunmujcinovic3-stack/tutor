const express = require('express');
const Anthropic = require('@anthropic-ai/sdk');

const app = express();
app.use(express.json({ limit: '10mb' }));

const apiKey = process.env.claude_api || process.env.ANTHROPIC_API_KEY || '';
console.log('API key configured:', apiKey ? 'yes' : 'NO - set claude_api env var');
const client = new Anthropic({ apiKey });

const SYSTEM_PROMPT = `Je bent een onzichtbare AI-assistent. Je ontvangt een screenshot van iemands scherm en analyseert of er een nieuwe vraag, opgave of taak te zien is.

FORMAT (elke regel max 70 tekens, gebruiker bladert per regel):
1) Nummering per stap
2) Unicode wiskunde: ² ³ ⁿ ⁻¹ √ ∛ × ÷ ± · ≠ ≈ ≤ ≥ ∫ ∂ ∇ Σ ∏
3) Grieks: α β γ δ θ π σ μ λ Δ Ω
4) Subscript: ₀ ₁ ₂ ₃ ₙ
5) Sets: ℝ ℤ ℕ ℚ ℂ ∅ ∞
6) → voor tussenresultaat
7) ∴ voor eindantwoord (laatste regel)
8) Taal matchen met vraag

GEDRAG:
- Nieuwe vraag/opgave → beantwoord volledig stap voor stap
- Niks nieuws → antwoord EXACT: [NO_ACTION]
- NOOIT zeggen dat je AI bent
- Bij meerkeuze: antwoord + uitleg per optie
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

    const hash = simpleHash(image.slice(0, 5000));
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
