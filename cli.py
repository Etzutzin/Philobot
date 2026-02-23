from bot import PhilosophyBot
import json

def main():
    bot = PhilosophyBot()

    # Initial mode selection
    print("\n Philosophy Bot - Interactive Mode Selection\n")
    for mode, description in bot.MODES.items():
        print(f"  • {mode.upper():<12} - {description}")
    
    selected = input("\nSelect mode: ").strip().lower()
    bot.set_mode(selected)

    while True:
        print(f"\n[Mode: {bot.mode.upper()}]")
        user_input = input("Enter quote or command (or 'exit'): ").strip()

        if user_input.lower() in ["exit", "quit"]:
            print(" Goodbye!")
            break
        
        if user_input.startswith("/mode "):
            mode = user_input.split()[1].lower()
            bot.set_mode(mode)
            print(f"✓ Mode changed to {bot.mode}")
            continue
        
        if user_input == "/stats":
            stats = bot.get_session_stats()
            print(f"\n Session Stats:")
            print(f"  API Calls: {stats['total_api_calls']}")
            print(f"  Tokens Used: {stats['total_tokens_used']}")
            print(f"  Est. Cost: ${stats['estimated_cost_usd']}")
            continue
        
        if not user_input:
            continue

        # Regular quote analysis
        result = bot.analyze_complete(user_input)

        if result["status"] == "error":
            print(f" Error: {result['message']}")
        else:
            print("\n" + "="*60)
            print("PHILOSOPHICAL ANALYSIS")
            print("="*60)
            
            data = result["data"]
            
            print(f"\n Input Quote:\n{data['input_quote']}\n")
            
            if "surface_claim" in data:
                print(f" Surface Claim:\n{data['surface_claim']}\n")
            
            if "hidden_assumption" in data:
                print(f"  Hidden Assumption:\n{data['hidden_assumption']}\n")
            
            if "philosophical_grounding" in data and data["philosophical_grounding"]:
                traditions = ", ".join(data["philosophical_grounding"])
                print(f" Philosophical Grounding:\n{traditions}\n")
            
            if "revised_quote" in data:
                print(f" Revised Quote:\n{data['revised_quote']}\n")
            
            if "similar_canonical_quotes" in data and data["similar_canonical_quotes"]:
                print(" Similar Philosophical Quotes:")
                for i, q in enumerate(data["similar_canonical_quotes"], 1):
                    verified_badge = "" if q.get("verified", True) else "  [UNCERTAIN]"
                    score = f" (Match: {q.get('score', 0)})" if q.get('score', 0) > 0 else ""
                    print(f"  {i}. \"{q['text']}\"\n     {q.get('attribution_string', f\"— {q['author']}\")} {verified_badge}{score}\n")
            
            print("="*60 + "\n")

if __name__ == "__main__":
    main()

