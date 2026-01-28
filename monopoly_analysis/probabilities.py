from dataclasses import dataclass
from collections import Counter
import game_board


@dataclass(frozen=True)
class MonopolyState:
    position: int
    counter: int
    in_jail: bool


class Probabilities:
    def __init__(self):
        game_version = game_board.GermanMonopoly()
        self.dice_probabilities_wo_doubles = self.get_dice_probabilities_wo_doubles()
        self.dice_probabilities_of_doubles = self.get_dice_probabilities_of_doubles()
        self.board_fields = range(0, 40)
        self.target_fields_chance_cards = game_version.target_fields_chance_cards
        self.target_fields_community_chest_cards = game_version.target_fields_community_chest_cards

    @staticmethod
    def get_dice_probabilities_wo_doubles() -> dict[int, float]:
        sums = (
            d1 + d2
            for d1 in range(1, 7)
            for d2 in range(1, 7)
            if d1 != d2
        )

        sum_counts = Counter(sums)
        total_outcomes = 30  # 6*6 - 6 Doubles

        return {
            dice_sum: round(sum_counts.get(dice_sum, 0) / total_outcomes, 4)
            for dice_sum in range(2, 13)
        }

    @staticmethod
    def get_dice_probabilities_of_doubles() -> dict[int, float]:
        sums = (
            d1 + d2
            for d1 in range(1, 7)
            for d2 in range(1, 7)
            if d1 == d2
        )

        sum_counts = Counter(sums)
        total_outcomes = 6  # 6 Doubles

        return {
            dice_sum: round(sum_counts.get(dice_sum, 0) / total_outcomes, 4)
            for dice_sum in range(2, 13)
        }

    def get_probabilities_of_chance_cards(self, total_cards: int, pos_changing_cards: int) -> dict[int:float]:
        possible_targets = self.target_fields_chance_cards
        total_cards = total_cards
        pos_changing_cards = pos_changing_cards
        probability_per_card = 1 / total_cards
        probability_no_change = (total_cards - pos_changing_cards) / total_cards
        field_counts = Counter(possible_targets)

        result = {
            field: count * probability_per_card
            for field, count in field_counts.items()
        }

        for chance_field in [7, 22, 36]:  # Chance Card Fields
            if chance_field in result:
                result[chance_field] = probability_no_change

        return result

    def get_probabilities_of_community_chest_cards(self, total_cards: int, pos_changing_cards: int) -> dict[int:float]:
        possible_targets = self.target_fields_community_chest_cards
        total_cards = total_cards
        pos_changing_cards = pos_changing_cards
        probability_per_card = 1 / total_cards
        probability_no_change = (total_cards - pos_changing_cards) / total_cards
        field_counts = Counter(possible_targets)

        result = {
            field: count * probability_per_card
            for field, count in field_counts.items()
        }

        for community_field in [2, 17, 33]:  # Community Chest Card Fields
            if community_field in result:
                result[community_field] = probability_no_change

        return result

    @staticmethod
    def create_state_space() -> list:
        states = []
        for pos in range(40):
            if pos == 10:
                for counter in range(3):
                    states.append(MonopolyState(pos, counter, False))
                    states.append(MonopolyState(pos, counter, True))
            else:
                for counter in range(3):
                    states.append(MonopolyState(pos, counter, False))

        return states

