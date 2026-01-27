from collections import Counter


class Probabilities:
    def __init__(self):
        self.dice_probabilities_wo_doubles = self.get_dice_probabilities_wo_doubles()
        self.board_fields = range(0, 40)
        self.name = "Luis"

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

    def get_dice_probabilities_of_doubles(self) -> dict[int, float]:
        pass

    def get_probabilities_of_chance_cards(self):
        pass

    def get_probabilities_of_community_chest_cards(self):
        pass

    def create_standard_events(self):
        pass

    def create_special_events(self):
        pass

    def create_state_space(self):
        pass

