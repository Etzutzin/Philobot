"""
Multi-language support for Philosophy Bot
Handles language detection and translation using Hugging Face transformers
"""

from typing import Dict, Tuple, Optional
import json
import os


class LanguageManager:
    """Manages language detection and translation."""
    
    # Supported languages with ISO 639-1 codes
    SUPPORTED_LANGUAGES = {
        "en": {
            "name": "English",
            "native_name": "English",
            "hf_model": "Helsinki-NLP/opus-mt-en-es",  # Base model for translation
        },
        "es": {
            "name": "Spanish",
            "native_name": "Español",
            "hf_model": "Helsinki-NLP/opus-mt-es-en",
        },
        "fr": {
            "name": "French",
            "native_name": "Français",
            "hf_model": "Helsinki-NLP/opus-mt-fr-en",
        },
        "de": {
            "name": "German",
            "native_name": "Deutsch",
            "hf_model": "Helsinki-NLP/opus-mt-de-en",
        },
        "it": {
            "name": "Italian",
            "native_name": "Italiano",
            "hf_model": "Helsinki-NLP/opus-mt-it-en",
        },
        "pt": {
            "name": "Portuguese",
            "native_name": "Português",
            "hf_model": "Helsinki-NLP/opus-mt-pt-en",
        },
        "ja": {
            "name": "Japanese",
            "native_name": "日本語",
            "hf_model": "Helsinki-NLP/opus-mt-ja-en",
        },
        "zh": {
            "name": "Chinese",
            "native_name": "中文",
            "hf_model": "Helsinki-NLP/opus-mt-zh-en",
        },
    }
    
    def __init__(self, default_language: str = "en"):
        """
        Initialize language manager.
        
        Args:
            default_language: Default language code (ISO 639-1)
        """
        self.default_language = default_language
        self.user_language = default_language
        self.translation_models = {}  # Cache for loaded translation models
        
        # System prompts in different languages
        self.system_prompts = self._load_system_prompts()
    
    def _load_system_prompts(self) -> Dict[str, str]:
        """Load system prompts in multiple languages."""
        return {
            "en": """You are a philosophy analyst. Return STRICT, VALID JSON with these EXACT fields:
{
    "surface_claim": "one sentence summary of the literal promise",
    "hidden_assumption": "the logical gap or oversimplification",
    "philosophical_grounding": ["Tradition1", "Tradition2"],
    "revised_quote": "more honest, intellectually rigorous version",
    "anchor_quote": {
        "text": "related canonical quote",
        "author": "philosopher name",
        "tradition": "tradition name"
    }
}

Tone: {tone}
Constraints: Keep each field under 80 words. Be intellectually honest. No invented quotes.""",

            "es": """Eres un analista de filosofía. Devuelve JSON ESTRICTO y VÁLIDO con estos campos EXACTOS:
{
    "surface_claim": "resumen de una frase de la promesa literal",
    "hidden_assumption": "la brecha lógica o oversimplificación",
    "philosophical_grounding": ["Tradición1", "Tradición2"],
    "revised_quote": "versión más honesta e intelectualmente rigurosa",
    "anchor_quote": {
        "text": "cita canónica relacionada",
        "author": "nombre del filósofo",
        "tradition": "nombre de la tradición"
    }
}

Tono: {tone}
Restricciones: Mantén cada campo bajo 80 palabras. Sé intelectualmente honesto. Sin citas inventadas.""",

            "fr": """Vous êtes un analyste de philosophie. Renvoyez un JSON STRICT et VALIDE avec ces champs EXACTS :
{
    "surface_claim": "résumé en une phrase de la promesse littérale",
    "hidden_assumption": "l'écart logique ou la simplification excessive",
    "philosophical_grounding": ["Tradition1", "Tradition2"],
    "revised_quote": "version plus honnête et intellectuellement rigoureuse",
    "anchor_quote": {
        "text": "citation canonique connexe",
        "author": "nom du philosophe",
        "tradition": "nom de la tradition"
    }
}

Ton : {tone}
Contraintes : Gardez chaque champ sous 80 mots. Soyez intellectuellement honnête. Aucune citation inventée.""",

            "de": """Sie sind ein Philosophieanalyst. Geben Sie striktes, gültiges JSON mit diesen EXAKTEN Feldern zurück:
{
    "surface_claim": "Zusammenfassung des wörtlichen Versprechens in einem Satz",
    "hidden_assumption": "die logische Lücke oder Vereinfachung",
    "philosophical_grounding": ["Tradition1", "Tradition2"],
    "revised_quote": "ehrlichere, intellektuell rigorosere Version",
    "anchor_quote": {
        "text": "verwandtes kanonisches Zitat",
        "author": "Name des Philosophen",
        "tradition": "Name der Tradition"
    }
}

Ton: {tone}
Einschränkungen: Halten Sie jedes Feld unter 80 Wörtern. Seien Sie intellektuell ehrlich. Keine erfundenen Zitate.""",
        }
    
    def detect_language(self, text: str) -> str:
        """
        Detect language from text using simple heuristics.
        Falls back to default language if detection fails.
        
        Args:
            text: Text to detect language from
            
        Returns:
            Language code (ISO 639-1)
        """
        try:
            from langdetect import detect
            
            detected = detect(text)
            
            # Map to supported languages
            if detected in self.SUPPORTED_LANGUAGES:
                return detected
            
            # Handle regional variants
            base_lang = detected.split('_')[0]
            if base_lang in self.SUPPORTED_LANGUAGES:
                return base_lang
            
        except Exception as e:
            print(f"⚠️  Language detection failed: {e}. Using default ({self.default_language})")
        
        return self.default_language
    
    def set_user_language(self, language_code: str) -> bool:
        """
        Set user's preferred language.
        
        Args:
            language_code: ISO 639-1 language code
            
        Returns:
            True if language is supported, False otherwise
        """
        if language_code in self.SUPPORTED_LANGUAGES:
            self.user_language = language_code
            print(f"✓ Language set to {self.SUPPORTED_LANGUAGES[language_code]['name']}")
            return True
        else:
            print(f"✗ Language '{language_code}' not supported.")
            print(f"Supported: {', '.join(self.SUPPORTED_LANGUAGES.keys())}")
            return False
    
    def translate_text(
        self, text: str, source_lang: str, target_lang: str
    ) -> Optional[str]:
        """
        Translate text from source to target language.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Translated text or None if translation fails
        """
        if source_lang == target_lang:
            return text
        
        try:
            # For now, use simple API (you can enhance with actual translation models)
            # Using https://api.mymemory.translated.net/ as free fallback
            import requests
            
            response = requests.get(
                "https://api.mymemory.translated.net/get",
                params={
                    "q": text,
                    "langpair": f"{source_lang}|{target_lang}"
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("responseStatus") == 200:
                    return data["responseData"]["translatedText"]
        
        except Exception as e:
            print(f"⚠️  Translation failed: {e}")
        
        return None
    
    def get_system_prompt(self, mode: str, language: str = None) -> str:
        """
        Get system prompt in specified language.
        Falls back to English if language not available.
        
        Args:
            mode: Analysis mode (clarity, brutal, compassion)
            language: Language code (uses user_language if None)
            
        Returns:
            Localized system prompt
        """
        lang = language or self.user_language
        
        # Fallback to English if language not in prompts
        if lang not in self.system_prompts:
            lang = "en"
        
        mode_descriptions = {
            "en": {
                "clarity": "Balanced precision, calm analytical tone.",
                "brutal": "Incisive and uncompromising critique.",
                "compassion": "Gentle, emotionally aware critique."
            },
            "es": {
                "clarity": "Precisión equilibrada, tono analítico tranquilo.",
                "brutal": "Crítica incisiva e inquebrantable.",
                "compassion": "Crítica gentil y emocionalmente consciente."
            },
            "fr": {
                "clarity": "Précision équilibrée, ton analytique calme.",
                "brutal": "Critique incisive et sans compromis.",
                "compassion": "Critique douce et émotionnellement consciente."
            },
            "de": {
                "clarity": "Ausgewogene Präzision, ruhiger analytischer Ton.",
                "brutal": "Scharfsinnige und kompromisslose Kritik.",
                "compassion": "Sanfte und emotional bewusste Kritik."
            },
        }
        
        mode_desc = mode_descriptions.get(lang, mode_descriptions["en"])[mode]
        
        return self.system_prompts[lang].format(tone=mode_desc)
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get dictionary of supported languages."""
        return {
            code: info["native_name"] 
            for code, info in self.SUPPORTED_LANGUAGES.items()
        }
    
    def list_languages(self) -> str:
        """Get formatted list of supported languages."""
        items = []
        for code, info in self.SUPPORTED_LANGUAGES.items():
            items.append(f"  {code.upper():<4} - {info['name']:12} ({info['native_name']})")
        return "\n".join(items)


def detect_language_simple(text: str) -> str:
    """
    Simple language detection based on character patterns.
    Fallback method if langdetect is not available.
    
    Args:
        text: Text to analyze
        
    Returns:
        Language code
    """
    import re
    
    # Character ranges for different languages
    japanese = len(re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]', text)) / len(text) > 0.3
    chinese = len(re.findall(r'[\u4E00-\u9FFF]', text)) / len(text) > 0.3
    cyrillic = len(re.findall(r'[\u0400-\u04FF]', text)) / len(text) > 0.3
    
    if japanese:
        return "ja"
    if chinese:
        return "zh"
    if cyrillic:
        return "ru"
    
    # English/Romance language detection
    english_words = {"the", "is", "and", "to", "of", "a", "in", "that", "i"}
    spanish_words = {"el", "la", "de", "que", "y", "a", "en", "es"}
    french_words = {"le", "de", "un", "et", "à", "est", "en", "que"}
    german_words = {"der", "die", "und", "in", "den", "von", "das", "zu"}
    
    text_lower = text.lower().split()
    
    scores = {
        "en": sum(1 for word in text_lower if word in english_words),
        "es": sum(1 for word in text_lower if word in spanish_words),
        "fr": sum(1 for word in text_lower if word in french_words),
        "de": sum(1 for word in text_lower if word in german_words),
    }
    
    # Return highest scoring language
    return max(scores, key=scores.get) if max(scores.values()) > 0 else "en"