import anthropic
from pydantic import BaseModel
from dotenv import load_dotenv
import json

load_dotenv()

client = anthropic.Anthropic()

# -------------------------------------------------------
# STEP 1: DEFINE THE OUTPUT SCHEMA
# This is what Claude must return — every field, every time.
# Pydantic validates it automatically.
# -------------------------------------------------------

class ICDResult(BaseModel):
    icd_code: str            # e.g. "E11.65"
    icd_description: str     # e.g. "Type 2 diabetes with hyperglycemia"
    ccsr_category: str       # e.g. "END002"
    ccsr_description: str    # e.g. "Diabetes mellitus with complication"
    confidence: str          # "high", "medium", or "low"
    reasoning: str           # Clinical reasoning behind the code selection
    alternative_codes: list  # Other possible ICD codes to consider


# -------------------------------------------------------
# STEP 2: THE SYSTEM PROMPT
# This is where your healthcare domain knowledge lives.
# The better this prompt, the more accurate the coding.
# -------------------------------------------------------

SYSTEM_PROMPT = """You are a clinical medical coder with expertise in ICD-10-CM 
coding and CCSR (Clinical Classifications Software Refined) categories.

Your job is to analyze clinical descriptions and return the most appropriate 
ICD-10-CM code and CCSR category.

ICD-10-CM coding guidelines you must follow:
- Code to the highest level of specificity
- For diabetes: always specify type (Type 1 = E10, Type 2 = E11) and any complications
- For hypertension: I10 for essential hypertension
- For unspecified conditions use the unspecified code (e.g. .9 suffix)
- Always consider whether a condition is acute or chronic

CCSR categories group ICD-10 codes into clinically meaningful categories.
Common CCSR categories:
- END002: Diabetes mellitus with complication
- END003: Diabetes mellitus without complication  
- CIR007: Hypertension with complication
- CIR008: Hypertension without complication
- CIR019: Coronary atherosclerosis and other heart disease
- RSP002: Pneumonia
- MUS010: Osteoarthritis

You must respond with a JSON object that has exactly these fields:
- icd_code: the primary ICD-10-CM code (e.g. "E11.65")
- icd_description: the official description of that code
- ccsr_category: the CCSR category code (e.g. "END002")
- ccsr_description: the CCSR category description
- confidence: "high", "medium", or "low" based on how specific the clinical info is
- reasoning: 2-3 sentences explaining why you chose this code
- alternative_codes: list of other ICD-10 codes to consider, each as a string

Respond with ONLY the JSON object. No preamble, no explanation outside the JSON."""


# -------------------------------------------------------
# STEP 3: THE EXPLAINER FUNCTION
# Sends the clinical description to Claude and parses
# the response into a validated Pydantic object.
# -------------------------------------------------------

def explain_icd_code(clinical_description: str) -> ICDResult:
    """Take a clinical description and return a structured ICD coding result."""

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Clinical description: {clinical_description}"
            }
        ]
    )

    # Extract the text response
    raw_text = response.content[0].text.strip()

    

    # Strip markdown code fences if Claude wrapped the JSON
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    # Parse JSON and validate with Pydantic
    raw_json = json.loads(raw_text)
    result = ICDResult(**raw_json)
    return result


# -------------------------------------------------------
# TEST IT — three clinical descriptions of increasing complexity
# -------------------------------------------------------

if __name__ == "__main__":
    print("\n" + "="*70)
    print("  ICD-10 Code Explainer — Clinical Coding AI")
    print("  Powered by Anthropic Claude + Pydantic")
    print("="*70)
    print("Type a clinical description and get ICD-10 + CCSR codes instantly.")
    print("Type 'quit' to exit.\n")

    while True:
        print("-" * 70)
        description = input("Clinical description: ").strip()

        if description.lower() in ["quit", "exit", "q"]:
            print("Goodbye.")
            break

        if not description:
            print("Please enter a clinical description.")
            continue

        print("Coding...\n")

        try:
            result = explain_icd_code(description)

            print(f"  ICD-10 Code:      {result.icd_code}")
            print(f"  Description:      {result.icd_description}")
            print(f"  CCSR Category:    {result.ccsr_category}")
            print(f"  CCSR Description: {result.ccsr_description}")
            print(f"  Confidence:       {result.confidence}")
            print(f"\n  Reasoning:")
            print(f"  {result.reasoning}")
            print(f"\n  Also consider:    {', '.join(result.alternative_codes)}")

        except Exception as e:
            print(f"  Error: {str(e)}")
            print("  Try rephrasing the clinical description.")