import os
from datetime import datetime
from typing import Dict, List
from huggingface_hub import InferenceClient

from quotes_db importimport os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from huggingface_hub import InferenceClient

from quotes_db import load_quotes_db
from validation import validate_quote
from cache_rate import RateLimiter
from multilingual import LanguageManager


class PhilosophyBot:

    MODES = {
        "clarity": "Balanced precision, calm analytical tone.",
        "brutal": "Incisive and uncompromising critique.",
        "compassion": "Gentle, emotionally aware critique."
    }

    def __init__(
        self, 
        api_key: str = None, 
        model_id: str = None, 
        stream: bool = False,
        language: str = "en",
        auto_detect_language: bool = True,
    ):
        self.api_key = api_key or os.getenv("HF_API_KEY")
    
        if not self.api_key:
            raise ValueError(
                "Missing HF_API_KEY. Set it via:\n"
                "  export HF_API_KEY='your_key_here'\n"
                "  OR pass api_key parameter to PhilosophyBot(api_key='...')"
            )
        
        self.model_id = model_id or os.getenv("MODEL_ID", "Qwen/Qwen2.5-7B-Instruct")

        self.client = InferenceClient(model=self.model_id, token=self.api_key)
        self.stream = stream

        self.mode = "clarity"
        self.quote_history = []
        self.similar_quotes_db = load_quotes_db()

        self.total_tokens_used = 0
        self.api_calls = 0

        self.rate_limiter = RateLimiter(max_calls=15, period=60)
        
        # Language support
        self.language_manager = LanguageManager(default_language=language)
        self.auto_detect_language = auto_detect_language
        self.language_manager.set_user_language(language)

    # ----------------------------
    # Core Public Method
    # ----------------------------

    def analyze_complete(self, user_quote: str) -> Dict:
        """Complete analysis pipeline with validation, rate limiting, and similar quotes."""
        
        # Auto-detect language if enabled
        if self.auto_detect_language:
            detected_lang = self.language_manager.detect_language(user_quote)
            if detected_lang != self.language_manager.user_language:
                print(f" Detected language: {self.language_manager.SUPPORTED_LANGUAGES[detected_lang]['name']}")
        
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
                "language": self.language_manager.user_language,
                "timestamp": datetime.now().isoformat()
            }
        }

        self.quote_history.append(result)
        return result


    # ----------------------------
    # LLM Structured Output
    # ----------------------------

    def _generate_structured_analysis(self, user_quote: str) -> Dict:
        """Generate structured analysis using LLM with language support."""
        
        self.api_calls += 1

        # Get localized system prompt
        system_prompt = self.language_manager.get_system_prompt(
            self.mode, 
            self.language_manager.user_language
        )

        try:
            response = self.client.chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f'Analyze this quote: "{user_quote}"'}
                ],
                max_tokens=500
            )

            content = response.choices[0].message.content
            
            # Extract JSON if wrapped in markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            if hasattr(response, "usage") and response.usage:
                self.total_tokens_used += response.usage.total_tokens

            parsed = json.loads(content)
            
            # Validate required fields
            required = ["surface_claim", "hidden_assumption", "philosophical_grounding", "revised_quote"]
            for field in required:
                if field not in parsed:
                    parsed[field] = ""
            
            return parsed
            
        except json.JSONDecodeError as e:
            print(f"  LLM returned invalid JSON: {e}")
            return {
                "surface_claim": "Analysis failed - model formatting error",
                "hidden_assumption": "",
                "philosophical_grounding": [],
                "revised_quote": "",
                "anchor_quote": {}
            }
        except Exception as e:
            print(f"  Error during analysis: {e}")
            return {
                "surface_claim": "Analysis failed",
                "hidden_assumption": "",
                "philosophical_grounding": [],
                "revised_quote": "",
                "anchor_quote": {}
            }

    # ----------------------------
    # Retrieval
    # ----------------------------

    def find_similar_quotes(self, user_quote: str, top_k: int = 3) -> List[Dict]:
        """Find similar quotes using theme-based scoring."""
        """    
        user_words = set(user_quote.lower().split())

         scored = []
         for quote in self.quotes_db:  # assuming loaded Quote objects
             overlap = user_words.intersection(set(quote.text.lower().split()))
             score = len(overlap)
   
             if score > 0:
                 scored.append((score, quote))

         scored.sort(reverse=True, key=lambda x: x[0])
         """

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

    # ----------------------------
    # Session Management
    # ----------------------------

    def get_session_stats(self) -> Dict:
        """Get usage statistics for the current session."""
        estimated_cost = (self.total_tokens_used / 1_000_000) * 0.07
        
        return {
            "total_api_calls": self.api_calls,
            "total_tokens_used": self.total_tokens_used,
            "estimated_cost_usd": round(estimated_cost, 6),
            "quotes_analyzed": len(self.quote_history),
            "rate_limit_remaining": self.rate_limiter.max_calls - len(self.rate_limiter.calls),
            "current_language": self.language_manager.user_language,
        }

    # ----------------------------
    # Language Management
    # ----------------------------

    def set_language(self, language_code: str) -> bool:
        """
        Change the bot's language.
        
        Args:
            language_code: ISO 639-1 language code
            
        Returns:
            True if successful, False otherwise
        """
        return self.language_manager.set_user_language(language_code)
    
    def get_available_languages(self) -> str:
        """Get formatted list of available languages."""
        return self.language_manager.list_languages()
    
    def toggle_auto_language_detection(self, enabled: bool):
        """Enable/disable automatic language detection."""
        self.auto_detect_language = enabled
        status = "enabled" if enabled else "disabled"
        print(f"✓ Auto-language detection {status}")

    # ----------------------------
    # Utility
    # ----------------------------

    def set_mode(self, mode: str):
        """Set the analysis mode."""
        if mode in self.MODES:
            self.mode = mode
            return True
        else:
            self.mode = "clarity"
            return False load_philosophy_quotes
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
    
    if not self.api_key:
        raise ValueError(
            "Missing HF_API_KEY. Set it via:\n"
            "  export HF_API_KEY='your_key_here'\n"
            "  OR pass api_key parameter to PhilosophyBot(api_key='...')"
        )
    
    self.model_id = model_id or os.getenv("MODEL_ID", "Qwen/Qwen2.5-7B-Instruct")

    self.client = InferenceClient(model=self.model_id, token=self.api_key)
        self.stream = stream

        self.mode = "clarity"
        self.quote_history = []
        self.similar_quotes_db = load_quotes_db()

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
        print(f"  LLM returned invalid JSON: {e}")
        return {
            "surface_claim": "Analysis failed - model formatting error",
            "hidden_assumption": "",
            "philosophical_grounding": [],
            "revised_quote": "",
            "anchor_quote": {}
        }
    except Exception as e:
        print(f"  Error during analysis: {e}")
        return {
            "surface_claim": "Analysis failed",
            "hidden_assumption": "",
            "philosophical_grounding": [],
            "revised_quote": "",
            "anchor_quote": {}
        }

    def _extract_traditions_from_analysis(self, analysis: Dict) -> List[str]:
    """Extract philosophical traditions mentioned in analysis."""
    traditions = analysis.get("philosophical_grounding", [])
    
    # Validate against known traditions
    known = self.similar_quotes_db.get_all_traditions()
    return [t for t in traditions if t in known]

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





