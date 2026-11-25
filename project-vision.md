Project vision

What we are building
A Halloween-themed browser learning game for the Kiroween 2026 Frankenstein category. Players answer questions. Every wrong answer feeds a monster and makes it grow. A correct answer does not change the monster's size.

The monster has five growth stages:
1. Stage 1: tiny and harmless (the starting stage)
2. Stage 2: small
3. Stage 3: medium
4. Stage 4: large and threatening
5. Stage 5: devours the player, and the game ends

Each wrong answer moves the monster up one stage. So the player can make
at most three wrong answers and survive, and the fourth one ends the game.

Working title
"FrankySense"

Who it is for
Beginner students learning Python basics: variables, data types, conditions, loops, functions, and lists.

Tech stack
- Front end: React with JavaScript
- Back end: Python
- AI: an AI model API that generates questions and feedback

Rules for Kiro
- I am a first-year student and want to understand every line, so keep code
  simple and add short comments that explain why, not just what.
- Explain each change in plain language when you finish a task.
- Keep files small and focused, one job per file.
- Never put API keys or secrets in the repo. Use a .env file and keep it out of Git.
- Never add the .kiro folder to .gitignore.
- Dark, spooky visual style with readable text.
- Every quiz question must have exactly one correct answer, and the app must check answers in code, never trust the AI to grade itself.
- The game must always be playable. If the AI is unavailable or the API key is missing, use a built-in bank of hand-written questions instead.