- Overview

A lightweight CLI "Philosophy Bot" that deconstructs inspirational quotes, it performs a structured five‑step philosophical analysis and configurable tone modes using Hugging Face conversational model.

- Features

• Structured 5‑step analysis — Surface Claim; Hidden Assumption; Philosophical Grounding; The Revision; Anchor Quote (optional).
• Mode switching — , ,  for adjustable tone and critique style.
• Stateless LLM requests — each request is independent to avoid hidden context drift.
• Streaming and synchronous support — choose  for incremental output or  for simple synchronous responses.
• Clean CLI system prompt with constraints — enforces output format, word limit, and headered sections to reduce drift and keep responses machine‑parsable.
• Safe fallbacks for model/task mismatches — the code detects unsupported chat pipelines and falls back to text‑generation endpoints or suggests chat‑capable models.



- Requirements

• Python 3.10+
• huggingface_hub Python package
• Hugging Face access token (fine‑grained) with Inference permissions:
           Make calls to Inference Providers
           Make calls to your Inference Endpoints



- Installation

1. Clone the repository:
```bash
git clone https://github.com/Etzutzin/philosophy-bot.git
cd philosophy-bot
```
2. Create and activate a virtual environment:
```bash
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
**requirements.txt** should include:
```
huggingface_hub>=0.16.0
```



- Configuration and Environment
Set your Hugging Face token and optional model id as environment variables.

Linux / macOS
```bash
export HF_API_KEY="your token"
export MODEL_ID="Qwen/Qwen2.5-7B-Instruct"   # optional; defaults to Qwen
```

Windows PowerShell
```powershell
$env:HF_API_KEY="yourmtoken"
$env:MODEL_ID="Qwen/Qwen2.5-7B-Instruct"

or

setx HF_API_KEY "your token"
```

- Token permissions  
When creating the token in your Hugging Face account, enable:
Make calls to Inference Providers
Make calls to your Inference Endpoints

If you see `401 Unauthorized`, verify the token is set in the same shell session you run the script and that it was copied exactly.


- Usage and Mode Switching
Run the bot:
```bash
python philo_bot.py
```

**Startup**
- You will be prompted to select a mode once:
  ```
  Select mode (clarity / brutal / compassion):
  ```
- Valid modes: **clarity**, **brutal**, **compassion**. Invalid input defaults to **clarity**.

**Mid-session mode switching**
- Change mode at any time by typing:
  ```
  /mode brutal
  /mode compassion
  /mode clarity
  ```
- Exit the program with `exit` or `quit`.

**Synchronous vs Streaming**
- The script defaults to **synchronous** (`stream=False`) for easier debugging. To enable streaming, set `stream=True` when constructing the `PhilosophyBot` instance or set the `stream` variable in the script.

**Example session**
```
Select mode (clarity / brutal / compassion): clarity
Enter a quote: hard times create strong men

Thinking...

**The Surface Claim:** Adversity fosters character development.

**The Hidden Assumption:** This statement implies that only those who experience hardship become strong, ignoring those who may become broken or bitter instead.

**Philosophical Grounding:** This concept aligns with **Existentialism**, particularly as articulated by Jean-Paul Sartre, who argued that individuals must create their own meaning and strength in the face of an indifferent universe.

**The Revision:** Adversity can foster strength, but it is up to the individual to choose how they respond and grow.

**Anchor Quote (Optional):** "Man is defined as a being who defies definitions." - Jean-Paul Sartre

--------------------------------------------------
Enter a quote: /mode brutal
Mode changed to brutal
Enter a quote: everything happens for a reason

Thinking...

**The Surface Claim:** Every event in life has a specific purpose or meaning.

**The Hidden Assumption:** This statement assumes that all events, even negative ones, are inherently meaningful and serve a higher purpose.

**Philosophical Grounding:** This idea aligns with **Existentialism**, particularly the concept that individuals must create their own meaning in a world without inherent purpose. Existentialists like Jean-Paul Sartre argue that life is absurd and that we must invent our own significance.

**The Revision:** It is often comforting to believe that every event has a purpose, but life can be chaotic and indifferent. We must find meaning ourselves, even in difficult circumstances.

**Anchor Quote (Optional):** Jean-Paul Sartre once said, "Hell is other people," highlighting the human struggle to find meaning in a sometimes indifferent world.
--------------------------------------------------
Enter a quote: /mode compassion
Mode changed to compassion
Enter a quote: Follow your passion and success will follow

Thinking...

**The Surface Claim:** Follow your passion, and success will naturally follow.

**The Hidden Assumption:** This ignores the complex nature of success and the role of hard work, skill, and luck.

**Philosophical Grounding:** **Existentialism:** Existentialists argue that individuals must create their own meaning and values, rather than relying on external conditions for happiness and success.

**The Revision:** Success often requires dedication and skill, but pursuing what you are passionate about can provide the motivation to develop these qualities.

**Anchor Quote (Optional):** "Man is defined as a being who desires to desire." - Jean-Paul Sartre


- Troubleshooting

**401 Unauthorized**
- Ensure `HF_API_KEY` is set.
 Linux/macOS: export HF_API_KEY="your token"
 Windows PowerShell: $env:HF_API_KEY="your token" if you wanted to use it only in that session 
                     or setx HF_API_KEY "your token" if you want to set it permanently.

- Confirm token has "Inference" permissions.
 Go to the token creation page.
 Select Fine-grained token.
 Under Inference, check:
 Make calls to Inference Providers
 Make calls to your Inference Endpoints
 Save the token and copy it.


- Revoke old tokens if unsure and create a fresh token.

**Model not supported for chat**

- Error: `model_not_supported` or message saying model is not a chat model.  
  
Fixes
  - Use a model that advertises **conversational/chat** on its model card (e.g., `Qwen/Qwen2.5-7B-Instruct`).
  - Or switch to `text_generation` calls for models that are text-generation only.

Token scope issues

- If `whoami` shows limited role (e.g., `read`), regenerate a token with the required Inference permissions.

Debugging tips

- Start with `stream=False` to get single, clear errors.
- Use the `HfApi` `model_info` to inspect `pipeline_tag` and `private` status if a model is rejected.
- If a model requires license acceptance, accept it on the model card before calling the Inference API.


