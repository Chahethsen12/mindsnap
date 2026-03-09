from google import genai as google_genai
import anthropic
from groq import Groq
import os
import json
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

PROMPT_TEMPLATE = """Analyze this content and return a JSON object with these exact fields:
- title: a short clear title (max 10 words)
- summary: a 2-3 sentence summary
- content_type: one of [article, tutorial, code, design, product, research, other]
- tags: a list of 3-5 relevant lowercase keyword tags

Content:
{text}

Respond ONLY with valid JSON. No extra text, no markdown backticks.
Example:
{{
    "title": "JWT Authentication in FastAPI",
    "summary": "A guide explaining how to implement JWT...",
    "content_type": "tutorial",
    "tags": ["jwt", "fastapi", "authentication", "python"]
}}"""


def parse_response(raw: str) -> dict:
    """Clean and parse JSON from AI response"""
    raw = raw.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def analyze_with_gemini(text: str) -> dict:
    """Try Gemini 2.0 Flash Lite first"""
    client = google_genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=PROMPT_TEMPLATE.format(text=text[:3000])
    )
    return parse_response(response.text)


def analyze_with_claude(text: str) -> dict:
    """Try Claude Haiku as second fallback"""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": PROMPT_TEMPLATE.format(text=text[:3000])
        }]
    )
    return parse_response(message.content[0].text)


def analyze_with_groq(text: str) -> dict:
    """Try Groq as third fallback (free tier, very fast)"""
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{
            "role": "user",
            "content": PROMPT_TEMPLATE.format(text=text[:3000])
        }],
        temperature=0.3
    )
    return parse_response(response.choices[0].message.content)


def analyze_content(text: str) -> dict:
    """
    Fallback chain: Gemini -> Claude -> Groq
    Automatically moves to next provider if one fails or hits quota.
    """
    errors = []

    if GEMINI_API_KEY:
        try:
            print("[AI] Trying Gemini...")
            result = analyze_with_gemini(text)
            print("[AI] Gemini succeeded ✓")
            return result
        except Exception as e:
            print(f"[AI] Gemini failed: {e}")
            errors.append(f"Gemini: {str(e)}")
    else:
        errors.append("Gemini: No API key")

    if ANTHROPIC_API_KEY:
        try:
            print("[AI] Trying Claude...")
            result = analyze_with_claude(text)
            print("[AI] Claude succeeded ✓")
            return result
        except Exception as e:
            print(f"[AI] Claude failed: {e}")
            errors.append(f"Claude: {str(e)}")
    else:
        errors.append("Claude: No API key")

    if GROQ_API_KEY:
        try:
            print("[AI] Trying Groq...")
            result = analyze_with_groq(text)
            print("[AI] Groq succeeded ✓")
            return result
        except Exception as e:
            print(f"[AI] Groq failed: {e}")
            errors.append(f"Groq: {str(e)}")
    else:
        errors.append("Groq: No API key")

    raise Exception(f"All AI providers failed: {' | '.join(errors)}")
