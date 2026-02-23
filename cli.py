from bot import PhilosophyBot

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
            print("Error:", result["message"])
        else:
            print("\nStructured Output:\n")
            print(result["data"])