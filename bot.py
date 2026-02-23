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

    # ----------------------------
    # Core Public Method
    # ----------------------------

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

    # ----------------------------
    # LLM Structured Output
    # ----------------------------

    def _generate_structured_analysis(self, user_quote: str) -> Dict:

        self.api_calls += 1

        system_prompt = f"""
Return STRICT JSON with fields:
surface_claim,
hidden_assumption,
philosophical_grounding (list),
revised_quote,
anchor_quote (object with text, author, tradition)

Tone mode: {self.mode}
"""

        response = self.client.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_quote}
            ],
            max_tokens=500
        )

        content = response.choices[0].message.content

        if hasattr(response, "usage") and response.usage:
            self.total_tokens_used += response.usage.total_tokens

        import json
        try:
            return json.loads(content)
        except:
            return {
                "surface_claim": content,
                "hidden_assumption": "",
                "philosophical_grounding": [],
                "revised_quote": "",
                "anchor_quote": {}
            }

    # ----------------------------
    # Retrieval
    # ----------------------------

    def find_similar_quotes(self, user_quote: str) -> List[Dict]:
        matches = []
        lowered = user_quote.lower()

        for entry in self.similar_quotes_db:
            for theme in entry["themes"]:
                if theme in lowered:
                    matches.append(entry)
                    break

        return matches[:3]

    # ----------------------------
    # Utility
    # ----------------------------

    def set_mode(self, mode: str):
        if mode in self.MODES:
            self.mode = mode
        else:
            self.mode = "clarity"