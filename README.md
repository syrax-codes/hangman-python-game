## Scenario 16 — Hangman Challenge

A multi-round terminal word-guessing game with categories, hints, scoring, and streaks.

## Provided files

- `main.py` — entry point.
- `game.py` — round state, guesses, hints, scoring, and session flow.
- `words.py` — in-memory word and hint data.
- `stats.py` — session statistics support.
- `requirements.txt` — dependency declaration.

## Setup

```bash
python main.py
```

## Before changing the code

Run several rounds and inspect how round state, score, guessed letters, and category
selection are represented. Reproduce the Task 1 issue before modifying it.

## Task 1 — Guess-state correctness

Correct repeated-guess handling so a previously attempted wrong letter cannot consume
another life, and a previously accepted correct letter cannot be counted as a new guess.

**Done when:** each distinct letter affects the round exactly once.

## Task 2 — Complete the session model

Integrate the supplied session-statistics component so rounds played, rounds won, and
best streak are tracked correctly across multiple rounds.

**Done when:** starting a new round resets only round-specific state; session statistics
continue across the whole run.

## Task 3 — Difficulty and scoring

Add difficulty choices that alter the available lives and scoring. Preserve category
selection and make hint usage affect scoring consistently.

**Done when:** difficulty changes round rules without leaking state between rounds.

## Task 4 — Robust input and feedback

Improve command handling for invalid letters, repeated commands, category selection,
and hint usage. Feedback should describe actual player actions once.

**Done when:** malformed input never changes game state and feedback is not duplicated.

## Required testing

Test repeated correct and incorrect guesses, hints, category changes, multiple rounds,
streak resets, difficulty changes, invalid input, and quitting.


## LLM usage

You may use an LLM during the lab. The goal is to use it as a coding assistant while
retaining responsibility for understanding and testing the result.

- Inspect the existing code before asking for changes.
- Ask for explanations when you do not understand a proposed change.
- Test generated code against the stated behaviour and edge cases.
- Keep your complete LLM chat history for submission.
- Do not replace the whole project with an unrelated implementation.
- Keep all state in memory; do not add CSV, JSON, SQLite, or other persistence.

## Submission checklist

- [ ] Task 1 completed and the original defect was reproduced and fixed.
- [ ] Tasks 2–4 completed and tested.
- [ ] Boundary and invalid-input cases tested.
- [ ] No unnecessary external dependencies added.
- [ ] No persistent storage added.
- [ ] Code remains understandable and modular.
- [ ] Complete LLM chat-history link included.

## Folder structure

```text
scenario-04-hangman/
├── README.md
├── requirements.txt
├── main.py
├── game.py
├── words.py
└── stats.py
```

## Submission Checklist

Submission is only the following three things:

- [ ] A 10-second video of gameplay **before** your changes, showing the bug/broken behavior
- [ ] A 10-second video of gameplay **after** your changes, showing the bug fixed and the new features working
- [ ] The Chat/LLM used page link, with the complete chat history

---

## Lab 4 – Vibe Coding Changes

**Tool used:** ChatGPT
**Full chat history:** <https://chatgpt.com/share/6abcbe4b-f358-83e8-b4ca-906867ac224e>

All changes are in `game.py`. `main.py`, `words.py` and `stats.py` are unchanged (`stats.py` is now used). State is kept in memory only: no files, databases or new dependencies.

### Task 1 – Guess-state correctness
- **Bug:** `guess()` only checked correct letters for repeats. Repeating a wrong letter passed the check and cost another life.
- **Fix:** the repeat check now covers both `guessed` and `wrong`. A repeated letter returns "Already guessed." before any state is touched, so each distinct letter affects the round exactly once.

### Task 2 – Session model
- `SessionStats` from `stats.py` is now integrated. Each finished round is recorded with its result and streak.
- Rounds played, rounds won and best streak are tracked across the whole run and printed in a session summary on every exit path (`n`, `q`, `/quit`, Ctrl+C).
- `start_round()` resets only round-specific state (secret, guessed letters, wrong letters, lives, hint flag). Score, streak and stats persist.
- A round abandoned with `/quit` is not counted as played, since it has no result.

### Task 3 – Difficulty and scoring
Difficulty rules live in a single `DIFFICULTIES` table:

| Difficulty | Lives | Score multiplier | Hint cost |
|---|---|---|---|
| easy | 8 | x1 | 1 |
| medium | 6 | x2 | 2 |
| hard | 4 | x3 | 3 |

- Points for a win are `(5 + streak) * multiplier`. A hint subtracts its cost once when the round is settled, for both wins and losses. The score never goes below 0.
- Category and difficulty are chosen before every round, and the rules are re-read from the table in `start_round()`, so nothing leaks between rounds.

### Task 4 – Robust input and feedback
- All input goes through one `ask()` helper (trimmed and lowercased; Ctrl+C / Ctrl+D act as `/quit`).
- Empty input, multiple characters, digits, symbols, non-ASCII letters and unknown `/commands` are rejected before any state changes.
- A repeated `/hint` reports "Hint already used this round." Hints at a menu prompt get a clear message.
- Category, difficulty and "Another round?" prompts re-ask on invalid input. `q` and `/quit` work at every prompt.
- Each action prints its feedback exactly once. `run()` has a single exit path, so the summary prints once.

### Extra feature – Max score display
- At the start of each round and on every turn, the game shows the maximum points still available, and the reduced maximum if a hint is taken. After `/hint`, it shows the reduced maximum.
- It matches what is actually awarded: `(5 + streak + 1) * multiplier`, minus the hint cost.

### How to run
```
python main.py
```
Commands during a round: a single letter, `/hint`, `/quit`.

### Testing done
Repeated correct and wrong guesses, hints (single and repeated), category changes, multiple rounds, streak resets, difficulty changes, invalid input (empty, digits, multi-character, symbols, unknown commands), invalid category/difficulty/y-n answers, and quitting via `/quit`, `q` and Ctrl+C.

### Submission contents (`Lab-4/` folder)
- `before.mp4` – gameplay showing the repeated-wrong-letter bug
- `after.mp4` – gameplay showing the fixes and new features
- Updated code
- Chat history export