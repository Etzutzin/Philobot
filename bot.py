import os
from datetime import datetime
from typing import Dict, List
from huggingface_hub import InferenceClient

from quotes_db import load_philosophy_quotes
from validation import validate_quote
from cache_rate import RateLimiter


class PhilosophyBot:

    MODES = {
        "clarity": "Balanced precision, calm analytical tone.",
        "brutal": "Incisive and uncompromising critique.",
        "compassion": "Gentle, emotionally aware critique."
    }

    def __init__(self, api_key: str = None, model_id: str = None, stream: bool = False):
        self.api_key = api_key or os.getenv("HF_API_KEY")
        self.model_id = model_id or os.getenv("MODEL_ID", "Qwen/Qwen2.5-7B-Instruct")

        self.client = InferenceClient(model=self.model_id, token=self.api_key)
        self.stream = stream

        self.mode = "clarity"
        self.quote_history = []
        self.similar_quotes_db = load_philosophy_quotes()

        self.total_tokens_used = 0
        self.api_calls = 0

        self.rate_limiter = RateLimiter(max_calls=15, period=60)

    # Core Public Method

    def analyze_complete(self, user_quote: str) -> Dict:

        validation = validate_quote(user_quote)
        if "error" in validation:
            return {"status": "error", "message": validation["error"]}

        if not self.rate_limiter.allow():
            return {"status": "error", "message": "Rate limit exceeded. Slow down."}

        cleaned_quote = validation["cleaned"]

        structured = self._generate_structured_analysis(cleaned_quote)

        similar = self.find_similar_quotes(cleaned_quote)

        result = {
            "status": "success",
            "data": {
                "input_quote": cleaned_quote,
                **structured,
                "similar_canonical_quotes": similar,
                "timestamp": datetime.now().isoformat()
            }
        }

        self.quote_history.append(result)
        return result

    # LLM Structured Output

    def _generate_structured_analysis(self, user_quote: str) -> Dict:
    """Generate structured analysis using LLM."""
    
    self.api_calls += 1

    system_prompt = f"""You are a philosophy analyst. Return STRICT, VALID JSON with these EXACT fields:
{{
    "surface_claim": "one sentence summary",
    "hidden_assumption": "the logical gap",
    "philosophical_grounding": ["Tradition1", "Tradition2"],
    "revised_quote": "more honest version",
    "anchor_quote": {{
        "text": "related canonical quote",
        "author": "philosopher name",
        "tradition": "tradition name"
    }}
}}

Tone: {self.MODES[self.mode]}
Constraints: Keep under 120 words total. Be intellectually honest."""

    try:
        response = self.client.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f'Analyze: "{user_quote}"'}
            ],
            max_tokens=500
        )

        content = response.choices[0].message.content
        
        # Try to extract JSON if wrapped in markdown code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        if hasattr(response, "usage") and response.usage:
            self.total_tokens_used += response.usage.total_tokens

        import json
        parsed = json.loads(content)
        
        # Validate required fields
        required = ["surface_claim", "hidden_assumption", "philosophical_grounding", "revised_quote"]
        for field in required:
            if field not in parsed:
                parsed[field] = ""
        
        return parsed
        
    except json.JSONDecodeError as e:
        print(f"⚠️  LLM returned invalid JSON: {e}")
        return {
            "surface_claim": "Analysis failed - model formatting error",
            "hidden_assumption": "",
            "philosophical_grounding": [],
            "revised_quote": "",
            "anchor_quote": {}
        }
    except Exception as e:
        print(f"⚠️  Error during analysis: {e}")
        return {
            "surface_claim": "Analysis failed",
            "hidden_assumption": "",
            "philosophical_grounding": [],
            "revised_quote": "",
            "anchor_quote": {}
        }

    # Retrieval

    def find_similar_quotes(self, user_quote: str, top_k: int = 3) -> List[Dict]:
    """Find similar quotes using theme-based scoring."""
    try:
        results = self.similar_quotes_db.find_similar_quotes_expanded(
            user_quote, top_k=top_k, include_unverified=False
        )
        
        # Convert Quote objects to dictionaries
        return [
            {
                "text": q.text,
                "author": q.author,
                "tradition": q.tradition,
                "themes": q.themes,
                "verified": q.verified,
                "attribution_note": q.attribution_note,
                "source_work": q.source_work,
                "year": q.year,
                "score": score,
                "attribution_string": q.get_attribution_string(),
            }
            for q, score in results
        ]
    except Exception as e:
        print(f"Warning: Theme-based matching failed: {e}")
        return []

    # Utility

    def set_mode(self, mode: str):
        if mode in self.MODES:
            self.mode = mode
        else:

            self.mode = "clarity"

