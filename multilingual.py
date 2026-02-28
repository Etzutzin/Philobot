"""
Multi-language support for Philosophy Bot
Handles language detection and translation using Hugging Face
"""

from typing import Dict, Optional


class LanguageManager:
    """Manages language detection and translation."""
    
    SUPPORTED_LANGUAGES = {
        "en": {
            "name": "English",
            "native_name": "English",
        },
        "es": {
            "name": "Spanish",
            "native_name": "Español",
        },
        "fr": {
            "name": "French",
            "native_name": "Français",
        },
        "de": {
            "name": "German",
            "native_name": "Deutsch",
        },
        "it": {
            "name": "Italian",
            "native_name": "Italiano",
        },
        "pt": {
            "name": "Portuguese",
            "native_name": "Português",
        },
        "ja": {
            "name": "Japanese",
            "native_name": "日本語",
        },
        "zh": {
            "name": "Chinese",
            "native_name": "中文",
        },
    }
    
    def __init__(self, default_language: str = "en"):
        """Initialize language manager."""
        self.default_language = default_language
        self.user_language = default_language
        
        self.system_prompts = self._load_system_prompts()
    
    def _load_system_prompts(self) -> Dict[str, str]:
        """Load system prompts in multiple languages."""
        return {
            "en": """You are a philosophy analyst. Return STRICT, VALID JSON with these EXACT fields:
{{
    "surface_claim": "one sentence summary of the literal promise",
    "hidden_assumption": "the logical gap or oversimplification",
    "philosophical_grounding": ["Tradition1", "Tradition2"],
    "revised_quote": "more honest, intellectually rigorous version",
    "anchor_quote": {{
        "text": "related canonical quote",
        "author": "philosopher name",
        "tradition": "tradition name"
    }}
}}

Tone: {tone}
Constraints: Keep each field under 80 words. Be intellectually honest. No invented quotes.
IMPORTANT: Return ONLY valid JSON, no markdown or extra text.""",

            "es": """Eres un analista de filosofía. Devuelve JSON ESTRICTO y VÁLIDO con estos campos EXACTOS:
{{
    "surface_claim": "resumen de una frase de la promesa literal",
    "hidden_assumption": "la brecha lógica o oversimplificación",
    "philosophical_grounding": ["Tradición1", "Tradición2"],
    "revised_quote": "versión más honesta e intelectualmente rigurosa",
    "anchor_quote": {{
        "text": "cita canónica relacionada",
        "author": "nombre del filósofo",
        "tradition": "nombre de la tradición"
    }}
}}

Tono: {tone}
Restricciones: Mantén cada campo bajo 80 palabras. Sé intelectualmente honesto. Sin citas inventadas.
IMPORTANTE: Devuelve SOLO JSON válido, sin markdown ni texto adicional.""",

            "fr": """Vous êtes un analyste de philosophie. Renvoyez un JSON STRICT et VALIDE avec ces champs EXACTS :
{{
    "surface_claim": "résumé en une phrase de la promesse littérale",
    "hidden_assumption": "l'écart logique ou la simplification excessive",
    "philosophical_grounding": ["Tradition1", "Tradition2"],
    "revised_quote": "version plus honnête et intellectuellement rigoureuse",
    "anchor_quote": {{
        "text": "citation canonique connexe",
        "author": "nom du philosophe",
        "tradition": "nom de la tradition"
    }}
}}

Ton : {tone}
Contraintes : Gardez chaque champ sous 80 mots. Soyez intellectuellement honnête. Aucune citation inventée.
IMPORTANT : Renvoyez UNIQUEMENT du JSON valide, sans markdown ni texte supplémentaire.""",

            "de": """Sie sind ein Philosophieanalyst. Geben Sie striktes, gültiges JSON mit diesen EXAKTEN Feldern zurück:
{{
    "surface_claim": "Zusammenfassung des wörtlichen Versprechens in einem Satz",
    "hidden_assumption": "die logische Lücke oder Vereinfachung",
    "philosophical_grounding": ["Tradition1", "Tradition2"],
    "revised_quote": "ehrlichere, intellektuell rigorosere Version",
    "anchor_quote": {{
        "text": "verwandtes kanonisches Zitat",
        "author": "Name des Philosophen",
        "tradition": "Name der Tradition"
    }}
}}

Ton: {tone}
Einschränkungen: Halten Sie jedes Feld unter 80 Wörtern. Seien Sie intellektuell ehrlich. Keine erfundenen Zitate.
WICHTIG: Geben Sie NUR gültiges JSON zurück, ohne Markdown oder zusätzlichen Text.""",
        }
    
    def detect_language(self, text: str) -> str:
        """Simple language detection based on keywords."""
        try:
            from langdetect import detect
            detected = detect(text)
            
            if detected in self.SUPPORTED_LANGUAGES:
                return detected
            
            base_lang = detected.split('_')[0]
            if base_lang in self.SUPPORTED_LANGUAGES:
                return base_lang
        except:
            pass
        
        return self.default_language
    
    def set_user_language(self, language_code: str) -> bool:
        """Set user's preferred language."""
        if language_code in self.SUPPORTED_LANGUAGES:
            self.user_language = language_code
            print(f"✓ Language set to {self.SUPPORTED_LANGUAGES[language_code]['name']}")
            return True
        else:
            print(f"✗ Language '{language_code}' not supported.")
            return False
    
    def get_system_prompt(self, mode: str, language: str = None) -> str:
        """Get system prompt in specified language."""
        lang = language or self.user_language
        
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
        
        mode_desc = mode_descriptions.get(lang, mode_descriptions["en"]).get(mode, "")
        
        return self.system_prompts[lang].format(tone=mode_desc)
    
    def list_languages(self) -> str:
        """Get formatted list of supported languages."""
        items = []
        for code, info in self.SUPPORTED_LANGUAGES.items():
            items.append(f"  {code.upper():<4} - {info['name']:12} ({info['native_name']})")
        return "\n".join(items)
