import random
from words import WORDS, HINTS
from stats import SessionStats

# NEW: one place that defines the rules for each difficulty
DIFFICULTIES = {
    "easy":   {"lives": 8, "multiplier": 1, "hint_cost": 1},
    "medium": {"lives": 6, "multiplier": 2, "hint_cost": 2},
    "hard":   {"lives": 4, "multiplier": 3, "hint_cost": 3},
}
DEFAULT_DIFFICULTY = "medium"


class HangmanGame:
    def __init__(self):
        # Session-level state (persists across rounds)
        self.score = 0
        self.streak = 0
        self.category = "technology"
        self.difficulty = DEFAULT_DIFFICULTY  # NEW: the player's choice
        self.stats = SessionStats()

        # Round-level state (rebuilt in start_round)
        self.secret = ""
        self.guessed = set()
        self.wrong = set()
        self.lives = 0
        self.multiplier = 1      # NEW
        self.hint_cost = 0       # NEW
        self.hint_used = False

    def start_round(self):
        # Round rules are re-read from the table every round: nothing leaks
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
        if len(letter) != 1 or not letter.isalpha():
            return "Enter one letter."
        if letter in self.guessed or letter in self.wrong:
            return "Already guessed."
        if letter in self.secret:
            self.guessed.add(letter)
            return "Correct."
        self.wrong.add(letter)
        self.lives -= 1
        return "Wrong."

    def use_hint(self):
        # CHANGED: no score change here. The cost is applied once, in
        # settle_score(), so it is identical for wins and losses.
        if self.hint_used:
            return None
        self.hint_used = True
        return HINTS.get(self.secret, "No hint available.")

    def settle_score(self, won):  # NEW: single place where points change
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
            raw = input("Letter, /hint, or /quit: ").strip().lower()
            if raw == "/quit":
                return False
            if raw == "/hint":
                hint = self.use_hint()
                print(hint if hint else "Hint already used.")
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

    # NEW: menu helpers keep run() short. Each returns None if the player quits.
    def choose_category(self):
        while True:
            print("\nCategories:", ", ".join(WORDS))
            raw = input("Choose category or q: ").strip().lower()
            if raw == "q":
                return None
            if raw in WORDS:
                return raw
            print("Unknown category.")

    def choose_difficulty(self):
        while True:
            print("\nDifficulty:", ", ".join(DIFFICULTIES))
            raw = input("Choose difficulty or q: ").strip().lower()
            if raw == "q":
                return None
            if raw in DIFFICULTIES:
                return raw
            print("Unknown difficulty.")

    def run(self):
        print("Hangman Challenge")
        print("A session consists of multiple rounds.")
        while True:
            category = self.choose_category()
            if category is None:
                self.print_summary()
                return
            difficulty = self.choose_difficulty()
            if difficulty is None:
                self.print_summary()
                return
            self.category = category
            self.difficulty = difficulty
            if not self.play_round():
                self.print_summary()
                return
            again = input("Another round? [y/n]: ").strip().lower()
            if again != "y":
                self.print_summary()
                return