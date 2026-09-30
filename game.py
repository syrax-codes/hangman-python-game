import random
from words import WORDS, HINTS
from stats import SessionStats

DIFFICULTIES = {
    "easy":   {"lives": 8, "multiplier": 1, "hint_cost": 1},
    "medium": {"lives": 6, "multiplier": 2, "hint_cost": 2},
    "hard":   {"lives": 4, "multiplier": 3, "hint_cost": 3},
}
DEFAULT_DIFFICULTY = "medium"


def ask(prompt):  # NEW: the single place input is read
    """Read, trim and lowercase input. Ctrl+C / Ctrl+D count as /quit."""
    try:
        return input(prompt).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return "/quit"


class HangmanGame:
    def __init__(self):
        # Session-level state (persists across rounds)
        self.score = 0
        self.streak = 0
        self.category = "technology"
        self.difficulty = DEFAULT_DIFFICULTY
        self.stats = SessionStats()

        # Round-level state (rebuilt in start_round)
        self.secret = ""
        self.guessed = set()
        self.wrong = set()
        self.lives = 0
        self.multiplier = 1
        self.hint_cost = 0
        self.hint_used = False

    def start_round(self):
        rules = DIFFICULTIES[self.difficulty]
        self.secret = random.choice(WORDS[self.category])
        self.guessed.clear()
        self.wrong.clear()
        self.lives = rules["lives"]
        self.multiplier = rules["multiplier"]
        self.hint_cost = rules["hint_cost"]
        self.hint_used = False

    def masked(self):
        return " ".join(ch if ch in self.guessed else "_" for ch in self.secret)

    def won(self):
        return all(ch in self.guessed for ch in set(self.secret))

    def guess(self, letter):
        # CHANGED: every rejection happens BEFORE any state is touched
        if letter == "":
            return "Nothing entered. Type a letter, /hint or /quit."
        if len(letter) != 1 or not (letter.isascii() and letter.isalpha()):
            return "Enter a single letter (a-z)."
        if letter in self.guessed or letter in self.wrong:
            return "Already guessed."
        if letter in self.secret:
            self.guessed.add(letter)
            return "Correct."
        self.wrong.add(letter)
        self.lives -= 1
        return "Wrong."

    def use_hint(self):
        # CHANGED: always returns the full message, so the caller prints once
        if self.hint_used:
            return "Hint already used this round."
        self.hint_used = True
        text = HINTS.get(self.secret, "No hint available.")
        return f"Hint: {text} (costs {self.hint_cost} points)"

    def settle_score(self, won):
        points = (5 + self.streak) * self.multiplier if won else 0
        if self.hint_used:
            points -= self.hint_cost
        self.score = max(0, self.score + points)
        return points

    def print_summary(self):
        print("\n--- Session Summary ---")
        print("Rounds played:", self.stats.rounds)
        print("Rounds won:", self.stats.wins)
        print("Best streak:", self.stats.best_streak)
        print("Final score:", self.score)

    def play_round(self):
        self.start_round()
        print(f"\nDifficulty: {self.difficulty} | Lives: {self.lives} | "
              f"Score x{self.multiplier} | Hint costs {self.hint_cost}")
        while self.lives > 0 and not self.won():
            print("\nWord:", self.masked())
            print("Wrong:", " ".join(sorted(self.wrong)) or "-")
            print("Lives:", self.lives, "Score:", self.score, "Streak:", self.streak)
            raw = ask("Letter, /hint, or /quit: ")
            if raw == "/quit":
                return False
            if raw == "/hint":
                print(self.use_hint())
                continue
            if raw.startswith("/"):  # NEW: unknown commands change nothing
                print("Unknown command. Use /hint or /quit.")
                continue
            print(self.guess(raw))

        if self.won():
            self.streak += 1
            points = self.settle_score(True)
            self.stats.record(True, self.streak)
            print("Solved:", self.secret, f"(+{points} points)")
            return True

        self.streak = 0
        self.settle_score(False)
        self.stats.record(False, self.streak)
        print("Out of lives. The word was:", self.secret)
        return True

    # NEW: one menu routine shared by category and difficulty
    def _choose(self, title, noun, options):
        while True:
            print(f"\n{title}:", ", ".join(options))
            raw = ask(f"Choose {noun} or q: ")
            if raw in ("q", "/quit"):
                return None
            if raw in options:
                return raw
            if raw == "":
                print(f"Nothing entered. Type a {noun} name or q.")
            elif raw == "/hint":
                print("Hints are only available during a round.")
            else:
                print(f"Unknown {noun}.")

    def choose_category(self):
        return self._choose("Categories", "category", WORDS)

    def choose_difficulty(self):
        return self._choose("Difficulty", "difficulty", DIFFICULTIES)

    def ask_another_round(self):  # NEW: strict y/n, re-asks on anything else
        while True:
            raw = ask("Another round? [y/n]: ")
            if raw in ("y", "yes"):
                return True
            if raw in ("n", "no", "q", "/quit"):
                return False
            print("Please answer y or n.")

    def run(self):
        print("Hangman Challenge")
        print("A session consists of multiple rounds.")
        while True:
            category = self.choose_category()
            if category is None:
                break
            difficulty = self.choose_difficulty()
            if difficulty is None:
                break
            self.category = category
            self.difficulty = difficulty
            if not self.play_round():
                break
            if not self.ask_another_round():
                break
        self.print_summary()  # CHANGED: one exit path, summary printed once