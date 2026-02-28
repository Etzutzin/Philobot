from bot import PhilosophyBot
import locale


def display_analysis(result: dict):
    """Format and display analysis results."""
    if result["status"] == "error":
        print(f"\n❌ Error: {result['message']}\n")
        return

    data = result["data"]
    
    print("\n" + "="*70)
    print("📖 PHILOSOPHICAL ANALYSIS")
    print("="*70)
    
    print(f"\n📌 Input Quote:\n   {data['input_quote']}\n")
    
    if data.get("surface_claim"):
        print(f"🔍 Surface Claim:\n   {data['surface_claim']}\n")
    
    if data.get("hidden_assumption"):
        print(f"⚠️  Hidden Assumption:\n   {data['hidden_assumption']}\n")
    
    if data.get("philosophical_grounding"):
        traditions = ", ".join(data["philosophical_grounding"])
        print(f"📚 Philosophical Grounding:\n   {traditions}\n")
    
    if data.get("revised_quote"):
        print(f"✨ Revised Quote:\n   {data['revised_quote']}\n")
    
    if data.get("similar_canonical_quotes"):
        print("🔗 Similar Philosophical Quotes:")
        for i, q in enumerate(data["similar_canonical_quotes"], 1):
            verified_badge = "" if q.get("verified", True) else "  [UNCERTAIN]"
            score = f" (Match: {q.get('score', 0)})" if q.get('score', 0) > 0 else ""
            # Build attribution without nesting f‑strings
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
        # Detect system language
        system_lang = locale.getlocale()[0]
        default_lang = system_lang.split('_')[0].lower() if system_lang else "en"
        
        # Validate language is supported
        from multilingual import LanguageManager
        supported = LanguageManager().SUPPORTED_LANGUAGES
        if default_lang not in supported:
            default_lang = "en"
        
        bot = PhilosophyBot(language=default_lang)
    except ValueError as e:
        print(f"\n❌ {e}\n")
        return

    print("\n" + "="*70)
    print("🧠 Welcome to Philosophy Bot - Interactive Quote Analysis")
    print("="*70)

    # Initial mode selection
    print("\nAvailable Modes:")
    for mode, description in bot.MODES.items():
        print(f"  • {mode.upper():<12} - {description}")
    
    selected = input("\nSelect mode (default: clarity): ").strip().lower()
    if selected:
        bot.set_mode(selected)

    print(f"\n✓ Mode set to: {bot.mode.upper()}")
    print(f"✓ Language: {bot.language_manager.SUPPORTED_LANGUAGES[bot.language_manager.user_language]['name']}")
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
                print("\n👋 Thank you for using Philosophy Bot!")
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
                    lang = parts[1].lower()
                    if bot.set_language(lang):
                        print()
                    else:
                        print()
                else:
                    print("Usage: /lang <language_code>\n")
                    print(bot.get_available_languages())
                    print()
                continue
            
            # List languages
            if user_input.lower() == "/langs":
                print("\n🌍 Available Languages:")
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
                    elif setting in ["off", "false", "no", "0"]:
                        bot.toggle_auto_language_detection(False)
                    else:
                        print("Usage: /auto_lang <on|off>\n")
                    print()
                else:
                    print("Usage: /auto_lang <on|off>\n")
                continue
            
            # Statistics
            if user_input.lower() == "/stats":
                stats = bot.get_session_stats()
                print(f"\n📊 Session Statistics:")
                print(f"   API Calls: {stats['total_api_calls']}")
                print(f"   Tokens Used: {stats['total_tokens_used']}")
                print(f"   Est. Cost: ${stats['estimated_cost_usd']}")
                print(f"   Quotes Analyzed: {stats['quotes_analyzed']}")
                print(f"   Rate Limit Remaining: {stats['rate_limit_remaining']}/15 per minute")
                print(f"   Language: {bot.language_manager.SUPPORTED_LANGUAGES[stats['current_language']]['name']}\n")
                continue

            # Regular quote analysis
            result = bot.analyze_complete(user_input)
            display_analysis(result)

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}\n")


if __name__ == "__main__":
    main()
