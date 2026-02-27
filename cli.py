from bot import PhilosophyBot
import json
import locale

# Mapping from full language names (as returned by locale) to ISO 639‑1 codes
LANG_NAME_TO_CODE = {
    "english": "en",
    "spanish": "es",
    "french": "fr",
    "german": "de",
    "italian": "it",
    "portuguese": "pt",
    "japanese": "ja",
    "chinese": "zh",
    "russian": "ru",
    "arabic": "ar",
    "hindi": "hi",
    # add more as needed
}

def display_analysis(result: dict):
    """Format and display analysis results."""
    if result["status"] == "error":
        print(f"\n Error: {result['message']}\n")
        return

    data = result["data"]
    
    print("\n" + "="*70)
    print(" PHILOSOPHICAL ANALYSIS")
    print("="*70)
    
    print(f"\n Input Quote:\n   {data['input_quote']}\n")
    
    if data.get("surface_claim"):
        print(f" Surface Claim:\n   {data['surface_claim']}\n")
    
    if data.get("hidden_assumption"):
        print(f"  Hidden Assumption:\n   {data['hidden_assumption']}\n")
    
    if data.get("philosophical_grounding"):
        traditions = ", ".join(data["philosophical_grounding"])
        print(f" Philosophical Grounding:\n   {traditions}\n")
    
    if data.get("revised_quote"):
        print(f" Revised Quote:\n   {data['revised_quote']}\n")
    
    if data.get("similar_canonical_quotes"):
        print(" Similar Philosophical Quotes:")
        for i, q in enumerate(data["similar_canonical_quotes"], 1):
            verified_badge = "" if q.get("verified", True) else "  [UNCERTAIN]"
            score = f" (Match: {q.get('score', 0)})" if q.get('score', 0) > 0 else ""
            # Build attribution string without nesting f‑strings
            attribution = q.get('attribution_string', f'— {q["author"]}')
            print(f'   {i}. "{q["text"]}"\n      {attribution} {verified_badge}{score}\n')
    
    print("="*70 + "\n")


def show_menu():
    """Display available commands."""
    print("\n" + "─"*70)
    print("Available Commands:")
    print("  /mode <clarity|brutal|compassion>     - Change analysis mode")
    print("  /lang <code>                           - Change language")
    print("  /langs                                 - List available languages")
    print("  /auto_lang <on|off>                    - Toggle auto language detection")
    print("  /stats                                 - Show session statistics")
    print("  /help                                  - Show this help menu")
    print("  exit, quit                             - Exit the program")
    print("─"*70 + "\n")


def main():
    try:
        # Detect system language and map to ISO code
        system_lang = locale.getlocale()[0]
        if system_lang:
            lang_name = system_lang.split('_')[0].lower()
            default_lang = LANG_NAME_TO_CODE.get(lang_name, "en")
        else:
            default_lang = "en"
        
        bot = PhilosophyBot(language=default_lang)
    except ValueError as e:
        print(f"\n {e}\n")
        return

    print("\n" + "="*70)
    print(" Welcome to Philosophy Bot - Interactive Quote Analysis")
    print("="*70)

    # Initial mode selection
    print("\nAvailable Modes:")
    for mode, description in bot.MODES.items():
        print(f"  • {mode.upper():<12} - {description}")
    
    selected = input("\nSelect mode (default: clarity): ").strip().lower()
    if selected:
        bot.set_mode(selected)

    print(f"\n✓ Mode set to: {bot.mode.upper()}")
    # Now user_language is a code, safe to use as key
    lang_name = bot.language_manager.SUPPORTED_LANGUAGES[bot.language_manager.user_language]['name']
    print(f"✓ Language: {lang_name}")
    print("\nType 'exit' to quit or '/help' for commands.\n")

    while True:
        try:
            lang_badge = bot.language_manager.user_language.upper()
            print(f"[{bot.mode.upper()}|{lang_badge}]", end=" ")
            user_input = input("Enter quote or command: ").strip()

            if not user_input:
                continue

            # Exit
            if user_input.lower() in ["exit", "quit"]:
                print("\n Thank you for using Philosophy Bot!")
                break
            
            # Help
            if user_input.lower() in ["/help", "-h", "--help"]:
                show_menu()
                continue
            
            # Mode switching
            if user_input.startswith("/mode"):
                parts = user_input.split()
                if len(parts) > 1:
                    mode = parts[1].lower()
                    if bot.set_mode(mode):
                        print(f"✓ Mode changed to {bot.mode.upper()}\n")
                    else:
                        print(f"✗ Invalid mode. Options: clarity, brutal, compassion\n")
                else:
                    print("Usage: /mode <clarity|brutal|compassion>\n")
                continue
            
            # Language switching
            if user_input.startswith("/lang"):
                parts = user_input.split()
                if len(parts) > 1:
                    lang_input = parts[1].lower()
                    # Allow both full names and codes: if it's a known name, map to code
                    lang_code = LANG_NAME_TO_CODE.get(lang_input, lang_input)
                    if bot.set_language(lang_code):
                        # Success message (optional)
                        new_lang = bot.language_manager.user_language
                        lang_display = bot.language_manager.SUPPORTED_LANGUAGES[new_lang]['name']
                        print(f"✓ Language changed to {lang_display}\n")
                    else:
                        print(f"✗ Invalid language. Use /langs to see available codes.\n")
                else:
                    print("Usage: /lang <language_code>\n")
                continue
            
            # List languages
            if user_input.lower() == "/langs":
                print("\n Available Languages:")
                print(bot.get_available_languages())
                print()
                continue
            
            # Auto language detection toggle
            if user_input.startswith("/auto_lang"):
                parts = user_input.split()
                if len(parts) > 1:
                    setting = parts[1].lower()
                    if setting in ["on", "true", "yes", "1"]:
                        bot.toggle_auto_language_detection(True)
                        print("✓ Auto language detection enabled\n")
                    elif setting in ["off", "false", "no", "0"]:
                        bot.toggle_auto_language_detection(False)
                        print("✓ Auto language detection disabled\n")
                    else:
                        print("Usage: /auto_lang <on|off>\n")
                else:
                    print("Usage: /auto_lang <on|off>\n")
                continue
            
            # Statistics
            if user_input.lower() == "/stats":
                stats = bot.get_session_stats()
                print(f"\n Session Statistics:")
                print(f"   API Calls: {stats['total_api_calls']}")
                print(f"   Tokens Used: {stats['total_tokens_used']}")
                print(f"   Est. Cost: ${stats['estimated_cost_usd']}")
                print(f"   Quotes Analyzed: {stats['quotes_analyzed']}")
                print(f"   Rate Limit Remaining: {stats['rate_limit_remaining']}/15 per minute")
                current_lang = stats['current_language']
                lang_display = bot.language_manager.SUPPORTED_LANGUAGES[current_lang]['name']
                print(f"   Language: {lang_display}\n")
                continue

            # Regular quote analysis
            result = bot.analyze_complete(user_input)
            display_analysis(result)

        except KeyboardInterrupt:
            print("\n\n Interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"\n Unexpected error: {e}\n")


if __name__ == "__main__":
    main()
