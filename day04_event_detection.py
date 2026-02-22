"""
day04_event_detection.py

Detects when a game becomes "interesting":
- Under 5 minutes remaining
- Score difference ≤ 5 (game is close)
Prints a notification the first time the game becomes interesting.
"""

# Configurable thresholds
MAX_TIME_REMAINING_MINUTES = 5   # Game is interesting when under this many minutes left
MAX_SCORE_DIFFERENCE = 5         # Game is interesting when score diff is within this (either way)

# Game states over time: (time_remaining_minutes, score_difference)
# Score difference: positive = we're ahead, negative = we're behind
GAME_STATES = [
    (10, 12),   # 10 min left, up by 12
    (8, 9),
    (6, 7),
    (5, 6),     # still 5 min, not under 5
    (4, 4),     # under 5 min, diff ≤ 5 → interesting
    (3, 3),
    (2, 2),
    (1, 1),
]


def is_interesting(time_remaining: float, score_diff: int) -> bool:
    """Game is interesting if under threshold minutes left and score diff within threshold."""
    return time_remaining < MAX_TIME_REMAINING_MINUTES and abs(score_diff) <= MAX_SCORE_DIFFERENCE


class InterestDetector:
    """
    Processes game states one at a time and notifies when a game first becomes interesting.
    Use this for real-time: create one detector per game and call process() for each
    state as it arrives (e.g. from a WebSocket, API poll, or event stream).
    """

    def __init__(self) -> None:
        self.already_notified = False

    def process(self, time_remaining: float, score_diff: int) -> bool:
        """
        Process one state. Returns True if a notification was printed (first time interesting).
        """
        if is_interesting(time_remaining, score_diff):
            if not self.already_notified:
                print(
                    f"*** GAME GETTING INTERESTING *** "
                    f"{time_remaining} min left, score difference: {score_diff}"
                )
                self.already_notified = True
                return True
        return False


def main() -> None:
    # List version: iterate over pre-loaded states
    detector = InterestDetector()
    for time_remaining, score_diff in GAME_STATES:
        detector.process(time_remaining, score_diff)

    # Real-time version would look like:
    #   detector = InterestDetector()
    #   while True:
    #       state = get_next_state()  # WebSocket, API poll, queue.get(), etc.
    #       detector.process(state.time_remaining, state.score_diff)
    #       # Optional: sleep or wait on I/O so we don't busy-loop
    #   # Reset per game: detector = InterestDetector() when a new game starts
