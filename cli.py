from bot import PhilosophyBot
import json

def main():
    bot = PhilosophyBot()

    print("Modes:", ", ".join(bot.MODES.keys()))
    selected = input("Select mode: ").strip()
    bot.set_mode(selected)

    while True:
        user_input = input("\nEnter quote (or exit): ")

        if user_input.lower() in ["exit", "quit"]:
            break

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
