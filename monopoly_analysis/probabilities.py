from dataclasses import dataclass
from collections import Counter, defaultdict
import numpy as np
import game_board


@dataclass(frozen=True)
class MonopolyState:
    position: int  # Field Number
    counter: int  # Doubles Counter / Round in Jail Counter
    in_jail: bool  # True only on Field 10 possible

    def __hash__(self):
        return hash((self.position, self.counter, self.in_jail))


class Probabilities:
    def __init__(self):
        self.game_version = game_board.GermanMonopoly()
        self.dice_probabilities = self.get_dice_probabilities(False)
        self.doubles_probabilities = self.get_doubles_probabilities()
        self.non_doubles_probabilities = self.get_dice_probabilities(True)
        self.board_fields = self.game_version.board_fields
        self.jail_field = self.game_version.jail_field  # 10 (int)
        self.go_in_jail_field = self.game_version.go_in_jail_field  # 30 (int)

    @staticmethod
    def get_dice_probabilities(exclude_doubles: bool = False) -> dict[int, float]:
        if exclude_doubles:
            sums = (
                d1 + d2
                for d1 in range(1, 7)
                for d2 in range(1, 7)
                if d1 != d2
            )
        else:
            sums = (
                d1 + d2
                for d1 in range(1, 7)
                for d2 in range(1, 7)
            )

        sum_counts = Counter(sums)
        total_outcomes = 36

        return {
            dice_sum: round(sum_counts.get(dice_sum, 0) / total_outcomes, 4)
            for dice_sum in range(2, 13)
        }

    @staticmethod
    def get_doubles_probabilities() -> dict[int, float]:
        sums = (
            d1 + d2
            for d1 in range(1, 7)
            for d2 in range(1, 7)
            if d1 == d2
        )

        sum_counts = Counter(sums)
        total_outcomes = 36

        return {
            dice_sum: round(count / total_outcomes, 4)
            for dice_sum, count in sum_counts.items()
        }

    def create_state_space(self) -> list[MonopolyState]:
        states = []
        for pos in self.board_fields:
            if pos == self.go_in_jail_field:  # it's not possible to end a move on "go in jail"-field!
                continue
            for counter in range(3):
                states.append(MonopolyState(pos, counter, False))  # counter = doubles streak
                if pos == self.jail_field:
                    states.append(MonopolyState(pos, counter, True))  # counter = rounds in jail

        return states

    def create_transition_matrix(self, state_space: list[MonopolyState]):
        probs_dice = self.dice_probabilities
        probs_doubles = self.doubles_probabilities

        n_states = len(state_space)
        transition_matrix = np.zeros((n_states, n_states))

