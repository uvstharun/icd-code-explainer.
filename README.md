# ICD Code Explainer — Clinical Coding AI

A clinical AI agent that takes unstructured patient descriptions and returns structured ICD-10-CM codes, CCSR categories, confidence scores, and clinical reasoning — powered by Anthropic Claude and Pydantic structured outputs.

---

## What It Does

Type a clinical description in plain English:

> "Patient on warfarin presenting with hematuria and supratherapeutic INR of 4.2"

Get back a structured coded result:

```json
{
  "icd_code": "T45.515A",
  "icd_description": "Adverse effect of anticoagulants, initial encounter",
  "ccsr_category": "INJ037",
  "ccsr_description": "Poisoning by and adverse effects of drugs",
  "confidence": "high",
  "reasoning": "Per ICD-10-CM guidelines, adverse effects require sequencing the T-code first...",
  "alternative_codes": ["R31.9", "R79.1", "Z79.01"]
}
```

---

## Architecture

```
Clinical description (free text)
        ↓
System prompt — ICD-10 coding rules + domain knowledge
        ↓
Claude (claude-opus-4-5) — medical knowledge from training
        ↓
Raw JSON response
        ↓
Pydantic validates all 7 fields
        ↓
FastAPI serves result to HTML frontend
```

No database. No vector store. No fine-tuning.
Claude's medical training is the knowledge source.
The system prompt is the coding rulebook.

---

## Tech Stack

| Layer | Tool |
|---|---|
| LLM | Anthropic Claude (claude-opus-4-5) |
| Structured outputs | Pydantic |
| API layer | FastAPI + uvicorn |
| Frontend | Custom HTML/CSS/JS |
| Language | Python 3.13 |

---

## Coding Rules in the System Prompt

The system prompt encodes real ICD-10-CM guidelines including:

- Code to highest level of specificity
- Diabetes: always specify Type 1 (E10) vs Type 2 (E11) with complications
- Hypertension + CKD: assumes causal relationship, codes as I12
- Adverse drug effects: T-code sequenced first, manifestation second
- Acute vs chronic distinction applied throughout

---

## Sample Results

| Clinical Description | Primary Code | Confidence |
|---|---|---|
| Type 2 diabetes with hyperglycemia | E11.65 | High |
| Inferior wall STEMI | I21.19 | High |
| Subarachnoid hemorrhage | I60.9 | Medium |
| Hypertensive CKD | I12.9 | High |
| Post-op sepsis | T81.44XA | High |
| Warfarin adverse effect with hematuria | T45.515A | High |

---

## How to Run It

### 1. Clone the repo
```bash
git clone https://github.com/uvstharun/icd-code-explainer.git
cd icd-code-explainer
```

### 2. Set up environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Add your Anthropic API key
```bash
touch .env
echo "ANTHROPIC_API_KEY=your_key_here" >> .env
```

### 4. Start the API
```bash
uvicorn api:app --reload --port 8000
```

### 5. Open the frontend
```bash
open icd_ui.html
```

---

## Project Structure

```
icd-code-explainer/
├── explainer.py     # Pydantic schema + system prompt + Claude call
├── api.py           # FastAPI backend — POST /code endpoint
├── icd_ui.html      # Light-themed HTML frontend
├── requirements.txt
├── .env             # API key (not tracked)
└── .gitignore
```

---

## Why This Project

Medical coding is one of the highest-value AI automation opportunities in healthcare. Manual ICD-10 coding is slow, expensive, and error-prone. This project demonstrates that a well-prompted LLM with structured output validation can apply real coding guidelines accurately — including nuanced rules like adverse effect sequencing that experienced coders often get wrong.

---

## Author

**Vishnu Sai** — Data Scientist | Healthcare AI
[LinkedIn](https://www.linkedin.com/in/vishnusai29/) · [GitHub](https://github.com/uvstharun)