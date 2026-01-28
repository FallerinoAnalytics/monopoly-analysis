class GermanMonopoly:
    def __init__(self):
        self.board_fields = range(0, 40)
        self.target_fields_chance_cards = [0, 1, 4, 5, 5, 7, 11, 15, 19, 22, 24, 25, 33, 36, 39, 30]
        self.target_fields_community_chest_cards = [0, 2, 17, 30, 33]